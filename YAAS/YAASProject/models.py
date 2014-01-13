from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

# Create your models here.
LANGUAGES_TRANS = (
    ('EN', 'English'),
    ('SE', 'Swedish'),
    ('FI', 'Finnish'),
    )

#lifecycle of the auction is represented by these statuses
AUCTION_STATUS = (
    ('ACT', 'Active'),
    ('BAN', 'Banned'),
    ('DUE', 'Due'),
    ('ADJ', 'Adjudicated'),
    )

class UserProfile (models.Model):
    user = models.OneToOneField(User)
    lang = models.CharField(max_length=2, choices=LANGUAGES_TRANS, default="EN")

class Auction(models.Model):
    #user - who create the auction
    user = models.ForeignKey(User)
    title=models.CharField(max_length=50)
    description=models.TextField()
    min_price = models.DecimalField(decimal_places=2, max_digits=19)
    current_price = models.DecimalField(decimal_places=2, max_digits=19)
    status = models.CharField(max_length=3, choices=AUCTION_STATUS, default="ACT")
    #winner_bid = which bid wins in this auction after the end date
    winner_bid=models.BigIntegerField(null=True, default=0)
    published_date = models.DateTimeField(auto_now_add=True)
    #deadline: user specifies it. Min is 72 hours from the creation
    deadline_date = models.DateTimeField(default=datetime.now()+timedelta(hours=72))
    version = models.IntegerField(default=0)

    @classmethod
    def getByID(cls, auctionId):
        return cls.objects.get(id = auctionId)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title','-published_date']

class Bid(models.Model):
    auction_id=models.ForeignKey(Auction)
    #user - who posts the bid
    user = models.ForeignKey(User)
    price=models.DecimalField(decimal_places=2, max_digits=19)
    bid_date=models.DateTimeField(auto_now_add=True)