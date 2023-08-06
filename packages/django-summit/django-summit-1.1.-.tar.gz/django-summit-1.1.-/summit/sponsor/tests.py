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


import datetime
import unittest
from django import test as djangotest
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from summit.schedule.models import Summit
from summit.sponsor.models import (
    Sponsorship,
    SponsorshipScore,
    SponsorshipSuggestion,
    SponsorshipSuggestionScore,
    NonLaunchpadSponsorship,
    NonLaunchpadSponsorshipScore,
)
from summit.sponsor.forms import SponsorshipSuggestionForm

class TestSponsorshipApplicationTestCase(djangotest.TestCase):

    def setUp(self):
        self.client = djangotest.Client(enforce_csrf_checks=True)
        self.summit = Summit.objects.create(
            name='test-summit',
            title='Test Summit',
            location='Test Location',
            description='Test Summit Description',
            timezone='UTC',
            last_update=datetime.datetime.now(),
            state='sponsor',
            date_start=(datetime.datetime.now() + datetime.timedelta(days=1)),
            date_end=(datetime.datetime.now() + datetime.timedelta(days=6)),
        )
        
        self.user = User.objects.create(
            username='testuser',
            first_name='Test',
            last_name='User',
            is_superuser=True,
        )
        self.user.set_password('password')
        self.user.save()
        
        self.form_data_0 = {
            '0-location': 'Test Location',
            '0-country': 'US',
            '0-about': 'Test About Description',
            '0-video_tos': 'Fake TOS text',
            '0-video_agreement': 1,
            'wizard_step': 0,
        }

        self.form_data_1 = {
            '1-needs_travel': 0,
            '1-needs_accomodation': 0,
            '1-would_crew': 'False',
            '1-diet': 'None',
            '1-further_info': 'Nothing',
            'wizard_step': 1,
        }

    def test_application_process(self):
        self.assertEquals(0, Sponsorship.objects.filter(user=self.user).count())

        auth = self.client.login(username='testuser', password='password')
        response = self.client.get('/test-summit/sponsorship/')
        self.assertContains(response, 'csrfmiddlewaretoken')
        data = self.form_data_0
        # Add csrftoken to form data
        data['csrfmiddlewaretoken'] = self.client.cookies['csrftoken'].value
        response = self.client.post('/test-summit/sponsorship/', data)
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'Finish')
        
        self.assertContains(response, 'csrfmiddlewaretoken')
        data.update(self.form_data_1)
        # Scrape the hashed value from the template context
        data['hash_0'] = response.context['previous_fields'][response.context['previous_fields'].index('hash_0')+15:response.context['previous_fields'].index('hash_0')+55]
        data['csrfmiddlewaretoken'] = self.client.cookies['csrftoken'].value
        response = self.client.post('/test-summit/sponsorship/', data, follow=False)
        self.assertEquals(302, response.status_code)
        self.assertEquals(response._headers['location'], ('Location', 'http://testserver/test-summit/sponsorship/done'))

        self.assertEquals(1, Sponsorship.objects.filter(user=self.user).count())
        
    def test_suggest_process(self):
        auth = self.client.login(username='testuser', password='password')
        response = self.client.get('/test-summit/suggestsponsorship/')
        self.assertContains(response, 'csrfmiddlewaretoken')
        # TODO: Finish testing the process

    def test_nonlaunchpad_process(self):
        auth = self.client.login(username='testuser', password='password')
        response = self.client.get('/test-summit/nonlaunchpadsponsorship/')
        self.assertContains(response, 'csrfmiddlewaretoken')
        # TODO: Finish testing the process


