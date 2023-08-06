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

import random

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from summit.schedule.models import Summit

__all__ = (
    'Command',
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        summit = Summit.objects.get()
        print "Randomising %s" % summit

        sets = [
            [
                (
                    summit.room_set.get(name="mobile-a"), # 12
                    summit.room_set.get(name="e5"),
                ),
                (
                    summit.room_set.get(name="mobile-b"), # 9
                    summit.room_set.get(name="c3"),
                ),
                (
                    summit.room_set.get(name="foundations-b"), # 9
                    summit.room_set.get(name="c4"),
                ),
                (
                    summit.room_set.get(name="kernel-b"), # 10
                    summit.room_set.get(name="e4"),
                ),
                (
                    summit.room_set.get(name="qa-b"), # 9
                    summit.room_set.get(name="c5"),
                ),
            ],
            [
                (
                    summit.room_set.get(name="desktop-b"), # 20
                    summit.room_set.get(name="c1-2"),
                ),
                (
                    summit.room_set.get(name="server-b"), # 20
                    summit.room_set.get(name="d1"),
                ),
                (
                    summit.room_set.get(name="community-b"), # 20
                    summit.room_set.get(name="d4"),
                ),
            ],
            [
                (
                    summit.room_set.get(name="community-a"), # 30
                    summit.room_set.get(name="e1-2"),
                ),
                (
                    summit.room_set.get(name="kernel-a"), # 24
                    summit.room_set.get(name="d2"),
                ),
                (
                    summit.room_set.get(name="qa-a"), # 24
                    summit.room_set.get(name="d3"),
                ),
            ],
            [
                (
                    summit.room_set.get(name="desktop-a"), # 50
                    summit.room_set.get(name="h2"),
                ),
                (
                    summit.room_set.get(name="server-a"), # 50
                    summit.room_set.get(name="h1"),
                ),
                (
                    summit.room_set.get(name="foundations-a"), # 48
                    summit.room_set.get(name="b1-3"),
                ),
            ]
        ]

        slots = list(summit.slot_set.all())
        for slot in slots:
            if slot.type != 'open':
                continue

            print slot
            for room_set in sets:
                input_set = [x[0] for x in room_set]
                output_set = [x[1] for x in room_set]

                assert (len(input_set) == len(output_set))

                meetings = []
                for room in input_set:
                    try:
                        agenda = room.agenda_set.get(slot=slot)
                        meetings.append(agenda.meeting)
                    except ObjectDoesNotExist:
                        pass

                for room in output_set:
                    # Check that the room is not in use by a double session
                    slot_num = slots.index(slot)
                    for i in range(slot_num, 0, -1):
                        distance = 2 + slot_num - i
                        prev_slot = slots[i - 1]
                        if prev_slot.type != slot.type:
                            break

                        for agenda in prev_slot.agenda_set.filter(room=room):
                            if agenda.meeting.slots >= distance:
                                print (
                                    "%s is in use by %s" %
                                    (room, agenda.meeting))
                                output_set.remove(room)

                rooms = list(output_set)
                assert (len(meetings) <= len(rooms))

                random.shuffle(meetings)
                random.shuffle(rooms)

                for meeting, room in zip(meetings, rooms):
                    print "%s -> %s" % (meeting, room)
                    room.agenda_set.create(
                        slot=slot,
                        meeting=meeting,
                        auto=True)
