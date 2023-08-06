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

from django.contrib import admin

from summit.schedule.models import Room, RoomBusy

__all__ = (
)


class RoomBusyInline(admin.TabularInline):
    model = RoomBusy
    extra = 3


class RoomAdmin(admin.ModelAdmin):
    list_display = ('summit', 'name', 'title', 'type', 'size')
    list_display_links = ('name', 'title')
    list_filter = ('summit', 'type', 'tracks', 'size')
    search_fields = ('name', 'title')
    filter_horizontal = ('tracks',)

    fieldsets = (
        (None, {
            'fields': ('summit', 'name', 'title', 'type', 'size', 'tracks',
                       'icecast_url', 'irc_channel', 'has_dial_in'),
        }),
        ("Availability", {
            'fields': ('start_utc', 'end_utc'),
        }),
    )

    inlines = (RoomBusyInline, )

admin.site.register(Room, RoomAdmin)
