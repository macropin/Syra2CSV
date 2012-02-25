# Settings for syra2csv

import os

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

TEMP_DIR = os.path.join(PROJECT_PATH, '..', 'tmp',)

RESELLER_USERNAME='' # Set Me
RESELLER_PASSWORD='' # Set Me

REPORT_PAGES_SCRAPE = 1 # How many pages to scrape

DO_DOWNLOAD = True # Or False, used for testing
DEBUG = False

# NB It's a better idea to put your settings in a local_settings.py overrides file.
try:
    from local_settings import *
except ImportError:
    pass
