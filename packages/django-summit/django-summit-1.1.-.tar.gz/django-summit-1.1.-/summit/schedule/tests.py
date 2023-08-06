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
import unittest
from django.core.management.base import CommandError
from django import test as djangotest
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIRequest
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from summit.schedule.management.commands import reschedule

from model_mommy import mommy as factory
from summit.schedule.fields import NameField

from summit.schedule.models import *
from summit.schedule.render import Schedule
from summit.schedule import launchpad

# Monkey-patch our NameField into the types of fields that the factory
# understands.  This is simpler than trying to subclass the Mommy
# class directly.
factory.default_mapping[NameField] = str

site_root = getattr(settings, 'SITE_ROOT', 'http://summit.ubuntu.com')

class RequestFactory(djangotest.Client):
    """
    Class that lets you create mock Request objects for use in testing.

    Usage:

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client

    Once you have a request object you can pass it to any view function, 
    just as if that view had been hooked up using a URLconf.

    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.input': '',
        }
        environ.update(self.defaults)
        environ.update(request)
        request = WSGIRequest(environ)
        handler = BaseHandler()
        handler.load_middleware()
        for middleware_method in handler._request_middleware:
            if middleware_method(request):
                raise Exception("Couldn't create request mock object - "
                                "request middleware %s returned a response" % middleware_method)
        return request


class RescheduleCommandTestCase(unittest.TestCase):
    """Tests for the 'reschedule' management command."""

    def test_passing_nonexistant_summit_raises_error(self):
        cmd = reschedule.Command()
        self.assertRaises(CommandError, cmd.handle, summit='uds-xxx')


class MeetingModelTestCase(djangotest.TestCase):
    """Tests for the Meeting model."""

    def test_meetings_can_not_be_scheduled_in_closed_slots(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        slot = factory.make_one(
            Slot,
            start_utc=now,
            end_utc=now+one_hour,
            type='closed')

        agenda = factory.make_one(Agenda, slot=slot)
        meeting = factory.make_one(Meeting, requires_dial_in=False, private=False)

        # XXX check_schedule should only be checking the schedule, not
        # checking and modifying the schedule.
        # XXX check_schedule's parameters should be an just an agenda object,
        # not the agenda object's attributes.
        self.assertRaises(
            Meeting.SchedulingError,
            meeting.check_schedule, agenda.slot, agenda.room)

    def test_participants_are_in_another_meeting(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        slot = factory.make_one(
            Slot,
            start_utc=now,
            end_utc=now+one_hour)
        room1 = factory.make_one(Room)
        room2 = factory.make_one(Room)

        meeting1 = factory.make_one(Meeting, summit=slot.summit, requires_dial_in=False, private=False)
        meeting2 = factory.make_one(Meeting, summit=slot.summit, requires_dial_in=False, private=False)

        attendee = factory.make_one(Attendee)
        factory.make_one(Participant, meeting=meeting1, attendee=attendee, required=True)
        factory.make_one(Participant, meeting=meeting2, attendee=attendee, required=True)

        factory.make_one(Agenda, meeting=meeting1, slot=slot, room=room1)
        agenda = factory.make_one(Agenda, meeting=meeting2, slot=slot, room=room2)

        missing = meeting2.check_schedule(agenda.slot, agenda.room)
        self.assertEqual([attendee.name], [a.name for a in missing])


    def make_open_slot(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        slot = factory.make_one(
            Slot,
            start_utc=now+one_hour,
            end_utc=now+one_hour+one_hour,
            type='open')
        return slot

    def test_check_schedule_errors_on_no_dial_in(self):
        slot = self.make_open_slot()
        room = factory.make_one(Room, has_dial_in=False, summit=slot.summit, name="testroom")
        meeting = factory.make_one(Meeting, requires_dial_in=True, summit=slot.summit, name="testmeeting", private=False)
        try:
            meeting.check_schedule(slot, room)
        except meeting.SchedulingError, e:
            self.assertEqual("Room has no dial-in capability", e.message)
            return
        self.fail("SchedulingError not thrown")

    def make_two_adjacent_slots(self):
        summit = factory.make_one(Summit, timezone='utc')
        now = datetime.datetime(2011, 9, 8, 12, 00)
        one_hour = datetime.timedelta(0, 3600)
        slot1 = factory.make_one(
            Slot,
            start_utc=now+one_hour,
            end_utc=now+one_hour+one_hour,
            type='open', summit=summit)
        slot2 = factory.make_one(
            Slot,
            start_utc=now+one_hour+one_hour,
            end_utc=now+one_hour+one_hour+one_hour,
            type='open', summit=summit)
        return slot1, slot2

    def test_check_schedule_errors_on_same_track_in_previous_slot(self):
        slot1, slot2 = self.make_two_adjacent_slots()
        room = factory.make_one(Room, summit=slot1.summit,
                name="testroom")
        track = factory.make_one(Track, summit=slot1.summit,
                title="testtrack", allow_adjacent_sessions=False)
        track2 = factory.make_one(Track, summit=slot1.summit,
                title="adjacenttrack", allow_adjacent_sessions=True)
        meeting1 = factory.make_one(Meeting, requires_dial_in=False,
                summit=slot1.summit, name="testmeeting1", type='blueprint', private=False)
        meeting2 = factory.make_one(Meeting, requires_dial_in=False,
                summit=slot1.summit, name="testmeeting2", type='blueprint', private=False)
        meeting1.tracks = [track, track2]
        meeting2.tracks = [track]
        meeting1.agenda_set.create(room=room, slot=slot1)
        try:
            meeting2.check_schedule(slot2, room)
        except meeting2.SchedulingError, e:
            self.assertEqual("Same track in the previous slot", e.message)
            return
        self.fail("SchedulingError not thrown")

    def test_check_schedule_errors_on_same_track_in_next_slot(self):
        slot1, slot2 = self.make_two_adjacent_slots()
        room = factory.make_one(Room, summit=slot1.summit,
                name="testroom")
        track = factory.make_one(Track, summit=slot1.summit,
                title="testtrack", allow_adjacent_sessions=False)
        meeting1 = factory.make_one(Meeting, requires_dial_in=False,
                summit=slot1.summit, name="testmeeting1", type='blueprint', private=False)
        meeting2 = factory.make_one(Meeting, requires_dial_in=False,
                summit=slot1.summit, name="testmeeting2", type='blueprint', private=False)
        meeting1.tracks = [track]
        meeting2.tracks = [track]
        meeting1.agenda_set.create(room=room, slot=slot2)
        try:
            meeting2.check_schedule(slot1, room)
        except meeting2.SchedulingError, e:
            self.assertEqual("Same track in the next slot", e.message)
            return
        self.fail("SchedulingError not thrown")

    def test_check_schedule_no_error_on_different_track(self):
        slot1, slot2 = self.make_two_adjacent_slots()
        room = factory.make_one(Room, summit=slot1.summit,
                name="testroom")
        track = factory.make_one(Track, summit=slot1.summit,
                title="testtrack", allow_adjacent_sessions=False)
        other_track = factory.make_one(Track, summit=slot1.summit,
                title="othertesttrack", allow_adjacent_sessions=False)
        meeting1 = factory.make_one(Meeting, requires_dial_in=False,
                summit=slot1.summit, name="testmeeting1", type='blueprint', private=False)
        meeting2 = factory.make_one(Meeting, requires_dial_in=False,
                summit=slot1.summit, name="testmeeting2", type='blueprint', private=False)
        meeting1.tracks = [track]
        meeting2.tracks = [other_track]
        meeting1.agenda_set.create(room=room, slot=slot2)
        meeting2.check_schedule(slot1, room)

    def test_check_schedule_no_error_on_same_track_for_plenaries(self):
        slot1, slot2 = self.make_two_adjacent_slots()
        room = factory.make_one(Room, summit=slot1.summit,
                name="testroom")
        track = factory.make_one(Track, summit=slot1.summit,
                title="testtrack", allow_adjacent_sessions=False)
        meeting1 = factory.make_one(Meeting, requires_dial_in=False,
                summit=slot1.summit, name="testmeeting1", type='blueprint', private=False)
        meeting2 = factory.make_one(Meeting, requires_dial_in=False,
                summit=slot1.summit, name="testmeeting2", type='plenary', private=False)
        meeting1.tracks = [track]
        meeting2.tracks = [track]
        meeting1.agenda_set.create(room=room, slot=slot2)
        meeting2.check_schedule(slot1, room)

    def test_check_schedule_no_error_on_same_track_for_ajdacent_sessions_allowed(self):
        slot1, slot2 = self.make_two_adjacent_slots()
        room = factory.make_one(Room, summit=slot1.summit,
                name="testroom")
        track = factory.make_one(Track, summit=slot1.summit,
                title="adjacenttrack", allow_adjacent_sessions=True)
        meeting1 = factory.make_one(Meeting, requires_dial_in=False,
                summit=slot1.summit, name="testmeeting1", type='blueprint', private=False)
        meeting2 = factory.make_one(Meeting, requires_dial_in=False,
                summit=slot1.summit, name="testmeeting2", type='blueprint', private=False)
        meeting1.tracks = [track]
        meeting2.tracks = [track]
        meeting1.agenda_set.create(room=room, slot=slot2)
        meeting2.check_schedule(slot1, room)

    def test_try_schedule_into_refuses_room_without_dial_in(self):
        slot = self.make_open_slot()
        room = factory.make_one(Room, has_dial_in=False, summit=slot.summit, name="testroom")
        meeting = factory.make_one(Meeting, requires_dial_in=True, summit=slot.summit, name="testmeeting", private=False)

        self.assertEqual(False, meeting.try_schedule_into([room]))
        self.assertEqual(0, meeting.agenda_set.all().count())

    def test_try_schedule_into_allows_room_with_dial_in(self):
        slot = self.make_open_slot()
        room = factory.make_one(Room, has_dial_in=True, summit=slot.summit, name="testroom")
        meeting = factory.make_one(Meeting, requires_dial_in=True, summit=slot.summit, name="testmeeting", private=False)

        self.assertEqual(True, meeting.try_schedule_into([room]))
        self.assertEqual(1, meeting.agenda_set.all().count())

    def test_link_to_pad_with_pad_url_set(self):
        url = 'http://pad.com/url'
        meeting = factory.make_one(Meeting, pad_url=url, private=False)
        self.assertEqual(url, meeting.link_to_pad)

    def get_pad_host(self):
        summit_name = 'testsummit'
        summit = factory.make_one(Summit, name=summit_name)
        return getattr(summit, 'etherpad', 'http://pad.ubuntu.com/')

    def test_link_to_pad_with_pad_url_unset(self):
        summit_name = 'testsummit'
        summit = factory.make_one(Summit, name=summit_name)
        name = 'testmeeting'
        meeting = factory.make_one(Meeting, pad_url=None, name=name,
                summit=summit, private=False)
        pad_host = self.get_pad_host()
        url = pad_host + summit_name + '-' + name
        self.assertEqual(url, meeting.link_to_pad)

    def test_link_to_pad_with_plus_in_meeting_name(self):
        summit_name = 'testsummit'
        summit = factory.make_one(Summit, name=summit_name)
        name = 'test+meeting'
        meeting = factory.make_one(Meeting, pad_url=None, name=name,
                summit=summit, private=False)
        pad_host = self.get_pad_host()
        url = pad_host + summit_name + '-' + name.replace("+", "-")
        self.assertEqual(url, meeting.link_to_pad)

    def test_edit_link_to_pad_with_pad_url_set(self):
        url = 'http://pad.com/url'
        meeting = factory.make_one(Meeting, pad_url=url, private=False)
        self.assertEqual(url, meeting.edit_link_to_pad)

    def test_edit_link_to_pad_with_pad_url_unset(self):
        summit_name = 'testsummit'
        summit = factory.make_one(Summit, name=summit_name)
        name = 'testmeeting'
        meeting = factory.make_one(Meeting, pad_url=None, name=name,
                summit=summit, private=False)
        pad_host = self.get_pad_host()
        url = pad_host + "ep/pad/view/" + summit_name + '-' + name + "/latest"
        self.assertEqual(url, meeting.edit_link_to_pad)

    def test_edit_link_to_pad_with_plus_in_meeting_name(self):
        summit_name = 'testsummit'
        summit = factory.make_one(Summit, name=summit_name)
        name = 'test+meeting'
        meeting = factory.make_one(Meeting, pad_url=None, name=name,
                summit=summit, private=False)
        pad_host = self.get_pad_host()
        url = (pad_host + "ep/pad/view/" + summit_name
                + '-' + name.replace("+", "-") + "/latest")
        self.assertEqual(url, meeting.edit_link_to_pad)

    def test_update_from_launchpad_sets_status(self):
        meeting = Meeting()
        status = "Discussion"
        elem = LaunchpadExportNode(status=status)
        meeting.update_from_launchpad(elem)
        self.assertEqual(status, meeting.status)

    def test_update_from_launchpad_sets_priority(self):
        meeting = Meeting()
        priority = 70
        elem = LaunchpadExportNode(priority=priority)
        meeting.update_from_launchpad(elem)
        self.assertEqual(priority, meeting.priority)

    def test_update_from_launchpad_sets_wiki_url(self):
        meeting = Meeting()
        wiki_url = "http://example.com/somespec"
        elem = LaunchpadExportNode(specurl=wiki_url)
        meeting.update_from_launchpad(elem)
        self.assertEqual(wiki_url, meeting.wiki_url)

    def get_person_node(self, username, required=False):
        elem = LaunchpadExportNode()
        required_map = {True: "True", False: "False"}
        elem.add_child("person",
                LaunchpadExportNode(name=username,
                    required=required_map[required]))
        return elem

    def make_summit_and_attendee(self):
        username = "username"
        user = factory.make_one(User, username=username)
        summit = factory.make_one(Summit)
        attendee = summit.attendee_set.create(user=user)
        return summit, attendee

    def test_update_from_launchpad_adds_participant(self):
        summit, attendee = self.make_summit_and_attendee()
        meeting = summit.meeting_set.create()
        elem = self.get_person_node(attendee.user.username, required=False)
        meeting.update_from_launchpad(elem)
        participant = meeting.participant_set.get()
        self.assertEqual(attendee, participant.attendee)
        self.assertEqual(False, participant.required)

    def test_update_from_launchpad_sets_participant_essential(self):
        summit, attendee = self.make_summit_and_attendee()
        meeting = summit.meeting_set.create()
        elem = self.get_person_node(attendee.user.username, required=True)
        meeting.update_from_launchpad(elem)
        participant = meeting.participant_set.get()
        self.assertEqual(True, participant.required)

    def test_update_from_launchpad_sets_from_launchpad(self):
        summit, attendee = self.make_summit_and_attendee()
        meeting = summit.meeting_set.create()
        elem = self.get_person_node(attendee.user.username)
        meeting.update_from_launchpad(elem)
        participant = meeting.participant_set.get()
        self.assertEqual(True, participant.from_launchpad)

    def test_update_from_launchpad_removes_from_launchpad_unsubscribed(self):
        summit, attendee = self.make_summit_and_attendee()
        meeting = summit.meeting_set.create()
        elem = self.get_person_node(attendee.user.username)
        otheruser = factory.make_one(User, username="otheruser")
        otherattendee = summit.attendee_set.create(user=otheruser)
        meeting.participant_set.create(attendee=otherattendee, from_launchpad=True)
        meeting.update_from_launchpad(elem)
        usernames = [p.attendee.user.username for p in meeting.participant_set.all()]
        self.assertEqual(["username"], usernames)


class ICalTestCase(djangotest.TestCase):

    def test_ical_meeting_without_name(self):
        """ Tests that ical doesn't break for nameless meetings"""
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        summit = factory.make_one(Summit, name='uds-test')
        summit.save()
        slot = factory.make_one(
            Slot,
            start_utc=now,
            end_utc=now+one_hour,
            type='open',
            summit=summit)
        slot.save()
        
        room = factory.make_one(Room, summit=summit)
        meeting = factory.make_one(Meeting, summit=summit, name='', private=False)
        agenda = factory.make_one(Agenda, slot=slot, meeting=meeting, room=room)
        
        self.assertEquals(meeting.meeting_page_url, '/uds-test/meeting/%s/-/' % meeting.id)
        
        response = self.client.get('/uds-test.ical')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'URL:%s/uds-test/meeting/%s/-/\n' % (site_root, meeting.id), 1)

    def test_ical_meeting_name_with_period(self):
        """ Tests that ical doesn't break for nameless meetings"""
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        summit = factory.make_one(Summit, name='uds-test')
        summit.save()
        slot = factory.make_one(
            Slot,
            start_utc=now,
            end_utc=now+one_hour,
            type='open',
            summit=summit)
        slot.save()
        
        room = factory.make_one(Room, summit=summit)
        meeting = factory.make_one(Meeting, summit=summit, name='test.name', private=False)
        agenda = factory.make_one(Agenda, slot=slot, meeting=meeting, room=room)
        
        self.assertEquals(meeting.meeting_page_url, '/uds-test/meeting/%s/test.name/' % meeting.id)
        
        response = self.client.get('/uds-test.ical')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'URL:%s/uds-test/meeting/%s/test.name/' % (site_root, meeting.id), 1)
        
    def test_ical_meeting_multiline_description(self):
        """ Tests that ical put spaces before multi-line descriptions"""
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        summit = factory.make_one(Summit, name='uds-test')
        summit.save()
        slot = factory.make_one(
            Slot,
            start_utc=now,
            end_utc=now+one_hour,
            type='open',
            summit=summit)
        slot.save()
        
        room = factory.make_one(Room, summit=summit)
        meeting = factory.make_one(Meeting, summit=summit, name='test.name', description="Test\r\nDescription", private=False)
        agenda = factory.make_one(Agenda, slot=slot, meeting=meeting, room=room)
        
        self.assertEquals(meeting.meeting_page_url, '/uds-test/meeting/%s/test.name/' % meeting.id)
        
        response = self.client.get('/uds-test.ical')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'DESCRIPTION:Test\NDescription', 1)
        
    def test_private_ical(self):
        """ Tests that private icals contain private meetings """
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        week = datetime.timedelta(days=7)
        summit = factory.make_one(Summit, name='uds-test')
        slot = factory.make_one(
            Slot,
            start_utc=now,
            end_utc=now+one_hour,
            type='open',
            summit=summit)
        
        room = factory.make_one(Room, summit=summit)
        meeting = factory.make_one(Meeting, summit=summit, name='test.name', private=True)
        agenda = factory.make_one(Agenda, slot=slot, meeting=meeting, room=room)
        
        self.assertEquals(meeting.meeting_page_url, '/uds-test/meeting/%s/test.name/' % meeting.id)

        user = factory.make_one(User, username='testuser', first_name='Test', last_name='User')
        attendee = factory.make_one(Attendee, summit=summit, user=user, start_utc=now, end_utc=now+week)
        participant = factory.make_one(Participant, attendee=attendee, meeting=meeting)

        response = self.client.get('/uds-test/participant/my_schedule_%s.ical' % attendee.secret_key)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'URL:%s/uds-test/meeting/%s/test.name/' % (site_root, meeting.id), 1)

