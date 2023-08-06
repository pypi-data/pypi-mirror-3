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

from urllib2 import Request, urlopen, HTTPError


class HeadRequest(Request):

    def get_method(self):
        return "HEAD"


__all__ = (
    'Command',
)


class Command(BaseCommand):
    help = "Fix an offset for slots in a summit"
    option_list = BaseCommand.option_list + (
        make_option("-s",
            "--summit",
            dest="summit",
            help="Supply a summit."),
        make_option(
            "-d",
            "--delete",
            dest="delete",
            help="Delete these dead blueprunts",
            action="store_true",
            default=False),
    )

    def handle(self, *args, **options):
        summit = options["summit"]
        delete = options["delete"]
        try:
            summit = Summit.objects.get(name=summit.__str__)
        except Summit.DoesNotExist:
            raise CommandError("Summit doesn't exist: %s" % summit)

        for meeting in summit.meeting_set.all():
            if meeting.spec_url:
                try:
                    urlopen(HeadRequest(meeting.spec_url))
                except HTTPError, e:
                    if e.code == 404:
                        print "%s:" % meeting
                        if delete:
                            print " * Deleted"
                            meeting.delete()
                        else:
                            print " * %s" % meeting.spec_url
                            print (" * http://summit.ubuntu.com/admin/"
                                "schedule/meeting/%s/" % meeting.pk)
                    else:
                        print "fail"
