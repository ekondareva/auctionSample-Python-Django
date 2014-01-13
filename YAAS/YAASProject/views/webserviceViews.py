__author__ = 'kate'
# Create your views here.
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from decimal import Decimal

from YAASProject.models import *

#offset: auction_id
#return: Auction object with auction_id=offset
class apiauction:
    def __call__(self, request, username, offset):
        self.request = request
        self.offset = offset
        # Look up the user and throw a 404 if it doesn't exist
        self.user =get_object_or_404(User, username=username)

        if not request.method in ["GET"]:
            return HttpResponseNotAllowed(["GET"])
        # Check and store HTTP basic authentication, even for methods that
        # don't require authorization.
        self.authenticate()
        # Call the request method handler
        if request.method=="GET":
            return self.do_GET()

    def authenticate(self):
        # Pull the auth info out of the Authorization: header
        auth_info = self.request.META.get("HTTP_AUTHORIZATION", None)
        print self.request
        print auth_info
        if auth_info and auth_info.startswith("Basic "):
            basic_info = auth_info.split(" ", 1)[1]
            #print basic_info, basic_info.decode("base64")
            u, p = basic_info.decode("base64").split(":")

            if str(self.user) == str(u):
                self.user=u
            # Authenticate against the User database. This will set
            # authenticated_user to None if authentication fails.
            self.authenticated_user = authenticate(username=u, password=p)
        else:
            self.authenticated_user = None

    def forbidden(self):
        response = HttpResponseForbidden()
        response["WWW-Authenticate"] = 'Basic realm="Auction"'
        return response

    def do_GET(self):
        # Check authorization
        if self.user != str(self.authenticated_user):
            print "forbidden"
            return self.forbidden()

        #auctions=get_list_or_404(Auction.objects.all().exclude(status="BAN").order_by('-published_date'))
        auction = get_object_or_404(Auction,  id=self.offset)
        try:
            json = serializers.serialize("json", [auction])
            response = HttpResponse(json, mimetype="application/json")
            response.status_code = 200
        except (ValueError, TypeError, IndexError):
            response = HttpResponse()
            response.status_code = 400
        return response

# we assume that searchstring is a part of the title or empty string
#return: if searchstring is empty then we return the whole list of auctions
#otherwise the list of Auctions containing searchstring in the title
class apisearch:
    def __call__(self, request, username, searchstring):
        self.request = request
        self.searchstring = searchstring
        # Look up the user and throw a 404 if it doesn't exist
        self.user =get_object_or_404(User, username=username)

        if not request.method in ["GET"]:
            return HttpResponseNotAllowed(["GET"])
            # Check and store HTTP basic authentication, even for methods that
        # don't require authorization.
        print "HALLO1"
        self.authenticate()
        # Call the request method handler
        if request.method=="GET":
            return self.do_GET()

    def authenticate(self):
        # Pull the auth info out of the Authorization: header
        auth_info = self.request.META.get("HTTP_AUTHORIZATION", None)
        #print self.request
        print auth_info
        if auth_info and auth_info.startswith("Basic "):
            basic_info = auth_info.split(" ", 1)[1]
            #print basic_info, basic_info.decode("base64")
            u, p = basic_info.decode("base64").split(":")
            #print u, p
            if str(self.user) == str(u):
                self.user=u
            # Authenticate against the User database. This will set
            # authenticated_user to None if authentication fails.
            self.authenticated_user = authenticate(username=u, password=p)
            #print "self.authenticated_user,", self.authenticated_user
            print "HALLO2"
        else:
            self.authenticated_user = None

    def forbidden(self):
        response = HttpResponseForbidden()
        response["WWW-Authenticate"] = 'Basic realm="Auction"'
        return response

    def do_GET(self):
        # Check authorization
        if self.user != str(self.authenticated_user):
            print "forbidden"
            return self.forbidden()

        auctions=get_list_or_404(Auction.objects.filter(title__contains=self.searchstring).exclude(status="BAN").order_by('-published_date'))

        try:
            json = serializers.serialize("json", auctions)
            response = HttpResponse(json, mimetype="application/json")
            response.status_code = 200
        except (ValueError, TypeError, IndexError):
            response = HttpResponse()
            response.status_code = 400
        return response

