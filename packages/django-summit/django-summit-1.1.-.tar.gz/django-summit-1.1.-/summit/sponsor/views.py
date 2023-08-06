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
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from summit.schedule.models import Summit
from summit.sponsor.models import (Sponsorship, SponsorshipSuggestion,
    NonLaunchpadSponsorship)

from summit.sponsor.forms import (SponsorshipWizard, SponsorshipForm1,
                                  SponsorshipForm3, SponsorshipSuggestionForm,
                                  SponsorshipSuggestionWizard,
                                  NonLaunchpadSponsorshipForm,
                                  NonLaunchpadSponsorshipWizard,
                                  SponsorshipScoreForm)

__all__ = (
    'sponsorship',
    'done',
    'review_list',
    'review',
    'nonlaunchpad_review',
    'export',
)


@login_required
def sponsorship(request, summit_name):
    summit = get_object_or_404(Summit, name=summit_name)
    topics = summit.topic_set.order_by('name')


    if len(summit.sponsorship_set.filter(user__id=request.user.id)):
        return render_to_response("sponsor/existing.html",
                                  {'summit': summit},
                                  context_instance=RequestContext(request))

    wizard = SponsorshipWizard([SponsorshipForm1, SponsorshipForm3])
    wizard.summit = summit
    wizard.extra_context = {'summit': wizard.summit}
    return wizard(request)


@login_required
def suggestsponsorship(request, summit_name):
    summit = get_object_or_404(Summit, name=summit_name)
    topics = summit.topic_set.order_by('name')

    wizard = SponsorshipSuggestionWizard(
        [SponsorshipSuggestionForm, ])
    wizard.summit = summit
    wizard.extra_context = {'summit': wizard.summit}
    return wizard(request)


@permission_required('sponsor.add_sponsorshipscore')
def nonlaunchpadsponsorship(request, summit_name):
    summit = get_object_or_404(Summit, name=summit_name)
    topics = summit.topic_set.order_by('name')

    wizard = NonLaunchpadSponsorshipWizard(
        [NonLaunchpadSponsorshipForm, ])
    wizard.summit = summit
    wizard.extra_context = {'summit': wizard.summit}
    return wizard(request)


def done(request, summit_name):
    summit = get_object_or_404(Summit, name=summit_name)

    return render_to_response("sponsor/done.html",
                              {'summit': summit},
                              context_instance=RequestContext(request))


@permission_required('sponsor.add_sponsorshipscore')
def suggestiondone(request, summit_name):
    summit = get_object_or_404(Summit, name=summit_name)

    return render_to_response("sponsor/suggestdone.html",
                              {'summit': summit},
                              context_instance=RequestContext(request))


@permission_required('sponsor.add_sponsorshipscore')
def nonlaunchpaddone(request, summit_name):
    summit = get_object_or_404(Summit, name=summit_name)

    return render_to_response("sponsor/nonlaunchpaddone.html",
                              {'summit': summit},
                              context_instance=RequestContext(request))


@permission_required('sponsor.add_sponsorshipscore')
def review_list(request, summit_name):
    summit = get_object_or_404(Summit, name=summit_name)
    sponsorships = sorted(summit.sponsorship_set.all(),
                          key=lambda x: (x.numscores > 0 and -1 or 0,
                                         -x.score, x.user.username, ))

    suggestedsponsorships = sorted(summit.sponsorshipsuggestion_set.all(),
                          key=lambda x: (x.numscores > 0 and -1 or 0,
                                         -x.score, x.suggested_by.username, ))

    nonlaunchpadsponsorships = sorted(summit.nonlaunchpadsponsorship_set.all(),
                          key=lambda x: (x.numscores > 0 and -1 or 0,
                                         -x.score, x.requested_by.username, ))


    return render_to_response("sponsor/review-index.html",
                              {'summit': summit,
                               'sponsorships': sponsorships,
                               'suggestedsponsorships': suggestedsponsorships,
                               'nonlaunchpadsponsorships':
                                   nonlaunchpadsponsorships},
                              context_instance=RequestContext(request))


