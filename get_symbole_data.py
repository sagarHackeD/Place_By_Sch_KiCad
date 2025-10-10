import os

from .paper_diamentions import get_paper_diamentions
from .wx_gui import debug_msg


from .s_expression_parser import S_ExpressionParser

sexparser = S_ExpressionParser()

def get_sch_file_name(_board) -> str:
    """Return schematic file name"""
    return _board.GetFileName().replace(".kicad_pcb", ".kicad_sch")


def get_symbols_positions(sch_file_name):
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
            sheetname = None
            paper_height = 0
            paper_width = 0

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



def get_hirachical_sheetnames( sch_file_name) -> list:
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