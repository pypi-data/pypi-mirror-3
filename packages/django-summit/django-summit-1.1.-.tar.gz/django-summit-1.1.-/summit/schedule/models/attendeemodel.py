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
import hashlib
from datetime import datetime

from django.db import models

from django.contrib.auth.models import User

from summit.schedule.models.summitmodel import Summit
from summit.schedule.models.trackmodel import Track
from summit.schedule.models.topicmodel import Topic

__all__ = (
    'Attendee',
    'AttendeeBusy',
)


class Attendee(models.Model):
    summit = models.ForeignKey(Summit)
    user = models.ForeignKey(User)
    start_utc = models.DateTimeField(db_column='start',
                                     verbose_name="Start (UTC)")
    end_utc = models.DateTimeField(db_column='end',
                                   verbose_name="End (UTC)")
    # FIXME restrict to tracks/topics that match summit
    tracks = models.ManyToManyField(Track, blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    crew = models.BooleanField(db_column='crew',
                               verbose_name='Willing to be Crew',
                               default=False)
    secret_key_id = models.CharField(max_length=32, blank=True, null=True)
    
    class Meta:
        app_label = 'schedule'
        ordering = ('user__username', 'summit')

    def __unicode__(self):
        return "%s (%s)" % (self.user.username, self.summit.name)

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

    def get_secret_key(self):
        if not self.secret_key_id:
            # generate a new secret key id
            key = hashlib.md5()
            key.update(str(self.pk))
            key.update(self.user.username)
            key.update(str(random.random()))
            self.secret_key_id = key.hexdigest()
            self.save()
        return self.secret_key_id

    def set_secret_key(self, key):
        self.secret_key_id = key

    secret_key = property(get_secret_key, set_secret_key)

    def update_from_launchpad(self, elem):
        """Update from Launchpad data."""
        # Update attendance start and end times from LP, we always stash
        # naive UTC datetimes into the db since that's what we get out
        start = elem.get("start")
        if start:
            self.start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
        end = elem.get("end")
        if end:
            self.end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")

        self.save()

        # Update user information from LP, we generally do this when they
        # login; but maybe they never will (logic copied from openid auth)
        fullname = elem.get("displayname", '')
        if fullname:
            if ' ' in fullname:
                self.user.first_name, self.user.last_name \
                    = fullname.rsplit(None, 1)
                self.user.first_name = self.user.first_name[:30]
                self.user.last_name = self.user.last_name[:30]
            else:
                self.user.first_name = u''
                self.user.last_name = fullname[:30]
        self.user.save()

    def available(self, slot):
        """Return whether the attendee is available for a given slot."""
        if slot.start_utc < self.start_utc:
            # Slot begins before we arrive
            return False
        if slot.end_utc > self.end_utc:
            # Slot ends after we leave
            return False

        # Slot overlaps or contains a busy period
        for busy in self.busy_set.all():
            if busy.start_utc < slot.end_utc and busy.end_utc > slot.start_utc:
                return False

        return True

    def name(self):
        """Returns a full name, or username if not available."""
        return self.user.get_full_name() or self.user.username


class AttendeeBusy(models.Model):
    attendee = models.ForeignKey(Attendee, related_name='busy_set')
    start_utc = models.DateTimeField(db_column='start',
                                     verbose_name="Start (UTC)")
    end_utc = models.DateTimeField(db_column='end',
                                   verbose_name="End (UTC)")

    class Meta:
        app_label = 'schedule'
        ordering = ('attendee', 'start_utc', 'end_utc')
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
        return self.attendee.summit.localize(self.start_utc)

    def _set_start(self, start):
        self.start_utc = self.attendee.summit.delocalize(start)

    start = property(_get_start, _set_start)

    def _get_end(self):
        return self.attendee.summit.localize(self.end_utc)

    def _set_end(self, end):
        self.end_utc = self.attendee.summit.delocalize(end)

    end = property(_get_end, _set_end)
