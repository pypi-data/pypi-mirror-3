from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #venues
    url(r'^summit/(.*)$', 'services.views.summit_service', name='team_service'),
    url(r'^track/(.*)$', 'services.views.track_service', name='team_service'),
    url(r'^topic/(.*)$', 'services.views.topic_service', name='team_service'),
    url(r'^user/(.*)$', 'services.views.user_service', name='team_service'),
    url(r'^attendee/(.*)$', 'services.views.attendee_service', name='team_service'),
    url(r'^crew/(.*)$', 'services.views.crew_service', name='team_service'),
    url(r'^participant/(.*)$', 'services.views.participant_service', name='team_service'),
    url(r'^room/(.*)$', 'services.views.room_service', name='team_service'),
    url(r'^meeting/(.*)$', 'services.views.meeting_service', name='team_service'),
    url(r'^slot/(.*)$', 'services.views.slot_service', name='team_service'),
    url(r'^agenda/(.*)$', 'services.views.agenda_service', name='team_service'),
)

