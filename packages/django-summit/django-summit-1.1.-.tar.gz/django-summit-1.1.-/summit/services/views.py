from django.contrib.auth.models import User, Group
from schedule.models import *

from services.handler import model_service

def user_service(request, url):
    return model_service(User, request, url, include=['id', 'username'])

def summit_service(request, url):
    return model_service(Summit, request, url)

def track_service(request, url):
    return model_service(Track, request, url)

def topic_service(request, url):
    return model_service(Topic, request, url)

def room_service(request, url):
    if request.user.is_authenticated and request.user.is_staff:
        return model_service(Room, request, url)
    else:
        limit = {
            'type__in': ['open', 'plenary'],
        }
        return model_service(Room, request, url, limit=limit)

def meeting_service(request, url):
    if request.user.is_authenticated and request.user.is_staff:
        return model_service(Meeting, request, url)
    else:
        limit = {
            'private': False,
        }
        return model_service(Meeting, request, url, exclude=['private'], limit=limit)

def attendee_service(request, url):
    return model_service(Attendee, request, url, exclude=['secret_key_id'])

def crew_service(request, url):
    return model_service(Crew, request, url)

def participant_service(request, url):
    if request.user.is_authenticated and request.user.is_staff:
        return model_service(Participant, request, url)
    else:
        limit = {
            'meeting__private': False,
        }
        return model_service(Participant, request, url, limit=limit)

def slot_service(request, url):
    return model_service(Slot, request, url)

def agenda_service(request, url):
    if request.user.is_authenticated and request.user.is_staff:
        return model_service(Agenda, request, url)
    else:
        limit = {
            'meeting__private': False,
            'room__type__in': ['open', 'plenary'],
        }
        return model_service(Agenda, request, url, limit=limit)
