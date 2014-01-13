__author__ = 'kate'
from django.core.management.base import BaseCommand, CommandError
from YAASProject.models import Auction, Bid

class Command(BaseCommand):
    args = '<auction_id auction_id ...>'
    help = 'Resolves the specified auction'

    def handle(self, *args, **options):
        self.stdout.write('Successfully resolved auctions')
        #for auction_id in args:
        #    try:
        #        auction = Auction.objects.filter(pk = auction_id)
        #    except Auction.DoesNotExist:
        #        raise CommandError('Auction "%s" does not exist' % auction_id)
            #poll.opened = False
            #poll.save()
        #    self.stdout.write('Successfully resolved auction "%s"' % auction_id)