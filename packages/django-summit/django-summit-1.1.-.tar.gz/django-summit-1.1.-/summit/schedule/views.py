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

from time import strftime
import datetime

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict

from summit.schedule.decorators import (summit_required,
                                        summit_only_required,
                                        summit_attendee_required)

from summit.schedule.models import Summit, Slot, Attendee, Meeting, Lead

from summit.schedule.render import schedule_factory, Schedule

from summit.schedule.forms import *

__all__ = (
    'summit',
    'by_date',
    'by_room',
    'csv',
    'today_view',
)
        
@summit_required
def summit(request, summit, attendee):
    edit = False
    if (summit.state != 'public'
        and 'readonly' not in request.GET) \
            or 'edit' in request.GET:
        if request.user.is_authenticated() \
                and summit.is_organizer(attendee):
            edit = True
    tracks = summit.track_set.all()

    context = {
        'summit': summit,
        'attendee': attendee,
        'edit': edit,
        'tracks': tracks,
        'summit_organizer': summit.is_organizer(attendee),
    }
    return render_to_response("schedule/summit.html", context,
                              context_instance=RequestContext(request))

@summit_required
def daily_schedule(request, summit, attendee, date):
    viewdate = summit.as_localtime(datetime.datetime.strptime(date, "%Y-%m-%d"))
    utc_date = summit.delocalize(viewdate)
    day = datetime.timedelta(days=1)

    schedule = SortedDict()
    multislot_meetings = SortedDict()

    for slot in summit.slot_set.filter(start_utc__gte=utc_date, end_utc__lte=(utc_date+day)).order_by('start_utc'):
        if not (slot.type == 'open' or slot.type == 'plenary' or slot.type == 'lunch'):
            continue
        if not slot in schedule:
            schedule[slot] = SortedDict()

        # Start with multi-slot meetings carried over from previous slots
        for agenda, count in multislot_meetings.items():
            schedule[slot][agenda.room] = agenda
            if count == 1:
                del multislot_meetings[agenda]
            else:
                multislot_meetings[agenda] = count -1

        # Add meetings from this slot
        for agenda in slot.agenda_set.select_related().order_by('room__name'):
            if not agenda.meeting.private or attendee in agenda.meeting.attendees:
                schedule[slot][agenda.room] = agenda
                if agenda.meeting.slots > 1:
                    multislot_meetings[agenda] = agenda.meeting.slots - 1
    
    if '_popup' in request.GET:
        is_popup = True
        
    context = {
        'summit': summit,
        'attendee': attendee,
        'schedule': schedule,
        'ical': '/%s.ical' % summit.name,
        'viewdate': viewdate,
        'nextday': viewdate + day,
        'previousday': viewdate - day,
        'summit_organizer': summit.is_organizer(attendee),
    }
    return render_to_response("schedule/daily.html", context,
                              context_instance=RequestContext(request))
    
@summit_attendee_required
def attendee_schedule(request, summit, attendee):
    pass
    
@summit_required
def by_date(request, summit, attendee, date):
    return _process_date_view(request, summit, attendee, date)

@summit_required
def today_view(request, summit, attendee):
    today = summit.localize(datetime.datetime.now()).date()
    return _process_date_view(request, summit, attendee, today.strftime("%Y-%m-%d"))

def _process_date_view(request, summit, attendee, date):
    if 'rooms' in request.GET:
        roomnames = request.GET.get('rooms', '').split(',')
        rooms = list(summit.room_set.filter(name__in=roomnames, type='open'))
        if request.user.is_authenticated() and request.user.is_staff:
            rooms += list(summit.room_set.filter(name__in=roomnames, type='private'))
    else:
        rooms = None
    schedule = schedule_factory(request, summit, attendee, room=rooms, date=date)

    if request.method == 'POST':
        return schedule.save_change()
    else:
        viewdate = datetime.datetime.strptime(date, "%Y-%m-%d")
        day = datetime.timedelta(days=1)

        context = {
            'summit': summit,
            'attendee': attendee,
            'schedule': schedule,
            'ical': '/%s.ical' % summit.name,
            'autoreload': 'reload' in request.GET,
            'nextday': viewdate + day,
            'previousday': viewdate - day,
            'can_change_agenda': summit.can_change_agenda(attendee),
        }
        converted_date = summit.delocalize(datetime.datetime.strptime(date, "%Y-%m-%d"))
        if Slot.objects.filter(summit=summit, start_utc__gte=converted_date, end_utc__lte=converted_date+datetime.timedelta(days=1)).count() > 0:
            schedule.calculate()
        else:
            return render_to_response("schedule/nosession.html", context,
                              context_instance=RequestContext(request))
    return render_to_response("schedule/schedule.html", context,
                              context_instance=RequestContext(request))

