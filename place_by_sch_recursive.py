"A KiCAD action plugin to move all footprints to match the schematic positions"

import os

import pcbnew
import wx

from .draw_page import draw_a_page
from .s_expression_parser import S_ExpressionParser

from .paper_diamentions import get_paper_diamentions

from .debug import debug_msg

sexparser = S_ExpressionParser()


class PlaceBySch(pcbnew.ActionPlugin):
    "main class of action plugin"

    def defaults(self):
        """Set the name, category and description of the plugin"""
        self.name = "Place By Sch"
        self.category = "Layout Helper"
        self.description = "places footprints acording to sch"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")

    def get_sch_file_name(self, _board) -> str:
        """Return schematic file name"""
        return _board.GetFileName().replace(".kicad_pcb", ".kicad_sch")

    def get_hirachical_sheetnames(self, sch_file_name) -> list:
        """return a list of hierarchical sheet names and their positions"""
        with open(sch_file_name, encoding="utf8") as sch_file:
            parsed = sexparser.parse_s_expression(sch_file.read())

        sheet_files = []

        for item in parsed:
            if item[0] != "sheet":
                continue

            sheetname = None  # Initialize sheetname to avoid unbound error

            for sheet in item:
                # if not isinstance(sheet, list):
                #     continue

                if sheet[0] == "property" and sheet[1] == '"Sheetname"':
                    sheetname = sheet[2].replace('"', "")

                if sheet[0] == "property" and sheet[1] == '"Sheetfile"':
                    if sheet[3][0] == "at":
                        x_position = sheet[3][1]
                        y_position = sheet[3][2]
                        rotation = sheet[3][3]
                    else:
                        x_position = y_position = rotation = 0
                    if sheetname is not None:
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

    def get_symbols_positions(self, sch_file_name):
        """return a list of symbols and their positions"""
        with open(sch_file_name, encoding="utf8") as sch_file:
            parsed = sexparser.parse_s_expression(sch_file.read())

        symbols = []
        sheet_files = []

        for i in parsed:
            if i[0] == "paper":
                
                paper_width, paper_height = get_paper_diamentions(i)

                debug_msg(f"{paper_width=}, {paper_height=}")

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
            if i[0] == "sheet":
                sheetname = None  # Initialize sheetname to avoid unbound error

                for sheet in i:
                    if sheet[0] == "property" and sheet[1] == '"Sheetname"':
                        sheetname = sheet[2].replace('"', "")

                    if sheet[0] == "property" and sheet[1] == '"Sheetfile"':
                        if sheet[3][0] == "at":
                            x_position = sheet[3][1]
                            y_position = sheet[3][2]
                            rotation = sheet[3][3]
                        else:
                            x_position = y_position = rotation = 0
                        if sheetname is not None:
                            sheet_files.append(
                                {
                                    "sheet_name": sheetname,
                                    "sheet_file": sheet[2].replace('"', ""),
                                    "sheet_path": os.path.join(
                                        os.path.dirname(sch_file_name),
                                        sheet[2].replace('"', ""),
                                    ),
                                    "x_position": x_position,
                                    "y_position": y_position,
                                    "rotation": rotation,
                                }
                            )

        return {
            "paper": {"paper_height": paper_height, "paper_width": paper_width},
            "symbols": symbols,
            "sheet_files": sheet_files,
        }

    def set_footprints_positions(self, _board, sch_page_data, sheet_level):
        """set_footprints_positions"""

        if sheet_level > 0:
            draw_a_page(_board, sch_page_data["paper"], sheet_level)

        symbols = sch_page_data["symbols"]

        for footprint in _board.Footprints():
            for symbol in symbols:
                if symbol["reference"] == footprint.GetReference():
                    footprint.SetPosition(
                        pcbnew.VECTOR2I(
                            pcbnew.FromMM(symbol["x_position"]),
                            pcbnew.FromMM(symbol["y_position"] + (sheet_level * 220)),
                        )
                    )
                    footprint.SetOrientationDegrees(symbol["rotation"])

    def place_footprints(self, _board, sheet_file_path, sheet_level=0):
        """place_footprints"""
        sch_page_data = self.get_symbols_positions(sheet_file_path)
        self.set_footprints_positions(_board, sch_page_data, sheet_level)

        if len(sch_page_data["sheet_files"]) > 0:
            for h_sheet in sch_page_data["sheet_files"]:
                sheet_level += 1
                self.place_footprints(_board, h_sheet["sheet_path"], sheet_level)

    def Run(self):
        """Run the plugin"""
        board = pcbnew.GetBoard()

        if (
            wx.MessageBox(
                "This will move all selected and not locked footprints to match the schematic positions. Continue?",
                "Place By Schematics",
                wx.ICON_QUESTION | wx.YES_NO,
            )
            == wx.YES
        ):
            sch_file_name = self.get_sch_file_name(board)
            self.place_footprints(board, sch_file_name)


# For debugging outside of KiCAD

if __name__ == "__main__":
    BRD_NAME = r"C:\Users\ECHS\Documents\KiCad\9.0\projects\action_plugin\action_plugin.kicad_pcb"
    pbs = PlaceBySch()
    SCH_NAME = pbs.get_sch_file_name(pcbnew.LoadBoard(BRD_NAME))
    _board = pcbnew.LoadBoard(BRD_NAME)
    # prj_dir = os.path.dirname(BRD_NAME)
    # pbs.place_hirachical_sheet_footprints(_board, SCH_NAME)
    # sheet_level = 1
    # sch_pos = pbs.get_symbols_positions(SCH_NAME)
    pbs.place_footprints(_board, SCH_NAME)
    # print(pbs.get_symbols_positions(SCH_NAME))
