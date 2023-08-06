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

from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from django.forms import ModelForm
from django import forms
from django.contrib import admin

from summit.schedule.models import Track, Topic, Summit, SummitSprint
__all__ = (
)


class TrackInline(admin.TabularInline):
    model = Track
    extra = 5

    template = 'admin/edit_inline/collapsed_tabular.html'

    def _media(self):
        media = super(TrackInline, self)._media()
        media.add_js(('%sjs/collapse.min.js'
                      % settings.ADMIN_MEDIA_PREFIX, ))
        return media
    media = property(_media)


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 5

    template = 'admin/edit_inline/collapsed_tabular.html'

    def _media(self):
        media = super(TopicInline, self)._media()
        media.add_js(('%sjs/collapse.min.js'
                      % settings.ADMIN_MEDIA_PREFIX, ))
        return media
    media = property(_media)


class SprintInline(admin.TabularInline):
    model = SummitSprint
    extra = 2

    template = 'admin/edit_inline/collapsed_tabular.html'

    def _media(self):
        media = super(SprintInline, self)._media()
        media.add_js(('%sjs/collapse.min.js'
                      % settings.ADMIN_MEDIA_PREFIX, ))
        return media
    media = property(_media)


class SummitAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'location', 'state')
    search_fields = ('name', 'title', 'location')

    inlines = (TrackInline, TopicInline, SprintInline)
    filter_horizontal = ('schedulers', 'managers')

admin.site.register(Summit, SummitAdmin)


class UsernameUserAdminForm(ModelForm):
    username = forms.CharField()

    class Meta:
        model = User


class UsernameUserAdmin(UserAdmin):
    form = UsernameUserAdminForm

admin.site.unregister(User)
admin.site.register(User, UsernameUserAdmin)
