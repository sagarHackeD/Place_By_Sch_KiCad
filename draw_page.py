import pcbnew

def draw_a_page(board, page, index, layer=pcbnew.Dwgs_User):
    """draw a rectangle"""

    page_height = page["paper_height"]
    page_width =  page["paper_width"]
    margin = 10
    y = (page_height + margin) * index

    rect = pcbnew.PCB_SHAPE(board)
    rect.SetShape(pcbnew.SHAPE_T_RECT)
    rect.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(0), pcbnew.FromMM(y)))
    rect.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(page_width), pcbnew.FromMM(y + 210)))
    rect.SetLayer(layer)
    rect.SetWidth(pcbnew.FromMM(0.15))
    board.Add(rect)
