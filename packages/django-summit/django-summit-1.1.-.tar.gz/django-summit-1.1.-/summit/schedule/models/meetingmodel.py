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

import re
import urllib2
from urlparse import urlparse
from datetime import datetime

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.urlresolvers import reverse

import simplejson as json
from summit.schedule.fields import NameField

from summit.schedule.models.summitmodel import Summit
from summit.schedule.models.trackmodel import Track
from summit.schedule.models.topicmodel import Topic
from summit.schedule.models.attendeemodel import Attendee

from summit.schedule.autoslug import AutoSlugMixin

__all__ = (
    'Meeting',
)


class Meeting(AutoSlugMixin, models.Model):

    class SchedulingError(Exception):
        pass

    TYPE_CHOICES = (
        (u'blueprint', u'Blueprint'),
        (u'roundtable', u'Roundtable'),
        (u'plenary', u'Plenary'),
        (u'talk', u'Plenary Talk'),
        (u'bof', u'BoF'),
        (u'presentation', u'Presentation'),
        (u'panel', u'Panel Discussion'),
        (u'workshop', u'Workshop'),
        (u'seminar', u'Seminar'),
        (u'special', u'Special Event'),
    )

    STATUS_CHOICES = (
        (u'NEW', u'New'),
        (u'DISCUSSION', u'Discussion'),
        (u'DRAFT', u'Drafting'),
    )

    PRIORITY_CHOICES = (
        (5, u'Undefined'),
        (10, u'Low'),
        (50, u'Medium'),
        (70, u'High'),
        (90, u'Essential'),
    )

    REVIEW_CHOICES = (
        (u'PENDING', u'Pending'),
        (u'APPROVED', u'Approved'),
        (u'DECLINED', u'Declined'),
    )

    summit = models.ForeignKey(Summit)
    name = NameField(max_length=100, help_text="Lowercase alphanumeric characters and dashes only.")
    title = models.CharField(max_length=100, help_text="Alphanumeric characters and spaces are allowed")
    description = models.TextField(max_length=2047, blank=True)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES,
                            default=TYPE_CHOICES[0][0])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              null=True, blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES,
                                   null=True, blank=True)
    # FIXME tracks and topics must be for the same summit
    # (will require js magic in admin to refresh the boxes)
    tracks = models.ManyToManyField(Track, blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    spec_url = models.URLField(blank=True,
                               verbose_name="Spec URL")
    wiki_url = models.URLField(blank=True, verify_exists=False,
                               verbose_name="Wiki URL")
    pad_url = models.URLField(verify_exists=False,
                               verbose_name="Pad URL", null=True, blank=True)
    slots = models.IntegerField(default=1)
    override_break = models.BooleanField(default=False, verbose_name="Override Break",
                              help_text="If this is a multi-slot meeting, should it be allowed to take place during a break")
    approved = models.CharField(max_length=10, choices=REVIEW_CHOICES,
                              null=True, default='PENDING')
    private = models.BooleanField(default=False)
    private_key = models.CharField(max_length=32, null=True, blank=True)

    requires_dial_in = models.BooleanField(verbose_name="This session requires dial in capabilities", default=False)
    video = models.BooleanField(verbose_name="This session is to be videotaped", default=False)
    
    # FIXME attendees must be for the same summit
    # (will require js magic in admin to refresh the boxes)
    drafter = models.ForeignKey(Attendee, null=True, blank=True,
                                related_name='drafter_set')
    assignee = models.ForeignKey(Attendee, null=True, blank=True,
                                 related_name='assignee_set')
    approver = models.ForeignKey(Attendee, null=True, blank=True,
                                 related_name='approver_set')
    scribe = models.ForeignKey(Attendee, null=True, blank=True,
                                 related_name='scribe_set')
    participants = models.ManyToManyField(Attendee, blank=True,
                                          through='Participant')

    class Meta:
        app_label = 'schedule'

    def save(self):
        super(Meeting, self).save()
        self.update_slug()

    def share(self):
        if not self.pk or not self.private:
            return

        if not self.private_key:
            import hashlib, random
            meeting_hash = hashlib.md5()
            meeting_hash.update(str(self.pk))
            meeting_hash.update(self.name)
            meeting_hash.update(str(random.random()))
            self.private_key = meeting_hash.hexdigest()
            self.save()
        return self.private_key

    def _etherpadise_string(self, string):
        return re.sub(r"[^a-zA-Z0-9\-]", '-', string)

    def get_link_to_pad(self):
        if self.pad_url is not None and self.pad_url != '':
            return self.pad_url
        elif self.private:
            import hashlib, random
            meeting_hash = hashlib.md5()
            meeting_hash.update(str(self.pk))
            meeting_hash.update(self.name)
            meeting_hash.update(str(random.random()))
            pad_host = self.summit.etherpad
            self.pad_url = '%(host)s%(summit)s-%(meeting)s' % {
                'host': pad_host,
                'summit': self.summit.name,
                'meeting': meeting_hash.hexdigest(),
            }
            self.save()
            return self.pad_url
        else:
            pad_host = self.summit.etherpad
            name = self._etherpadise_string(self.name)
            return '%(host)s%(summit)s-%(meeting)s' % {
                'host': pad_host,
                'summit': self.summit.name,
                'meeting': name,
            }
    link_to_pad = property(get_link_to_pad)

    def get_edit_link_to_pad(self):
        if self.pad_url is not None and self.pad_url != '':
            return self.pad_url
        else:
            pad_host = self.summit.etherpad
            name = self._etherpadise_string(self.name)
            return '%(host)sep/pad/view/%(summit)s-%(meeting)s/latest' % {
                'host': pad_host,
                'summit': self.summit.name,
                'meeting': name,
            }
    edit_link_to_pad = property(get_edit_link_to_pad)

    def get_meeting_page_url(self):
        if self.name is None or self.name == '':
            name = '-'
        else:
            name = self.name
        args = [self.summit.name, self.id, name]
        return reverse('summit.schedule.views.meeting', args=args)
    meeting_page_url = property(get_meeting_page_url)

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return self.title

    @property
    def track_color(self):
        if self.tracks.exclude(color='FFFFFF').count() > 0:
            return '#'+self.tracks.exclude(color='FFFFFF')[0].color
        else:
            return '#FFFFFF'

    @property
    def spec_priority(self):
        label = dict(self.PRIORITY_CHOICES)[self.priority]
        icon = label.lower()
        
    def can_edit_pm(self, attendee):
        if attendee is not None:
            if attendee.user == self.approver or attendee.user == self.drafter or attendee.user == self.assignee or summit.is_organizer(attendee):
                return True
            else:
                return False
        else:
            return False

    @property
    def attendees(self):
        attendees = []
        if self.scribe and self.scribe not in attendees:
            attendees.append(self.scribe)
        if self.drafter:
            attendees.append(self.drafter)
        if self.assignee and self.assignee not in attendees:
            attendees.append(self.assignee)
#       if self.approver and self.approver not in attendees:
#           attendees.append(self.approver)

        participants = []
        for attendee in self.participants.all():
            if attendee not in attendees:
                participants.append(attendee)

        attendees.extend(sorted(participants, key=lambda x: x.user.username))
        return attendees

    @property
    def required_attendees(self):
        attendees = set()
        if self.drafter:
            attendees.add(self.drafter)
        if self.assignee:
            attendees.add(self.assignee)
        if self.scribe:
            attendees.add(self.scribe)
        #if self.approver:
        #    attendees.add(self.approver)

        for participant in self.participant_set.all():
            if participant.required:
                attendees.add(participant.attendee)

        return attendees

    def update_from_launchpad(self, elem):
        """Update from Launchpad data."""

        self.approved = 'APPROVED'
        
        status = elem.get("status")
        if status:
            self.status = status
        else:
            self.status = None

        priority = elem.get("priority")
        if priority:
            self.priority = priority
        else:
            self.priority = None

        spec_url = elem.get("lpurl")
        if spec_url:
            self.spec_url = spec_url

            # fetch to update the title
            # Now, LP has an API, we're stopping the sceen scrape :)
            try:
                apiurl = spec_url.replace('blueprints.launchpad.net', 'api.launchpad.net/devel') + '?ws.accept=application/json'
                lpdata = urllib2.urlopen(apiurl)
                data = json.load(lpdata)
                if 'title' in data:
                    self.title = data['title'][:100]
                if 'summary' in data:
                    self.description = data['summary']
            except (urllib2.HTTPError, KeyError):
                pass
        else:
            self.spec_url = ''

        wiki_url = elem.get("specurl")
        if wiki_url:
            self.wiki_url = wiki_url
        else:
            self.wiki_url = ''

        # Lookup drafter, assignee and approver before updating.
        # They might not be attending, in which case we don't bother mentioning
        # it (only attendance is interesting to us)
        self.drafter = None
        drafter = elem.get("drafter")
        if drafter:
            try:
                self.drafter = self.summit.attendee_set.get(
                    user__username__exact=drafter)
            except ObjectDoesNotExist:
                pass

        self.assignee = None
        assignee = elem.get("assignee")
        if assignee:
            try:
                self.assignee = self.summit.attendee_set.get(
                    user__username__exact=assignee)
            except ObjectDoesNotExist:
                pass

        self.approver = None
        approver = elem.get("approver")
        if approver:
            try:
                self.approver = self.summit.attendee_set.get(
                    user__username__exact=approver)
            except ObjectDoesNotExist:
                pass

        # Lookup other participants, again ignoring any not attending.
        from_lp = set()
        for p_elem in elem.findall("person"):
            username = p_elem.get("name")
            if not username:
                continue
            from_lp.add(username)

            required = p_elem.get("required", "False") != "False"

            try:
                attendee = self.summit.attendee_set.get(
                    user__username__exact=username)

                try:
                    participant = self.participant_set.get(
                        attendee=attendee)
                except ObjectDoesNotExist:
                    participant = self.participant_set.create(
                        attendee=attendee)
                except:
                    participant = self.participant_set.filter(
                        attendee=attendee)[0]


                participant.from_launchpad = True
                participant.required = required
                participant.save()
            except ObjectDoesNotExist:
                pass

        self.participant_set.filter(from_launchpad=True).filter(~models.Q(attendee__user__username__in=from_lp)).delete()

        self.save()

    def check_schedule(self, slot, room):
        """Check whether we can schedule this meeting in the given slot
        and room."""
        missing = set()

        slots = [slot]
        if self.slots > 1:
            slots.extend(s for s
                         in self.summit.slot_set.filter(start_utc__gte=slot.end_utc).order_by('start_utc')
                         if s.start.date() == slot.start.date())
        if len(slots) < self.slots:
            raise Meeting.SchedulingError("Insufficient slots available")

        all_slots = [s for s in self.summit.slot_set.all()
                     if s.start.date() == slot.start.date()]

        slots = slots[:self.slots]
        for this_slot in slots:
            if this_slot.type == 'break' and self.override_break:
                continue
            if this_slot.type not in ('open', 'plenary'):
                raise Meeting.SchedulingError("Slot not available")
            if this_slot.type == 'plenary' and self.type not in ('plenary', 'talk', 'special'):
                raise Meeting.SchedulingError(
                    "Not a plenary event, talk or special event")
            
            # Check that the room is not already in use
            try:
                existing = room.agenda_set.get(slot=this_slot)
                if existing.meeting != self:
                    raise Meeting.SchedulingError("Room is in use by %s"
                                                  % existing.meeting)
            except ObjectDoesNotExist:
                pass

            # Check that the room is not in use by a double session
            slot_num = all_slots.index(this_slot)
            for i in range(slot_num, 0, -1):
                distance = 2 + slot_num - i
                prev_slot = all_slots[i - 1]
                if prev_slot.type != this_slot.type:
                    break

                for agenda in prev_slot.agenda_set.filter(room=room):
                    if agenda.meeting != self \
                            and agenda.meeting.slots >= distance:
                        raise Meeting.SchedulingError("Room is in use by %s"
                                                      % agenda.meeting)

            # Check that the room is available
            if not room.available(this_slot):
                raise Meeting.SchedulingError("Room is not available")

            if self.requires_dial_in:
                if not room.has_dial_in:
                    raise Meeting.SchedulingError("Room has no dial-in capability")

            # Work out who is busy in this slot
            busy = set()
            for agenda in this_slot.agenda_set.all():
                if agenda.meeting != self:
                    busy.update([a.pk for a in agenda.meeting.required_attendees])

            slot_num = all_slots.index(this_slot)
            for i in range(slot_num, 0, -1):
                distance = 2 + slot_num - i
                prev_slot = all_slots[i - 1]
                if prev_slot.type != this_slot.type:
                    break

                for agenda in prev_slot.agenda_set.all():
                    if agenda.meeting != self \
                            and agenda.meeting.slots >= distance:
                        busy.update([a.pk for a in agenda.meeting.required_attendees])

            # Check that all required attendees are free in this slot
            for attendee in self.required_attendees:
                if not attendee.available(this_slot):
                    missing.add(attendee)
                if attendee.pk in busy:
                    missing.add(attendee)

            # Check that next/previous slots are not from the same track
            def check_not_same_track(other_slot, relative_position):
                type_exceptions = ('presentation', 'plenary', 'talk')
                if other_slot is not None and self.type not in type_exceptions:
                    for agenda in other_slot.agenda_set.filter(room__exact=room).exclude(
                            meeting__exact=self).filter(meeting__tracks__in=self.tracks.all()):
                        if agenda.meeting.tracks.filter(
                                pk__in=self.tracks.all()).exclude(allow_adjacent_sessions=True).count() > 0:
                            raise Meeting.SchedulingError(
                                "Same track in the %s slot" % relative_position)

            check_not_same_track(this_slot.previous(), "previous")
            check_not_same_track(this_slot.next(), "next")

        # Check that all required attendees can access this room
        # FIXME

        return missing

    def try_schedule(self):
        """Try to schedule this meeting in a suitable room."""
        if self.private:
            print "Not scheduling private meeting: %s" % self
            return
        open_rooms = self.summit.room_set.filter(type__exact='open')

        tracks = self.tracks.all()
        if tracks:
            rooms = open_rooms.filter(tracks__in=tracks)
            if self.try_schedule_into(rooms):
                return

        rooms = open_rooms.filter(tracks__isnull=True)
        if not self.try_schedule_into(rooms):
            print "Gave up scheduling %s" % self

    def try_schedule_into(self, rooms):
        """Try to schedule this meeting in one of the given rooms."""
        today = datetime.now()
        for room in rooms:
            for slot in self.summit.slot_set.filter(type__exact='open',start_utc__gt=today):
                try:
                    room.agenda_set.get(slot=slot)
                except ObjectDoesNotExist:
                    try:
                        missing = self.check_schedule(slot, room)
                        if len(missing):
                            raise Meeting.SchedulingError("Required people not available: %s"
                                                          % ', '.join(m.user.username for m in missing))

                        print "Schedule %s in %s at %s" % (self, room, slot)
                        room.agenda_set.create(
                            slot=slot, meeting=self, auto=True)
                        return True
                    except Meeting.SchedulingError, e:
                        print "-- could not schedule %s in %s at %s (%s)" % (self, room, slot, e)

        return False
