import pcbnew


def VECTORIZE_MM(x, y):
    try:
        return pcbnew.VECTOR2I(x, y)
    except:
        return pcbnew.wxPoint(x, y)