class MeetingPageTestCase(djangotest.TestCase):

    def test_meeting_page_url(self):
        """ Tests the creation and reverse lookup of meeting page urls"""
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        summit = factory.make_one(Summit, name='uds-test')
        summit.save()
        slot = factory.make_one(
            Slot,
            start_utc=now,
            end_utc=now+one_hour,
            type='open',
            summit=summit)
        slot.save()
        
        room = factory.make_one(Room, summit=summit)
        meeting = factory.make_one(Meeting, summit=summit, name='test-meeting', private=False)
        agenda = factory.make_one(Agenda, slot=slot, meeting=meeting, room=room)

        # check meeting page url generation
        self.assertEquals(meeting.meeting_page_url, '/uds-test/meeting/%s/test-meeting/' % meeting.id)
        
        # check meeting page url reverse lookup
        rev_args = ['uds-test', 1, 'test-meeting']
        reverse_url = reverse('summit.schedule.views.meeting', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/meeting/%s/test-meeting/' % meeting.id)
        
        # check meeting details page
        response = self.client.get(reverse_url)
        self.assertEquals(response.status_code, 200)

        # check meeting in ical
        response = self.client.get('/uds-test.ical')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'URL:%s/uds-test/meeting/%s/test-meeting/' % (site_root, meeting.id), 1)