class apibrowse:
    def __call__(self, request, username):
        self.request = request
        # Look up the user and throw a 404 if it doesn't exist
        self.user =get_object_or_404(User, username=username)

        if not request.method in ["GET"]:
            return HttpResponseNotAllowed(["GET"])
            # Check and store HTTP basic authentication, even for methods that
        # don't require authorization.
        self.authenticate()
        # Call the request method handler
        if request.method=="GET":
            return self.do_GET()

    def authenticate(self):
        # Pull the auth info out of the Authorization: header
        auth_info = self.request.META.get("HTTP_AUTHORIZATION", None)
        #print self.request
        print auth_info
        if auth_info and auth_info.startswith("Basic "):
            basic_info = auth_info.split(" ", 1)[1]
            #print basic_info, basic_info.decode("base64")
            u, p = basic_info.decode("base64").split(":")
            #print u, p
            if str(self.user) == str(u):
                self.user=u
            # Authenticate against the User database. This will set
            # authenticated_user to None if authentication fails.
            self.authenticated_user = authenticate(username=u, password=p)
        else:
            self.authenticated_user = None

    def forbidden(self):
        response = HttpResponseForbidden()
        response["WWW-Authenticate"] = 'Basic realm="Auction"'
        return response

    def do_GET(self):
        # Check authorization
        if self.user != str(self.authenticated_user):
            print "forbidden"
            return self.forbidden()

        auctions=get_list_or_404(Auction.objects.all().exclude(status="BAN").order_by('-published_date'))

        try:
            json = serializers.serialize("json", auctions)
            response = HttpResponse(json, mimetype="application/json")
            response.status_code = 200
        except (ValueError, TypeError, IndexError):
            response = HttpResponse()
            response.status_code = 400
        return response

class apibid:
    def __call__(self, request, username, auctionid, bidprice):
        self.request = request
        self.auctionid = auctionid
        self.bidprice=Decimal(bidprice)

        # Look up the user and throw a 404 if it doesn't exist
        self.user =get_object_or_404(User, username=username)

        if not request.method in ["PUT"]:
            return HttpResponseNotAllowed(["PUT"])
            # Check and store HTTP basic authentication, even for methods that
        # don't require authorization.
        self.authenticate()
        # Call the request method handler
        if request.method=="PUT":
            return self.do_PUT()

    def authenticate(self):
        # Pull the auth info out of the Authorization: header
        auth_info = self.request.META.get("HTTP_AUTHORIZATION", None)
        print self.request
        print auth_info
        if auth_info and auth_info.startswith("Basic "):
            basic_info = auth_info.split(" ", 1)[1]
            #print basic_info, basic_info.decode("base64")
            u, p = basic_info.decode("base64").split(":")
            if str(self.user) == str(u):
                self.user=u
            # Authenticate against the User database. This will set
            # authenticated_user to None if authentication fails.
            self.authenticated_user = authenticate(username=u, password=p)
        else:
            self.authenticated_user = None

    def forbidden(self):
        response = HttpResponseForbidden()
        response["WWW-Authenticate"] = 'Basic realm="Auction"'
        return response

    def do_PUT(self):
        # Check authorization
        if self.user != str(self.authenticated_user):
            return self.forbidden()

        auction = Auction.objects.filter(pk = self.auctionid)
        if len(auction) >0:
            auction=Auction.getByID(self.auctionid)
        else:
            print "auction is not found"
            response = HttpResponse("auction is not found")
            response.status_code = 400
            return response
        try:
            if auction.user==self.authenticated_user:
                print auction.user
                print "you are the author"
                response = HttpResponseForbidden("you are the author")
                return response
            if auction.status!="ACT":
                print auction.status
                print "status is bad"
                response = HttpResponseForbidden("status is bad")
                return response
            bids=Bid.objects.filter(auction_id=auction)
            if len(bids)>0:
                lastbid=Bid.objects.filter(auction_id=auction).latest('bid_date')
                #a bidder cannot bid on an auction that is already wining
                print lastbid.user
                self.authenticated_user
                if lastbid.user==self.authenticated_user:
                    print "you are winning now"
                    response = HttpResponseForbidden("you are winning now")
                    return response
            if (auction.deadline_date-timezone.now()).seconds<=1:
                print "auction has expired, sorry"
                auction.status="DUE"
                auction.save()
                response = HttpResponseForbidden("auction has expired, sorry")
                return response


            if self.bidprice>auction.min_price and self.bidprice>auction.current_price:
                bid=Bid()
                bid.user=self.authenticated_user
                bid.auction_id=auction
                bid.price=self.bidprice
                bid.save()
                dt=auction.deadline_date-bid.bid_date
                if dt.seconds<=5*60:
                    auction.deadline_date = auction.deadline_date + timedelta(seconds=5*60)
                auction.current_price=self.bidprice
                auction.save()

                #the seller is notified by email
                body = "New bid for Auction has been registered!"
                from_email = 'noreply@yaas.com'
                to_email = auction.user.email
                send_mail('New bid', body, from_email, [to_email,], fail_silently=False)
                #all the bidders are notified by email that new bid has been registered
                bidUsers=Bid.objects.filter(auction_id=auction).values('user').distinct()
                for users in bidUsers:
                    thisUser=User.objects.get(pk=users['user'])
                    to_email = thisUser.email
                    send_mail('New bid', body, from_email, [to_email,], fail_silently=False)

                response = HttpResponse("your bid is accepted!")
                response.status_code = 201
                return response
            else:
                print "price should be bigger than any last bids and minimum price"
                return HttpResponseForbidden("price should be bigger than any last bids and minimum price")
        except (ValueError, TypeError, IndexError):
            response = HttpResponse()
            response.status_code = 400
            return response