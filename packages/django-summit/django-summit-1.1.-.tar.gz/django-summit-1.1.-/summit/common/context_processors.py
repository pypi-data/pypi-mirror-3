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

# context processors for The Summit Scheduler
# see http://docs.djangoproject.com/en/dev/ref/settings/#setting-TEMPLATE_CONTEXT_PROCESSORS

from schedule.models.summitmodel import Summit

from django.conf import settings

from common.models import Menu


def url_base(request):
    url = request.get_full_path().split('/')
    return {'url_base':url[1]}


def next_summit(request):
    return {'next_summit': Summit.on_site.next()}


def login_redirect(request):
    return {'login_next': request.get_full_path()}


def summit_version(request):
    """
    add The Summit Scheduler version to template context processor.
    """

    version = getattr(settings, 'VERSION_STRING', 'unknown')
    return {'summit_version': version}

def site_menu(request):
    """
    Adds the site's menu to the template context
    """
    return {'main_menu': Menu.on_site.all()[0].slug}
