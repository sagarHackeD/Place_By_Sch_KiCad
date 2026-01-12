import pcbnew

from .compatibility import VECTORIZE_MM


def draw_a_page(board, w, h, x, y, layer=pcbnew.Dwgs_User):
    """draw a rectangle"""

    # if page_start_position == 0:
    #     return

    page_height = h
    page_width = w

    rect = pcbnew.PCB_SHAPE(board)
    rect.SetShape(pcbnew.SHAPE_T_RECT)
    rect.SetStart(VECTORIZE_MM(pcbnew.FromMM(x), pcbnew.FromMM(y)))

    rect.SetEnd(
        VECTORIZE_MM(pcbnew.FromMM(page_width + x), pcbnew.FromMM(page_height + y))
    )
    rect.SetLayer(layer)
    rect.SetWidth(pcbnew.FromMM(0.15))
    board.Add(rect)