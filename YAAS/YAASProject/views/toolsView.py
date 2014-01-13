__author__ = 'kate'
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseNotFound, Http404, HttpResponseNotAllowed,HttpResponseForbidden
from django.contrib.auth import authenticate

from YAASProject.models import *

def genTestData(request):
    lastuser=User.objects.latest('id')
    s=lastuser.id
    print s
    auctions=Auction.objects.all()
    if len(auctions)>0:
        lastauction=Auction.objects.latest('id')
        a=lastauction.id
    else:
        a=0


    for i in range(60):
        print 'john%s' % (i+s+1)
        user=User.objects.create_user('john%s' % (i+s+1), 'smith%s@mail.com'% str(i+s+1), 'test')
        up=UserProfile()
        up.user=user
        up.save()
        auction=Auction()
        auction.title = 'title %s' % str(i+a+1)
        auction.description = 'descr %s' % str(i+a+1)
        auction.user=user
        auction.min_price=i
        auction.current_price=i
        auction.save()

    for i in range (10):
        auction=Auction.getByID(a+i+1)
        user=User.objects.get(pk=s+i+2)
        bid=Bid()
        bid.user=user
        bid.auction_id=auction
        bid.price=10+i
        bid.save()
        auction.current_price=10+i
        auction.save()

    auction=Auction.getByID(10)
    auction.status="BAN"
    auction.save()
    auction=Auction.getByID(11)
    auction.status="ADJ"
    auction.save()

    return HttpResponseRedirect('/')