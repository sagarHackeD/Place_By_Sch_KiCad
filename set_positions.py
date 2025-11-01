import pcbnew

from .wx_gui import debug_msg
from .draw_page import draw_a_page


def set_footprints_positions(_board, sch_page_data, page_start_position, sheet_level):
    """set_footprints_positions"""

    # if sheet_level > 0:
    #     debug_msg(f"sagar {sheet_level} {page_start_position=}")
    #     draw_a_page(_board, sch_page_data["paper"], page_start_position, sheet_level)

    symbols = sch_page_data["symbols"]

    for footprint in _board.Footprints():
        for symbol in symbols:
            if symbol["reference"] == footprint.GetReference():
                footprint.SetPosition(
                    pcbnew.VECTOR2I(
                        pcbnew.FromMM(symbol["x_position"]),
                        pcbnew.FromMM(symbol["y_position"] + page_start_position),
                    )
                )
                footprint.SetOrientationDegrees(symbol["rotation"])

    # debug_msg(f" before return -> {page_start_position=}")
    
    return sch_page_data["paper"]["paper_height"] + page_start_position + 10
