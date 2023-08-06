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

from summit.schedule.models.meetingmodel import Meeting
from summit.schedule.models.attendeemodel import Attendee

__all__ = (
    'Participant',
)


HELP_TEXT = {
    "attendee": ("Be sure to choose the attendee from the correct "
        "event. If the person is not listed for the event in question "
        "then they are not known to be attending yet, and have to "
        "sign up to attend."),
    "required": ("The person is required to attend the session. "
        "If this is set the scheduler will attempt to ensure that "
        "the person is able to attend. If it is not checked then "
        "the scheduler won't consider the person when deciding "
        "where the meeting can go on the schedule."),
    "from_launchpad": ("Set to indicate the participant comes from "
        "a subscription to the Launchpad blueprint. Don't set this "
        "if you are adding the participant, as they may end up "
        "getting deleted if you do."),
}


class Participant(models.Model):
    meeting = models.ForeignKey(Meeting)
    attendee = models.ForeignKey(Attendee,
            help_text=HELP_TEXT["attendee"])
    required = models.BooleanField(default=False,
            help_text=HELP_TEXT["required"])
    from_launchpad = models.BooleanField(default=False,
            help_text=HELP_TEXT["from_launchpad"])

    class Meta:
        app_label = 'schedule'
        ordering = ('meeting', 'attendee', 'required')

    def __unicode__(self):
        return self.attendee.user.username
