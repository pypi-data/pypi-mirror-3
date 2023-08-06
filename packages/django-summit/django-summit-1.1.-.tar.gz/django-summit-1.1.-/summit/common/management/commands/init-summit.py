#!/usr/bin/python

from django.core.management.base import NoArgsCommand

import settings

import subprocess
import os


class Command(NoArgsCommand):
    help = "Make sure The Summit Scheduler is set up properly."

    def handle_noargs(self, **options):
        path = settings.PROJECT_PATH

        print " * Adding Bzr Apps:",
        if os.path.isdir(os.path.join(path, "bzr_apps", ".bzr")):
            print "not necessary."
        else:
            subprocess.call(["bzr", "branch", "-q", "--use-existing-dir",
                             "lp:ubuntu-django-foundations/bzr-apps",
                             "bzr_apps"])
            print "added."
