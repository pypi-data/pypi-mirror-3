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

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from summit.schedule.models import Summit

__all__ = (
    'summit_required',
    'summit_only_required',
    'summit_attendee_required',
)


def summit_required(func):

    def inner(request, summit_name, *args, **kwds):
        summit = get_object_or_404(Summit, name=summit_name)
        try:
            if request.user.is_authenticated():
                attendee = summit.attendee_set.get(user=request.user)
            else:
                attendee = None
        except ObjectDoesNotExist:
            attendee = None
        return func(request, summit, attendee, *args, **kwds)
    inner.__name__ = func.__name__
    return inner


def summit_only_required(func):

    def inner(request, summit_name, *args, **kwds):
        summit = get_object_or_404(Summit, name=summit_name)
        return func(request, summit, *args, **kwds)
    inner.__name__ = func.__name__
    return inner


def summit_attendee_required(func):

    @login_required
    @summit_required
    def inner(request, summit, attendee, *args, **kwds):
        if not attendee:
            context = {
                'summit': summit,
                }
            return render_to_response("schedule/not-attending.html", context,
                                      context_instance=RequestContext(request))
        return func(request, summit, attendee, *args, **kwds)
    inner.__name__ = func.__name__
    return inner
