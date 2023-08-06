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

from django import forms
from django.conf import settings
from django.contrib import admin
from django.forms.util import flatatt
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from summit.schedule.models import Attendee, Meeting, Participant

__all__ = (
)


class AttendeeInput(forms.TextInput):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            try:
                pkey = long(value)
                final_attrs['value'] = (
                    Attendee.objects.get(pk=pkey).user.username)
            except ValueError:
                # Assume we got a username, return as is (on a form error)
                final_attrs['value'] = force_unicode(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class ParticipantInline(admin.TabularInline):
    model = Participant
    template = 'admin/edit_inline/collapsed_tabular.html'

    def _media(self):
        media = super(ParticipantInline, self)._media()
        media.add_js(('%sjs/collapse.min.js'
                      % settings.ADMIN_MEDIA_PREFIX, ))
        return media
    media = property(_media)

    def get_formset(self, request, obj=None, **kwargs):
        fs = super(ParticipantInline, self).get_formset(request, obj, **kwargs)
        if fs and obj:
            fs = super(ParticipantInline, self).get_formset(request, obj, **kwargs)
            fs.form.base_fields['attendee'].queryset = fs.form.base_fields['attendee'].queryset.filter(summit=obj.summit)
        return fs

class MeetingAdminForm(forms.ModelForm):
    drafter = forms.CharField(required=False, widget=AttendeeInput)
    assignee = forms.CharField(required=False, widget=AttendeeInput)
    approver = forms.CharField(required=False, widget=AttendeeInput)
    scribe = forms.CharField(required=False, widget=AttendeeInput)

    class Meta:
        model = Meeting

    ### FIXME: Should really remove this duplication
    def clean_drafter(self):
        if 'drafter' in self.cleaned_data:
            data = self.cleaned_data['drafter']
            if len(data) == 0:
                return None
            try:
                return Attendee.objects.get(
                    summit=self.cleaned_data['summit'],
                    user__username=data)
            except Attendee.DoesNotExist:
                raise forms.ValidationError(
                    "Username is invalid (doesn't exist or not an attendee).")

    def clean_assignee(self):
        if 'assignee' in self.cleaned_data:
            data = self.cleaned_data['assignee']
            if len(data) == 0:
                return None
            try:
                return Attendee.objects.get(
                    summit=self.cleaned_data['summit'],
                    user__username=data)
            except Attendee.DoesNotExist:
                raise forms.ValidationError(
                    "Username is invalid (doesn't exist or not an attendee).")

    def clean_approver(self):
        if 'approver' in self.cleaned_data:
            data = self.cleaned_data['approver']
            if len(data) == 0:
                return None
            try:
                return Attendee.objects.get(
                    summit=self.cleaned_data['summit'],
                    user__username=data)
            except Attendee.DoesNotExist:
                raise forms.ValidationError(
                    "Username is invalid (doesn't exist or not an attendee).")

    def clean_scribe(self):
        if 'scribe' in self.cleaned_data:
            data = self.cleaned_data['scribe']
            if len(data) == 0:
                return None
            try:
                return Attendee.objects.get(
                    summit=self.cleaned_data['summit'],
                    user__username=data)
            except Attendee.DoesNotExist:
                raise forms.ValidationError(
                    "Username is invalid (doesn't exist or not an attendee).")


def share(modeladmin, request, queryset):
    for meeting in queryset.all():
        meeting.share()
share.short_description = "Share Meetings (Private only)"

class MeetingAdmin(admin.ModelAdmin):
    list_display = ('summit', 'slots', 'name', 'title', 'type', 'approved')
    list_display_links = ('name', 'title')
    list_filter = ('summit', 'type', 'tracks', 'topics', 'slots', 'private',
                   'status', 'priority')
    search_fields = ('name', 'title')

    fieldsets = (
        (None, {
            'fields': ('summit', 'name', 'title', 'description', 'approved',
                       'type', 'tracks', 'topics', 'requires_dial_in', 'video'),
        }),
        ("References", {
            'fields': ('spec_url', 'wiki_url', 'pad_url'),
        }),
        ("Scheduling details", {
            'classes': ('collapse', ),
            'fields': ('slots', 'override_break', 'private', 'private_key', 'status', 'priority')
        }),
        ("Key people", {
            'classes': ('collapse', ),
            'fields': ('drafter', 'assignee', 'approver', 'scribe'),
        }),
    )

    inlines = (ParticipantInline, )
    form = MeetingAdminForm
    actions = [share]
admin.site.register(Meeting, MeetingAdmin)
