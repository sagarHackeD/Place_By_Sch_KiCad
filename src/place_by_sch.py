"A KiCAD action plugin to move all footprints to match the schematic positions"

import os
import pcbnew
import wx

from .compatibility import VECTORIZE_MM
from .draw import draw_a_page, add_page_title
from .pack import MaxRectsBin
from .wx_gui import ActionDialog, debug_msg
from .get_symbol_data import get_symbols_positions


class CheckListDialog(wx.Dialog):
    def OnAllLayers(self, _):
        for i in range(self.sheet_checkboxs.GetCount()):
            self.sheet_checkboxs.Check(i, True)

    def OnNoLayers(self, _):
        for i in range(self.sheet_checkboxs.GetCount()):
            self.sheet_checkboxs.Check(i, False)

    def __init__(
        self,
        parent,
        choices,
        title="Select Sheets to place",
        size=(400, 500),
    ):
        super().__init__(parent, title=title, size=size)
        choices = choices or []

        vbox = wx.BoxSizer(wx.VERTICAL)

        # First CheckListBox
        vbox.Add(wx.StaticText(self, label="Sheets"), 0, wx.ALL, 5)
        self.sheet_checkboxs = wx.CheckListBox(self, choices=choices)
        vbox.Add(self.sheet_checkboxs, 1, wx.EXPAND | wx.ALL, 5)
        # self.sheet_checkboxs.SetChecked(0, True)  # Pre-check Python

        allLayersBtn = wx.Button(self, label="All layers")
        self.Bind(wx.EVT_BUTTON, self.OnAllLayers, id=allLayersBtn.GetId())

        noLayersBtn = wx.Button(self, label="No layers")
        self.Bind(wx.EVT_BUTTON, self.OnNoLayers, id=noLayersBtn.GetId())

        vbox.Add(allLayersBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        vbox.Add(noLayersBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # OK / Cancel buttons
        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(btns, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(vbox)

    def get_values(self):
        return [
            self.sheet_checkboxs.GetString(i)
            for i in self.sheet_checkboxs.GetCheckedItems()
        ]


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
        return self.all_data

    def sch_to_dict_recursive(self, file_path, sheet_name="Main Sheet"):
        """place_footprints"""
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
        packed_pages,
        selected_sheets=None,
        advance_mode=False,
        layer=pcbnew.Dwgs_User,
    ):
        """place_footprints"""

        offset = 0
        intX = 0
        intY = offset

        if selected_sheets is None:
            selected_sheets = []

        for page in packed_pages:
            if page["sheet_name"] in selected_sheets or not advance_mode:
                try:
                    w = page["paper"]["paper_width"]
                    h = page["paper"]["paper_height"]
                    x = page["cordinates"][0] + intX
                    y = page["cordinates"][1] + intY

                    draw_a_page(board, w, h, x, y, layer)
                    add_page_title(board, x, y, page["sheet_name"], layer)

                    for footprint in board.Footprints():
                        for symbol in page["symbols"]:
                            if (
                                symbol["reference"] == footprint.GetReference()
                                and footprint.IsSelected()
                                and not footprint.IsLocked()
                            ):
                                footprint.SetPosition(
                                    VECTORIZE_MM(
                                        pcbnew.FromMM(symbol["x_position"] + x),
                                        pcbnew.FromMM(symbol["y_position"] + y),
                                    )
                                )
                                footprint.SetOrientationDegrees(symbol["rotation"])

                except Exception as e:
                    debug_msg(f"Error processing {page['sheet_name']}: {e}")


class PlaceBySch(pcbnew.ActionPlugin):
    "main class of action plugin"

    def defaults(self):
        """Set the name, category and description of the plugin"""
        self.name = "Place By Sch"
        self.category = "Layout Helper"
        self.description = "places footprints acording to sch"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")

    def Run(self):
        """Run the plugin"""
        # Get the current board
        board = pcbnew.GetBoard()
        pbs_plugin = PlaceBySchPlugin(board)

        dlg = ActionDialog(None)

        result = dlg.ShowModal()

        if result == 1:  # Advance
            data = pbs_plugin.sch_to_dict(pbs_plugin.get_sch_file_name())
            sorted_papers = sorted(
                data,
                key=lambda x: (x["paper"]["paper_height"], x["paper"]["paper_width"]),
                reverse=True,
            )

            selected_sheets = {}

            dlg = CheckListDialog(
                None, [paper["sheet_name"] for paper in sorted_papers]
            )
            if dlg.ShowModal() == wx.ID_OK:
                selected_sheets = dlg.get_values()
            dlg.Destroy()

            packed_pages, all_packed = pbs_plugin.pack_pages(
                sorted_papers, selected_sheets, advance_mode=True
            )

            pbs_plugin.place(board, packed_pages, selected_sheets, advance_mode=True)

        elif result == 2:  # Place
            data = pbs_plugin.sch_to_dict(pbs_plugin.get_sch_file_name())
            sorted_papers = sorted(
                data,
                key=lambda x: (x["paper"]["paper_height"], x["paper"]["paper_width"]),
                reverse=True,
            )

            packed_pages, all_packed = pbs_plugin.pack_pages(
                sorted_papers, advance_mode=False
            )

            if all_packed:
                pbs_plugin.place(board, packed_pages)
            else:
                wx.MessageBox(
                    "Not all sheets could be placed on the board at a time. Please use the 'Advance' option to select specific sheets.",
                    "Packing Error",
                    wx.OK | wx.ICON_ERROR, #ignore
                )
        else:  # Cancel
            pass

        dlg.Destroy()
