"""Provide information about pages

PAGES: Read from the pages.ini file

    * Used by raisin.pyramid to register pages in Pyramid

    * Used by raisin.restyler to render pages

"""

import os
from configobj import ConfigObj

PAGES = ConfigObj(os.path.join(os.path.dirname(__file__), "pages.ini"))
