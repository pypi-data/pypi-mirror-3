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

from summit.schedule.models import Attendee, AttendeeBusy, Participant, Meeting

__all__ = (
)


class AttendeeBusyInline(admin.TabularInline):
    model = AttendeeBusy
    extra = 3


class AttendeeAdmin(admin.ModelAdmin):
    list_display = ('summit', 'user')
    list_display_links = ('user', )
    list_filter = ('summit', 'tracks', 'topics')
    search_fields = ('user__username', 'user__first_name', 'user__last_name',
                     'user__email')
    inlines = (AttendeeBusyInline, )


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'attendee', 'required')
    list_display_links = ('attendee', )
    search_fields = ('attendee__user__username', 'attendee__user__first_name', 'attendee__user__last_name',
                     'attendee__user__email', 'meeting__name', 'meeting__title')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "meeting":
            kwargs["queryset"] = Meeting.objects.order_by('name')
        if db_field.name == "attendee":
            kwargs["queryset"] = Attendee.objects.order_by('user__username')
        return super(ParticipantAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Attendee, AttendeeAdmin)

admin.site.register(Participant, ParticipantAdmin)
