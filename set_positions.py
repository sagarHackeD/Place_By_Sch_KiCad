import pcbnew

def set_footprints_positions(_board, sch_page_data, page_start_position):
    """set_footprints_positions"""

    symbols = sch_page_data["symbols"]

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
                        pcbnew.FromMM(symbol["y_position"] + page_start_position),
                    )
                )
                footprint.SetOrientationDegrees(symbol["rotation"])

    return sch_page_data["paper"]["paper_height"] + page_start_position + 10
