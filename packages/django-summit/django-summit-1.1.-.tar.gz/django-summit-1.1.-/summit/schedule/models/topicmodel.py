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

from summit.schedule.models.summitmodel import Summit

__all__ = (
    'Topic',
)


class Topic(models.Model):
    summit = models.ForeignKey(Summit)
    title = models.CharField(max_length=100)

    class Meta:
        app_label = 'schedule'
        ordering = ('summit', 'title')

    def __unicode__(self):
        return self.title