class ParticipationRegistrationTestCase(djangotest.TestCase):

    def setUp(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        week = datetime.timedelta(days=5)
        self.summit = factory.make_one(Summit, name='uds-test')
        self.slot = factory.make_one(
            Slot,
            start_utc=now+one_hour,
            end_utc=now+(2*one_hour),
            type='open',
            summit=self.summit)
        
        self.room = factory.make_one(Room, summit=self.summit, type='open')
        self.meeting = factory.make_one(Meeting, summit=self.summit, name='meeting1', private=False, requires_dial_in=False, spec_url=None)

        self.user = factory.make_one(User, username='testuser', first_name='Test', last_name='User', is_active=True)
        self.user.set_password('password')
        self.user.save()

        self.attendee = factory.make_one(Attendee, summit=self.summit, user=self.user, start_utc=now, end_utc=now+week)
        
    def login(self):
        logged_in = self.client.login(username='testuser', password='password')
        self.assertTrue(logged_in)
        
    def test_attend_link(self):
        self.assertEquals(0, Participant.objects.filter(attendee=self.attendee).count())
        self.login()
        response = self.client.get(reverse('summit.schedule.views.meeting', args=('uds-test', self.meeting.id, 'meeting1')))
        self.assertContains(response, 'Attend this meeting', 1)
        self.assertContains(response, 'Subscribe to this meeting', 0)
        self.assertContains(response, 'Skip this meeting', 0)

    def test_subscribe_link(self):
        self.assertEquals(0, Participant.objects.filter(attendee=self.attendee).count())
        self.login()
        self.meeting.spec_url = 'http://examplespec.com/test'
        self.meeting.save()
        response = self.client.get(reverse('summit.schedule.views.meeting', args=('uds-test', self.meeting.id, 'meeting1')))
        self.assertContains(response, 'Subscribe to Blueprint', 1)
        self.assertContains(response, 'http://examplespec.com/test/+subscribe', 1)
        self.assertContains(response, 'Attend this meeting', 1)
        self.assertContains(response, 'Skip this meeting', 0)

    def test_skip_link(self):
        self.meeting.participant_set.create(attendee=self.attendee, required=False, from_launchpad=False)
        self.assertEquals(1, Participant.objects.filter(attendee=self.attendee).count())
        self.login()
        response = self.client.get(reverse('summit.schedule.views.meeting', args=('uds-test', self.meeting.id, 'meeting1')))
        self.assertContains(response, 'Skip this meeting', 1)
        self.assertContains(response, 'Subscribe to this meeting', 0)
        self.assertContains(response, 'Attend this meeting', 0)

    def test_add_participation(self):
        self.assertEquals(0, Participant.objects.filter(attendee=self.attendee).count())
        self.login()
        response = self.client.get(reverse('summit.schedule.views.register', args=('uds-test', self.meeting.id, 'meeting1')))
        self.assertEquals(1, Participant.objects.filter(attendee=self.attendee).count())

    def test_delete_participation(self):
        self.meeting.participant_set.create(attendee=self.attendee, required=False, from_launchpad=False)
        self.assertEquals(1, Participant.objects.filter(attendee=self.attendee).count())
        self.login()
        response = self.client.get(reverse('summit.schedule.views.unregister', args=('uds-test', self.meeting.id, 'meeting1')))
        self.assertEquals(0, Participant.objects.filter(attendee=self.attendee).count())

class ReverseUrlLookupTestCase(djangotest.TestCase):

    def setUp(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        self.summit = factory.make_one(Summit, name='uds-test')
        self.summit.save()
        self.slot = factory.make_one(
            Slot,
            start_utc=now,
            end_utc=now+one_hour,
            type='open',
            summit=self.summit)
        self.slot.save()
        
    def test_meeting_name_with_period(self):
        ''' Test the following Meeting urlconf
        (r'^(?P<summit_name>[\w-]+)/meeting/(?P<meeting_id>\d+)/(?P<meeting_slug>[\.\w-]+)/$', 'meeting'),
        '''
        meeting = factory.make_one(Meeting, summit=self.summit, name='test.meeting', private=False)
        
        rev_args = ['uds-test', meeting.id, 'test.meeting']
        reverse_url = reverse('summit.schedule.views.meeting', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/meeting/%s/test.meeting/' % meeting.id)


    def test_room_name_with_period(self):
        ''' Test the following Room urlconfs
        (r'^(?P<summit_name>[\w-]+)/(?P<room_name>[\w-]+)/$', 'by_room'),
        (r'^(?P<summit_name>[\w-]+)/room/(?P<room_name>[\w-]+).ical$', 'room_ical'),
        '''
        room = factory.make_one(Room, summit=self.summit, name='test.room')

        rev_args = ['uds-test', 'test.room']
        reverse_url = reverse('summit.schedule.views.by_room', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/test.room/')

        reverse_url = reverse('summit.schedule.views.room_ical', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/room/test.room.ical')

    def test_track_name_with_period(self):
        ''' Test the following Track urlconfs
        (r'^(?P<summit_name>[\w-]+)/track/(?P<track_slug>[\w-]+)/$', 'by_track'),
        (r'^(?P<summit_name>[\w-]+)/track/(?P<track_slug>[\w-]+).ical$', 'track_ical'),
        '''
        track = factory.make_one(Track, summit=self.summit, slug='test.track')

        rev_args = ['uds-test', 'test.track']
        reverse_url = reverse('summit.schedule.views.by_track', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/track/test.track/')

        reverse_url = reverse('summit.schedule.views.track_ical', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/track/test.track.ical')
        
    def test_participant_name_with_period(self):
        ''' Test the following User urlconf
        (r'^(?P<summit_name>[\w-]+)/participant/(?P<username>[\w-]+)\.ical$', 'user_ical'),
        '''
        user = factory.make_one(User, username='test.user')

        rev_args = ['uds-test', 'test.user']
        reverse_url = reverse('summit.schedule.views.user_ical', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/participant/test.user.ical')
        
    def test_meeting_name_with_percent(self):
        ''' Test the following Meeting urlconf
        (r'^(?P<summit_name>[\w-]+)/meeting/(?P<meeting_id>\d+)/(?P<meeting_slug>[\.\w-]+)/$', 'meeting'),
        '''
        meeting = factory.make_one(Meeting, summit=self.summit, name='test.meeting', private=False)
        
        rev_args = ['uds-test', meeting.id, 'test%meeting']
        reverse_url = reverse('summit.schedule.views.meeting', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/meeting/%s/test%%meeting/' % meeting.id)

    def test_meeting_name_with_plus_sign(self):
        meeting = factory.make_one(Meeting, summit=self.summit, name='test.meeting', private=False)
        rev_args = ['uds-test', meeting.id, 'test+meeting']
        reverse_url = reverse('summit.schedule.views.meeting', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/meeting/%s/test+meeting/' % meeting.id)

    def test_room_name_with_percent(self):
        ''' Test the following Room urlconfs
        (r'^(?P<summit_name>[\w-]+)/(?P<room_name>[\.\w-]+)/$', 'by_room'),
        (r'^(?P<summit_name>[\w-]+)/room/(?P<room_name>[\.\w-]+).ical$', 'room_ical'),
        '''
        room = factory.make_one(Room, summit=self.summit, name='test.room')

        rev_args = ['uds-test', 'test%room']
        reverse_url = reverse('summit.schedule.views.by_room', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/test%room/')

        reverse_url = reverse('summit.schedule.views.room_ical', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/room/test%room.ical')

    def test_room_name_with_plus_sign(self):
        room = factory.make_one(Room, summit=self.summit, name='test.room')

        rev_args = ['uds-test', 'test+room']
        reverse_url = reverse('summit.schedule.views.by_room', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/test+room/')

        reverse_url = reverse('summit.schedule.views.room_ical', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/room/test+room.ical')

    def test_track_name_with_percent(self):
        ''' Test the following Track urlconfs
        (r'^(?P<summit_name>[\w-]+)/track/(?P<track_slug>[\.\w-]+)/$', 'by_track'),
        (r'^(?P<summit_name>[\w-]+)/track/(?P<track_slug>[\.\w-]+).ical$', 'track_ical'),
        '''
        track = factory.make_one(Track, summit=self.summit, slug='test.track')

        rev_args = ['uds-test', 'test%track']
        reverse_url = reverse('summit.schedule.views.by_track', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/track/test%track/')

        reverse_url = reverse('summit.schedule.views.track_ical', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/track/test%track.ical')

    def test_track_name_with_plus_sign(self):
        track = factory.make_one(Track, summit=self.summit, slug='test.track')

        rev_args = ['uds-test', 'test+track']
        reverse_url = reverse('summit.schedule.views.by_track', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/track/test+track/')

        reverse_url = reverse('summit.schedule.views.track_ical', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/track/test+track.ical')

    def test_participant_name_with_percent(self):
        ''' Test the following User urlconf
        (r'^(?P<summit_name>[\w-]+)/participant/(?P<username>[\.\w-]+)\.ical$', 'user_ical'),
        '''
        user = factory.make_one(User, username='test.user')

        rev_args = ['uds-test', 'test%user']
        reverse_url = reverse('summit.schedule.views.user_ical', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/participant/test%user.ical')

    def test_participant_name_with_plus_sign(self):
        user = factory.make_one(User, username='test.user')

        rev_args = ['uds-test', 'test+user']
        reverse_url = reverse('summit.schedule.views.user_ical', args=rev_args)
        self.assertEquals(reverse_url, '/uds-test/participant/test+user.ical')

class EtherpadEditUrl(djangotest.TestCase):

    def setUp(self):
        self.summit = factory.make_one(Summit, name='uds-test')
        self.summit.save()

    def tearDown(self):
        pass

    def test_etherpad_edit_url(self):

        slot = factory.make_one(
            Slot,
            type='open',
            summit=self.summit)
        slot.save()

        room = factory.make_one(Room, summit=self.summit)
        meeting = factory.make_one(Meeting, summit=self.summit, name='test-meeting', private=False)
        agenda = factory.make_one(Agenda, slot=slot, meeting=meeting, room=room)

        response = self.client.get('/uds-test/meeting/%s/test-meeting/' % meeting.id)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'http://pad.ubuntu.com/ep/pad/view/uds-test-test-meeting/latest', 1)

class SchedulingConflictsTestCase(djangotest.TestCase):

    def setUp(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        week = datetime.timedelta(days=5)
        self.summit = factory.make_one(Summit, name='uds-test')
        self.slot = factory.make_one(
            Slot,
            start_utc=now,
            end_utc=now+one_hour,
            type='open',
            summit=self.summit)
        
        self.room1 = factory.make_one(Room, summit=self.summit)
        self.meeting1 = factory.make_one(Meeting, summit=self.summit, name='meeting1', requires_dial_in=False)
        self.agenda1 = factory.make_one(Agenda, slot=self.slot, meeting=self.meeting1, room=self.room1)

        self.room2 = factory.make_one(Room, summit=self.summit)
        self.meeting2 = factory.make_one(Meeting, summit=self.summit, name='meeting2', requires_dial_in=False)
        
        self.user = factory.make_one(User, username='testuser', first_name='Test', last_name='User')
        self.attendee = factory.make_one(Attendee, summit=self.summit, user=self.user, start_utc=now, end_utc=now+week)
        
    def tearDown(self):
        pass
        
    def assertRaises(self, exception_type, function, args):
        try:
            function(*args)
            raise AssertionError('Callable failed to raise exception %s' % exception_type)
        except exception_type, e:
            return True

    def test_meeting_check_schedule_no_conflict(self):
        '''Checks the Meeting model's check_schedule'''
        missing = self.meeting1.check_schedule(self.slot, self.room1)
        self.assertEquals(len(missing), 0)
        
        missing = self.meeting2.check_schedule(self.slot, self.room2)
        self.assertEquals(len(missing), 0)
        
    def test_meeting_check_room_conflict(self):
        '''Checks that two meetings will not be scheduled in the same room 
            at the same time
        '''
        missing = self.meeting1.check_schedule(self.slot, self.room1)
        self.assertEquals(len(missing), 0)
        
        self.assertRaises(Meeting.SchedulingError,
                          Meeting.check_schedule, 
                          (self.meeting2, self.slot, self.room1))
        
    def test_meeting_check_schedule_participant_conflict(self):
        '''Checks that a two meetings requiring the same attendee will mark that
            user as missing.
        '''
        participant1 = Participant.objects.create(
            meeting=self.meeting1,
            attendee=self.attendee,
            required=True
        )
        missing = self.meeting1.check_schedule(self.slot, self.room1)
        self.assertEquals(len(missing), 0)
        
        participant1 = Participant.objects.create(
            meeting=self.meeting2,
            attendee=self.attendee,
            required=True
        )
        missing = self.meeting2.check_schedule(self.slot, self.room2)
        self.assertEquals(len(missing), 1)


class PrivateSchedulingTestCase(djangotest.TestCase):

    def setUp(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        week = datetime.timedelta(days=5)
        self.summit = factory.make_one(Summit, name='uds-test')
        self.slot = factory.make_one(
            Slot,
            start_utc=now+one_hour,
            end_utc=now+(2*one_hour),
            type='open',
            summit=self.summit)
        
        self.open_room = factory.make_one(Room, summit=self.summit, type='open')
        self.public_meeting = factory.make_one(Meeting, summit=self.summit, name='meeting1', private=False, requires_dial_in=False)

        self.private_room = factory.make_one(Room, summit=self.summit, type='private')
        self.private_meeting = factory.make_one(Meeting, summit=self.summit, name='meeting2', private=True, requires_dial_in=False)
        
        self.user = factory.make_one(User, username='testuser', first_name='Test', last_name='User')
        self.attendee = factory.make_one(Attendee, summit=self.summit, user=self.user, start_utc=now, end_utc=now+week)
        
    def tearDown(self):
        pass
        
    def assertRaises(self, exception_type, function, args):
        try:
            function(*args)
            raise AssertionError('Callable failed to raise exception %s' % exception_type)
        except exception_type, e:
            return True

    def run_autoschedule(self):
        from django.core.management import execute_from_command_line
        execute_from_command_line(argv=['manage.py', 'autoschedule', 'uds-test', '-v', '2'])

    def test_private_meeting_schedule(self):
        ''' General run of the autoschedule, no gurantee of what ends up where'''
        self.run_autoschedule()

        # Private meetings should not ever be autoscheduled
        self.assertEquals(0, Agenda.objects.filter(slot__summit=self.summit, meeting__private=True, room__type='open').count())
        self.assertEquals(0, Agenda.objects.filter(slot__summit=self.summit, meeting__private=False, room__type='private').count())
        # Private rooms should not ever be autoscheduled
        self.assertEquals(0, Agenda.objects.filter(slot__summit=self.summit, meeting__private=True, room__type='private').count())

        # Public meetings in open rooms should be autoscheduled
        self.assertEquals(1, Agenda.objects.filter(slot__summit=self.summit, meeting__private=False, room__type='open').count())

    def test_no_available_public_room(self):
        '''Make sure public meetings will not be autoscheduled into private rooms'''
        self.open_room.type = 'private'
        self.open_room.save()
        
        self.run_autoschedule()

        # Without an open room, public meetings should not be autoscheduled
        self.assertEquals(0, self.public_meeting.agenda_set.count())

        # Private meetings should not ever be autoscheduled
        self.assertEquals(0, self.private_meeting.agenda_set.count())
        
        # Private rooms should not ever be autoscheduled
        self.assertEquals(0, Agenda.objects.filter(room__type='private').count())
    
    def test_no_available_private_room(self):
        '''Make sure private meetings will not be autoscheduled into open rooms'''
        self.private_room.type = 'open'
        self.private_room.save()
        
        self.run_autoschedule()
        
        # Private meetings should not ever be autoscheduled
        self.assertEquals(0, self.private_meeting.agenda_set.count())

        # Public meeting should be autoscheduled into one of the two open rooms
        self.assertEquals(1, self.public_meeting.agenda_set.count())
        self.assertEquals(1, Agenda.objects.filter(room__type='open').count())

    def test_required_participant_in_private_meeting(self):
        '''Make sure meetings aren't scheduled when someone is in a private meeting.'''
        # Make the same person required for both meetings
        self.public_meeting.participant_set.create(attendee=self.attendee, required=True)
        self.private_meeting.participant_set.create(attendee=self.attendee, required=True)
        # Schedule the private meeting in the one available slot
        self.private_room.agenda_set.create(slot=self.slot, meeting=self.private_meeting)

        self.run_autoschedule()

        # Check that the private meeting is still scheduled
        self.assertEquals(1, self.private_meeting.agenda_set.count())
        # Check that the public meeting is not scheduled
        self.assertEquals(0, self.public_meeting.agenda_set.count())


class RenderScheduleTestCase(djangotest.TestCase):

    def setUp(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        week = datetime.timedelta(days=5)
        self.summit = factory.make_one(Summit, name='uds-test', timezone='UTC')
        self.slot = factory.make_one(
            Slot,
            start_utc=now+one_hour,
            end_utc=now+(2*one_hour),
            type='open',
            summit=self.summit)

        self.track1 = factory.make_one(Track, summit=self.summit)
        self.room1 = factory.make_one(Room, summit=self.summit, name='room1')
        self.meeting1 = factory.make_one(Meeting, summit=self.summit, name='meeting1', private=False, requires_dial_in=False)
        self.agenda1 = factory.make_one(Agenda, slot=self.slot, meeting=self.meeting1, room=self.room1)

        self.user = factory.make_one(User, username='testuser', first_name='Test', last_name='User')
        self.attendee = factory.make_one(Attendee, summit=self.summit, user=self.user, start_utc=now, end_utc=now+week)

    def tearDown(self):
        # Cached requests cause render.py to return old data, so clear the cache
        if hasattr(cache, 'clear'):
            cache.clear()
        # Older django didn't have .clear, but locmem cache did have ._cull
        elif hasattr(cache, '_cull'):
            cache._cull()

    def request_schedule(self):
        schedule_args = [self.summit.name, self.agenda1.slot.start_utc.date()]
        schedule_url = reverse('summit.schedule.views.by_date', args=schedule_args)
        response = self.client.get(schedule_url)
        return response

    def test_percent_in_meeting_name(self):
        self.meeting1.name = 'test%meeting'
        self.meeting1.save()

        response = self.request_schedule()

        self.assertContains(response, 'test%meeting', 1)

    def test_percent_in_meeting_title(self):
        self.meeting1.title = 'test % meeting'
        self.meeting1.save()

        response = self.request_schedule()

        self.assertContains(response, 'test % meeting', 1)

    def test_percent_in_room_title(self):
        self.meeting1.type = 'talk'
        self.meeting1.save()
        self.room1.title = 'test % room'
        self.room1.save()

        response = self.request_schedule()

        # Room title is displayed at top and bottom of the schedule, and also
        # on the meeting div for self.meeting1 which is scheduled for that room
        self.assertContains(response, 'test % room', 4)

    def test_percent_in_meeting_track_title(self):
        self.track1.title = 'test % track'
        self.track1.save()
        self.meeting1.tracks.add(self.track1)

        response = self.request_schedule()

        self.assertContains(response, 'test % track', 1)

    def test_percent_in_meeting_track_slug(self):
        self.track1.slug = 'test%track'
        self.track1.save()
        self.meeting1.tracks.add(self.track1)

        response = self.request_schedule()

        self.assertContains(response, 'test%track', 1)

    def test_specify_rooms_in_schedule(self):
        room2 = factory.make_one(Room, summit=self.summit, name='room2', title='Room 2')
        self.room1.title = 'Room 1'
        self.room1.save()
        self.agenda1.delete()
        
        schedule_args = [self.summit.name, self.agenda1.slot.start_utc.date()]
        schedule_url = reverse('summit.schedule.views.by_date', args=schedule_args)

        response = self.client.get(schedule_url)
        self.assertContains(response, self.room1.title, 2)
        self.assertContains(response, room2.title, 2)

        response = self.client.get(schedule_url + '?rooms=room1')
        self.assertContains(response, self.room1.title, 2)
        self.assertContains(response, room2.title, 0)
        
        response = self.client.get(schedule_url + '?rooms=room2')
        self.assertContains(response, self.room1.title, 0)
        self.assertContains(response, room2.title, 2)
        
        response = self.client.get(schedule_url + '?rooms=room1,room2')
        self.assertContains(response, self.room1.title, 2)
        self.assertContains(response, room2.title, 2)
        
        response = self.client.get(schedule_url + '?rooms=unknown1,unknown2')
        self.assertContains(response, self.room1.title, 0)
        self.assertContains(response, room2.title, 0)


class ScheduleCacheTestCase(djangotest.TestCase):

    def setUp(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        week = datetime.timedelta(days=5)
        self.summit = factory.make_one(Summit, name='uds-test', timezone='UTC')
        self.slot = factory.make_one(
            Slot,
            start_utc=now+one_hour,
            end_utc=now+(2*one_hour),
            type='open',
            summit=self.summit)

        self.track = factory.make_one(Track, slug='test.track', summit=self.summit)
        self.room = factory.make_one(Room, name='test.room', title='Test Room', summit=self.summit)
        self.room.tracks = [self.track]
        self.meeting = factory.make_one(Meeting, summit=self.summit, title='Test Meeting', name='meeting', private=False, requires_dial_in=False)
        self.meeting.tracks = [self.track]
        self.agenda = factory.make_one(Agenda, slot=self.slot, meeting=self.meeting, room=self.room)

        self.user = factory.make_one(User, username='testuser', first_name='Test', last_name='User')
        self.attendee = factory.make_one(Attendee, summit=self.summit, user=self.user, start_utc=now, end_utc=now+week)

    def tearDown(self):
        # Cached requests cause render.py to return old data, so clear the cache
        if hasattr(cache, 'clear'):
            cache.clear()
        # Older django didn't have .clear, but locmem cache did have ._cull
        elif hasattr(cache, '_cull'):
            cache._cull()

    def request_schedule_by_date(self):
        schedule_args = [self.summit.name, self.agenda.slot.start_utc.date()]
        schedule_url = reverse('summit.schedule.views.by_date', args=schedule_args)
        response = self.client.get(schedule_url)
        return response

    def request_schedule_by_track(self):
        schedule_args = [self.summit.name, self.track.slug]
        schedule_url = reverse('summit.schedule.views.by_track', args=schedule_args)
        response = self.client.get(schedule_url)
        return response

    def test_cache_cleared_on_meeting_change(self):
        self.assertEqual(None, cache.get('meeting-html-%s' % self.meeting.id))
        response = self.request_schedule_by_date()
        self.assertTrue('Test Meeting' in cache.get('meeting-html-%s' % self.meeting.id, ''))
        
        self.meeting.save()
        
        self.assertEqual(None, cache.get('meeting-html-%s' % self.meeting.id))
        response = self.request_schedule_by_date()
        self.assertTrue('Test Meeting' in cache.get('meeting-html-%s' % self.meeting.id, ''))

    def test_cache_cleared_on_agenda_change(self):
        self.assertEqual(None, cache.get('meeting-html-%s' % self.meeting.id))
        response = self.request_schedule_by_date()
        self.assertTrue('Test Meeting' in cache.get('meeting-html-%s' % self.meeting.id, ''))
        
        self.agenda.save()
        
        self.assertEqual(None, cache.get('meeting-html-%s' % self.meeting.id))
        response = self.request_schedule_by_date()
        self.assertTrue('Test Meeting' in cache.get('meeting-html-%s' % self.meeting.id, ''))

    def test_track_cache_cleared_on_meeting_change(self):
        self.assertEqual(None, cache.get('meeting-track-html-%s' % self.meeting.id))
        response = self.request_schedule_by_track()
        self.assertTrue('Test Meeting' in cache.get('meeting-track-html-%s' % self.meeting.id, ''))
        
        self.meeting.save()
        
        self.assertEqual(None, cache.get('meeting-track-html-%s' % self.meeting.id))
        response = self.request_schedule_by_track()
        self.assertTrue('Test Meeting' in cache.get('meeting-track-html-%s' % self.meeting.id, ''))

    def test_track_cache_cleared_on_agenda_change(self):
        self.assertEqual(None, cache.get('meeting-track-html-%s' % self.meeting.id))
        response = self.request_schedule_by_track()
        self.assertTrue('Test Meeting' in cache.get('meeting-track-html-%s' % self.meeting.id, ''))
        
        self.agenda.save()
        
        self.assertEqual(None, cache.get('meeting-track-html-%s' % self.meeting.id))
        response = self.request_schedule_by_track()
        self.assertTrue('Test Meeting' in cache.get('meeting-track-html-%s' % self.meeting.id, ''))


class ScheduleTestCase(djangotest.TestCase):

    def get_request(self):
        return RequestFactory().request()

    def get_schedule_from_request(self, date=None):
        request = self.get_request()
        summit = factory.make_one(Summit)
        return Schedule.from_request(request, summit, date=date)

    def test_default_read_only(self):
        schedule = self.get_schedule_from_request()
        self.assertEqual(False, schedule.edit)

    def get_user_with_schedule_permission(self):
        user = factory.make_one(User, is_active=True, is_staff=False,
                is_superuser=False)
        user.user_permissions.create(
            codename='change_agenda',
            content_type=factory.make_one(ContentType, app_label='schedule'))
        return user

    def get_get_request(self, **kwargs):
        return RequestFactory().get('/someurl/', data=kwargs)

    def get_edit_request(self, **kwargs):
        kwargs['edit'] = True
        return self.get_get_request(**kwargs)

    def test_editable(self):
        user = self.get_user_with_schedule_permission()
        request = self.get_edit_request()
        request.user = user
        summit = factory.make_one(Summit, state='schedule')
        attendee = factory.make_one(Attendee, summit=summit, user=user)
        schedule = Schedule.from_request(request, summit, attendee)
        self.assertEqual(True, schedule.edit)

    def test_read_only_for_public_summit(self):
        user = self.get_user_with_schedule_permission()
        request = self.get_edit_request()
        request.user = user
        summit = factory.make_one(Summit, state='public')
        attendee = factory.make_one(Attendee, summit=summit, user=user)
        schedule = Schedule.from_request(request, summit, attendee)
        self.assertEqual(False, schedule.edit)

    def test_read_only_for_non_edit_request(self):
        user = self.get_user_with_schedule_permission()
        request = self.get_request()
        request.user = user
        summit = factory.make_one(Summit, state='schedule')
        attendee = factory.make_one(Attendee, summit=summit, user=user)
        schedule = Schedule.from_request(request, summit, attendee)
        self.assertEqual(False, schedule.edit)

    def test_read_only_for_unauthenticated_user(self):
        request = self.get_edit_request()
        summit = factory.make_one(Summit, state='schedule')
        schedule = Schedule.from_request(request, summit)
        self.assertEqual(False, schedule.edit)

    def test_read_only_for_user_without_permission(self):
        user = factory.make_one(User, is_active=True, is_superuser=False)
        request = self.get_edit_request()
        request.user = user
        summit = factory.make_one(Summit, state='schedule')
        schedule = Schedule.from_request(request, summit)
        self.assertEqual(False, schedule.edit)

    def test_default_not_personal(self):
        schedule = self.get_schedule_from_request()
        self.assertEqual(False, schedule.personal)

    def test_personal_if_specified_in_get(self):
        request = self.get_get_request(personal=True)
        summit = factory.make_one(Summit)
        schedule = Schedule.from_request(request, summit)
        self.assertEqual(True, schedule.personal)

    def test_date_set_from_date(self):
        date = datetime.date.today()
        schedule = self.get_schedule_from_request(date=date)
        self.assertEqual(date, schedule.date)
        self.assertEqual([date], schedule.dates)

    def test_date_parsed_from_string(self):
        date = datetime.date.today()
        date_str = date.strftime("%Y-%m-%d")
        schedule = self.get_schedule_from_request(date=date_str)
        self.assertEqual(date, schedule.date)
        self.assertEqual([date], schedule.dates)

    def test_dates_set_from_summit_if_not_passed(self):
        schedule = self.get_schedule_from_request()
        self.assertEqual(None, schedule.date)
        self.assertEqual(schedule.summit.dates(), schedule.dates)

    def test_room_set_from_room(self):
        request = self.get_request()
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit)
        schedule = Schedule.from_request(request, summit, room=room)
        self.assertEqual(room, schedule.room)
        self.assertEqual([room], schedule.rooms)

    def test_room_set_from_rooms(self):
        request = self.get_request()
        summit = factory.make_one(Summit)
        rooms = factory.make_many(Room, 2, summit=summit)
        schedule = Schedule.from_request(request, summit, room=rooms)
        self.assertEqual(None, schedule.room)
        self.assertEqual(rooms, schedule.rooms)

    def test_room_set_from_summit_if_not_passed(self):
        request = self.get_request()
        summit = factory.make_one(Summit)
        room1 = factory.make_one(Room, summit=summit, type='open',
                name="room1")
        room2 = factory.make_one(Room, summit=summit, type='open',
                name="room2")
        factory.make_one(Room, summit=summit, type='closed')
        factory.make_one(Room, summit=summit, type='private')
        schedule = Schedule.from_request(request, summit)
        self.assertEqual(None, schedule.room)
        self.assertEqual(["room1", "room2"],
                sorted([r.name for r in schedule.rooms]))

    def test_rooms_include_private_if_user_is_staff(self):
        user = factory.make_one(User, is_active=True, is_staff=True,
                is_superuser=False)
        request = self.get_request()
        request.user = user
        summit = factory.make_one(Summit)
        room1 = factory.make_one(Room, summit=summit, type='open',
                name="room1")
        room2 = factory.make_one(Room, summit=summit, type='open',
                name="room2")
        factory.make_one(Room, summit=summit, type='closed')
        factory.make_one(Room, summit=summit, type='private',
                name="privateroom")
        schedule = Schedule.from_request(request, summit)
        self.assertEqual(None, schedule.room)
        self.assertEqual(["privateroom", "room1", "room2"],
                sorted([r.name for r in schedule.rooms]))

    def test_rooms_include_private_if_show_private(self):
        request = self.get_request()
        summit = factory.make_one(Summit)
        room1 = factory.make_one(Room, summit=summit, type='open',
                name="room1")
        room2 = factory.make_one(Room, summit=summit, type='open',
                name="room2")
        factory.make_one(Room, summit=summit, type='closed')
        factory.make_one(Room, summit=summit, type='private',
                name="privateroom")
        schedule = Schedule.from_request(request, summit, show_private=True)
        self.assertEqual(None, schedule.room)
        self.assertEqual(["privateroom", "room1", "room2"],
                sorted([r.name for r in schedule.rooms]))

    def test_track_is_none_by_default(self):
        schedule = self.get_schedule_from_request()
        self.assertEqual(None, schedule.track)

    def test_track_set_from_track(self):
        request = self.get_request()
        summit = factory.make_one(Summit)
        track = factory.make_one(Track, summit=summit)
        schedule = Schedule.from_request(request, summit, track=track)
        self.assertEqual(track, schedule.track)

    def test_nextonly_false_by_default(self):
        schedule = self.get_schedule_from_request()
        self.assertEqual(False, schedule.nextonly)

    def test_nextonly_set_from_get_parameters(self):
        request = self.get_get_request(next=True)
        summit = factory.make_one(Summit)
        schedule = Schedule.from_request(request, summit)
        self.assertEqual(True, schedule.nextonly)

    def test_fakenow_none_by_default(self):
        schedule = self.get_schedule_from_request()
        self.assertEqual(None, schedule.fakenow)

    def test_fakenow_set_from_get_parameters(self):
        summit = factory.make_one(Summit)
        date = datetime.datetime(2011, 7, 8, 19, 12)
        date = pytz.timezone(summit.timezone).localize(date)
        request = self.get_get_request(fakenow=date.strftime("%Y-%m-%d_%H:%M"))
        schedule = Schedule.from_request(request, summit)
        self.assertEqual(date, schedule.fakenow)

    def test_fakenow_set_to_none_if_invalid(self):
        summit = factory.make_one(Summit)
        request = self.get_get_request(fakenow="AAAAA")
        schedule = Schedule.from_request(request, summit)
        self.assertEqual(None, schedule.fakenow)

    def get_schedule(self, edit=False, room=None, summit=None, dates=None,
            rooms=None):
        request = self.get_request()
        if summit is None:
            summit = factory.make_one(Summit)
        schedule = Schedule(request, summit, edit=edit, room=room,
            dates=dates, rooms=rooms)
        return schedule

    def test_calculate_unscheduled_does_nothing_when_read_only(self):
        schedule = self.get_schedule(edit=False)
        schedule.calculate_unscheduled()
        self.assertEqual([], schedule.unscheduled)

    def test_calculate_unscheduled_includes_unscheduled(self):
        schedule = self.get_schedule(edit=True)
        meeting = factory.make_one(Meeting, summit=schedule.summit, private=False)
        schedule.calculate_unscheduled()
        self.assertEqual([meeting], schedule.unscheduled)

    def test_calculate_unscheduled_ignores_scheduled_meetings(self):
        schedule = self.get_schedule(edit=True)
        meeting = factory.make_one(Meeting, summit=schedule.summit, private=False)
        room = factory.make_one(Room, summit=schedule.summit)
        slot = factory.make_one(Slot, summit=schedule.summit)
        meeting.agenda_set.create(room=room, slot=slot)
        schedule.calculate_unscheduled()
        self.assertEqual([], schedule.unscheduled)

    def test_calculate_unscheduled_ignores_meetings_in_tracks_not_in_this_room(self):
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit, type='open')
        schedule = self.get_schedule(edit=True, room=room, summit=summit)
        meeting = factory.make_one(Meeting, summit=schedule.summit,
                type='blueprint', private=False)
        track = factory.make_one(Track, summit=summit)
        other_track = factory.make_one(Track, summit=summit)
        room.tracks = [track]
        meeting.tracks = [other_track]
        schedule.calculate_unscheduled()
        self.assertEqual([], schedule.unscheduled)

    def test_calculate_unscheduled_includes_meetings_without_a_track(self):
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit, type='open')
        schedule = self.get_schedule(edit=True, room=room, summit=summit)
        meeting = factory.make_one(Meeting, summit=schedule.summit,
                type='blueprint', private=False)
        track = factory.make_one(Track, summit=summit)
        room.tracks = [track]
        schedule.calculate_unscheduled()
        self.assertEqual([meeting], schedule.unscheduled)

    def test_calculate_unscheduled_includes_all_meetings_in_room_without_a_track(self):
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit, type='open')
        schedule = self.get_schedule(edit=True, room=room, summit=summit)
        meeting = factory.make_one(Meeting, summit=schedule.summit,
                type='blueprint', private=False)
        track = factory.make_one(Track, summit=summit)
        meeting.tracks = [track]
        schedule.calculate_unscheduled()
        self.assertEqual([meeting], schedule.unscheduled)

    def test_calculate_unscheduled_includes_meetings_of_the_right_track(self):
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit, type='open')
        schedule = self.get_schedule(edit=True, room=room, summit=summit)
        meeting = factory.make_one(Meeting, summit=schedule.summit,
                type='blueprint', private=False)
        track = factory.make_one(Track, summit=summit)
        meeting.tracks = [track]
        room.tracks = [track]
        schedule.calculate_unscheduled()
        self.assertEqual([meeting], schedule.unscheduled)

    def test_calculate_unscheduled_includes_meetings_with_one_right_track(self):
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit, type='open')
        schedule = self.get_schedule(edit=True, room=room, summit=summit)
        meeting = factory.make_one(Meeting, summit=schedule.summit,
                type='blueprint', private=False)
        track = factory.make_one(Track, summit=summit)
        other_track = factory.make_one(Track, summit=summit)
        meeting.tracks = [track, other_track]
        room.tracks = [track]
        schedule.calculate_unscheduled()
        self.assertEqual([meeting], schedule.unscheduled)

    def test_calculate_unscheduled_ignores_plenaries_in_the_room_view(self):
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit, type='open')
        schedule = self.get_schedule(edit=True, room=room, summit=summit)
        meeting = factory.make_one(Meeting, summit=schedule.summit,
                type='plenary', private=False)
        schedule.calculate_unscheduled()
        self.assertEqual([], schedule.unscheduled)

    def test_calculate_unscheduled_ignores_talks_in_the_room_view(self):
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit, type='open')
        schedule = self.get_schedule(edit=True, room=room, summit=summit)
        meeting = factory.make_one(Meeting, summit=schedule.summit,
                type='talk', private=False)
        schedule.calculate_unscheduled()
        self.assertEqual([], schedule.unscheduled)

    def test_calculate_unscheduled_ignores_specials_in_the_room_view(self):
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit, type='open')
        schedule = self.get_schedule(edit=True, room=room, summit=summit)
        meeting = factory.make_one(Meeting, summit=schedule.summit,
                type='special', private=False)
        schedule.calculate_unscheduled()
        self.assertEqual([], schedule.unscheduled)

    def test_calculate_unscheduled_shows_plenaries_in_the_plenary_room_view(self):
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit, type='plenary')
        schedule = self.get_schedule(edit=True, room=room, summit=summit)
        meeting = factory.make_one(Meeting, summit=schedule.summit,
                type='plenary', private=False)
        schedule.calculate_unscheduled()
        self.assertEqual([meeting], schedule.unscheduled)

    def test_calculate_unscheduled_ignores_non_plenaries_in_the_plenary_room_view(self):
        summit = factory.make_one(Summit)
        room = factory.make_one(Room, summit=summit, type='plenary')
        schedule = self.get_schedule(edit=True, room=room, summit=summit)
        meeting = factory.make_one(Meeting, summit=schedule.summit,
                type='blueprint', private=False)
        schedule.calculate_unscheduled()
        self.assertEqual([], schedule.unscheduled)

    def test_calculate_passes_with_multiple_plenary_rooms_if_editing(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(hours=1)
        summit = factory.make_one(
            Summit, date_start=now.date(), date_end=now.date(),
            timezone='UTC')
        slot = factory.make_one(
            Slot, summit=summit, type='plenary',
            start_utc=now-(2*one_hour), end_utc=now-(1*one_hour))
        room1 = factory.make_one(Room, summit=summit, type='plenary', start_utc=now-(2*one_hour), end_utc=now-(1*one_hour))
        room2 = factory.make_one(Room, summit=summit, type='plenary', start_utc=now-(2*one_hour), end_utc=now-(1*one_hour))
        schedule = self.get_schedule(
            edit=True, rooms=[room1, room2], summit=summit,
            dates=[now.date()])
        schedule.calculate()
        # To avoid test being fragile and arbitrarily dependent on the
        # room order, we check the returned schedule.meetings bit-by-bit.
        self.assertEqual([slot], schedule.meetings.keys())
        self.assertEqual(1, len(set(schedule.meetings[slot])))


class LaunchpadExportNode(dict):

    def __init__(self, *args, **kwargs):
        self.__children = {}
        super(LaunchpadExportNode, self).__init__(*args, **kwargs)

    def add_child(self, key, node):
        self.__children.setdefault(key, [])
        self.__children[key].append(node)

    def findall(self, key):
        return self.__children.get(key, [])

    def find(self, key):
        return self.findall(key)[0]


class SummitModelTestCase(djangotest.TestCase):

    def get_basic_launchpad_response(self):
        elem = LaunchpadExportNode()
        elem.add_child("attendees", LaunchpadExportNode())
        elem.add_child("unscheduled", LaunchpadExportNode())
        return elem

    def make_one_future_slot(self, summit=None):
        if summit is None:
            summit = factory.make_one(Summit)
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(hours=1)
        return factory.make_one(Slot, summit=summit, start=now+one_hour,
                end=now+one_hour+one_hour, type='open')

    def test_update_meeting_skips_no_name(self):
        summit = factory.make_one(Summit)
        elem = LaunchpadExportNode()
        meeting = summit.update_meeting_from_launchpad(elem)
        self.assertEqual(None, meeting)
        self.assertEqual(0, Meeting.objects.all().count())

    def test_update_meeting_trims_name(self):
        summit = factory.make_one(Summit)
        elem = LaunchpadExportNode(name="very " * 20 + "longname")
        meeting = summit.update_meeting_from_launchpad(elem)
        # Names are truncated at 100 chars.
        expected_name = "very " * 20
        self.assertEqual(expected_name, meeting.name)
        self.assertEqual(1, summit.meeting_set.filter(name__exact=expected_name).count())

    def test_update_meeting_accepts_existing_meeting(self):
        summit = factory.make_one(Summit)
        name = "meeting-name"
        title = "other-title"
        elem = LaunchpadExportNode(name=name)
        summit.meeting_set.create(name=name, title=title)
        meeting = summit.update_meeting_from_launchpad(elem)
        self.assertEqual(name, meeting.name)
        self.assertEqual(1, summit.meeting_set.filter(name__exact=name, title__exact=title).count())

    def test_update_from_launchpad_response_empty(self):
        summit = factory.make_one(Summit)
        elem = self.get_basic_launchpad_response()
        meetings = summit.update_from_launchpad_response(elem)
        self.assertEqual(set(), meetings)
        self.assertEqual(0, Meeting.objects.all().count())
        self.assertEqual(0, Attendee.objects.all().count())

    def test_update_from_launchpad_response_handles_no_name(self):
        summit = factory.make_one(Summit)
        elem = self.get_basic_launchpad_response()
        meeting_node = LaunchpadExportNode(name=None)
        elem.find("unscheduled").add_child("meeting", meeting_node)
        meetings = summit.update_from_launchpad_response(elem)
        self.assertEqual(set(), meetings)

    def test_launchpad_sprint_import_urls_uses_default(self):
        summit = factory.make_one(Summit, name='test-sprint')
        self.assertEqual(
            ['https://launchpad.net/sprints/test-sprint/+temp-meeting-export'],
            summit.launchpad_sprint_import_urls())

    def test_launchpad_sprint_import_url_uses_one_summit_sprint(self):
        import_url = 'http://example.com/test'
        summit = factory.make_one(Summit)
        factory.make_one(SummitSprint, summit=summit, import_url=import_url)
        self.assertEqual([import_url], summit.launchpad_sprint_import_urls())

    def test_launchpad_sprint_import_url_uses_two_summit_sprint(self):
        import_url1 = 'http://example.com/test1'
        import_url2 = 'http://example.com/test2'
        summit = factory.make_one(Summit)
        factory.make_one(SummitSprint, summit=summit, import_url=import_url1)
        factory.make_one(SummitSprint, summit=summit, import_url=import_url2)
        self.assertEqual(sorted([import_url1, import_url2]), sorted(summit.launchpad_sprint_import_urls()))

    def test_update_from_launchpad_gets_info_for_all_import_urls(self):
        import_url1 = 'http://example.com/test1'
        import_url2 = 'http://example.com/test2'
        summit = factory.make_one(Summit)
        factory.make_one(SummitSprint, summit=summit, import_url=import_url1)
        factory.make_one(SummitSprint, summit=summit, import_url=import_url2)
        called_urls = []
        def get_sprint_info(url):
            called_urls.append(url)
            return self.get_basic_launchpad_response()
        summit._get_sprint_info_from_launchpad = get_sprint_info
        summit.update_from_launchpad()
        self.assertEqual(sorted([import_url1, import_url2]), sorted(called_urls))

    def test_update_from_launchpad_does_the_update(self):
        summit = factory.make_one(Summit)
        def get_sprint_info(url):
            elem = self.get_basic_launchpad_response()
            meeting_node = LaunchpadExportNode(name="foo")
            elem.find("unscheduled").add_child("meeting", meeting_node)
            return elem
        summit._get_sprint_info_from_launchpad = get_sprint_info
        summit.update_from_launchpad()
        self.assertEqual(1, summit.meeting_set.all().count())

    def test_update_from_launchpad_deletes_unseen_meetings(self):
        summit = factory.make_one(Summit)
        meeting = summit.meeting_set.create(spec_url='test_url', name="name")
        def get_sprint_info(url):
            elem = self.get_basic_launchpad_response()
            meeting_node = LaunchpadExportNode(name="other")
            elem.find("unscheduled").add_child("meeting", meeting_node)
            return elem
        summit._get_sprint_info_from_launchpad = get_sprint_info
        summit.update_from_launchpad()
        self.assertEqual(0, summit.meeting_set.filter(name__exact="name").count())

    def test_update_from_launchpad_doesnt_delete_meetings_with_no_spec_url(self):
        summit = factory.make_one(Summit)
        meeting = summit.meeting_set.create(spec_url='', name="name")
        def get_sprint_info(url):
            elem = self.get_basic_launchpad_response()
            meeting_node = LaunchpadExportNode(name="other")
            elem.find("unscheduled").add_child("meeting", meeting_node)
            return elem
        summit._get_sprint_info_from_launchpad = get_sprint_info
        summit.update_from_launchpad()
        self.assertEqual(1, summit.meeting_set.filter(name__exact="name").count())

    def test_update_from_launchpad_updates_last_update(self):
        old_now = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        summit = factory.make_one(Summit, last_update=old_now)
        def get_sprint_info(url):
            return self.get_basic_launchpad_response()
        summit._get_sprint_info_from_launchpad = get_sprint_info
        summit.update_from_launchpad()
        self.assertTrue(old_now < summit.last_update)

    def test_reschedule_does_nothing_on_empty_schedule(self):
        summit = factory.make_one(Summit)
        summit.reschedule()

    def test_reschedule_removes_missing_participants(self):
        summit = factory.make_one(Summit)
        meeting1 = factory.make_one(Meeting, summit=summit,
                requires_dial_in=False, private=False)
        meeting2 = factory.make_one(Meeting, summit=summit,
                requires_dial_in=False, private=False)
        room1 = factory.make_one(Room, summit=summit)
        room2 = factory.make_one(Room, summit=summit)
        slot = self.make_one_future_slot(summit=summit)
        attendee = factory.make_one(Attendee, summit=summit,
                start_utc=slot.start_utc, end_utc=slot.end_utc)
        meeting1.participant_set.create(attendee=attendee, required=True)
        meeting2.participant_set.create(attendee=attendee, required=True)
        factory.make_one(Agenda, meeting=meeting1, room=room1, slot=slot,
                auto=True)
        factory.make_one(Agenda, meeting=meeting2, room=room2, slot=slot,
                auto=True)
        summit.reschedule()
        self.assertEqual(1, slot.agenda_set.all().count())

    def test_reschedule_removes_unavailable_participants(self):
        summit = factory.make_one(Summit)
        meeting = factory.make_one(Meeting, summit=summit,
                requires_dial_in=False, private=False)
        room = factory.make_one(Room, summit=summit)
        slot = self.make_one_future_slot(summit=summit)
        attendee = factory.make_one(Attendee, summit=summit,
                start_utc=slot.end_utc,
                end_utc=slot.end_utc+datetime.timedelta(hours=1))
        meeting.participant_set.create(attendee=attendee, required=True)
        factory.make_one(Agenda, meeting=meeting, room=room, slot=slot,
                auto=True)
        summit.reschedule()
        self.assertEqual(0, slot.agenda_set.all().count())

    def test_reschedule_removes_insufficient_slots(self):
        summit = factory.make_one(Summit)
        meeting = factory.make_one(Meeting, summit=summit, slots=2,
                requires_dial_in=False, private=False)
        room = factory.make_one(Room, summit=summit)
        slot = self.make_one_future_slot(summit=summit)
        factory.make_one(Agenda, meeting=meeting, room=room, slot=slot,
                auto=True)
        summit.reschedule()
        self.assertEqual(0, slot.agenda_set.all().count())

    def test_reschedule_leaves_old_slots(self):
        summit = factory.make_one(Summit)
        meeting = factory.make_one(Meeting, summit=summit, slots=2,
                requires_dial_in=False, private=False)
        room = factory.make_one(Room, summit=summit)
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(hours=1)
        slot = factory.make_one(Slot, summit=summit, start=now-one_hour,
                end=now, type='open')
        factory.make_one(Agenda, meeting=meeting, room=room, slot=slot,
                auto=True)
        summit.reschedule()
        self.assertEqual(1, slot.agenda_set.all().count())

    def test_reschedule_leaves_manually_scheduled(self):
        summit = factory.make_one(Summit)
        meeting = factory.make_one(Meeting, summit=summit, slots=2,
                requires_dial_in=False, private=False)
        room = factory.make_one(Room, summit=summit)
        slot = self.make_one_future_slot(summit=summit)
        factory.make_one(Agenda, meeting=meeting, room=room, slot=slot,
                auto=False)
        summit.reschedule()
        self.assertEqual(1, slot.agenda_set.all().count())

    def test_update_from_launchpad_adds_attendees(self):
        def mock_set_openid(user, force=False):
            self.assertEquals(user.username, 'testuser')
            mock_set_openid.called = True
            return True
        mock_set_openid.called = False
        launchpad.set_user_openid = mock_set_openid

        summit = factory.make_one(Summit)
        attendee_node = LaunchpadExportNode(name='testuser')
        summit.update_attendee_from_launchpad(attendee_node)

        self.assertEqual(1, summit.attendee_set.filter(user__username__exact="testuser").count())
        self.assertTrue(mock_set_openid.called)
