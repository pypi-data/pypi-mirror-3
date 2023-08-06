# The Summit Scheduler web application
# Copyright (C) 2008 - 2012 Ubuntu Community, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.core.management.base import BaseCommand, CommandError

from summit.schedule.models import *

from optparse import make_option
import datetime
import sys

__all__ = (
    'Command',
)


class Command(BaseCommand):
    help = "Fix an offset for slots in a summit"
    option_list = BaseCommand.option_list + (
        make_option(
            "-s",
            "--summit",
            dest="summit",
            help="Supply a summit."),
        make_option(
            "-o",
            "--offset",
            dest="offset",
            help="Please supply an hour offset --offset=-1 for example.",
            type=int,
            default=0),
        make_option(
            "-d",
            "--dryrun",
            dest="dryrun",
            help="To test the changes, and see a diff style change",
            action="store_true",
            default=False),
    )

    def handle(self, *args, **options):
        summit = options["summit"]
        offset = options["offset"]
        dryrun = options["dryrun"]

        if not offset:
            print ("Please provide an hour offset as an"
                " option, use --help for more info")

        try:
            summit = Summit.objects.get(name=summit.__str__)
        except Summit.DoesNotExist:
            raise CommandError("Summit doesn't exist: %s" % summit)
        slots = Slot.objects.filter(summit=summit)
        for s in slots:
                fixed_start_utc = (
                    s.start_utc + datetime.timedelta(hours=offset))
                fixed_end_utc = s.end_utc + datetime.timedelta(hours=offset)
                if dryrun:
                    print (
                        "-%s: Start: %s, Ends: %s" %
                        (summit, s.start_utc, s.end_utc))
                    print (
                        "+%s: Start: %s, Ends: %s" %
                        (summit, fixed_start_utc, fixed_end_utc))
                else:
                    try:
                        s.start_utc = fixed_start_utc
                        s.end_utc = fixed_end_utc
                        s.save()

                    except:
                        print "Opps! Unexpected error:", sys.exc_info()[0]
                        raise

        if dryrun:
            print ("**** Please check the output, and if it is correct,"
                " re-run without --dryrun to action ****")
        else:
            print (" * Offset for %s successfully updated by %s hour(s)"
                " for %s slots" % (summit, offset, slots.count()))
