import pcbnew
from .draw_page import draw_a_page


def set_footprints_positions(_board, sch_page_data, sheet_level):
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
