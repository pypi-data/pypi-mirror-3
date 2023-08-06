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

from django.contrib import admin

from summit.sponsor.models import (Sponsorship, SponsorshipScore,
    NonLaunchpadSponsorship, NonLaunchpadSponsorshipScore,
    SponsorshipSuggestion, SponsorshipSuggestionScore)

__all__ = (
)


class SponsorshipScoreInline(admin.TabularInline):
    model = SponsorshipScore


class NonLaunchpadSponsorshipScoreInline(admin.TabularInline):
    model = NonLaunchpadSponsorshipScore


class SponsorshipSuggestionScoreInline(admin.TabularInline):
    model = SponsorshipSuggestionScore


class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ('summit', 'user')
    list_display_links = ('user', )
    list_filter = ('summit', 'would_crew', 'needs_travel',
        'needs_accomodation')
    fieldsets = (
        (None, {
            'fields': ('user', 'summit', 'location', 'country', 'about'),
        }),
        ("Further details", {
            'fields': ('needs_travel', 'needs_accomodation', 'would_crew',
                'diet', 'further_info', 'video_agreement'),
        }),
    )

    inlines = (SponsorshipScoreInline, )
admin.site.register(Sponsorship, SponsorshipAdmin)


class NonLaunchpadSponsorshipAdmin(admin.ModelAdmin):
    list_display = ('summit', 'name', 'company', 'requested_by')
    list_display_links = ('name', )
    list_filter = ('summit', 'would_crew', 'needs_travel',
        'needs_accomodation')
    fieldsets = (
        (None, {
            'fields': ('requested_by', 'summit', 'name', 'email', 'company',
                'about'),
        }),
        ("Further details", {
            'fields': (
                'location', 'country', 'needs_travel', 'needs_accomodation',
                'would_crew', 'diet', 'further_info'),
        }),
    )

    inlines = (NonLaunchpadSponsorshipScoreInline, )
admin.site.register(NonLaunchpadSponsorship, NonLaunchpadSponsorshipAdmin)


class SponsorshipSuggestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'launchpad_name', 'summit', 'suggested_by')
    list_display_links = ('name', )
    list_filter = ('summit', 'would_crew', 'needs_travel',
        'needs_accomodation')
    fieldsets = (
        (None, {
            'fields': ('suggested_by', 'summit', 'name', 'launchpad_name',
                'about'),
        }),
        ("Further details", {
            'fields': ('location', 'country', 'needs_travel',
            'needs_accomodation', 'would_crew', 'diet', 'further_info'),
        }),
    )

    inlines = (SponsorshipSuggestionScoreInline, )
admin.site.register(SponsorshipSuggestion, SponsorshipSuggestionAdmin)
