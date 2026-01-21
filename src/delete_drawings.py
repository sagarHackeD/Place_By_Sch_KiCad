import pcbnew

def delete_drawings_from_layer(board, layer=pcbnew.Dwgs_User):
    """Delete all drawings from a specific layer"""

    for item in board.GetDrawings():
        if item.GetLayer() == layer:
            board.Remove(item)
