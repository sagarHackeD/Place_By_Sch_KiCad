import pcbnew


def draw_a_page(board, page, page_start_position, layer=pcbnew.Dwgs_User):
    """draw a rectangle"""

    # if page_start_position == 0:
    #     return

    page_height = page["paper_height"]
    page_width = page["paper_width"]

    rect = pcbnew.PCB_SHAPE(board)
    rect.SetShape(pcbnew.SHAPE_T_RECT)
    rect.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(0), pcbnew.FromMM(page_start_position)))
    rect.SetEnd(
        pcbnew.VECTOR2I(
            pcbnew.FromMM(page_width), pcbnew.FromMM(page_start_position + page_height)
        )
    )
    rect.SetLayer(layer)
    rect.SetWidth(pcbnew.FromMM(0.15))
    board.Add(rect)
