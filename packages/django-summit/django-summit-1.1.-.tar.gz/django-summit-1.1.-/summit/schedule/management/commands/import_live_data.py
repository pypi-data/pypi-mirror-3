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

import sys
import urllib2
import json
import datetime
import re

import urllib
try:
    import json
except ImportError:
    import simplejson as json

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from summit.schedule.models import (
    Summit,
    Slot,
    Room,
    Attendee,
    Meeting,
    Agenda,
    Participant,
    Track,
    Crew,
    Lead,
)

__all__ = (
    'Command',
)

SERVICE_ROOT = 'http://summit.ubuntu.com/api'

class Command(BaseCommand):
    help = "Import data from the services API of the live site"
    option_list = BaseCommand.option_list + (
        make_option("-s", "--summit",
            dest="summit",
            help="Supply a remote summit to import."),
        make_option("-u", "--url",
            dest="service_root",
            default='http://summit.ubuntu.com/api/',
            help="Live instance service root."),
        make_option("-A", "--all", dest="all", action="store_true",
            help="Import all data, not just scheduling", default=False),
    )


    def handle(self, *args, **options):
        summit_name = options["summit"]
        if summit_name is None or summit_name == '':
            print "You must supply a summit name to import.  Run manage.py import_live_data --help for more info."
            return
        
        import_all = options["all"]
        service = SummitImporter(options["service_root"])
        print "Service root: %s" % service.service_root
        print "Summit: %s" % summit_name

        service.import_summit(summit_name)
        print "Import complete."

