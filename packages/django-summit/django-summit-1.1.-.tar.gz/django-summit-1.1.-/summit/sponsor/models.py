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

from django.db import models

from django.contrib.auth.models import User

from summit.schedule.models import Summit

__all__ = (
    'Sponsorship',
    'SponsorshipScore',
    'NonLaunchpadSponsorship',
    'NonLaunchpadSponsorshipScore',
)


class Sponsorship(models.Model):
    user = models.ForeignKey(User)
    summit = models.ForeignKey(Summit)
    location = models.CharField(max_length=50)
    country = models.CharField(max_length=2)
    about = models.TextField(max_length=1000)
    needs_travel = models.BooleanField()
    needs_accomodation = models.BooleanField()
    would_crew = models.BooleanField()
    diet = models.CharField(max_length=100, blank=True)
    further_info = models.TextField(max_length=1000, blank=True)
    video_agreement = models.BooleanField()

    def __unicode__(self):
        return self.user.username

    @property
    def score(self):
        return sum(s.score for s in self.sponsorshipscore_set.all())

    @property
    def numscores(self):
        return self.sponsorshipscore_set.count()


class SponsorshipScore(models.Model):
    sponsorship = models.ForeignKey(Sponsorship)
    user = models.ForeignKey(User)
    score = models.IntegerField()
    comment = models.TextField(max_length=500, blank=True)

    def __unicode__(self):
        return "%s by %s: %d" % (
            self.sponsorship.user.username,
            self.user.username,
            self.score)


class NonLaunchpadSponsorship(models.Model):
    '''A Sponsorship model for those without a Launchpad account.'''
    requested_by = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=200)
    email = models.EmailField()

    # XXX: rockstar - I'd LIKE to use a mixin here, but man, inheritance for
    # models is funky broken.
    summit = models.ForeignKey(Summit)
    location = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=2, blank=True)
    about = models.TextField(max_length=1000)
    needs_travel = models.BooleanField()
    needs_accomodation = models.BooleanField()
    would_crew = models.BooleanField()
    diet = models.CharField(max_length=100, blank=True)
    further_info = models.TextField(max_length=1000, blank=True)

    @property
    def score(self):
        return sum(s.score for s in self.nonlaunchpadsponsorshipscore_set.all())

    @property
    def numscores(self):
        return self.nonlaunchpadsponsorshipscore_set.count()


class NonLaunchpadSponsorshipScore(models.Model):
    sponsorship = models.ForeignKey(NonLaunchpadSponsorship)
    user = models.ForeignKey(User)
    score = models.IntegerField()
    comment = models.TextField(max_length=500, blank=True)

    def __unicode__(self):
        return "%s by %s: %d" % (
            self.sponsorship.name,
            self.user.username,
            self.score)


class SponsorshipSuggestion(models.Model):
    '''A Sponsorship model for those without a Launchpad account.'''
    suggested_by = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    launchpad_name = models.CharField(max_length=100)

    # XXX: rockstar - I'd LIKE to use a mixin here, but man, inheritance for
    # models is funky broken.
    summit = models.ForeignKey(Summit)
    location = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=2, blank=True)
    about = models.TextField(max_length=1000)
    needs_travel = models.BooleanField()
    needs_accomodation = models.BooleanField()
    would_crew = models.BooleanField()
    diet = models.CharField(max_length=100, blank=True)
    further_info = models.TextField(max_length=1000, blank=True)

    @property
    def score(self):
        return sum(s.score for s in self.sponsorshipsuggestionscore_set.all())

    @property
    def numscores(self):
        return self.sponsorshipsuggestionscore_set.count()


class SponsorshipSuggestionScore(models.Model):
    sponsorship = models.ForeignKey(SponsorshipSuggestion)
    user = models.ForeignKey(User)
    score = models.IntegerField()
    comment = models.TextField(max_length=500, blank=True)

    def __unicode__(self):
        return "%s by %s: %d" % (
            self.sponsorship.launchpad_name,
            self.user.username,
            self.score)
