import pcbnew

from .compatibility import VECTORIZE_MM


def draw_a_page(board, w, h, x, y, layer=pcbnew.User_15):
    """draw a rectangle"""

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

def add_page_title(board, x, y, title="", layer=pcbnew.User_15):
    """Add a page title text to the PCB at each page."""

    text = pcbnew.PCB_TEXT(board)

    text.SetText(title)
    text.SetPosition(VECTORIZE_MM(pcbnew.FromMM(x + 5), pcbnew.FromMM(y + 5)))

    text.SetLayer(layer)
    text.SetTextHeight(pcbnew.FromMM(10))
    text.SetTextWidth(pcbnew.FromMM(10))
    text.SetTextThickness(pcbnew.FromMM(1))
    text.SetMirrored(False)
    text.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    text.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_TOP)
    board.Add(text)


def add_custom_layer():
    """Add a custom layer to the PCB."""
    board = pcbnew.GetBoard()
    layer_id = pcbnew.User_5
    enabled = board.GetEnabledLayers()
    enabled.AddLayer(layer_id)
    board.SetEnabledLayers(enabled)
    board.SetLayerName(layer_id, "PlaceNySch")
    visible = board.GetVisibleLayers()
    visible.AddLayer(layer_id)
    board.SetVisibleLayers(visible)
    pcbnew.Refresh()
