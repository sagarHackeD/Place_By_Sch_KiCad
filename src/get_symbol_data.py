"""Get symbol data from schematic file."""

import os

from .wx_gui import debug_msg

from .paper_diamentions import get_paper_diamentions
from .s_expression_parser import S_ExpressionParser

sexparser = S_ExpressionParser()


def get_sch_file_name(board) -> str:
    """Return schematic file name"""
    return board.GetFileName().replace(".kicad_pcb", ".kicad_sch")


def get_symbols_positions(sch_file_name, sheet_name="Main Sheet") -> dict:
    """return a list of symbols and their positions"""
    with open(sch_file_name, encoding="utf8") as sch_file:
        parsed = sexparser.parse_s_expression(sch_file.read())

    symbols = []
    sheet_files = []

    paper_height = 210
    paper_width = 297

    for i in parsed:
        if i[0] == "paper":
            print(f"{i}")
            paper_height, paper_width = get_paper_diamentions(i)

            print(f"{paper_height=} {paper_width=}")
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
            h_sheetname = None

            for sheet in i:
                if sheet[0] == "property" and sheet[1] == '"Sheetname"':
                    h_sheetname = handle_spaceed_names(sheet)

                if sheet[0] == "property" and sheet[1] == '"Sheetfile"':
                    h_sheet_path = handle_spaceed_names(sheet)

                    if sheet[3][0] == "at":
                        x_position = sheet[3][1]
                        y_position = sheet[3][2]
                        rotation = sheet[3][3]
                    else:
                        x_position = y_position = rotation = 0
                    if h_sheetname is not None:
                        sheet_files.append(
                            {
                                "sheet_name": h_sheetname,
                                "sheet_file": h_sheet_path,
                                "sheet_path": os.path.join(
                                    os.path.dirname(sch_file_name),
                                    h_sheet_path,
                                ),
                                "x_position": x_position,
                                "y_position": y_position,
                                "rotation": rotation,
                            }
                        )

    return {
        "sheet_name": sheet_name,
        "sheet_path": sch_file_name,
        "paper": {"paper_height": paper_height, "paper_width": paper_width},
        "symbols": symbols,
        "sheet_files": sheet_files,
    }

def handle_spaceed_names(sheet):
    name_or_path = ""
    c = 2
    while 1:
        try:
            " ".join(sheet[2:c]).replace('"', "")
            c += 1
        except TypeError:
            name_or_path = " ".join(sheet[2 : (c - 1)]).replace('"', "")
            break
    return name_or_path


def get_hirachical_sheetnames(sch_file_name) -> list:
    """return a list of hierarchical sheet names and their positions"""
    with open(sch_file_name, encoding="utf8") as sch_file:
        parsed = sexparser.parse_s_expression(sch_file.read())

    sheet_files = []

    for item in parsed:
        if item[0] != "sheet":
            continue

        sheet_name = None  # Initialize sheetname to avoid unbound error

        for sheet in item:
            # if not isinstance(sheet, list):
            #     continue

            if sheet[0] == "property" and sheet[1] == '"Sheetname"':
                sheet_name = sheet[2].replace('"', "")

            if sheet[0] == "property" and sheet[1] == '"Sheetfile"':
                if sheet[3][0] == "at":
                    x_position = sheet[3][1]
                    y_position = sheet[3][2]
                    rotation = sheet[3][3]
                else:
                    x_position = y_position = rotation = 0
                if sheet_name is not None:
                    sheet_files.append(
                        {
                            "sheet_name": sheet_name,
                            "sheet_file": sheet[2].replace('"', ""),
                            "x_position": x_position,
                            "y_position": y_position,
                            "rotation": rotation,
                        }
                    )

    return sheet_files