@summit_required
def next_session(request, summit, attendee):
    if 'rooms' in request.GET:
        roomnames = request.GET.get('rooms', '').split(',')
        rooms = list(summit.room_set.filter(name__in=roomnames, type='open'))
        if request.user.is_authenticated() and request.user.is_staff:
            rooms += list(summit.room_set.filter(name__in=roomnames, type='private'))
    else:
        rooms = None
    schedule = Schedule.from_request(request, summit, attendee, room=rooms, nextonly=True)

    schedule.calculate()

    context = {
        'summit': summit,
        'attendee': attendee,
        'schedule': schedule,
        'autoreload': 'reload' in request.GET,
    }
    return render_to_response("schedule/nextsession.html", context,
                              context_instance=RequestContext(request))

@summit_required
def by_room(request, summit, attendee, room_name):
    try:
        room = summit.room_set.get(tracks__title__iexact=room_name)
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        room = get_object_or_404(summit.room_set, name__exact=room_name)

    schedule = schedule_factory(request, summit, attendee, room=room)

    if request.method == 'POST':
        return schedule.save_change()
    else:
        schedule.calculate()

    context = {
        'summit': summit,
        'attendee': attendee,
        'schedule': schedule,
        'ical': '/%s/room/%s.ical' % (summit.name, room.name),
        'autoreload': 'reload' in request.GET,
        'can_change_agenda': summit.can_change_agenda(attendee),
    }
    return render_to_response("schedule/schedule.html", context,
                              context_instance=RequestContext(request))


@summit_required
def by_track(request, summit, attendee, track_slug):
    track = get_object_or_404(summit.track_set, slug__iexact=track_slug)

    schedule = Schedule.from_request(request, summit, attendee, track=track)

    if request.method == 'POST':
        return schedule.save_change()
    else:
        schedule.calculate()

    context = {
        'summit': summit,
        'attendee': attendee,
        'schedule': schedule,
        'autoreload': 'reload' in request.GET,
        'ical': '/%s/track/%s.ical' % (summit.name, track.slug),
        'can_change_agenda': summit.can_change_agenda(attendee),
    }
    return render_to_response("schedule/schedule.html", context,
                              context_instance=RequestContext(request))

@summit_only_required
def tracks(request, summit):

    context = {
        'summit': summit,
    }
    return render_to_response("schedule/tracks.html", context,
                              context_instance=RequestContext(request))

@summit_required
def meeting(request, summit, attendee, meeting_id, meeting_slug):
    meeting = get_object_or_404(summit.meeting_set, id=meeting_id)
    if meeting.private:
        # check if the user should be able to see this private meeting
        if attendee is None:
            raise Http404
            
        attendee_allowed = False
        for a in meeting.attendees:
            if a.user.pk == attendee.user.pk:
                attendee_allowed = True
                break
        if not attendee_allowed:
            raise Http404
    return _show_meeting(request, summit, meeting, attendee)

@summit_required
def private_meeting(request, summit, attendee, private_key, meeting_slug):
    meeting = get_object_or_404(summit.meeting_set, private_key=private_key)
    return _show_meeting(request, summit, meeting, attendee)

def _show_meeting(request, summit, meeting, attendee):
    agendaitems=meeting.agenda_set.all()
    participants=meeting.participant_set.all()
    attendees=meeting.attendees
    tracks=meeting.tracks.all()
    user_is_attending = attendee is not None and attendee in meeting.attendees
    user_is_participating = attendee is not None and attendee in [p.attendee for p in participants if not p.from_launchpad]
    
    if attendee == meeting.drafter:
        drafter = True
    else:
        drafter = False
    
    context = {
        'summit': summit,
        'meeting':meeting,
        'agenda_items':agendaitems,
        'participants':participants,
        'attendees': attendees,
        'user_is_attending': user_is_attending,
        'user_is_participating': user_is_participating,
        'tracks':tracks,
        'ETHERPAD_HOST': summit.etherpad,
        'summit_organizer': summit.is_organizer(attendee),
        'scheduler': summit.can_change_agenda(attendee),
        'drafter': drafter,
    }
    #import pdb; pdb.set_trace()
    return render_to_response("schedule/meeting.html", context,
                              context_instance=RequestContext(request))

@summit_required
def share_meeting(request, summit, attendee, meeting_id, meeting_slug):
    meeting = get_object_or_404(summit.meeting_set, id=meeting_id)
    if meeting.private:
        # check if the user should be able to see this private meeting
        if attendee is None:
            raise Http404
            
        attendee_allowed = False
        for a in meeting.attendees:
            if a.user.pk == attendee.user.pk:
                meeting.share()
                return HttpResponseRedirect(reverse(private_meeting, args=[summit.name, meeting.private_key, meeting_slug]))
        raise Http404
    return HttpResponseRedirect(reverse(meeting, summit.name, meeting.id, meeting_slug))
    
