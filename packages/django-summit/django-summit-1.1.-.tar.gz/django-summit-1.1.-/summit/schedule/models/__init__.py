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

from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete

from summitmodel import *
from trackmodel import *
from topicmodel import *
from slotmodel import *
from roommodel import *
from attendeemodel import *
from meetingmodel import *
from participantmodel import *
from agendamodel import *
from crewmodel import *
from leadmodel import *


def meeting_update_callback(sender, **kwargs):
    # Invalidate meeting HTML cache
    instance = kwargs['instance']
    if isinstance(instance, Meeting):
        cache.set('meeting-html-%d' % instance.id, None)
        cache.set('meeting-track-html-%d' % instance.id, None)
    elif isinstance(instance, Agenda):
        cache.set('meeting-html-%d' % instance.meeting.id, None)
        cache.set('meeting-track-html-%d' % instance.meeting.id, None)


post_save.connect(meeting_update_callback, sender=Meeting)
post_save.connect(meeting_update_callback, sender=Agenda)
pre_delete.connect(meeting_update_callback, sender=Agenda)
