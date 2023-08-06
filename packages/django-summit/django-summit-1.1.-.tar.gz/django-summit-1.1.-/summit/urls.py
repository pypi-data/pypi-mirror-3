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

from django.conf.urls.defaults import *
from django.conf import settings
import ubuntu_website

from common.views import login_failure

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^$', 'summit.common.views.index'),
    (r'^admin/', admin.site.urls),
    (r'^api/', include('services.urls')),
)

urlpatterns += patterns('django_openid_auth.views',
    url(r'^openid/login/$', 'login_begin', name='openid-login',
        kwargs={'render_failure': login_failure}),
    url(r'^openid/complete/$', 'login_complete', name='openid-complete',
        kwargs={'render_failure': login_failure}),
    url(r'^openid/logo.gif$', 'logo', name='openid-logo'),
)

urlpatterns += patterns('summit.sponsor.views',
    (r'^(?P<summit_name>[\w-]+)/sponsorship/$', 'sponsorship'),
    (r'^(?P<summit_name>[\w-]+)/sponsorship/done/$', 'done'),
    (r'^(?P<summit_name>[\w-]+)/sponsorship/review/$', 'review_list'),

    (r'^(?P<summit_name>[\w-]+)/suggestsponsorship/$', 'suggestsponsorship'),
    (r'^(?P<summit_name>[\w-]+)/suggestsponsorship/done/$', 'suggestiondone'),

    (r'^(?P<summit_name>[\w-]+)/nonlaunchpadsponsorship/$',
        'nonlaunchpadsponsorship'),
    (r'^(?P<summit_name>[\w-]+)/nonlaunchpadsponsorship/done/$',
        'nonlaunchpaddone'),

    (r'^(?P<summit_name>[\w-]+)/sponsorship/review/(?P<sponsorship_id>[0-9]+)$',
        'review'),
    (r'^(?P<summit_name>[\w-]+)/suggestedsponsorship/review/(?P<sponsorship_id>[0-9]+)$',
        'suggestion_review'),
    (r'^(?P<summit_name>[\w-]+)/nonlaunchpadsponsorship/review/(?P<sponsorship_id>[0-9]+)$',
        'nonlaunchpad_review'),

    (r'^(?P<summit_name>[\w-]+)/sponsorship/export/$', 'export'),
)

urlpatterns += patterns('summit.schedule.views',
    url(r'^today/(?P<summit_name>[\w-]+)/$', 'today_view', name='today'),
    url(r'^past/', 'past', name='past'),
    url(r'^mobile/', 'mobile', name='mobile'),
    url(r'^logout$', 'logout_view', name='logout'),
    (r'^(?P<summit_name>[\w-]+)/$', 'summit'),
    (r'^(?P<summit_name>[\w-]+)/propose_meeting/$', 'propose_meeting'),
    (r'^(?P<summit_name>[\w-]+)/edit_meeting/(?P<meeting_id>\d+)/(?P<meeting_slug>[%+\.\w-]+)/$', 'edit_meeting'),
    (r'^(?P<summit_name>[\w-]+)/review/$', 'review_pending'),
    (r'^(?P<summit_name>[\w-]+)/review_meeting/(?P<meeting_id>\d+)/$', 'meeting_review'),
    (r'^(?P<summit_name>[\w-]+)/create_meeting/$', 'create_meeting'),
    (r'^(?P<summit_name>[\w-]+)/edit_mtg/(?P<meeting_id>\d+)/(?P<meeting_slug>[%+\.\w-]+)/$', 'organizer_edit_meeting'),
    (r'^(?P<summit_name>[\w-]+)/tracks$', 'tracks'),
    (r'^(?P<summit_name>[\w-]+)/next$', 'next_session'),
    (r'^(?P<summit_name>[\w-]+)/(?P<username>[%+\.\w-]+)/meetings$', 'created_meetings'),
    (r'^(?P<summit_name>[\w-]+)/(?P<date>[\d-]+)/$', 'daily_schedule'),
    (r'^(?P<summit_name>[\w-]+)/(?P<date>[\d-]+)/display$', 'by_date'),
    (r'^(?P<summit_name>[\w-]+)/(?P<room_name>[%+\.\w-]+)/$', 'by_room'),
    (r'^(?P<summit_name>[\w-]+)/track/(?P<track_slug>[%+\.\w-]+)/$', 'by_track'),
    (r'^(?P<summit_name>[\w-]+)/meeting/(?P<meeting_id>\d+)/(?P<meeting_slug>[%+\.\w-]+)/\+share$', 'share_meeting'),
    (r'^(?P<summit_name>[\w-]+)/meeting/(?P<meeting_id>\d+)/(?P<meeting_slug>[%+\.\w-]+)/\+register', 'register'),
    (r'^(?P<summit_name>[\w-]+)/meeting/(?P<meeting_id>\d+)/(?P<meeting_slug>[%+\.\w-]+)/\+unregister', 'unregister'),
    (r'^(?P<summit_name>[\w-]+)/meeting/(?P<meeting_id>\d+)/(?P<meeting_slug>[%+\.\w-]+)/$', 'meeting'),
    (r'^(?P<summit_name>[\w-]+)/private/(?P<private_key>[0-9a-f]{32})/(?P<meeting_slug>[%+\.\w-]+)/$', 'private_meeting'),
    (r'^(?P<summit_name>[\w-]+)/meeting/(?P<meeting_id>\d+)/(?P<meeting_slug>[%+\.\w-]+)/copy/$', 'meeting_copy'),
    (r'^(?P<summit_name>[\w-]+)\.csv$', 'csv'),
    (r'^(?P<summit_name>[\w-]+)\.ical$', 'ical'),
    (r'^(?P<summit_name>[\w-]+)/participant/my_schedule_(?P<secret_key>[0-9a-f]{32})\.ical$', 'user_private_ical'),
    (r'^(?P<summit_name>[\w-]+)/participant/(?P<username>[%+\.\w-]+)\.ical$', 'user_ical'),
    (r'^(?P<summit_name>[\w-]+)/room/(?P<room_name>[%+\.\w-]+).ical$', 'room_ical'),
    (r'^(?P<summit_name>[\w-]+)/track/(?P<track_slug>[%+\.\w-]+).ical$', 'track_ical'),
)

if settings.DEBUG or settings.SERVE_STATIC:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
        (r'^(robots.txt)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
        (r'^ubuntu-website/media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.THEME_MEDIA}),
    )
