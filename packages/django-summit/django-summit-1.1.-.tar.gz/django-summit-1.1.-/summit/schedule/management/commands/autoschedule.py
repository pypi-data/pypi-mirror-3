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

from summit.schedule.models import Summit

__all__ = (
    'Command',
)


class Command(BaseCommand):

    def handle(self, summit='', *args, **options):
        if not summit:
            for summit in Summit.objects.all():
                print "Auto-scheduling %s" % summit
                summit.fill_schedule()
        else:
            try:
                summit = Summit.objects.get(name=summit)
            except Summit.DoesNotExist:
                raise CommandError("Summit doesn't exist: %s" % summit)
            print "Auto-scheduling %s" % summit
            summit.fill_schedule()
