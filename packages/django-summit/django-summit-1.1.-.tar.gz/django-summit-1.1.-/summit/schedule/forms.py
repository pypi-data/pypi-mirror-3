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
from django.contrib.formtools import wizard
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from launchpadlib.credentials import Credentials

from django.db import models

from summit.schedule.fields import NameField

from summit.schedule.models.meetingmodel import Meeting
from summit.schedule.models.attendeemodel import Attendee
from summit.schedule.models.participantmodel import Participant

from common.forms import RenderableMixin

class MultipleAttendeeField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return u"%s %s (%s)" % (
            obj.user.first_name, obj.user.last_name, obj.user.username)


class MeetingFormBase(forms.ModelForm):
    participants = MultipleAttendeeField(
        queryset=Attendee.objects.all,
        widget=forms.CheckboxSelectMultiple,
        label='Participants',
        required=False)

    class Media:
        css = {'all': (
                       '/media/css/colortip-1.0-jquery.css', 
                       )}
        js = (
              '/media/js/colortip-1.0-jquery.js',
              )

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            if kwargs['instance'].pk is not None:
                # We get the 'initial' keyword argument or initialize it
                # as a dict if it didn't exist.
                initial = kwargs.setdefault('initial', {})
                # The widget for a ModelMultipleChoiceField expects
                # a list of primary key for the selected data.
                initial['participants'] = [
                    attendee.pk
                    for attendee in kwargs['instance'].participants.all()]

        super(MeetingFormBase, self).__init__(*args, **kwargs)
        self.fields['tracks'].queryset = self.instance.summit.track_set.all()

        summit = self.instance.summit
        self.fields['participants'].queryset = Attendee.objects.filter(
            summit=summit).order_by('user__first_name',
                                    'user__last_name',
                                    'user__username')

    def save(self, commit=True):
        instance = super(MeetingFormBase, self).save(commit)

        # Prepare a 'save_m2m' method for the form,
        if 'save_m2m' in dir(self):
            old_save_m2m = self.save_m2m
        else:
            old_save_m2m = None
        def save_m2m():
            if old_save_m2m is not None:
                old_save_m2m()
            # This is where we actually link the pizza with toppings
            instance.participants.clear()
            for participant in self.cleaned_data['participants']:
                record = Participant(meeting=instance, attendee=participant,
                                     required=True)
                record.save()
        self.save_m2m = save_m2m

        # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()

        return instance


class CreateMeeting(MeetingFormBase, RenderableMixin):
    class Meta:
        model = Meeting
        fields = ('title', 'description', 'tracks', 'type', 'spec_url', 'wiki_url', 'pad_url',
                  'requires_dial_in', 'private', 'slots', 'approved', 'video', 'override_break')

class OrganizerEditMeeting(MeetingFormBase, RenderableMixin):
    class Meta:
        model = Meeting
        fields = ('title', 'description', 'tracks', 'type', 'spec_url', 'wiki_url', 'pad_url',
                  'requires_dial_in', 'private', 'slots', 'approved', 'video', 'override_break')

class ProposeMeeting(MeetingFormBase, RenderableMixin):
    class Meta:
        model = Meeting
        fields = ('title', 'description', 'tracks', 'spec_url', 'wiki_url', 'pad_url')


class EditMeeting(MeetingFormBase, RenderableMixin):
    class Meta:
        model = Meeting
        fields = ('title', 'description', 'tracks', 'spec_url', 'wiki_url', 'pad_url')

class MeetingReview(forms.ModelForm, RenderableMixin):
    class Meta:
        model = Meeting
        fields = ('approved',)
