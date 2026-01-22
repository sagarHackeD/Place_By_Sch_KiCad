import json

import wx
import pcbnew
from .delete_drawings import delete_drawings_from_layer
from .wx_gui import CheckListDialog, debug_msg

from .compatibility import VECTORIZE_MM
from .draw import draw_a_page, add_page_title
from .pack import MaxRectsBin
from .get_symbol_data import get_symbols_positions


class PlaceBySchPlugin:
    """A KiCAD action plugin to move all footprints to match the schematic positions"""

    def __init__(self, board):
        self.board = board
        self.all_data = []

    def get_sch_file_name(self) -> str:
        """Return schematic file name"""
        return self.board.GetFileName().replace(".kicad_pcb", ".kicad_sch")

    def sch_to_dict(self, file_path, sheet_name="Main Sheet"):
        """Convert schematic to dictionary recursively"""
        self.all_data = []
        self.sch_to_dict_recursive(file_path, sheet_name)
        with open(
            r"C:\Users\ECHS\Documents\KiCad\9.0\scripting\plugins\Place_By_Sch_KiCad\sch_data.json",
            "w",
            encoding="utf8",
        ) as f:
            f.write(json.dumps(self.all_data, indent=4))
        return self.all_data

    def sch_to_dict_recursive(self, file_path, sheet_name):
        """place_footprints"""
        # debug_msg(f"sch_to_dict_recursive {file_path}")
        sch_page_data = get_symbols_positions(file_path, sheet_name)

        self.all_data.append(sch_page_data)

        if len(sch_page_data["sheet_files"]) > 0:
            for h_sheet in sch_page_data["sheet_files"]:
                self.sch_to_dict_recursive(h_sheet["sheet_path"], h_sheet["sheet_name"])

    def pack_pages(self, sorted_papers, selected_sheets=None, advance_mode=False):
        """pack pages"""
        if selected_sheets is None:
            selected_sheets = {}

        main_index = 0

        for index, paper in enumerate(sorted_papers):
            if paper["sheet_name"] == "Main Sheet":
                main_index = index

        elem = sorted_papers.pop(main_index)

        if advance_mode:
            sorted_selected = [
                paper
                for paper in sorted_papers
                if paper["sheet_name"] in selected_sheets
            ]
        else:
            sorted_selected = sorted_papers

        sorted_selected.insert(0, elem)

        offset = 0

        MARGIN = 10
        MAX_SIZE = 2146

        bin_ = MaxRectsBin(MAX_SIZE, MAX_SIZE - offset, allow_rotate=False)

        all_packed = True

        for i in sorted_selected:
            r = bin_.insert(
                i["paper"]["paper_width"] + MARGIN,
                i["paper"]["paper_height"] + MARGIN,
            )
            if r:
                # debug_msg(f"""Placed {i["sheet_name"]} at ({r.x}, {r.y}) size {r.w}x{r.h}""")
                i["cordinates"] = [r.x, r.y]
            else:
                all_packed = False
                # debug_msg(f"""Failed to place {i["sheet_name"]}""")

        return sorted_selected, all_packed

    def place(
        self,
        board,
        checkbox_values=None,
        advance_mode=False,
        layer=pcbnew.User_15,
    ):
        """place_footprints"""

        offset = 0
        int_x = 0
        int_y = offset

        delete_drawings_from_layer(board, layer)

        data = self.sch_to_dict(self.get_sch_file_name())
        sorted_papers = sorted(
            data,
            key=lambda x: (x["paper"]["paper_height"], x["paper"]["paper_width"]),
            reverse=True,
        )

        selected_sheets = [paper["sheet_name"] for paper in sorted_papers]

        if advance_mode:
            checklistdlg = CheckListDialog(None, selected_sheets)
            if checklistdlg.ShowModal() == wx.ID_OK:
                selected_sheets = checklistdlg.get_values()
            checklistdlg.Destroy()

        packed_pages, all_packed = self.pack_pages(
            sorted_papers, selected_sheets, advance_mode=True
        )

        if all_packed:
            for page in packed_pages:
                if page["sheet_name"] in selected_sheets or not advance_mode:
                    try:
                        w = page["paper"]["paper_width"]
                        h = page["paper"]["paper_height"]
                        x = page["cordinates"][0] + int_x
                        y = page["cordinates"][1] + int_y

                        draw_a_page(board, w, h, x, y, layer)
                        add_page_title(board, x, y, page["sheet_name"], layer)
                        self.place_footprints(board, page, x, y, checkbox_values)

                    except Exception as e:
                        debug_msg(f"Error processing {page['sheet_name']}: {e}")
        else:
            wx.MessageBox(
                "Not all sheets could be placed on the board at a time. Please use the 'Advance' option to select specific sheets.",
                "Packing Error",
                wx.OK | wx.ICON_ERROR,  # ignore
            )

        # if selected_sheets is None:
        #     selected_sheets = []

        # self.move_all_footprints_out(board)

    def move_all_footprints_out(self, board):
        offset = 0
        max_height = 0
        for footprint in board.Footprints():
            if footprint.IsSelected() and not footprint.IsLocked():
                footprint.SetPosition(
                    VECTORIZE_MM(
                        offset,
                        0,
                    )
                )
                bbox = footprint.GetBoundingBox()
                offset += bbox.GetWidth()
                max_height = max(max_height, bbox.GetHeight())

    def place_footprints(self, board, page, x, y, checkbox_values):
        """place_footprints"""
        placed = 0
        for footprint in board.Footprints():
            for symbol in page["symbols"]:
                if (
                    symbol["reference"] == footprint.GetReference()
                    and (footprint.IsSelected() or checkbox_values[1])
                    and (not footprint.IsLocked() or checkbox_values[0])
                ):
                    footprint.SetPosition(
                        VECTORIZE_MM(
                            pcbnew.FromMM(symbol["x_position"] + x),
                            pcbnew.FromMM(symbol["y_position"] + y),
                        )
                    )
                    footprint.SetOrientationDegrees(symbol["rotation"])
                    placed += 1
        return placed


## debug_msg("First select footprints you want to place or ctrl+a")
