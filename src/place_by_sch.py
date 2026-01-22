"A KiCAD action plugin to move all footprints to match the schematic positions"

import os

import pcbnew
import wx

from .delete_drawings import delete_drawings_from_layer

from .place_by_sch_plugin import PlaceBySchPlugin
from .wx_gui import ActionDialog, CheckListDialog, ProgressDialog, debug_msg


import json


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

        checkbox_values = dlg.get_checkbox_values()

        self.custom_layer(board,pcbnew.User_15,"PlaceBySch")


        if result == 1:  # Advance
            # progress_dlg = ProgressDialog(None)
            # progress_dlg.ShowModal()

            delete_drawings_from_layer(board, layer=pcbnew.User_15)

            data = pbs_plugin.sch_to_dict(pbs_plugin.get_sch_file_name())
            sorted_papers = sorted(
                data,
                key=lambda x: (x["paper"]["paper_height"], x["paper"]["paper_width"]),
                reverse=True,
            )

            selected_sheets = {}

            checklistdlg = CheckListDialog(
                None, [paper["sheet_name"] for paper in sorted_papers]
            )
            if checklistdlg.ShowModal() == wx.ID_OK:
                selected_sheets = checklistdlg.get_values()
            checklistdlg.Destroy()

            packed_pages, all_packed = pbs_plugin.pack_pages(
                sorted_papers, selected_sheets, advance_mode=True
            )

            pbs_plugin.place(board, packed_pages, selected_sheets, checkbox_values, advance_mode=True)

            # progress_dlg.Destroy()

        elif result == 2:  # Place
            # progress_dlg = ProgressDialog(None)
            # progress_dlg.ShowModal()

            # debug_msg(f"Placing   {pbs_plugin.get_sch_file_name()}")

            dlg.gauge.Pulse()

            delete_drawings_from_layer(board, layer=pcbnew.User_15)

            data = pbs_plugin.sch_to_dict(pbs_plugin.get_sch_file_name())

            sorted_papers = sorted(
                data,
                key=lambda x: (x["paper"]["paper_height"], x["paper"]["paper_width"]),
                reverse=True,
            )

            packed_pages, all_packed = pbs_plugin.pack_pages(
                sorted_papers, advance_mode=False
            )

            with open(r"C:\Users\ECHS\Documents\KiCad\9.0\scripting\plugins\Place_By_Sch_KiCad\log.json","w",encoding="utf-8") as f:
                f.write(json.dumps(packed_pages, indent=4))

            if all_packed:
                pbs_plugin.place(board, packed_pages, checkbox_values=checkbox_values)
            else:
                wx.MessageBox(
                    "Not all sheets could be placed on the board at a time. Please use the 'Advance' option to select specific sheets.",
                    "Packing Error",
                    wx.OK | wx.ICON_ERROR,  # ignore
                )
            # progress_dlg.EndModal(wx.ID_OK)
            # progress_dlg.Destroy()

        elif result == 3:
            delete_drawings_from_layer(board, layer=pcbnew.User_15)
        else:  # Cancel
            pass

        dlg.Destroy()

    def custom_layer(self, board,layer,name):
        lset = board.GetEnabledLayers()
        lset.AddLayer(layer)
        board.SetEnabledLayers(lset)
        board.SetLayerName(layer, name)






#         import pcbnew

# board = pcbnew.GetBoard()

# # Get current enabled layers
# lset = board.GetEnabledLayers()

# # Enable a user layer
# lset.AddLayer(pcbnew.User_1)

# # Apply back to board
# board.SetEnabledLayers(lset)

# # Rename it
# board.SetLayerName(pcbnew.User_1, "My_Custom_Layer")

# pcbnew.Refresh()

