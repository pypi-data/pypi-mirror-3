#!/usr/bin/python

from django.core.management.base import LabelCommand
from django.conf import settings

import subprocess
import sys
import os

def write_version_strings(version):
    try:
        from bzrlib.branch import Branch
        branch = Branch.open_containing('.')[0]
        bzr_revno = '%s' % (int(branch.revno())+1)
    except:
        bzr_revno = 'unknown'

    file_name = os.path.join(settings.PROJECT_PATH, "version")
    if os.path.exists(file_name):
        os.remove(file_name)
    f = open(file_name, "w")
    f.write("""version: %s
revno: %s
""" % (version, bzr_revno))
    f.close()
    return (version, bzr_revno)

class Command(LabelCommand):
    help = "Prepare release of The Summit Scheduler. Please pass <version> as an argument."

    def handle_label(self, label, **options):
        (version, bzr_revno) = write_version_strings(label)
        subprocess.call(["bzr", "tag", version])
        print >> sys.stdout, "Released %s." % label