class SponsorshipDisplayTestCase(djangotest.TestCase):
    """Tests for the 'reschedule' management command."""

    def setUp(self):
        self.summit = Summit.objects.create(
            name='test-summit',
            title='Test Summit',
            location='Test Location',
            description='Test Summit Description',
            timezone='UTC',
            last_update=datetime.datetime.now(),
            state='sponsor',
            date_start=(datetime.datetime.now() + datetime.timedelta(days=1)),
            date_end=(datetime.datetime.now() + datetime.timedelta(days=6)),
        )
        
        self.user = User.objects.create(
            username='testuser',
            first_name='Test',
            last_name='User',
        )
        
    def test_sponsorship_display(self):
        sponsorship = SponsorshipSuggestion.objects.create(
            suggested_by=self.user,
            name='Test Suggestion',
            launchpad_name='testsuggestion',
            summit=self.summit,
            location='Test Location',
            country='Test Country',
            about='Test About Description',
            needs_travel=False,
            needs_accomodation=False,
            would_crew=True,
            diet='Test Diet',
            further_info='Test Further Info',
        )
        
        scorer = User.objects.create(
            username='testscorer',
            first_name='Test',
            last_name='Scorer',
        )
        score = SponsorshipSuggestionScore.objects.create(
            sponsorship=sponsorship,
            user=scorer,
            score=1,
            comment='Test Comment',
        )
        
        self.assertEquals(unicode(score), "testsuggestion by testscorer: 1")

    def test_nonlaunchpad_display(self):
        sponsorship = NonLaunchpadSponsorship.objects.create(
            requested_by=self.user,
            name='Test Sponsorship',
            company='Test Company',
            email='test@example.org',
            summit=self.summit,
            location='Test Location',
            country='Test Country',
            about='Test About Description',
            needs_travel=False,
            needs_accomodation=False,
            would_crew=True,
            diet='Test Diet',
            further_info='Test Further Info',
        )
        
        scorer = User.objects.create(
            username='testscorer',
            first_name='Test',
            last_name='Scorer',
        )
        score = NonLaunchpadSponsorshipScore.objects.create(
            sponsorship=sponsorship,
            user=scorer,
            score=1,
            comment='Test Comment',
        )
        
        self.assertEquals(unicode(score), "Test Sponsorship by testscorer: 1")

class SponsorshipFormTestCase(djangotest.TestCase):

    def setUp(self):
        self.summit = Summit.objects.create(
            name='test-summit',
            title='Test Summit',
            location='Test Location',
            description='Test Summit Description',
            timezone='UTC',
            last_update=datetime.datetime.now(),
            state='sponsor',
            date_start=(datetime.datetime.now() + datetime.timedelta(days=1)),
            date_end=(datetime.datetime.now() + datetime.timedelta(days=6)),
        )
        
        self.user = User.objects.create(
            username='testuser',
            first_name='Test',
            last_name='User',
        )
        
    def test_suggest_valid_username(self):
        form_data = {
            'launchpad_name': 'mhall119',
        }
        form = SponsorshipSuggestionForm(form_data)
        self.assertTrue(form.is_valid())

    def test_suggest_invalid_username(self):
        form_data = {
            'launchpad_name': 'mhall119000',
        }
        form = SponsorshipSuggestionForm(form_data)
        self.assertFalse(form.is_valid())


class SponsorshipReviewTestCase(djangotest.TestCase):

    def setUp(self):
        self.summit = Summit.objects.create(
            name='test-summit',
            title='Test Summit',
            location='Test Location',
            description='Test Summit Description',
            timezone='UTC',
            last_update=datetime.datetime.now(),
            state='sponsor',
            date_start=(datetime.datetime.now() + datetime.timedelta(days=1)),
            date_end=(datetime.datetime.now() + datetime.timedelta(days=6)),
        )
        
        self.user = User.objects.create(
            username='testuser',
            first_name='Test',
            last_name='User',
        )
        
        self.sponsorship = Sponsorship.objects.create(
            user=self.user,
            summit=self.summit,
            location='Test Location',
            country='Test Country',
            about='Test About Description',
            needs_travel=False,
            needs_accomodation=False,
            would_crew=True,
            diet='Test Diet',
            further_info='Test Further Info',
        )
        
        self.scorer = User.objects.create(
            username='testscorer',
            first_name='Test',
            last_name='Scorer',
            is_superuser=True,
        )
        self.scorer.set_password('password')
        self.scorer.save()
        
        self.score = SponsorshipScore.objects.create(
            sponsorship=self.sponsorship,
            user=self.scorer,
            score=1,
            comment='Test Comment',
        )

    def test_sponsorship_review_display(self):
        self.client.login(username='testscorer', password='password')
        response = self.client.get('/test-summit/sponsorship/review/%s' % self.sponsorship.id)
        self.assertContains(response, '<h1>Test User</h1>', 1)
        self.assertContains(response, '<th>Location:</th><td>Test Location</td>', 1)
        self.assertContains(response, '<th>Country:</th><td>Test Country</td>', 1)
        self.assertContains(response, '<p>\nTest About Description\n</p>', 1)

    def test_sponsorship_about_paras_filtering(self):
        self.sponsorship.about = 'Test\nAbout\nDescription'
        self.sponsorship.save()

        self.client.login(username='testscorer', password='password')
        response = self.client.get('/test-summit/sponsorship/review/%s' % self.sponsorship.id)
        self.assertContains(response, '<p>\nTest</p>\n<p>\nAbout</p>\n<p>\nDescription\n</p>', 1)

    def test_sponsorship_about_urlize_filtering(self):
        self.sponsorship.about = 'Test http://example.org Description'
        self.sponsorship.save()

        self.client.login(username='testscorer', password='password')
        response = self.client.get('/test-summit/sponsorship/review/%s' % self.sponsorship.id)
        self.assertContains(response, '<p>\nTest <a href="http://example.org" rel="nofollow">http://example.org</a> Description\n</p>', 1)

    def test_sponsorship_xss_escaping(self):
        self.sponsorship.location = '"><script>alert(/xss/)</script>'
        self.sponsorship.country = '"><script>alert(/xss/)</script>'
        self.sponsorship.about = '"><script>alert(/xss/)</script>'
        self.sponsorship.diet = '"><script>alert(/xss/)</script>'
        self.sponsorship.further_info = '"><script>alert(/xss/)</script>'
        self.sponsorship.save()
        
        self.user.first_name= '"><script>alert(/xss/)</script>'
        self.user.last_name=''
        self.user.save()
        
        self.client.login(username='testscorer', password='password')
        response = self.client.get('/test-summit/sponsorship/review/%s' % self.sponsorship.id)
        # All displayed fields should have their html escaped
        self.assertContains(response, '<h1>&quot;&gt;&lt;script&gt;alert(/xss/)&lt;/script&gt;</h1>', 1)
        self.assertContains(response, '<th>Location:</th><td>&quot;&gt;&lt;script&gt;alert(/xss/)&lt;/script&gt;</td>', 1)
        self.assertContains(response, '<th>Country:</th><td>&quot;&gt;&lt;script&gt;alert(/xss/)&lt;/script&gt;</td>', 1)
        self.assertContains(response, '"><script>alert(/xss/)</script>', 0)


