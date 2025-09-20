"""This file is executed when the package is imported (on PCB editor startup)"""

from .place_by_sch import PlaceBySch  # Note the relative import!

PlaceBySch().register()  # Instantiate and register to PCB editor
