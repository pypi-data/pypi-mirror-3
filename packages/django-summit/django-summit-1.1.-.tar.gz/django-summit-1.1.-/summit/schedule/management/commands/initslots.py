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

import datetime
import pytz

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from summit.schedule.models import Summit, Slot

__all__ = (
    'Command',
)


class Command(BaseCommand):
    help = "Create slots for a summit"
    option_list = BaseCommand.option_list + (
        make_option("-s", "--summit",
            dest="summit",
            help="Supply a summit."),
        make_option("-b", "--begin", dest="begin",
            help="Beginning slot time.", default='09:00'),
        make_option("-e", "--end", dest="end",
            help="End slot time.", default='17:00'),
        make_option("-l", "--lunch", dest="lunch",
            help="Lunch Time.", default='13:00'),
        make_option("-p", "--plenary", dest="plenary",
            help="Plenary Time.", default='14:00'),
        make_option("-d", "--duration", dest="duration",
            help="Minutes per slot", type=int, default=60),
        make_option("-i", "--interval", dest="interval",
            help="Minutes between sessions", type=int, default=5),
    )

    def handle(self, *args, **options):
        summit = options["summit"]
        begin = datetime.datetime.strptime(options["begin"], '%H:%M').time()
        end = datetime.datetime.strptime(options["end"], '%H:%M').time()
        lunch = datetime.datetime.strptime(options["lunch"], '%H:%M').time()
        plenary = datetime.datetime.strptime(
                                            options["plenary"],
                                            '%H:%M').time()
        duration = datetime.timedelta(minutes=options["duration"])
        interval = datetime.timedelta(minutes=options["interval"])
        breaktime = datetime.timedelta(minutes=15)
        try:
            summit = Summit.objects.get(name=summit.__str__)
        except Summit.DoesNotExist:
            raise CommandError("Summit doesn't exist: %s" % summit)

        day = datetime.timedelta(days=1)
        hour = datetime.timedelta(hours=1)
        date = summit.date_start
        while date <= summit.date_end:
            slottime = pytz.timezone(summit.timezone).localize(
                        datetime.datetime.combine(date, begin))
            slot_count = 0
            while (slottime - interval).time() <= end:
                slot_count += 1
                start_time = summit.delocalize(slottime)

                # Determines the type of the session
                if slottime.time() == lunch:
                    slot_type = 'lunch'
                elif slottime.time() == plenary:
                    slot_type = 'plenary'
                else:
                    slot_type = 'open'
                slot_length = duration

                # Morning Break
                if slot_count == 2:
                    slot, created = Slot.objects.get_or_create(
                        summit=summit,
                        start_utc=start_time + slot_length - breaktime,
                        end_utc=start_time + slot_length,
                        type='break',
                    )
                    slot_length = slot_length - breaktime
                # Afternoon Break
                elif slot_count == 8:
                    slot, created = Slot.objects.get_or_create(
                        summit=summit,
                        start_utc=start_time,
                        end_utc=start_time + breaktime,
                        type='break',
                    )
                    start_time = start_time + breaktime
                    slot_length = slot_length - breaktime
                    slottime = slottime + interval
                # Non-break intervals
                elif slot_type == 'open':
                    nexthour = slottime + hour
                    if nexthour.time() != lunch \
                    and nexthour.time() != plenary \
                    and slot_count != 7:
                        slot_length = slot_length - interval

                end_time = start_time + slot_length

                # Add the slot
                slot, created = Slot.objects.get_or_create(
                    summit=summit,
                    start_utc=start_time,
                    end_utc=end_time,
                    type=slot_type)

                slottime = slottime + duration

            date = date + day
        print "Initializing slots complete."
