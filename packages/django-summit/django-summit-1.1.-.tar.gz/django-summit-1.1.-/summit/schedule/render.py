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
import datetime
import pytz
import simplejson as json
import urllib

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.utils.html import escape
from django.utils.safestring import mark_safe

from schedule.models import *

__all__ = (
    'Schedule',
)


def escape_strings(value):
    escaped = value.replace('%', '%%')
    return escape(escaped)


def get_style_def_for_meeting(meeting, pos=None):
    if pos:
        style = {
            'left':        '%dpx' % pos['left'],
            'top':         '%dpx' % pos['top'],
            'height':      '%dpx' % pos['height'],
            'min-height':  '%dpx' % pos['height'],
            'width':       '%dpx' % pos['width'],
        }
    else:
        height = meeting.slots * 120 - 12
        style = {
            'height':      '%dpx' % height,
            'min-height':  '%dpx' % height,
        }
    if meeting.tracks.count() > 0:
        style['background-color'] = '#'+meeting.tracks.all()[0].color
    return '; '.join(': '.join(x) for x in style.items())


class Schedule(object):

    @classmethod
    def from_request(cls, request, summit,
                     attendee=None, date=None, room=None, track=None,
                     show_private=False, nextonly=False):
        edit = False
        if summit.state != 'public' \
                and 'edit' in request.GET:
            if request.user.is_authenticated() \
                    and summit.can_change_agenda(attendee):
                edit = True

        if 'personal' in request.GET:
            personal = True
        else:
            personal = False

        if isinstance(date, basestring):
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            dates = [date]
        elif date is not None:
            date = date
            dates = [date]
        else:
            date = None
            dates = summit.dates()

        if isinstance(room, (list, tuple)):
            rooms = room
            room = None
        elif room is not None:
            room = room
            rooms = [room]
        else:
            room = None
            rooms = summit.open_rooms()

            if (show_private
                or (request.user.is_authenticated() and request.user.is_staff)):
                    rooms = rooms + summit.private_rooms()

        if 'next' in request.GET:
            nextonly = True

        fakenow = None
        if 'fakenow' in request.GET:
            try:
                fakenow = datetime.datetime.strptime(
                    request.GET['fakenow'], "%Y-%m-%d_%H:%M")
                fakenow = pytz.timezone(
                    summit.timezone).localize(fakenow)
                fakenow = fakenow.astimezone(pytz.utc)
            except ValueError:
                fakenow = None

        return cls(request, summit, attendee=attendee, date=date, room=room,
                track=track, edit=edit, personal=personal, dates=dates,
                rooms=rooms, nextonly=nextonly, fakenow=fakenow)

    def __init__(self, request, summit,
                 attendee=None, date=None, room=None, track=None,
                 edit=False, personal=False, dates=None, rooms=None,
                 nextonly=False, fakenow=None):
        """Create a Schedule.

        :param request: the Request that is being acted on.
        :param summit: the Summit that is being viewed.
        :param attendee: the Attendee whose schedule is being viewed.
        :param edit: whether the schedule should be editable.
        :param personal: whether the personal schedule should be shown.
        :param date: the date which is being viewed, or None if several
            dates.
        :param dates: all the dates to show.
        :param room: the room that is being viewed.
        :param rooms: all the rooms to show.
        :param track: the track to show.
        :param nextonly: whether to show the next slot only.
        :param fakenow: the datetime to pretend that it currently is.
        """
        self.request = request
        self.summit = summit
        self.attendee = attendee
        self.edit = edit
        self.personal = personal
        # Maybe make self.date be a boolean?
        self.date = date
        self.dates = []
        if dates:
            self.dates = dates
        # Maybe make self.room be a boolean?
        self.room = room
        self.rooms = []
        if rooms:
            self.rooms = rooms
        self.track = track
        self.nextonly = nextonly
        self.fakenow = fakenow
        self.endofday = False

    def calculate(self):
        # Cache slot list for each date we're going to be showing
        self.slots = {}
        for date in self.dates:
             self.slots[date] = []
        self.meetings = {}
        if not self.nextonly:
            _slots = self.summit.slot_set.select_related().all()
        else:
            _now = datetime.datetime.utcnow()
            if self.fakenow is not None:
                _now = self.fakenow
            _local_now = self.summit.localize(_now)
            try:
                _slots = self.summit.slot_set.filter(
                    start_utc__lte=_now, end_utc__gte=_now)[0]
                _next_slot = _slots.next()
                if _next_slot is None or _next_slot.start.date() != _now.date():
                    self.endofday = True
                    return
                else:
                    if _next_slot.type == 'lunch':
                        _slots = [_next_slot.next()]
                    else:
                        _slots = [_next_slot]
            except IndexError:
                try:
                    # Guessing. We are in a non-slotted break.
                    _guess = self.summit.slot_set.filter(
                        start_utc__gt=_now).order_by('start_utc')[0]
                    if _guess.start.date() != _local_now.date():
                        self.endofday = True
                        return
                    else:
                        _slots = [_guess]
                except IndexError:
                    _slots = []
        for slot in _slots:
            date = slot.start.date()
            if date in self.slots:
                self.slots[date].append(slot)
                self.meetings[slot] = []

        # Catch the day given having no slots
        if self.date is not None and not len(self.slots[self.date]):
            raise Http404

        agenda_cache = {}
        for a in Agenda.objects.select_related().filter(slot__summit=self.summit):
            if not agenda_cache.has_key(a.slot.id):
                agenda_cache[a.slot.id] = {}
            agenda_cache[a.slot.id][a.room.id] = a
            
        # Work out what item goes into each slot, and the position in
        # the rendered schedule for it
        for date in self.dates:
            for slot in self.slots[date]:
                slot_agenda = agenda_cache.get(slot.id, {})
                # If this is a plenary slot, force the room to be the
                # current allocated one, or a room of plenary type,
                # no matter what room we're looking at
                if slot.type == 'plenary':
                    try:
                        agendas = slot.agenda_set.all()
                        if len(agendas) == 0:
                            raise ObjectDoesNotExist
                        else:
                            agenda = agendas[0]
                        self.meetings[slot].append(
                            (agenda.room, agenda.meeting))
                    except ObjectDoesNotExist:
                        try:
                            rooms = [r for r
                                     in self.summit.room_set.filter(type__exact='plenary')
                                     if r.available(slot)]
                            if len(rooms) > 0:
                                self.meetings[slot].append((rooms[0], None))
                                meeting_room = rooms[0]
                        except KeyError:
                            if not self.track:
                                self.meetings[slot].append((None, None))
                elif slot.type in ('break', 'lunch'):
                    rooms = [r for r in self.summit.room_set.all() if r.available(slot)]
                    if len(rooms) > 0:
                        self.meetings[slot].append((rooms[0], None))
                else:
                    for room in self.rooms:
                        if room.id in slot_agenda:
                            agenda = slot_agenda[room.id]
                            if not self.track \
                                    or self.track in agenda.meeting.tracks.all():
                                self.meetings[slot].append(
                                    (room, agenda.meeting))
                        else:
                            show_empty = False

                            # If we're not in track view, always show the
                            # empty slot for the room
                            if not self.track:
                                show_empty = True

                            # If we're in track view, check for a previous
                            # double meeting that means we need the empty
                            # slot to reserve the space
                            if self.track:
                                slot_num = self.slots[date].index(slot)
                                for i in range(slot_num, 0, -1):
                                    distance = 2 + slot_num - i
                                    prev_slot = self.slots[date][i - 1]
                                    if prev_slot.type != slot.type:
                                        break

                                    prev_meeting = dict(self.meetings[prev_slot])
                                    if room not in prev_meeting:
                                        continue

                                    if prev_meeting[room] is not None \
                                            and prev_meeting[room].slots >= distance:
                                        show_empty = True

                            # Otherwise if we're editing the track view,
                            # show an empty slot if the room is available
                            # for this track
                            if self.edit and self.track and self.track in room.tracks.all():
                                show_empty = True

                            if show_empty:
                                self.meetings[slot].append((room, None))
        self.calculate_unscheduled()

    def calculate_unscheduled(self):
        # When editing, we also need the list of unscheduled meetings
        self.unscheduled = []
        if self.edit:
            query_parts = []
            # Don't show scheduled meetings
            query_parts.append(Q(agenda__isnull=True))
            if self.room:
                # Don't show meetings unless they're on this room's track
                # (but do show meetings without a track, or all meetings
                # in un-tracked rooms)
                room_tracks = self.room.tracks.all()
                if room_tracks.count() > 0:
                    query_parts.append(
                        Q(tracks__isnull=True)|Q(tracks__in=room_tracks))
                only_plenary_meetings = Q(type__in=('plenary', 'talk', 'special'))
                # Don't show unscheduled plenary tracks in room view unless
                # it's the plenary room
                if self.room.type != 'plenary':
                    query_parts.append(~only_plenary_meetings)
                # Don't show unscheduled non-plenary tracks in room view
                # unless it's the plenary room
                if self.room.type == 'plenary':
                    query_parts.append(only_plenary_meetings)
            self.unscheduled = list(
                self.summit.meeting_set.filter(*query_parts))

    def crew(self):
        from schedule.models import Crew
        return Crew.objects.filter(date_utc__in=self.dates)

    def next_session(self):
        import traceback
        try:
            return self._now_and_next()
        except:
            return mark_safe("<pre>%s</pre>" % escape(traceback.format_exc()))

    def _now_and_next(self):
        html = u''

        if self.endofday:
            html += '<p><strong>No more sessions for today.</strong></p>'
            return mark_safe(html)

        headings = u''
        meetings = u''

        for date_num, date in enumerate(self.dates):
            for slot_num, slot in enumerate(self.slots[date]):
                for room_num, info in enumerate(self.meetings[slot]):
                    (room, meeting) = info
                    if room is None: 
                        continue
                    if meeting is None:
                        meeting_title = ''
                    else:
                        meeting_title = meeting.title
                    try:
                        color = meeting.tracks.all()[0].color
                    except (IndexError, AttributeError):
                        color = "aaaaaa"
                    headings += '<th>%s</th>\n' % escape(room.title)
                    meetings += '<td style="background-color: #%s;">%s</td>\n' % (color, escape(meeting_title))

        html += '<table>\n'

        html += '<tr>\n'
        html += headings
        html += '</tr>\n'

        html += '<tr>\n'
        html += meetings
        html += '</tr>\n'

        html += '</table>\n'

        return mark_safe(html)

    def debug(self):
        import traceback
        try:
            return self.as_html()
        except:
            return mark_safe("<pre>%s</pre>" % escape(traceback.format_exc()))

    def gen_slot_html(self, slot, slot_num, meeting, room, date, date_num, room_num):
        html = ""
        pos = {}
        # Left is calculated by day and room,
        # with 12px added for each column for borders and margin
        if slot.type == 'plenary':
            meeting_width = (
                112*self.day_width/len(self.meetings[slot]))
            pos['left'] = (date_num * meeting_width) + (room_num * 112)
        else:
            pos['left'] = (date_num * self.day_width + room_num) * 112
            # Top is calculated based on time from first slot of the
        # day, 2px per minute
        # Lunch slot is smaller, so if we are already past that,
        # reduce the value
        pos['top'] = (slot.start
                      - self.slots[date][0].start).seconds / 30 + (self.height - 10)
        if self.had_lunch:
            pos['top'] -= 100
        if slot.type == 'lunch':
            self.had_lunch = True
            # Height is calculated based on slot length,
        # with 12px removed for borders and margin
        pos['height'] = (slot.end - slot.start).seconds / 30 - self.height
        if slot.type == 'lunch':
            pos['height'] = 12
            # Width is fixed at 100px per column, unless this is the
        # first slot of the day and it's a special one in which
        # case it spans all rooms, with 12px removed for borders
        # and margin
        full_width = self.day_width * 112
        if slot.type in ('break', 'lunch'):
            if room_num > 0:
                return
            else:
                pos['width'] = full_width - 12
        elif slot.type == 'plenary':
            pos['width'] = full_width / len(self.meetings[slot]) - 12
        else:
            pos['width'] = 100

        if meeting:
            # Always place a hidden slot in edit mode
            if self.edit:
                html += self.slot_div(room, slot, pos, hidden=True)

            # If this meeting spans multiple slots, adjust the
            # height to match.  Take care not to cross any
            # non-open or scheduled slots though!
            last = slot_num + meeting.slots
            if meeting.slots > 1 and last <= len(self.slots[date]):
                i = slot_num + 1
                while i < last:

                #for i in range(slot_num + 1, last):
                    next_slot = self.slots[date][i]

                    # Ignore break slots
                    if next_slot.type == 'break' and meeting.override_break:
                        last += 1  # Didn't use a slot over the break...
                        i += 1
                        continue

                    if next_slot.type != slot.type:
                        break

                    # Rearrange the next meeting list to make
                    # sure we line up
                    for next_num, next_info in enumerate(self.meetings[next_slot]):
                        (next_room, next_meeting) = next_info
                        if next_room == room:
                            if next_num != room_num:
                                next_info = self.meetings[next_slot].pop(next_num)
                                self.meetings[next_slot].insert(room_num, next_info)
                            break

                    next_meeting = dict(self.meetings[next_slot])
                    if room not in next_meeting:
                        break
                    if next_meeting[room]:
                        break

                    i += 1

                else:
                    pos['height'] = (next_slot.end - slot.start).seconds / 30 - 12

            html += self.meeting_div(meeting, room, slot, pos)
        else:
            # Always output the slot time div, but since its z position is
            # behind that of meetings, it will only be visible if a meeting
            # does not occupy a slot
            html += self.slot_div(room, slot, pos, hidden=False)

        return html

    def as_html(self):
        html = (u'<span class="last-updated" style="float: right;">Updated '
            '<span id="refresh-time">0</span> seconds ago</span>'
            '<div style="clear: both;"></div>')
        

        if self.endofday:
            html += '<p><strong>No more sessions for today.</strong></p>'
            return mark_safe(html)

        if self.track:
            self.day_width = 0
            for date in self.dates:
                for slot in self.slots[date]:
                    if len(self.meetings[slot]) > self.day_width:
                        self.day_width = len(self.meetings[slot])
        else:
            self.day_width = len(self.rooms)

        cal_width = self.day_width * len(self.dates) * 112 + 34

        if self.edit:
            html += '<div class="calendar edit" style="width: %spx; background: white;">\n' % cal_width
        else:
            html += '<div class="calendar" style="width: %spx; background: white;">\n' % cal_width
        html_headings = u'<div class="headings">\n'
        for date_num, date in enumerate(self.dates):
            for column in range(0, self.day_width):
                if not self.track:
                    room = self.rooms[column]

                left = (date_num * self.day_width + column) * 112
                if self.date:
                    heading = ''
                    if room.icecast_url:
                        heading += '<a href="%s">' % escape(room.icecast_url)
                    if self.edit:
                        heading += '%s (%s)' % (escape(room.title), room.size)
                    else:
                        heading += escape(room.title)
                    if room.icecast_url:
                        heading += '</a>'
                elif self.room or self.track:
                    heading = date.strftime("%A")
                else:
                    heading = '%s, %s' % (escape(room.title),
                                          date.strftime("%a"))

                style = {
                    'left': '%dpx' % left,
                    }
                html_headings += ('<div class="heading" style="%s">%s</div>\n'
                         % ('; '.join(': '.join(x) for x in style.items()),
                            heading))
        html_headings += '</div>\n'
        html += html_headings

        # Height of the schedule is the difference in time between the
        # start of the first slot of the longest day and the end of the
        # last slot on the same day
        height = max(self.slots[date][-1].end - self.slots[date][0].start
                     for date in self.dates).seconds / 30
        # Reduce the height with lunch. Just 80 pixels to have some space
        # between the last slot and the repeated headings.
        # FIXME: causes a problem if there is no lunch slot.
        height -= 80

        width = self.day_width * len(self.dates) * 112 - 12

        style = {
            'min-height': '%dpx' % height,
            'height':     '%dpx' % height,
            'width':      '%dpx' % width,
            'min-width':  '%dpx' % width,
            }

        html += '<div class="grid">\n'
        html += '<div class="schedule"\n'
        html += '     style="%s">\n' % '; '.join(': '.join(x) for x in style.items())

        for date_num, date in enumerate(self.dates):
            self.had_lunch = False
            self.height = 10
            for slot_num, slot in enumerate(self.slots[date]):
                for room_num, info in enumerate(self.meetings[slot]):
                    (room, meeting) = info
                    if room is None and meeting is None:
                        continue

                    html += self.gen_slot_html(slot, slot_num, meeting, room, date, date_num, room_num)

                self.height = 12
        html += '</div>\n'

        # Grid lines
        markers = []
        for date in self.dates:
            had_lunch = False
            height = 10
            for slot in self.slots[date]:
                top = (slot.start - self.slots[date][0].start).seconds / 30
                top += height - 10
                if had_lunch:
                    top -= 100
                height = (slot.end - slot.start).seconds / 30 - 12

                if slot.type == 'lunch':
                    had_lunch = True

                # Avoid duplicating markers
                if slot.start.strftime("%H:%M")  not in markers:
                    markers.append(slot.start.strftime("%H:%M"))

                    style = {
                        'top': '%dpx' % top,
                        'height': '%dpx' % height,
                        }
                    html += '<div class="marker"\n'
                    html += '     style="%s">\n' % '; '.join(': '.join(x) for x in style.items())
                    html += '  %s\n' % slot.start.strftime("%H:%M")
                    html += '</div>\n'

                top = (slot.end - self.slots[date][0].start).seconds / 30
                if had_lunch:
                    top -= 100
                height = 12

                # Avoid duplicating markers
                if slot.end.strftime("%H:%M")  not in markers:
                    markers.append(slot.end.strftime("%H:%M") )

                    style = {
                        'top': '%dpx' % top,
                        'height': '%dpx' % height,
                        }
                    html += '<div class="marker"\n'
                    html += '     style="%s">\n' % '; '.join(': '.join(x) for x in style.items())
                    html += '  %s\n' % slot.end.strftime("%H:%M")
                    html += '</div>\n'

        html += html_headings
        html += '</div>\n'
        html += '</div>\n'

        if self.edit:
            html += '<div id="dock" class="unscheduled">\n'
            html += '<p class="help">\n'
            html += 'Unscheduled meetings.  You may return items here.'
            html += '</p>\n'
            for meeting in self.unscheduled:
                html += self.meeting_div(meeting)
            html += '</div>\n'

        return mark_safe(html)

    def slot_div(self, room, slot, pos=None, hidden=False):
        html = u''

        classes = ["slot", escape(slot.type)]

        show_room_name = False
        if (self.edit
                and ((slot.type == 'open' and self.track)
                    or slot.type == 'plenary')):
            show_room_name = True

        if show_room_name:
            line_height = pos['height'] / 2
        else:
            line_height = pos['height']

        if pos:
            style = {
                'left':        '%dpx' % pos['left'],
                'top':         '%dpx' % pos['top'],
                'height':      '%dpx' % pos['height'],
                'min-height':  '%dpx' % pos['height'],
                'line-height': '%dpx' % line_height,
                'width':       '%dpx' % pos['width'],
                }
        else:
            style = {}
        
        if room.type == 'private':
            classes.append('private')

        if slot.type in ('break', 'lunch'):
            title = slot.type.title()
        else:
            title = '..'.join((slot.start.strftime("%H:%M"),
                               slot.end.strftime("%H:%M")))
            if slot.type not in ('open', 'closed'):
                title = "%s:&nbsp;%s" % (slot.type.title(), title)

        html += '<div id="room%dslot%d"\n' % (room.id, slot.id)
        html += '     class="%s"\n' % ' '.join(classes)
        html += '     style="%s">\n' % '; '.join(': '.join(x) for x in style.items())
        html += '  <span class="title">%s</span>\n' % title
        if show_room_name:
            room_name = escape(room.title)
            if room.size and self.edit:
                room_name += ' (%d)' % room.size
            html += '  <span class="roomsize">%s</span>\n' % room_name
        html += '</div>\n'

        return mark_safe(html)

    def meeting_div(self, meeting, room=None, slot=None, pos=None):
        _cached_html = cache.get('meeting-html-%d' % meeting.id)
        if self.track:
            _cached_html = cache.get('meeting-track-html-%d' % meeting.id)
            if _cached_html is not None:
                return mark_safe(_cached_html % {'style': get_style_def_for_meeting(meeting, pos)})
        else:
            if _cached_html is not None:
                return mark_safe(_cached_html % {'style': get_style_def_for_meeting(meeting, pos)})
        html = u''

        classes = ["meeting", escape(meeting.type)]
        classes.extend(escape_strings(track.slug.lower())
                       for track in meeting.tracks.all())

        if self.edit:
            hide_details = False
        else:
            hide_details = meeting.private

        if meeting.private:
            classes.append('private')
