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

from datetime import datetime

from django.db import models

from django.contrib.auth.models import User

from summit.schedule.models.summitmodel import Summit
from summit.schedule.models.attendeemodel import Attendee

__all__ = (
    'Crew',
)


class Crew(models.Model):
    attendee = models.ForeignKey(Attendee,
                                 related_name='crew_schedule',
                                 limit_choices_to={'crew': True})
    date_utc = models.DateField(db_column='date',
                                verbose_name="Date (UTC)")

    class Meta:
        app_label = 'schedule'
        ordering = ('date_utc', 'attendee')

    def __unicode__(self):
        return '%s on %s' % (self.attendee, self.date_utc)

    def _get_date(self):
        return self.attendee.summit.localize(self.date_utc)

    def _set_date(self, date):
        self.date_utc = self.attendee.summit.delocalize(date)

    date = property(_get_date, _set_date)