class SuggestionReviewTestCase(djangotest.TestCase):

    def setUp(self):
        self.summit = Summit.objects.create(
            name='test-summit',
            title='Test Summit',
            location='Test Location',
            description='Test Summit Description',
            timezone='UTC',
            last_update=datetime.datetime.now(),
            state='sponsor',
            date_start=(datetime.datetime.now() + datetime.timedelta(days=1)),
            date_end=(datetime.datetime.now() + datetime.timedelta(days=6)),
        )
        
        self.user = User.objects.create(
            username='testuser',
            first_name='Test',
            last_name='User',
        )
        
        self.sponsorship = SponsorshipSuggestion.objects.create(
            suggested_by=self.user,
            name='Test Suggestion',
            launchpad_name='testsuggestion',
            summit=self.summit,
            location='Test Location',
            country='Test Country',
            about='Test About Description',
            needs_travel=False,
            needs_accomodation=False,
            would_crew=True,
            diet='Test Diet',
            further_info='Test Further Info',
        )
        
        self.scorer = User.objects.create(
            username='testscorer',
            first_name='Test',
            last_name='Scorer',
            is_superuser=True,
        )
        self.scorer.set_password('password')
        self.scorer.save()
        
        self.score = SponsorshipSuggestionScore.objects.create(
            sponsorship=self.sponsorship,
            user=self.scorer,
            score=1,
            comment='Test Comment',
        )

    def test_sponsorshipsuggestion_review_display(self):
        self.client.login(username='testscorer', password='password')
        response = self.client.get('/test-summit/suggestedsponsorship/review/%s' % self.sponsorship.id)
        self.assertContains(response, '<h1>Test Suggestion</h1>', 1)

    def test_sponsorshipsuggestion_xss_escaping(self):
        self.client.login(username='testscorer', password='password')
        self.sponsorship.name = '"><script>alert(/xss/)</script>'
        self.sponsorship.location = '"><script>alert(/xss/)</script>'
        self.sponsorship.country = '"><script>alert(/xss/)</script>'
        self.sponsorship.about = '"><script>alert(/xss/)</script>'
        self.sponsorship.diet = '"><script>alert(/xss/)</script>'
        self.sponsorship.further_info = '"><script>alert(/xss/)</script>'
        self.sponsorship.save()
        response = self.client.get('/test-summit/suggestedsponsorship/review/%s' % self.sponsorship.id)
        # All displayed fields should have their html escaped
        self.assertContains(response, '"><script>alert(/xss/)</script>', 0)


