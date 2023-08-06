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

from django.db import models

from django.contrib.auth.models import User

from summit.schedule.models.summitmodel import Summit
from summit.schedule.models.trackmodel import Track
from summit.schedule.models.attendeemodel import Attendee

__all__ = (
    'Lead',
)


class Lead(models.Model):
    summit = models.ForeignKey(Summit)
    track = models.ForeignKey(Track)
    lead = models.ForeignKey(Attendee, related_name='lead')

    class Meta:
        app_label = 'schedule'
        ordering = ('summit', 'track')
