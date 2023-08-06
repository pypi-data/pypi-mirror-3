#!/usr/bin/python

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from schedule import launchpad
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Set openid identity urls from launchpad"
    option_list = BaseCommand.option_list + (
        make_option("-u", "--user", dest='user',
            help="Supply a user to setup the openid identity url from launchpad."),
    )

    def handle(self, *args, **options):
        username = options['user']

        if not username:
            for user in User.objects.all():
                launchpad.set_user_openid(user, force=True)
        else:
            user = User.objects.get(username=username)
            launchpad.set_user_openid(user, force=True)
