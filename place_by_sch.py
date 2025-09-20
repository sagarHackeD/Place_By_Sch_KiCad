"A KiCAD action plugin to snap components to the grid"

import re
import os
import pcbnew


class PlaceBySch(pcbnew.ActionPlugin):
    "main class of action plugin"

    def defaults(self):
        """Set the name, category and description of the plugin"""
        self.name = "Place By Sch"
        self.category = "Layout Helper"
        self.description = "places footprints acording to sch"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")

    def tokenize(self, s):
        "Convert a string into a list of tokens."
        return re.findall(r"\(|\)|[^\s()]+", s)

    def atom(self, token):
        "Numbers become numbers; every other token is a symbol."
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return str(token)

    def parse(self, tokens):
        "Parse a sequence of tokens into an S-expression."
        if len(tokens) == 0:
            raise SyntaxError("unexpected EOF")

        token = tokens.pop(0)

        if token == "(":
            _list = []
            while tokens[0] != ")":
                _list.append(self.parse(tokens))
            tokens.pop(0)  # pop off ')'
            return _list
        elif token == ")":
            raise SyntaxError("unexpected )")
        else:
            return self.atom(token)

    def parse_s_expression(self, s):
        "Parse a string into an S-expression."
        return self.parse(self.tokenize(s))

    def get_sch_file_name(self, _board) -> str:
        """Return schematic file name"""
        pcb_file_name = _board.GetFileName()
        # path = Path(pcb_file_name)
        # sch_file_name = path.with_suffix("." + "kicad_sch")
        return pcb_file_name.replace(".kicad_pcb", ".kicad_sch")

    def get_hirachical_sheetnames(self, sch_file_name) -> list:
        """return a list of hierarchical sheet names and their positions"""
        with open(sch_file_name, encoding="utf8") as sch_file:
            parsed = self.parse_s_expression(sch_file.read())

        sheet_files = []

        for item in parsed:
            if item[0] != "sheet":
                continue

            for sheet in item:
                if not isinstance(sheet, list):
                    continue

                if sheet[0] == "property" and sheet[1] == '"Sheetname"':
                    sheetname = sheet[2].replace('"', "")

                if sheet[0] == "property" and sheet[1] == '"Sheetfile"':
                
                    if sheet[3][0] == "at":
                        x_position = sheet[3][1]
                        y_position = sheet[3][2]
                        rotation = sheet[3][3]
                    else:
                        x_position = y_position = rotation = 0
                    sheet_files.append(
                        {
                            "sheet_name": sheetname,
                            "sheet_file": sheet[2].replace('"', ""),
                            "x_position": x_position,
                            "y_position": y_position,
                            "rotation": rotation,
                        }
                    )
        return sheet_files

    def get_symbols_positions(self, sch_file_name) -> list:
        """return a list of symbols and their positions"""
        with open(sch_file_name, encoding="utf8") as sch_file:
            parsed = self.parse_s_expression(sch_file.read())

        symbols = []

        for i in parsed:
            if i[0] == "symbol":
                footprint = i
                x_position = y_position = rotation = None
                reference = None
                for item in footprint:
                    if isinstance(item, list):
                        if item[0] == "at":
                            x_position = item[1]
                            y_position = item[2]
                            rotation = item[3]
                        if len(item) > 1 and item[1] == '"Reference"':
                            reference = item[2].replace('"', "")
                if (
                    reference is not None
                    and x_position is not None
                    and y_position is not None
                    and rotation is not None
                ):
                    symbols.append(
                        {
                            "reference": reference,
                            "x_position": x_position,
                            "y_position": y_position,
                            "rotation": rotation,
                        }
                    )
        return symbols

    def set_footprints_positions(self, _board, symbols, offset=0):
        """set_footprints_positions"""

        offset = offset * 220  # A4 papper height

        for footprint in _board.Footprints():
            for symbol in symbols:
                if (
                    symbol["reference"] == footprint.GetReference()
                    and footprint.IsSelected()
                    and not footprint.IsLocked()
                ):
                    footprint.SetPosition(
                        pcbnew.VECTOR2I(
                            pcbnew.FromMM(symbol["x_position"]),
                            pcbnew.FromMM(symbol["y_position"] + offset),
                        )
                    )
                    footprint.SetOrientationDegrees(symbol["rotation"])

    def place_primary_sheet_footprints(self, _board, sch_file_name):
        """place_primary_sheet_footprints"""
        symbols = self.get_symbols_positions(sch_file_name)
        self.set_footprints_positions(_board, symbols)

    def place_hirachical_sheet_footprints(self, _board, sch_file_name):
        """place_hirachical_sheet_footprints"""
        for sheet_no, sheet_file_name in enumerate(
            self.get_hirachical_sheetnames(sch_file_name), start=1
        ):

            sheet_file_path = os.path.join(
                os.path.dirname(sch_file_name), sheet_file_name["sheet_file"]
            )
            print(sheet_file_path,sheet_file_name, sheet_no)

            symbols = self.get_symbols_positions(sheet_file_path)
            self.set_footprints_positions(_board, symbols, offset=sheet_no)

    def Run(self):
        """Run the plugin"""
        board = pcbnew.GetBoard()
        sch_file_name = self.get_sch_file_name(board)
        self.place_primary_sheet_footprints(board, sch_file_name)
        self.place_hirachical_sheet_footprints(board, sch_file_name)


if __name__ == "__main__":
    BRD_NAME = r"C:\Users\ECHS\Documents\KiCad\9.0\projects\action_plugin\action_plugin.kicad_pcb"
    pbs = PlaceBySch()
    SCH_NAME = pbs.get_sch_file_name(pcbnew.LoadBoard(BRD_NAME))

    board = pcbnew.LoadBoard(BRD_NAME)


    pbs.place_hirachical_sheet_footprints(board,SCH_NAME)
