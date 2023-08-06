# -*- coding: utf-8 -*-
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
from launchpadlib.launchpad import Launchpad, EDGE_SERVICE_ROOT

from summit.extra.formsets import WizardFormSet
from summit.extra.fields import CountryField

from summit.sponsor.models import (Sponsorship, SponsorshipSuggestion,
    SponsorshipScore, NonLaunchpadSponsorship)


__all__ = (
    'SponsorshipForm1',
    'SponsorshipFormSet',
    'SponsorshipForm3',
    'SponsorshipWizard',
    'SponsorshipScoreForm',
)


VIDEO_TERMS = (
'''Under the terms set below, you hereby consent to and authorize the use
by of any and all photographs, video images and audio taken of me
including derivative works thereof, and any reproduction of them in
any form in any media whatsoever (such as books, DVDs, etc.),
throughout the world at the Ubuntu Developer Summit.

You also consent to the use of my own name the aforesaid photographs,
video images or audio.

You hereby release any and all claims whatsoever in connection with
the use of your photographs, video images, audio and name and the
reproduction thereof as aforesaid. This work and any and all
photographs, video images and audio taken of you including derivative
works thereof, and any reproduction of them in any form in any media
whatsoever (such as books, DVDs, etc.), throughout the world are
licensed under the Creative Commons Attribution-ShareAlike 3.0 License
as described below:

We are free:
to Share - to copy, distribute and transmit the work
to Remix - to adapt the work

Under the following conditions:
Attribution - We must attribute the work in the manner specified by
the author or licensor (but not in any way that suggests that you
endorse us or our use of the work).
Share Alike - If we alter, transform, or build upon this work, we may
distribute the resulting work only under the same, similar or a
compatible license.

To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/3.0/''')


class SponsorshipForm1(forms.Form):
    location = forms.CharField(max_length=50,
                               help_text='Enter your nearest city or airport')
    country = CountryField()
    about = forms.CharField(max_length=3000,
                            label='About yourself',
                            help_text='Tell us about yourself and your work within the Ubuntu community',
                            widget=forms.Textarea)
    video_tos = forms.CharField(
        label='Video agreement (optional)',
        initial=VIDEO_TERMS,
        widget=forms.Textarea(attrs={'readonly': 'readonly'}))
    video_agreement = forms.BooleanField(required=False,
        label='I agree to the video agreement (optional)')


class NonLaunchpadSponsorshipForm(forms.Form):
    '''A Sponsorship form for people without Launchpad accounts.'''
    name = forms.CharField(max_length=100, required=True)
    company = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)
    about = forms.CharField(max_length=3000,
        label='About your suggestion',
        help_text='Add the person\'s involvement in projects related to Ubuntu.',
        widget=forms.Textarea)


class SponsorshipSuggestionForm(forms.Form):
    '''A Sponsorship form for suggesting someone else for sponsorship.'''
    launchpad_name = forms.CharField(label='Launchpad Username')

    def clean_launchpad_name(self):
        data = self.cleaned_data['launchpad_name']
        launchpad = Launchpad.login("Summit", "", "", EDGE_SERVICE_ROOT,
                settings.LAUNCHPAD_CACHE)
        name = None
        try:
            name = launchpad.people[data].display_name
        except KeyError:
            raise forms.ValidationError("%s is not a valid user on Launchpad" %
                    data)
        return data

PARTICIPATION_CHOICES = [
    ("not", "I am NOT interested in this idea"),
    ("may", "I MAY attend discussions about this idea"),
    ("will", "I WILL discuss this idea"),
    ("lead", "I will LEAD discussion and development of this idea"),
]

class SponsorshipFormSet(WizardFormSet):

    class MagicWidget(forms.Widget):

        class Media:
            js = ('sponsor/formset.js', )

    def _get_media(self):
        media = super(SponsorshipFormSet, self)._get_media()
        media = media + self.MagicWidget().media
        return media
    media = property(_get_media)

    def as_table(self):
        forms = u'\n'.join([form.as_tr() for form in self.forms])
        return mark_safe(u'\n'.join([unicode(self.management_form), forms]))


class SponsorshipForm3(forms.Form):
    needs_travel = forms.BooleanField(label='Sponsorship of Travel:',
                                      required=False,
                                      initial=True)
    needs_accomodation = forms.BooleanField(label='Sponsorship of Accomodation:',
                                            required=False,
                                            initial=True)

    would_crew = forms.BooleanField(label='Would you be willing to participate as member of the crew?',
                                    required=False,
                                    widget=forms.Select(choices=[(False, "no"), (True, "Yes")]))

    diet = forms.CharField(max_length=100,
                           label='Special dietary requirements',
                           required=False)

    further_info = forms.CharField(max_length=3000,
                                   label='Futher information',
                                   help_text='Enter any further information to support your sponsorship request',
                                   widget=forms.Textarea,
                                   required=False)


class SponsorshipWizard(wizard.FormWizard):

    def get_template(self, step):
        return 'sponsor/step%d.html' % step

    def done(self, request, form_list):
        sponsorship = Sponsorship.objects.create(
            user=request.user, summit=self.summit,
            location=form_list[0].cleaned_data['location'],
            country=form_list[0].cleaned_data['country'],
            about=form_list[0].cleaned_data['about'],
            # 2 -> 1
            needs_travel=form_list[1].cleaned_data['needs_travel'],
            needs_accomodation=form_list[1].cleaned_data['needs_accomodation'],
            would_crew=form_list[1].cleaned_data['would_crew'],
            diet=form_list[1].cleaned_data['diet'],
            further_info=form_list[1].cleaned_data['further_info'],
            video_agreement=form_list[0].cleaned_data['video_agreement'])

        return HttpResponseRedirect("/%s/sponsorship/done" % self.summit.name)


class SponsorshipSuggestionWizard(wizard.FormWizard):
    '''A Wizard for suggesting other people for sponsorship.'''

    def get_template(self, step):
        return 'sponsor/suggeststep%d.html' % step

    def done(self, request, form_list):

        launchpad_name = form_list[0].cleaned_data['launchpad_name']

        launchpad = Launchpad.login("Summit", "", "", EDGE_SERVICE_ROOT, settings.LAUNCHPAD_CACHE)
        name = launchpad.people[launchpad_name].display_name

        sponsorship = SponsorshipSuggestion.objects.create(
            suggested_by=request.user, summit=self.summit,
            launchpad_name=launchpad_name, name=name)
            #location=form_list[0].cleaned_data['location'],
            #country=form_list[0].cleaned_data['country'],
            #about=form_list[0].cleaned_data['about'])

        return HttpResponseRedirect(
            "/%s/suggestsponsorship/done" % self.summit.name)


class NonLaunchpadSponsorshipWizard(wizard.FormWizard):
    '''A Wizard for suggesting other people for sponsorship.'''

    def get_template(self, step):
        return 'sponsor/nonlaunchpadstep%d.html' % step

    def done(self, request, form_list):
        sponsorship = NonLaunchpadSponsorship.objects.create(
            requested_by=request.user, summit=self.summit,
            name=form_list[0].cleaned_data['name'],
            company=form_list[0].cleaned_data['company'],
            email=form_list[0].cleaned_data['email'],
            about=form_list[0].cleaned_data['about'])

        return HttpResponseRedirect(
            "/%s/nonlaunchpadsponsorship/done" % self.summit.name)


class SponsorshipScoreForm(forms.ModelForm):

    class Meta:
        model = SponsorshipScore
        fields = ('score', 'comment')