@permission_required('sponsor.add_sponsorshipscore')
def review(request, summit_name, sponsorship_id):
    sponsorship = get_object_or_404(Sponsorship, id=sponsorship_id)
    scores = sponsorship.sponsorshipscore_set.exclude()
    try:
        score = sponsorship.sponsorshipscore_set.get(user=request.user)
    except ObjectDoesNotExist:
        score = None

    if request.POST:
        if score is None:
            score = sponsorship.sponsorshipscore_set.create(user=request.user,
                                                            score=0,
                                                            comment="")

        form = SponsorshipScoreForm(request.POST, instance=score)
        form.save()

        return HttpResponseRedirect(
            '/%s/sponsorship/review' % sponsorship.summit.name)

    else:
        form = SponsorshipScoreForm(instance=score)

        return render_to_response("sponsor/review.html",
                                  {'sponsorship': sponsorship,
                                   'score': score,
                                   'scores': scores,
                                   'form': form},
                                  context_instance=RequestContext(request))


@permission_required('sponsor.add_sponsorshipscore')
def suggestion_review(request, summit_name, sponsorship_id):
    sponsorship = get_object_or_404(SponsorshipSuggestion, id=sponsorship_id)
    scores = sponsorship.sponsorshipsuggestionscore_set.exclude()
    try:
        score = sponsorship.sponsorshipsuggestionscore_set.get(
            user=request.user)
    except ObjectDoesNotExist:
        score = None

    if request.POST:
        if score is None:
            score = sponsorship.sponsorshipsuggestionscore_set.create(
                user=request.user,
                score=0,
                comment="")

        form = SponsorshipScoreForm(request.POST, instance=score)
        form.save()

        return HttpResponseRedirect(
            '/%s/sponsorship/review' % sponsorship.summit.name)

    else:
        form = SponsorshipScoreForm(instance=score)

        return render_to_response("sponsor/suggestionreview.html",
                                  {'sponsorship': sponsorship,
                                   'score': score,
                                   'scores': scores,
                                   'form': form},
                                  context_instance=RequestContext(request))


@permission_required('sponsor.add_sponsorshipscore')
def nonlaunchpad_review(request, summit_name, sponsorship_id):
    sponsorship = get_object_or_404(NonLaunchpadSponsorship, id=sponsorship_id)
    scores = sponsorship.nonlaunchpadsponsorshipscore_set.exclude()
    try:
        score = sponsorship.nonlaunchpadsponsorshipscore_set.get(
            user=request.user)
    except ObjectDoesNotExist:
        score = None

    if request.POST:
        if score is None:
            score = sponsorship.nonlaunchpadsponsorshipscore_set.create(
                user=request.user,
                score=0,
                comment="")

        form = SponsorshipScoreForm(request.POST, instance=score)
        form.save()

        return HttpResponseRedirect(
            '/%s/sponsorship/review' % sponsorship.summit.name)

    else:
        form = SponsorshipScoreForm(instance=score)

        return render_to_response("sponsor/nonlaunchpadreview.html",
                                  {'sponsorship': sponsorship,
                                   'score': score,
                                   'scores': scores,
                                   'form': form},
                                  context_instance=RequestContext(request))


@permission_required('sponsor.add_sponsorshipscore')
def export(request, summit_name):
    summit = get_object_or_404(Summit, name=summit_name)

    sponsorships = sorted([s for s in summit.sponsorship_set.all()
                           if s.numscores > 0 and s.score >= 0],
                          key=lambda x: (-x.score, x.user.username))

    csv = '"Score","Name","E-Mail","Location","Country","Travel","Accomodation","Would Crew","Diet"\n'

    for sponsorship in sponsorships:
        csv += '%d,"%s","%s","%s","%s","%s","%s","%s","%s"\n' \
            % (sponsorship.score,
               sponsorship.user.get_full_name(),
               sponsorship.user.email,
               sponsorship.location,
               sponsorship.country,
               sponsorship.needs_travel and "Y" or "N",
               sponsorship.needs_accomodation and "Y" or "N",
               sponsorship.would_crew and "Y" or "N",
               sponsorship.diet)

    return HttpResponse(csv, mimetype='text/csv')
