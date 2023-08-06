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
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from summit.schedule.fields import NameField

from summit.schedule.models.summitmodel import Summit
from summit.schedule.models.trackmodel import Track

__all__ = (
    'Room',
    'RoomBusy',
)


class Room(models.Model):
    TYPE_CHOICES = (
        (u'open', u'Openly scheduled'),
        (u'plenary', u'Plenary events'),
        (u'closed', u'Closed'),
        (u'private', u'Private'),
    )

    summit = models.ForeignKey(Summit)
    name = NameField(max_length=50)
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES,
                            default=TYPE_CHOICES[0][0])
    size = models.IntegerField(default=0)
    # FIXME tracks must be for the same summit
    # (will require js magic in admin to refresh the boxes)
    tracks = models.ManyToManyField(Track, blank=True)
    start_utc = models.DateTimeField(db_column='start', null=True, blank=True,
                                     verbose_name="Start (UTC)")
    end_utc = models.DateTimeField(db_column='end', null=True, blank=True,
                                   verbose_name="End (UTC)")
    icecast_url = models.URLField(blank=True, verify_exists=False,
                                  verbose_name="Icecast URL")
    irc_channel = models.CharField(max_length=50, verbose_name="IRC Channel", blank=True, help_text="Please enter the IRC channel without the #")
    
    # Whether the room has dial-in capability
    has_dial_in = models.BooleanField(default=False)

    # people who cannot be scheduled here
    # voip, listen-only and icecast urls
    class Meta:
        app_label = 'schedule'
        ordering = ('summit', 'name')

    def __unicode__(self):
        return self.name

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

    @property
    def track(self):
        try:
            return self.tracks.get()
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            return None

    def available(self, slot):
        """Return whether the room is available for a given slot."""
        if self.start_utc is not None and slot.start_utc < self.start_utc:
            # Slot begins before we arrive
            return False
        if self.end_utc is not None and slot.end_utc > self.end_utc:
            # Slot ends after we leave
            return False

        # Slot overlaps or contains a busy period
        for busy in self.busy_set.all():
            if busy.start_utc < slot.end_utc and busy.end_utc > slot.start_utc:
                return False

        return True


class RoomBusy(models.Model):
    room = models.ForeignKey(Room, related_name='busy_set')
    start_utc = models.DateTimeField(db_column='start',
                                     verbose_name="Start (UTC)")
    end_utc = models.DateTimeField(db_column='end',
                                   verbose_name="End (UTC)")

    class Meta:
        app_label = 'schedule'
        ordering = ('room', 'start_utc', 'end_utc')
        verbose_name = 'busy'
        verbose_name_plural = 'busy'

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
        return self.room.summit.localize(self.start_utc)

    def _set_start(self, start):
        self.start_utc = self.room.summit.delocalize(start)

    start = property(_get_start, _set_start)

    def _get_end(self):
        return self.room.summit.localize(self.end_utc)

    def _set_end(self, end):
        self.end_utc = self.room.summit.delocalize(end)

    end = property(_get_end, _set_end)
