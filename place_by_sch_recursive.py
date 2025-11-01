"A KiCAD action plugin to move all footprints to match the schematic positions"

import os
import pcbnew

from .draw_page import draw_a_page
from .get_symbol_data import get_sch_file_name, get_symbols_positions
from .set_positions import set_footprints_positions
from .wx_gui import ask_to_run


class PlaceBySch(pcbnew.ActionPlugin):
    "main class of action plugin"

    def defaults(self):
        """Set the name, category and description of the plugin"""
        self.name = "Place By Sch"
        self.category = "Layout Helper"
        self.description = "places footprints acording to sch"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")

    def place_footprints(
        self, _board, sheet_file_path, page_start_position=0, sheet_level=0
    ):
        """place_footprints"""
        sch_page_data = get_symbols_positions(sheet_file_path)
        draw_a_page(_board, sch_page_data["paper"], page_start_position)
        page_start_position = set_footprints_positions(
            _board, sch_page_data, page_start_position
        )

        if len(sch_page_data["sheet_files"]) > 0:
            for h_sheet in sch_page_data["sheet_files"]:
                sheet_level += 1
                page_start_position = self.place_footprints(
                    _board, h_sheet["sheet_path"], page_start_position, sheet_level
                )
        return page_start_position

    def Run(self):
        """Run the plugin"""
        board = pcbnew.GetBoard()

        if ask_to_run():
            sch_file_name = get_sch_file_name(board)
            self.place_footprints(board, sch_file_name)
