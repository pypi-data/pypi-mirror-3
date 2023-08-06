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
from django import test as djangotest
from django.conf import settings
from model_mommy import mommy as factory
from summit.schedule.fields import NameField

from summit.schedule.models import Summit

# Monkey-patch our NameField into the types of fields that the factory
# understands.  This is simpler than trying to subclass the Mommy
# class directly.
factory.default_mapping[NameField] = str

class MenuTestCase(djangotest.TestCase):

    def setUp(self):
        now = datetime.datetime.utcnow()
        one_hour = datetime.timedelta(0, 3600)
        summit = factory.make_one(Summit, name='uds-test')
        
    def test_menu_highlights(self):
        schedule_page = self.client.get('/uds-test/')
        self.assertContains(schedule_page, '<a class="main-nav-item current" href="/uds-test/" title="Schedule">Schedule</a>', 1)
        self.assertContains(schedule_page, '<a class="main-nav-item current" href="/today/uds-test/" title="Today">Today</a>', 0)

        today_page = self.client.get('/today/uds-test/')
        self.assertContains(today_page, '<a class="main-nav-item current" href="/uds-test/" title="Schedule">Schedule</a>', 0)
        self.assertContains(today_page, '<a class="main-nav-item current" href="/today/uds-test/" title="Today">Today</a>', 1)

