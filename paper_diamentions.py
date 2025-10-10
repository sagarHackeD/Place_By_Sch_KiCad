
from .wx_gui import debug_msg


def get_paper_diamentions(page_data):
    """get paper dimensions in mm"""

    page = page_data[1].replace('"', "")

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
    if page == "User":
            width = float(page_data[2])
            height = float(page_data[3])
            return width, height

    debug_msg(f"Unknown page size '{page}', defaulting to A4")
    # Default to A4
    return 210, 297