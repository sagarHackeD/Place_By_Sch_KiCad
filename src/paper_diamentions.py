"""get paper dimensions in mm"""

from .wx_gui import debug_msg


def get_paper_diamentions(page_data):
    """get paper dimensions in mm"""

    page = page_data[1].replace('"', "")

    # determine orientation (original logic kept)
    try:
        orientation = "portrait" if page_data[2] == "portrait" else "landscape"
    except IndexError:
        orientation = "landscape"

    # base dimensions (height, width) in mm for portrait orientation
    if page == "A5":
        h,w = 148, 210
    elif page == "A4":
        h,w = 210, 297
    elif page == "A3":
        h,w= 297, 420
    elif page == "A2":
        h,w = 420, 594
    elif page == "A1":
        h,w= 594, 841
    elif page == "A0":
        h,w = 841, 1189
    elif page == "A":
        h,w = 841, 1189
    elif page == "B":
        h,w = 1030, 1456
    elif page == "C":
        h,w = 1297, 1832
    elif page == "D":
        h,w = 1456, 2059
    elif page == "E":
        h,w = 2059, 2916
    elif page == "Letter":
        w, h = 216, 279
    elif page == "Legal":
        h,w = 216, 356
    elif page == "User":
        # for User the page_data provides width and height
        width = float(page_data[2])
        height = float(page_data[3])
        w, h = width, height
    else:
        debug_msg(f"Unknown page size '{page}', defaulting to A4")
        h,w = 210, 297

    # flip if orientation is Landscape
    if orientation == "landscape":
        return h, w
    return w, h
