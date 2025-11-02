"""Add a title to each page of the Schematic."""

import pcbnew
from .compatibility import VECTORIZE_MM


def add_page_title(board, page_start_position, title="",layer=pcbnew.Dwgs_User):
    """Add a page title text to the PCB at each page."""

    text = pcbnew.PCB_TEXT(board)
    text.SetText(title)
    text.SetPosition(
        VECTORIZE_MM(pcbnew.FromMM(5), pcbnew.FromMM(page_start_position + 5))
    )
    text.SetLayer(layer)
    text.SetTextHeight(pcbnew.FromMM(10))
    text.SetTextWidth(pcbnew.FromMM(10))
    text.SetTextThickness(pcbnew.FromMM(1))
    text.SetMirrored(False)
    text.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    text.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_TOP)
    board.Add(text)