class SummitImporter(object):

    def __init__(self, service_root=None):
        self.service_root = service_root or SERVICE_ROOT
        self.cache = {}
        self.summit_map = {}
        self.slot_map = {}
        self.meeting_map = {}
        self.room_map = {}
        self.agenda_map = {}
        self.track_map = {}
        self.attendee_map = {}
        self.user_map = {}
        
    def clearCache(self, resource=None):
        if resource is None:
            self.cache = {}
        elif self.cache.has_key(resource):
            self.cache[resource] = {}
        
    # Generic, caching Collection
    def getCollection(self, resource, id_field='id', **kargs):
        if not self.cache.has_key(resource):
            self.cache[resource] = {}
        url = '/'.join([self.service_root, resource, ''])
        if len(kargs) > 0:
            url = '?'.join([url, urllib.urlencode(kargs)])
        s = urllib.urlopen(url)
        col = dict([(o[id_field], o) for o in json.load(s)])
        self.cache[resource].update(col)
        return col

    # Generic, cacheable Entity
    def getEntity(self, resource, entity_id):
        if not self.cache.has_key(resource):
            self.cache[resource] = {}
        if not self.cache[resource].has_key(entity_id):
            url = '/'.join([self.service_root, resource, str(entity_id)])
            s = urllib.urlopen(url)
            self.cache[resource][entity_id] = json.load(s)
        return self.cache[resource][entity_id]

    def import_summit(self, summit_name):
        try:
            Summit.objects.get(name=summit_name).delete()
            print "Deleting existing summit."
        except Summit.DoesNotExist:
            # If we don't already have a summit by that name, there's nothing to
            # delete
            pass

        print "Importing summit..."
        collection = self.getCollection('summit', name=summit_name)
        data = collection.values()[0]
        summit = Summit.objects.create(
            name = data['name'],
            title = data['title'],
            date_start = datetime.datetime.strptime(data['date_start'], '%Y-%m-%d'),
            date_end = datetime.datetime.strptime(data['date_end'], '%Y-%m-%d'),
            state = data['state'],
            location = data['location'],
            timezone = data['timezone'],
        )
        self.summit_map[summit.id] = data['id']
        
        self.import_users()
        self.import_slots(summit)
        self.import_tracks(summit)
        self.import_rooms(summit)
        self.import_meetings(summit)
        self.import_agenda(summit)
        self.import_attendees(summit)

    def import_users(self):
        print "Importing users..."
        collection = self.getCollection('user')
        for user_id, data in collection.items():
			#print "User: %s" % data
            user, created = User.objects.get_or_create(
                username = data['username'],
            )
            self.user_map[user_id] = user.id

    def import_tracks(self, summit):
        print "Importing tracks..."
        collection = self.getCollection('track', summit=self.summit_map[summit.id])
        for track_id, data in collection.items():
            #print "Track: %s" % data
            track = Track.objects.create(
                summit = summit,
                title = data['title'],
                slug = data['slug'],
                color = data['color'],
                allow_adjacent_sessions = data['allow_adjacent_sessions'],
            )
            self.track_map[track_id] = track.id

    def import_slots(self, summit):
        print "Importing slots..."
        collection = self.getCollection('slot', summit=self.summit_map[summit.id])
        for slot_id, data in collection.items():
            #print "Slot: %s" % data
            slot = Slot.objects.create(
                summit = summit,
                type = data['type'],
                start_utc = datetime.datetime.strptime(data['start_utc'], '%Y-%m-%d %H:%M:%S'),
                end_utc = datetime.datetime.strptime(data['end_utc'], '%Y-%m-%d %H:%M:%S'),
            )
            self.slot_map[slot_id] = slot.id

    def import_rooms(self, summit):
        print "Importing rooms..."
        collection = self.getCollection('room', summit=self.summit_map[summit.id])
        for room_id, data in collection.items():
            #print "Room: %s" % data
            room = Room.objects.create(
                summit = summit,
                name = data['name'],
                title = data['title'],
                icecast_url = data['icecast_url'],
                type = data['type'],
                size = data['size'],
                has_dial_in = data['has_dial_in'],
                start_utc = datetime.datetime.strptime(data['start_utc'] or '1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'),
                end_utc = datetime.datetime.strptime(data['end_utc'] or '1970-01-01 23:59:59', '%Y-%m-%d %H:%M:%S'),
            )
            for track_id in data['tracks']:
                try:
                    room.tracks.add(self.track_map[track_id])
                except KeyError, e:
                    print "Warning. Unknown track: %s" % track_id
                
            self.room_map[room_id] = room.id

    def import_meetings(self, summit):
        print "Importing meetings..."
        collection = self.getCollection('meeting', summit=self.summit_map[summit.id])
        for meeting_id, data in collection.items():
            #print "Meeting: %s" % data
            meeting = Meeting.objects.create(
                summit = summit,
                name = data['name'],
                title = data['title'],
                description = data['description'],
                wiki_url = data['wiki_url'],
                spec_url = data['spec_url'],
                pad_url = data['pad_url'],
                priority = data['priority'],
                status = data['status'],
                slots = data['slots'],
            )
            for track_id in data['tracks']:
                try:
                    meeting.tracks.add(self.track_map[track_id])
                except KeyError, e:
                    print "Warning. Unknown track: %s" % track_id
            self.meeting_map[meeting_id] = meeting.id

    def import_agenda(self, summit):
        print "Importing agenda..."
        collection = self.getCollection('agenda', room__summit=self.summit_map[summit.id])
        for agenda_id, data in collection.items():
            #print "Agenda: %s" % data
            agenda = Agenda.objects.create(
                room_id = self.room_map[data['room']],
                slot_id = self.slot_map[data['slot']],
                meeting_id = self.meeting_map[data['meeting']],
                auto = data['auto'],
            )
            self.agenda_map[agenda_id] = agenda.id
            
    def import_attendees(self, summit):
        print "Importing attendees..."
        collection = self.getCollection('attendee', summit=self.summit_map[summit.id])
        for attendee_id, data in collection.items():
            #print "Attendee: %s" % data
            attendee = Attendee.objects.create(
                summit = summit,
                user_id = self.user_map[data['user']],
                start_utc = datetime.datetime.strptime(data['start_utc'] or '1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'),
                end_utc = datetime.datetime.strptime(data['end_utc'] or '1970-01-01 23:59:59', '%Y-%m-%d %H:%M:%S'),
                crew = data['crew'],
            )
            self.attendee_map[attendee_id] = attendee.id