@summit_attendee_required
def register(request, summit, attendee, meeting_id, meeting_slug):
    meeting = get_object_or_404(summit.meeting_set, id=meeting_id)
    user_is_attending = attendee is not None and attendee in meeting.attendees
    if not user_is_attending:
        meeting.participant_set.create(attendee=attendee, required=False, from_launchpad=False)

    return HttpResponseRedirect(reverse('summit.schedule.views.meeting', args=(summit.name, meeting.id, meeting_slug)))

@summit_attendee_required
def unregister(request, summit, attendee, meeting_id, meeting_slug):
    meeting = get_object_or_404(summit.meeting_set, id=meeting_id)
    meeting.participant_set.filter(attendee=attendee, required=False, from_launchpad=False).delete()

    return HttpResponseRedirect(reverse('summit.schedule.views.meeting', args=(summit.name, meeting.id, meeting_slug)))

@summit_only_required
def csv(request, summit):
    schedule = Schedule.from_request(request, summit)
    schedule.calculate()

    return HttpResponse(schedule.as_csv(),
                        mimetype='text/csv')

@summit_only_required
def ical(request, summit):
    """Return any list events as an ical"""
    schedule = Schedule.from_request(request, summit)
    schedule.calculate()
    
    filename = "%s.ical" % summit.name.replace(' ', '-').lower()
    response = HttpResponse(mimetype='text/calendar')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename.encode('ascii', 'replace')
    response.write(schedule.as_ical())
    return response

@summit_only_required
def user_ical(request, summit, username):
    """Returns a user's registered events as an ical"""
    schedule = Schedule.from_request(request, summit)
    schedule.calculate()
    
    filename = "%s_%s.ical" % (summit.name, username)
    response = HttpResponse(mimetype='text/calendar')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename.replace(' ', '-').lower().encode('ascii', 'replace')
    response.write(schedule.as_ical(only_username=username, show_private=False))
    return response
    
@summit_only_required
def user_private_ical(request, summit, secret_key):
    """Returns a user's registered events as an ical"""
    attendee = get_object_or_404(Attendee, secret_key_id=secret_key)
    schedule = Schedule.from_request(request, summit, show_private=True)
    schedule.calculate()
    
    response = HttpResponse(mimetype='text/calendar')
    response['Content-Disposition'] = 'attachment; filename=my_schedule_%s.ical' % attendee.secret_key
    response.write(schedule.as_ical(only_username=attendee.user.username, show_private=True))
    return response
    
@summit_only_required
def room_ical(request, summit, room_name):
    """Returns a room's events as an ical"""
    schedule = Schedule.from_request(request, summit)
    schedule.calculate()
    
    filename = "%s_%s.ical" % (summit.name, room_name)
    response = HttpResponse(mimetype='text/calendar')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename.replace(' ', '-').lower().encode('ascii', 'replace')
    response.write(schedule.as_ical(only_room=room_name))
    return response
    
@summit_only_required
def track_ical(request, summit, track_slug):
    """Returns a track's events as an ical"""
    schedule = Schedule.from_request(request, summit)
    schedule.calculate()
    
    filename = "%s_%s.ical" % (summit.name, track_slug)
    response = HttpResponse(mimetype='text/calendar')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename.replace(' ', '-').lower().encode('ascii', 'replace')
    response.write(schedule.as_ical(only_track=track_slug))
    return response
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def mobile(request):
    return render_to_response("schedule/mobile.html", {}, RequestContext(request))

def past(request):
    pastsummit = Summit.on_site.filter(date_end__lte=datetime.date.today())
    context = {
        'past_summit': pastsummit,
    }
    return render_to_response("schedule/past_summit.html", context,
                          context_instance=RequestContext(request))

@summit_attendee_required
def create_meeting(request, summit, attendee):

    if not summit.is_organizer(attendee):
        return HttpResponseRedirect(reverse('summit.schedule.views.summit', args=(summit.name,)))
    else:
        meeting = Meeting(summit=summit, approver=attendee, drafter=attendee, approved='APPROVED')
    
        if request.method == 'POST':        
            form = CreateMeeting(data=request.POST, instance=meeting)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(meeting.meeting_page_url)
        else:
            form = CreateMeeting(instance=meeting)

    context = {
        'summit': summit,
        'form': form,
    }
    return render_to_response('schedule/create_meeting.html', 
                          context, RequestContext(request))

