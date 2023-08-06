import os
import sys

from settings import *

SITE_ROOT = 'http://summit.ubuntu.com'


SITE_ID = 1

try:
    import ubuntu_website

    TEMPLATE_CONTEXT_PROCESSORS += (
        "ubuntu_website.media_processor",
        "ubuntu_website.popup_check",
    )
    TEMPLATE_DIRS += (
        ubuntu_website.TEMPLATE_DIR,
    )

    THEME_MEDIA = ubuntu_website.MEDIA_ROOT
except ImportError:
    if not 'init-summit' in sys.argv:
        print "You will need to run ./manage.py init-summit to make The Summit Scheduler fully work."
    else:
        pass