# (phanatic) Quick fix for the 'caching attendee state' aka. grey issue
#        if self.attendee:
#            interested_tracks = set(self.attendee.tracks.all())
#            interested_topics = set(self.attendee.topics.all())

#            try:
#                participant = meeting.participant_set.get(attendee=self.attendee)
#            except ObjectDoesNotExist:
#                participant = None

#            if self.attendee == meeting.approver \
#                    or self.attendee == meeting.scribe \
#                    or self.attendee == meeting.assignee \
#                    or self.attendee == meeting.drafter \
#                    or (participant and participant.required):
#                classes.append("required")
#                hide_details = False
#            elif meeting.type in ('plenary', 'talk'):
#                classes.append("required")
#            elif interested_tracks.intersection(meeting.tracks.all()) \
#                    or interested_topics.intersection(meeting.topics.all()) :
#                if meeting.type == 'roundtable':
#                    classes.append("required")
#                else:
#                    classes.append("interested")
#            elif not participant:
#                if len(interested_tracks) or len(interested_topics):
#                    classes.append("uninterested")
#                else:
#                    classes.append("ambivalent")
#                if self.personal:
#                    return ''

        error = None
        missing = set()
        if self.edit and slot and room:
            try:
                missing = meeting.check_schedule(slot, room)
                if len(missing):
                    classes.append("warning")
                    error = "Required participants unavailable"
            except meeting.SchedulingError, e:
                classes.append("error")
                error = str(e)

        if meeting.spec_url and meeting.priority:
            try:
                spec = meeting.spec_url
                label = dict(meeting.PRIORITY_CHOICES)[meeting.priority]
                icon = label.lower()
            except KeyError:
                spec = label = icon = None
        else:
            spec = label = icon = None

        html += '<div id="meeting%d"\n' % meeting.id
        html += '     class="%s"\n' % ' '.join(classes)
        html += '     style="%(style)s">\n'

        if slot and room:
            html += '  <span class="time">%s, %s</span>\n' % (slot.start.strftime("%A %H:%M"),
                                                              escape_strings(room.title))
        html += '  <span class="title">'

        should_have_details_link = not meeting.private

        if hide_details:
            html += 'Private Meeting'
        else:
            html += '<a href="%s">' % escape_strings(meeting.meeting_page_url)
            html += escape_strings(meeting.title)
            html += '</a>'
        html += '</span>\n'
        if error:
            html += '  <span class="errortext">%s</span>\n' % escape_strings(error)
        if meeting.type in ('plenary', 'talk', 'special') \
                or self.track:
            try:
                room = meeting.agenda_set.exclude(room__type__exact="closed").get().room
                room_name = room.title
                if room.size and self.edit:
                    room_name += ' (%d)' % room.size
                html += '  <span class="room">%s</span>\n' % escape_strings(room_name)
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                pass
        html += '  <ul class="tracks">\n'
        for track in sorted(meeting.tracks.all(), key=lambda x: x.title.lower()):
            html += '    <li>%s</li>' % escape_strings(track.title.lower())
        html += '  </ul>\n'

        html += '</div>\n'

        if self.track:
            cache.set('meeting-track-html-%d' % meeting.id, html)
        else:
            cache.set('meeting-html-%d' % meeting.id, html)
        return mark_safe(html % {'style': get_style_def_for_meeting(meeting, pos)})

    def js_data(self):
        slot_table = {}
        slot_list = []
        slot_nexts = {}

        meeting_table = {}
        meeting_list = []
        meeting_slots = {}

        for date in self.dates:
            for slot_num, slot in enumerate(self.slots[date]):
                for room, meeting in self.meetings[slot]:
                    if room is None and meeting is None:
                        continue

                    # Don't allow plenary slots to be targets in room view
                    # unless it's the plenary room - don't allow closed or special
                    # slots to be targets
                    if slot.type == 'plenary' \
                            and self.room and self.room.type != 'plenary':
                        continue
                    elif slot.type not in ('open', 'plenary'):
                        continue

                    slot_ref = 'room%dslot%d' % (room.id, slot.id)
                    slot_list.append(slot_ref)

                    if slot_num + 1 < len(self.slots[date]):
                        next_slot = self.slots[date][slot_num + 1]
                        next_meeting = dict(self.meetings[next_slot])
                        if next_slot.type == slot.type \
                                and room in next_meeting:
                            next_ref = 'room%dslot%d' % (room.id, next_slot.id)
                            slot_nexts[slot_ref] = next_ref

                    if meeting:
                        # Don't allow plenary or talk meetings to be edited
                        # in room view unless it's the plenary room
                        if meeting.type in ('plenary', 'talk', 'special') \
                                and self.room and self.room.type != 'plenary':
                            continue

                        meeting_ref = 'meeting%d' % meeting.id
                        meeting_list.append(meeting_ref)

                        slot_table[slot_ref] = meeting_ref
                        meeting_table[meeting_ref] = slot_ref

                        meeting_slots[meeting_ref] = meeting.slots
                    else:
                        slot_table[slot_ref] = None

        for meeting in self.unscheduled:
            meeting_ref = 'meeting%d' % meeting.id
            meeting_list.append(meeting_ref)

            meeting_table[meeting_ref] = None

            meeting_slots[meeting_ref] = meeting.slots


        js = u'\n'
        js += 'var Data = {\n'
        js += '  slot: %s,\n' % json.dumps(slot_table, indent=4)
        js += '  slots: %s,\n' % json.dumps(slot_list)
        js += '\n'
        js += '  slotNext: %s,\n' % json.dumps(slot_nexts, indent=4)
        js += '\n'
        js += '  meeting: %s,\n' % json.dumps(meeting_table, indent=4)
        js += '  meetings: %s,\n' % json.dumps(meeting_list)
        js += '\n'
        js += '  meetingSlots: %s,\n' % json.dumps(meeting_slots, indent=4)
        js += '}\n'

        return js

    def save_change(self):
        if not self.edit:
            return HttpResponseForbidden()

        missing = set()

        meeting_re = re.compile(r'^meeting(\d+)$')
        slot_re = re.compile(r'^room(\d+)slot(\d+)$')

        try:
            meeting_match = meeting_re.search(self.request.POST['meeting'])
            meeting_id = int(meeting_match.group(1))
            meeting = self.summit.meeting_set.get(pk=meeting_id)
        except KeyError:
            return HttpResponse('<error>Missing meeting field</error>',
                                mimetype='text/xml')
        except (AttributeError, ValueError):
            return HttpResponse('<error>Invalid meeting field</error>',
                                mimetype='text/xml')
        except ObjectDoesNotExist:
            return HttpResponse('<error>Unknown meeting</error>',
                                mimetype='text/xml')

        try:
            remove_match = slot_re.search(self.request.POST['remove'])
            remove_room_id = int(remove_match.group(1))
            remove_room = self.summit.room_set.get(pk=remove_room_id)

            remove_slot_id = int(remove_match.group(2))
            remove_slot = self.summit.slot_set.get(pk=remove_slot_id)

            remove_agenda = meeting.agenda_set.get(slot=remove_slot,
                                                   room=remove_room)
        except KeyError:
            remove_agenda = None
        except (AttributeError, ValueError):
            return HttpResponse('<error>Invalid remove field</error>',
                                mimetype='text/xml')
        except ObjectDoesNotExist:
            return HttpResponse('<error>Meeting not in that slot</error>',
                                mimetype='text/xml')

        try:
            add_match = slot_re.search(self.request.POST['add'])
            add_room_id = int(add_match.group(1))
            add_room = self.summit.room_set.get(pk=add_room_id)

            add_slot_id = int(add_match.group(2))
            add_slot = self.summit.slot_set.get(pk=add_slot_id)

            try:
                missing = meeting.check_schedule(add_slot, add_room)
            except meeting.SchedulingError, e:
                return HttpResponse('<error target="%s">%s</error>'
                                    % (self.request.POST['add'], escape(str(e))),
                                    mimetype='text/xml')
        except KeyError:
            add_room = None
            add_slot = None
        except (AttributeError, ValueError):
            return HttpResponse('<error>Invalid add field</error>',
                                mimetype='text/xml')
        except ObjectDoesNotExist:
            return HttpResponse('<error>Unknown slot</error>',
                                mimetype='text/xml')

        if 'check' not in self.request.POST:
            if remove_agenda:
                remove_agenda.delete()
            if add_slot and add_room:
                meeting.agenda_set.create(slot=add_slot, room=add_room)

        if len(missing):
            xml = "<ok>"
            for m in missing:
                xml += "<missing>%s</missing>" % m.user.username
            xml += "</ok>"
        else:
            xml = "<ok/>"

        return HttpResponse(xml, mimetype='text/xml')

    def as_csv(self):
        csv = u''

        csv += ",".join(['"Start"', '"End"', '"Room"', '"Track"',
                         '"Name"', '"Title"'])
        csv += "\n"

        for date in self.dates:
            for slot in self.slots[date]:
                for room, meeting in self.meetings[slot]:
                    if room is None or meeting is None:
                        continue

                    csv += ",".join(['"%s"' % slot.start_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                     '"%s"' % slot.end_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                     '"%s"' % room.title,
                                     '"%s"' % (room.track or ""),
                                     '"%s"' % (meeting.name or ""),
                                     '"%s"' % meeting.title.replace('"', "''")])
                    csv += "\n"

        return csv

    def as_ical(self, only_username=None, 
                      only_room=None, 
                      only_track=None, 
                      show_private=True):
        """
        return a schedule as ical
        """
        ical = u'''BEGIN:VCALENDAR
PRODID:-//summit.ubuntu.com//EN
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-TIMEZONE:UTC
'''
        ical += 'X-WR-CALNAME:%s\n' % self.summit.name
        ical += 'X-WR-CALDESC:%s\n' % self.summit.name
        for date in self.dates:
            for slot in self.slots[date]:
                for room, meeting in self.meetings[slot]:
                    if room is None or meeting is None:
                        continue
                    if only_username is not None and meeting.participants.filter(user__username=only_username).count() == 0:
                        continue
                    if only_room is not None and room.name != only_room:
                        continue
                    if only_track is not None and meeting.tracks.filter(slug=only_track).count() == 0:
                        continue
                    if not show_private and meeting.private:
                        continue
                    dtstart = str(slot.start_utc).replace(' ','T', 1).replace(':','',2).replace('-','',2)
                    dtend = str(slot.end_utc).replace(' ','T', 1).replace(':','',2).replace('-','',2)
                    categories = ','.join([t.title for t in meeting.tracks.all()])
                    ical += '''BEGIN:VEVENT
UID:%(id)s
DTSTART:%(dtstart)sZ
DTEND:%(dtend)sZ
CATEGORIES:%(category)s
SUMMARY:%(eventname)s
LOCATION:%(eventplace)s
DESCRIPTION:%(description)s
URL:%(base_url)s%(meeting_url)s
X-TYPE:%(type)s
X-ROOMNAME:%(roomname)s
END:VEVENT
''' % {'id':meeting.id, 'dtstart':dtstart, 'dtend':dtend, 'category':categories,
       'eventname':meeting.title, 'eventplace': room.title, 'type': meeting.type,
       'roomname':room.name, 'description': getattr(meeting, 'description', '').replace('\r', '').replace('\n', '\N'),
       'meeting_url':meeting.meeting_page_url,
       'base_url':getattr(settings, 'SITE_ROOT', 'http://summit.ubuntu.com')}
        ical += 'END:VCALENDAR'
        return ical

def schedule_factory(
        request, summit, attendee=None, date=None, room=None, track=None):
    """Create and return a Schedule instance with the given arguments.

    """
    return Schedule.from_request(
        request, summit, attendee, room=room, date=date, track=track)
