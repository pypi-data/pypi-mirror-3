import os
import sys

from settings import *

SITE_ROOT = 'http://summit.linaro.org'

SITE_ID = 2

try:
    import linaro_website

    TEMPLATE_CONTEXT_PROCESSORS += (
        "linaro_website.media_processor",
        "linaro_website.popup_check",
    )
    TEMPLATE_DIRS += (
        linaro_website.TEMPLATE_DIR,
    )

    THEME_MEDIA = linaro_website.MEDIA_ROOT
except ImportError:
    if not 'init-summit' in sys.argv:
        print "You will need to run ./manage.py init-summit to make The Summit Scheduler fully work."
    else:
        pass

