import pcbnew

from .debug import debug_msg

def get_page_size(page):
    """get_page_size"""

    if page == "A5":
        return 148, 210
    if page == "A4":
        return 210, 297
    if page == "A3":
        return 297, 420
    if page == "A2":
        return 420, 594
    if page == "A1":
        return 594, 841
    if page == "A0":
        return 841, 1189
    if page == "A":
        return 841, 1189
    if page == "B":
        return 1030, 1456
    if page == "C":
        return 1297, 1832
    if page == "D":
        return 1456, 2059
    if page == "E":
        return 2059, 2916
    if page == "Letter":
        return 216, 279
    if page == "Legal":
        return 216, 356

    debug_msg(f"Unknown page size '{page}', defaulting to A4")
    return 210, 297  # Default to A4



def draw_a_page(board, page, index, layer=pcbnew.Dwgs_User):
    """draw a rectangle"""

    page_height, page_width = get_page_size(page)
    margin = 10
    y = (page_height + margin) * index

    rect = pcbnew.PCB_SHAPE(board)
    rect.SetShape(pcbnew.SHAPE_T_RECT)
    rect.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(0), pcbnew.FromMM(y)))
    rect.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(page_width), pcbnew.FromMM(y + 210)))
    rect.SetLayer(layer)
    rect.SetWidth(pcbnew.FromMM(0.15))
    board.Add(rect)
