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
import pytz

from django.db import models

from summit.schedule.models.summitmodel import Summit

__all__ = (
    'Slot',
)


class Slot(models.Model):
    TYPE_CHOICES = (
        (u'open', u'Openly scheduled'),
        (u'plenary', u'Plenary event'),
        (u'break', u'Break'),
        (u'lunch', u'Lunch'),
        (u'closed', u'Closed'),
    )

    summit = models.ForeignKey(Summit)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES,
                            default=TYPE_CHOICES[0][0])
    start_utc = models.DateTimeField(db_column='start',
                                     verbose_name="Start (UTC)")
    end_utc = models.DateTimeField(db_column='end',
                                   verbose_name="End (UTC)")

    class Meta:
        app_label = 'schedule'
        ordering = ('summit', 'start_utc', 'end_utc')

    def __unicode__(self):
        return self.span

    @property
    def span(self):
        if self.start.date() == self.end.date():
            return "%s..%s" % (self.start.strftime("%Y-%m-%d %H:%M"),
                               self.end.strftime("%H:%M"))
        else:
            return "%s..%s" % (self.start.strftime("%Y-%m-%dT%H:%M"),
                               self.end.strftime("%Y-%m-%dT%H:%M"))

    def _get_start(self):
        return self.summit.localize(self.start_utc)

    def _set_start(self, start):
        self.start_utc = self.summit.delocalize(start)

    start = property(_get_start, _set_start)

    def _get_end(self):
        return self.summit.localize(self.end_utc)

    def _set_end(self, end):
        self.end_utc = self.summit.delocalize(end)

    end = property(_get_end, _set_end)

    def next(self):
        valid_types = ('closed', 'lunch', 'open', 'plenary')
        range_start = self.summit.delocalize(
            datetime(
                self.start.year,
                self.start.month,
                self.start.day,
                0, 0,
                tzinfo=pytz.timezone(self.summit.timezone)))
        range_end = self.summit.delocalize(
            datetime(
                self.start.year,
                self.start.month,
                self.start.day,
                23, 59,
                tzinfo=pytz.timezone(self.summit.timezone)))
        try:
            next_slot = Slot.objects.filter(
                start_utc__range=(range_start, range_end)).filter(
                    start_utc__gte=self.end_utc).filter(
                        type__in=valid_types).order_by('start_utc')[0]
        except IndexError:
            next_slot = None
        return next_slot

    def previous(self):
        valid_types = ('closed', 'lunch', 'open', 'plenary')
        range_start = self.summit.delocalize(
            datetime(
                self.start.year,
                self.start.month,
                self.start.day,
                0, 0,
                tzinfo=pytz.timezone(self.summit.timezone)))
        range_end = self.summit.delocalize(
            datetime(
                self.start.year,
                self.start.month,
                self.start.day,
                23, 59,
                tzinfo=pytz.timezone(self.summit.timezone)))
        try:
            prev_slot = Slot.objects.filter(
                start_utc__range=(range_start, range_end)).filter(
                    end_utc__lte=self.start_utc).filter(
                        type__in=valid_types).order_by('-start_utc')[0]
        except IndexError:
            prev_slot = None
        return prev_slot
