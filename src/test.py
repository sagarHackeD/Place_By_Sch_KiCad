from get_symbol_data import get_symbols_positions


def sch_to_dict(self, file_path, sheet_name="Main Sheet"):
    """Convert schematic to dictionary recursively"""
    self.all_data = []
    self.sch_to_dict_recursive(file_path, sheet_name)
    return self.all_data

def sch_to_dict_recursive(self, file_path, sheet_name):
    """place_footprints"""
    print(f"sch_to_dict_recursive {file_path}")
    sch_page_data = get_symbols_positions(file_path, sheet_name)

    self.all_data.append(sch_page_data)

    if len(sch_page_data["sheet_files"]) > 0:
        for h_sheet in sch_page_data["sheet_files"]:
            self.sch_to_dict_recursive(h_sheet["sheet_path"], h_sheet["sheet_name"])


sch_to_dict(r"C:\Users\ECHS\Desktop\place_v2\kicad_project_testing\kicad_project_testing.kicad_sch")