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

import pytz
import sys
import time
import urllib2

from datetime import datetime, timedelta

try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.query_utils import Q

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from summit.schedule.fields import NameField
from summit.schedule import launchpad

__all__ = (
    'Summit',
    'SummitSprint',
)

#Monkey patch for better use in the admin
User._meta.ordering = ['username']
def unicode_user(user):
    display = []
    if user.first_name:
        display.append(user.first_name)
    if user.last_name:
        display.append(user.last_name)
    if len(display) == 0:
        return user.username
    else:
        return user.username + ' (' +' '.join(display) + ')'
User.__unicode__ = unicode_user

class SummitManager(CurrentSiteManager):
    
    def next(self):
        try:
            return self.order_by('-date_start')[0]
        except IndexError:
            # No summits have been defined in the database yet
            return Summit(name="no_summits", title="No Summits Defined")

class Summit(models.Model):
    STATE_CHOICES = (
        (u'sponsor', u'Sponsorship Requests'),
        (u'review', u'Sponsorship Reviews'),
        (u'schedule', u'Scheduling'),
        (u'public', u'Public'),
    )

    name = NameField(max_length=50)
    title = models.CharField(max_length=100)
    sites = models.ManyToManyField(Site)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=2047, blank=True)
    etherpad = models.URLField(verify_exists=False, max_length=75, blank=False, default='http://pad.ubuntu.com/', help_text="Enter the URL of the etherpad server you would like to use")
    qr = models.URLField(verify_exists=False, max_length=100, blank=True, default='', help_text="Enter the URL of the QR code for mobile device application")
    hashtag = models.CharField(max_length=25, blank=True)
    timezone = models.CharField(max_length=50,
                                choices=[(x, x) for x in pytz.common_timezones])
    last_update = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES,
                             default=STATE_CHOICES[0][0])
    date_start = models.DateField(blank=False, null=True)
    date_end = models.DateField(blank=False, null=True)
    managers = models.ManyToManyField(User, blank=True, related_name='managers')
    schedulers = models.ManyToManyField(User, blank=True, related_name='schedulers')
    
    objects = models.Manager()
    on_site = SummitManager()
    
    class Meta:
        app_label = 'schedule'
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    def localize(self, datetime):
        """Convert a datetime to the summit-local timezone.

        Normally this is used on naive objects from the database which
        contain UTC representations, but it will shift any aware timezone
        properly.
        """
        if datetime.utcoffset() is None:
            datetime = pytz.utc.localize(datetime)
        return datetime.astimezone(pytz.timezone(self.timezone))

    def delocalize(self, datetime):
        """Convert a datetime into a naive UTC representation.

        The returned object is naive and contains the UTC representation
        of the time, which is what we store in the database.  Normally
        this is used on aware objects, if not, the same object is returned.
        """
        if datetime.utcoffset() is not None:
            datetime = datetime.astimezone(pytz.utc)
        return datetime.replace(tzinfo=None)

    def as_localtime(self, datetime):
        return pytz.timezone(self.timezone).localize(datetime)

    @property
    def start(self):
        try:
            return self.slot_set.order_by('start_utc')[0].start
        except IndexError:
            return None

    @property
    def end(self):
        try:
            return self.slot_set.order_by('-end_utc')[0].end
        except IndexError:
            return None

    def days(self):
        day = timedelta(days=1)
        start = self.date_start
        end = self.date_end
        days = [start]
        current = start + day
        while (current <= end):
            days.append(current)
            current = current + day
        return days

    def dates(self):
        """List of dates for this summit.

        Returns sorted naive date objects in local time.
        """
        dates = set()
        dates.update(slot.start.date() for slot in self.slot_set.all())
        dates.update(slot.end.date() for slot in self.slot_set.all())
        return sorted(dates)

    def public_rooms(self):
        """List of public rooms for this summit.

        Returns sorted rooms.
        """

        def by_title(a, b):
            if a.type == 'plenary':
                return -1
            elif b.type == 'plenary':
                return 1
            elif a.track is None:
                return 1
            elif b.track is None:
                return -1
            else:
                return cmp(a.track.title, b.track.title)

        rooms = self.room_set.exclude(Q(type__exact='closed') | Q(type__exact='private'))
        return sorted(rooms, cmp=by_title)

    def open_rooms(self):
        """List of open rooms for this summit.

        Returns sorted rooms.
        """

        def by_title(a, b):
            if a.track is None:
                return 1
            elif b.track is None:
                return -1
            else:
                return cmp(a.track.title, b.track.title)

        rooms = self.room_set.filter(type__exact='open')
        return sorted(rooms, cmp=by_title)

    def private_rooms(self):
        """List fo private rooms for this summit."""
        
        def by_title(a, b):
            if a.track is None:
                return 1
            elif b.track is None:
                return -1
            else:
                return cmp(a.track.title, b.track.title)

        rooms = self.room_set.filter(type__exact='private')
        return sorted(rooms, cmp=by_title)

    def launchpad_sprint_import_urls(self):
        sprints = self.sprint_set.all()
        if sprints.count() > 0:
            urls = [sprint.import_url for sprint in sprints]
        else:
            urls = [("https://launchpad.net/sprints/%s/+temp-meeting-export"
                   % self.name)]
        return urls

    def update_from_launchpad_response(self, response):
        meetings = set()
        for elem in response.find("attendees").findall("person"):
            self.update_attendee_from_launchpad(elem)
        for elem in response.find("unscheduled").findall("meeting"):
            meeting = self.update_meeting_from_launchpad(elem)
            if meeting is not None:
                meetings.add(meeting)
        return meetings

    def _get_sprint_info_from_launchpad(self, url):
        trycounter = 0
        retrytotal = 5
        while trycounter <= retrytotal:
            req = urllib2.Request(url)
            req.add_header("Cache-Control", "no-cache")
            req.add_header("Cookie", "please-don't-cache-me")
            try:
                 export = urllib2.urlopen(req)
            except urllib2.HTTPError, e:
                trycounter += 1
                if trycounter >= retrytotal:
                    print "Error while calling the launchpad API: " + str(e)
                    sys.exit(1)
                else:
                    time.sleep(2)
            else:
                break
        sprint_info = ElementTree.parse(export)
        return sprint_info

    def update_from_launchpad(self):
        """Update from Launchpad data."""
        in_lp = set()
        urls = self.launchpad_sprint_import_urls()
        for url in urls:
            print "Importing from %s" % url
            sprint_info = self._get_sprint_info_from_launchpad(url)
            in_lp |= self.update_from_launchpad_response(sprint_info)

        in_db = set(m for m in self.meeting_set.exclude(spec_url=''))

        for extra in in_db.difference(in_lp):
            if not len(extra.agenda_set.all()):
                print "will delete %s" % extra.name
                extra.delete()

        self.last_update = datetime.utcnow()
        self.save()

    def update_attendee_from_launchpad(self, elem):
        """Update or create single attendee from Launchpad data."""
        username = elem.get("name", "")
        if not username:
            return

        print "user %s" % username

        try:
            attendee = self.attendee_set.get(user__username__exact=username[:30])
        except ObjectDoesNotExist:
            try:
                user = User.objects.get(username__exact=username[:30])
            except ObjectDoesNotExist:
                user = User.objects.create_user(username[:30], '', password=None)
                launchpad.set_user_openid(user)

            # Create with any start/end time since we overwrite shortly
            attendee = self.attendee_set.create(user=user,
                                                start=datetime.utcnow(),
                                                end=datetime.utcnow())

        attendee.update_from_launchpad(elem)

    def update_meeting_from_launchpad(self, elem):
        """Update or create single meeting from Launchpad data."""
        full_name = elem.get("name", "")
        if not full_name:
            return
        name = full_name[:100]

        print "meeting %s" % name
        meeting = ""
        try:
            meeting = self.meeting_set.get(name__exact=name)
        except ObjectDoesNotExist:
            meeting = self.meeting_set.create(name=name, title=full_name[:100])
        except:
            pass

        if meeting:
            meeting.update_from_launchpad(elem)
        return meeting

    def fill_schedule(self):
        """Fill empty slots and rooms in the schedule with unscheduled meetings

        This is a pretty simple best-fit/first-come-first-served scheduler,
        but it suffices.
        """
        for meeting in self.meeting_set.filter(approved='APPROVED', agenda__isnull=True):
            meeting.try_schedule()

    def check_schedule(self):
        """Check the schedule for existant errors."""
        for meeting in self.meeting_set.all():
            for agenda in meeting.agenda_set.all():
                try:
                    missing = meeting.check_schedule(agenda.slot, agenda.room)
                    if len(missing):
                        print "Warning: required people not available: %s at %s in %s: %s" % (
                            meeting, agenda.slot, agenda.room,
                            ', '.join(m.user.username for m in missing))
                except meeting.SchedulingError, e:
                    print "Error: %s at %s in %s: %s" % (meeting,
                                                         agenda.slot,
                                                         agenda.room,
                                                         e)

    def reschedule(self):
        """Delete any automatically created agenda items that have problems."""
        today = datetime.now()
        for meeting in self.meeting_set.all():
            for agenda in meeting.agenda_set.filter(auto=True, slot__start_utc__gt=today):
                try:
                    missing = meeting.check_schedule(agenda.slot, agenda.room)
                    if len(missing):
                        print "Warning: required people not available: %s (%s) at %s in %s: %s" % (
                            meeting, meeting.drafter, agenda.slot, agenda.room,
                            ', '.join(m.user.username for m in missing))
                        agenda.delete()
                except meeting.SchedulingError, e:
                    print "Error: %s at %s in %s: %s" % (meeting,
                                                         agenda.slot,
                                                         agenda.room,
                                                         e)
                    agenda.delete()

    def can_change_agenda(self, attendee):
        if attendee is not None:
            if attendee.user in self.schedulers.all() or attendee.user.has_perm('schedule.change_agenda'):
                return True
            else:
                return False
        else:
            return False

    def is_organizer(self, attendee):
        if attendee is not None:
            if attendee.user in self.managers.all() or self.lead_set.filter(lead=attendee).exists() or self.can_change_agenda(attendee):
                return True
            else:
                return False
        else:
            return False

class SummitSprint(models.Model):

    summit = models.ForeignKey(Summit, related_name='sprint_set')
    import_url = models.URLField(verify_exists=False)

    class Meta:
        app_label = 'schedule'
        ordering = ('summit', 'import_url', )
        verbose_name = 'Launchpad sprint'
