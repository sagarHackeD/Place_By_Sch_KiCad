"""KiCad Plugin: Place By Schematic Recursive"""

import os
import traceback


LOG_FILE = os.path.expanduser(
    "place_by_sch_plugin_error.log"
)

try:
    from .place_by_sch import PlaceBySch
    PlaceBySch().register()

except Exception:
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
        f.write("\n\n")
