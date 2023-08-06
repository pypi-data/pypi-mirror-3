from gevent import monkey #the best thing to do is put this import in manage.py
monkey.patch_all()
from gevent.pool import Group
from django.core.management.base import NoArgsCommand
from twittersync.models import TwitterAccount
from twittersync.helpers import TwitterSyncHelper


class Command(NoArgsCommand):
    help = 'Sync all active Twitter account streams.'

    def twitter_sync_helper(self, account):
        return TwitterSyncHelper(account).sync_twitter_account()

    def handle_noargs(self, **options):
        group = Group()
        accounts = TwitterAccount.active.all()
        group.imap_unordered(self.twitter_sync_helper, accounts)
        

    
