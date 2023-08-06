# -*- coding: utf-8 -*-

from launchpadlib.launchpad import Launchpad
from launchpadlib.errors import HTTPError

from django.conf import settings

from django.contrib.auth.models import User

import os
import sys


def is_debug_user(username):
    try:
        if settings.DEBUG and username in settings.DEBUG_USERS:
            return True
    except AttributeError:
        return False
    return False


def lp_login(lp_instance='production'):
    cachedir = os.path.join(settings.PROJECT_PATH, 'lp-cache')
    client_ident = getattr(settings, 'LP_PROJECT_NAME', "The Summit Scheduler")
    try:
        launchpad = Launchpad.login_anonymously(client_ident,
                                                lp_instance, cachedir)
    except:
        try:
            # Support for launchpadlib pre 1.5.4.
            launchpad = Launchpad.login(client_ident, "", "",
                                        lp_instance, cachedir)
        except:
            # Launchpad might be offline.
            return None
    return launchpad


def get_permanent_openid_from_username(username):
    import urllib
    from openid.consumer.discover import OpenIDServiceEndpoint
    url = "https://launchpad.net/~%s" % username
    f = urllib.urlopen(url)
    html = f.read()
    services = OpenIDServiceEndpoint().fromHTML(url, html)
    if services is not None and len(services) > 0:
        return services[0]
    else:
        return None
    # ... or use this line if you want the Ubuntu SSO OpenID:
    # return services[0].local_id.replace('launchpad.net', 'ubuntu.com')


def set_user_openid(user, force=False):
    from django_openid_auth.models import UserOpenID
    openids = UserOpenID.objects.filter(user=user)
    if len(openids) == 0 or force:
        if len(openids) == 0:
            openid_assoc = UserOpenID(user=user)
        else:
            openid_assoc = openids[0]
        openid = get_permanent_openid_from_username(user.username)
        if openid is not None:
            claimed_by = UserOpenID.objects.filter(claimed_id=openid.local_id)
            if bool(claimed_by):
                if force:
                    claimed_by.delete()
                else:
                    return False
            openid_assoc.claimed_id = openid.local_id
            openid_assoc.display_id = openid.local_id
            openid_assoc.save()
            return True
    return False