@summit_attendee_required
def propose_meeting(request, summit, attendee):

    meeting = Meeting(summit=summit, drafter=attendee, private=False, approved='PENDING')

    if request.method == 'POST':        
        form = ProposeMeeting(data=request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(meeting.meeting_page_url)
    else:
        form = ProposeMeeting(instance=meeting)

    context = {
        'summit': summit,
        'form': form,
    }
    return render_to_response('schedule/propose_meeting.html', 
                          context, RequestContext(request))
                          
@summit_attendee_required
def organizer_edit_meeting(request, summit, attendee, meeting_id, meeting_slug):
    meeting = get_object_or_404(summit.meeting_set, id=meeting_id)
    
    if not summit.is_organizer(attendee):
        return HttpResponseRedirect(reverse('summit.schedule.views.summit', args=(summit.name,)))
    else:
        if request.method == 'POST':        
            form = OrganizerEditMeeting(data=request.POST, instance=meeting)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(meeting.meeting_page_url)
        else:
            form = OrganizerEditMeeting(instance=meeting)

    context = {
        'summit': summit,
        'form': form,
    }
    return render_to_response('schedule/org_edit_meeting.html', 
                          context, RequestContext(request))

@summit_attendee_required
def edit_meeting(request, summit, attendee, meeting_id, meeting_slug):
    meeting = get_object_or_404(summit.meeting_set, id=meeting_id)
    
    if attendee != meeting.drafter:
        return HttpResponseRedirect(reverse('summit.schedule.views.summit', args=(summit.name,)))
    else:
        if request.method == 'POST':        
            form = EditMeeting(data=request.POST, instance=meeting)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(meeting.meeting_page_url)
        else:
            form = EditMeeting(instance=meeting)

    context = {
        'summit': summit,
        'form': form,
    }
    return render_to_response('schedule/edit_meeting.html', 
                          context, RequestContext(request))

@summit_required
def review_pending(request, summit, attendee):

    if not summit.is_organizer(attendee):
        return HttpResponseRedirect(reverse('summit.schedule.views.summit', args=(summit.name,)))
    else:
        schedule = SortedDict()

        for track in summit.track_set.all():
            if not track in schedule:
                schedule[track] = list()

            # Add meetings from this slot
            for meeting in track.meeting_set.exclude(approved='APPROVED'):
                schedule[track].append(meeting)

    context = {
        'summit': summit,
        'schedule': schedule,
    }
    return render_to_response("schedule/review.html", context,
                              context_instance=RequestContext(request))

@summit_required
def meeting_review(request, summit, attendee, meeting_id):
    meeting = get_object_or_404(summit.meeting_set, id=meeting_id)

    if not summit.is_organizer(attendee):
        return HttpResponseRedirect(reverse('summit.schedule.views.summit', args=(summit.name,)))
    else:
        if request.method == 'POST':
            form = MeetingReview(data=request.POST, instance=meeting)
            if form.is_valid():
                meeting = form.save(commit=False)
                meeting.approver = attendee
                meeting.save()
                return HttpResponseRedirect(meeting.meeting_page_url)
        else:
            form = MeetingReview(instance=meeting)

    context = {
        'summit': summit,
        'form': form,
    }
    return render_to_response('schedule/meeting_review.html',
                          context, RequestContext(request))

@summit_required
def created_meetings(request, summit, attendee, username):

    drafter = get_object_or_404(Attendee, summit=summit, user__username=username)
    if attendee.id != drafter.id:
        meetings = summit.meeting_set.filter(drafter=drafter).exclude(private=True)
    else:
        meetings = summit.meeting_set.filter(drafter=drafter)

    context = {
        'summit': summit,
        'meetings': meetings,
        'drafter': drafter,
        'attendee': attendee,
    }
    return render_to_response("schedule/mine.html", context,
                              context_instance=RequestContext(request))

@summit_required
def meeting_copy(request, summit, attendee, meeting_id, meeting_slug):
    meeting = get_object_or_404(summit.meeting_set, id=meeting_id)

    if not summit.can_change_agenda(attendee):
        return HttpResponseRedirect(reverse('summit.schedule.views.summit', args=(summit.name,)))
    else:
        if request.method == 'POST':
            form = CreateMeeting(instance=meeting, data=request.POST)
            meeting.id = meeting.pk = None
            meeting.approver = attendee
            meeting.drafter = attendee
            meeting.approved = 'APPROVED'

            if form.is_valid():
                meeting = form.save()
                meeting_id = meeting.id
                return HttpResponseRedirect(meeting.meeting_page_url)
                
        else:
            form = CreateMeeting(instance=meeting)

    context = {
        'summit': summit,
        'form': form,
    }
    
    return render_to_response('schedule/create_meeting.html', 
                          context, RequestContext(request))
