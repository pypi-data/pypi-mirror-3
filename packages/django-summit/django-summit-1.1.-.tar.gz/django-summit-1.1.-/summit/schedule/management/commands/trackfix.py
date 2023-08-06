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

__all__ = (
    'Command',
)


class Command(BaseCommand):

    def handle(self, summit='', *args, **options):
        if not summit:
            print "Please provide a summit as an option"
        else:
            try:
                summit = Summit.objects.get(name=summit)
            except Summit.DoesNotExist:
                raise CommandError("Summit doesn't exist: %s" % summit)
            orphans = Meeting.objects.filter(tracks=None, summit=summit)
            tracks = list(summit.track_set.all())
            # sort the tracks by length of name so that we take
            # more-specific matches first. We shouldn't have track
            # overlaps like this as it's confusing for people, but if
            # it happens this is the likely desired behaviour
            tracks.sort(cmp=lambda x, y: cmp(len(x.slug), len(y.slug)),
                    reverse=True)
            for o in orphans:
                print o
                try:
                    o_str = str(o)
                    for track in tracks:
                        if o_str.startswith(track.slug):
                            print "%s is now part of %s" % (o_str, track)
                            o.tracks.add(track)
                            o.save()
                            break
                    if o.tracks.all().count() < 1:
                        print "%s is still without a track" % o_str
                except:
                    pass # means it's probably a manual scheduled item
