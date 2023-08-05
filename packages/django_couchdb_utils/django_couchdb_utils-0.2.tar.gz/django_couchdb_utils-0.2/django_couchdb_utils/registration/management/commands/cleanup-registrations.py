"""
A management command which deletes expired accounts (e.g.,
accounts which signed up but never activated) from the database.

Calls ``RegistrationProfile.objects.delete_expired_users()``, which
contains the actual logic for determining which accounts are deleted.

"""

import re
from optparse import make_option

from django.core.management.base import BaseCommand

from ...models import delete_expired_users


RE_YES = re.compile('^[yY]$')
RE_NO  = re.compile('^[nN]?$')

class Command(BaseCommand):
    help = "Delete expired user registrations from the database"

    option_list = BaseCommand.option_list + (
        make_option('--force', action='store_true', dest='force',
            default=False, help="Don't ask but delete all expired users"),
    )


    def handle(self, **options):

        if options.get('force'):
            decide_delete = lambda _: True
        else:
            decide_delete = self.read_input

        users = delete_expired_users()

        user = users.next()

        while True:
            delete = decide_delete(user)

            if delete:
                print 'Deleting user {user} {user_id} (registered {registered}).'.format(
                    user=user, user_id=user._id, registered=user.date_joined)

            user = users.send(delete)


    def read_input(self, user):
        while True:
            answer = raw_input('Deletin user {user} {user_id} (registered {registered})? [y|N] '.format(
                    user=user, user_id=user._id, registered=user.date_joined))

            delete = self.parse_input(answer)
            if delete is not None:
                return delete


    def parse_input(self, inp):
        if RE_YES.match(inp):
            return True

        if RE_NO.match(inp):
            return False

        return None
