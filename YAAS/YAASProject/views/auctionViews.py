# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseNotFound, Http404, HttpResponseNotAllowed,HttpResponseForbidden
from django.contrib.sessions.models import Session
from datetime import datetime
from django.utils import timezone
from django.template.loader import get_template
from django.contrib import messages
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.mail import send_mail
from django.utils import translation
from django.utils.translation import ugettext as _

import re
from YAASProject.models import *
from YAASProject.forms import *

def resolveAuction():
    auctions = Auction.objects.all().exclude(status="BAN").exclude(status="ADJ").order_by('-published_date')
    for a in auctions:
        if a.deadline_date<=timezone.now():
            #the wining bid is the bid with the largest offer
            bids=Bid.objects.filter(auction_id=a)
            if len(bids)>0:
                lastbid=Bid.objects.filter(auction_id=a).latest('bid_date')
                a.winner_bid=lastbid.id
            a.status="ADJ"
            a.save()
            #all the bidders and the seller are notified by email that the auction has been resolved
            #the seller is notified by email that auction has been resolved
            body = "Auction has been resolved!"
            from_email = 'noreply@yaas.com'
            to_email = a.user.email
            send_mail('Auction Resolved', body, from_email, [to_email,], fail_silently=False)
            #all the bidders are notified by email that the auction has been resolved
            bidsUsers=Bid.objects.filter(auction_id=a).values('user').distinct()
            for users in bidsUsers:
                thisUser=User.objects.get(pk=users['user'])
                to_email = thisUser.email
                send_mail('Auction Resolved', body, from_email, [to_email,], fail_silently=False)
    return 0

def home(request):
    resolveAuction()

    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    auctions = Auction.objects.all().exclude(status="BAN").order_by('-published_date')
    mp = map(None, auctions)
    #if (request.session.has_key("loggedinUser")==False):
    #    request.session["loggedinUser"]=0
    return render_to_response('index.html',
        {'values':mp
         #'loggedinUser':request.session["loggedinUser"]
        },
        context_instance = RequestContext(request))

@login_required
def addAuction(request):
    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    if request.method=="POST":
        form = createAuction(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            auction_title = cd['title']
            auction_description = cd['description']
            auction_minprice=cd['minprice']
            #check input!
            #if all input is correct then...
            #if auction_title=="":
            #    return render_to_response('addauction.html', {'form' : form, "error" : "Title cannot be empty" },
            #        context_instance=RequestContext(request))
            #if auction_description=="":
            #    return render_to_response('addauction.html', {'form' : form, "error" : "Description cannot be empty" },
            #        context_instance=RequestContext(request))
            #if auction_minprice<=0:
            #    return render_to_response('addauction.html',
            #        {'form' : form, "error" : "Minimum price should be more than 0" },
            #        context_instance=RequestContext(request))
            form = confAuction()
            return render_to_response('addauctionconf.html',
                {'form' : form,
                 "a_title" : auction_title,
                 "a_description" : auction_description,
                 "a_minprice": auction_minprice
                 #'loggedinUser':request.session["loggedinUser"]
                },
                context_instance=RequestContext(request))
        else:
            return render_to_response('addauction.html',
                {'form' : form,
                 #'loggedinUser':request.session["loggedinUser"],
                 "error" : "Not valid data" },
                context_instance=RequestContext(request))
    else:
        form =  createAuction()
        return render_to_response("addauction.html",
            { 'form':form
             #'loggedinUser':request.session["loggedinUser"]
            },
            context_instance=RequestContext(request))

@login_required
def saveAuctionConf(request):
    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    option = request.POST.get('option', '')
    if option == 'Yes':
        auction=Auction()
        auction.title = request.POST["a_title"].strip() #request.POST.get('a_title', '')
        auction.description = request.POST["a_description"].strip() #request.POST.get('a_description', '')
        auction.user=request.user
        auction.min_price=request.POST["a_minprice"].strip() #request.POST.get('a_minprice', '')
        auction.current_price=request.POST["a_minprice"].strip()
        #next are default_values
        #auction.published_date=datetime.datetime.now()
        #auction.deadline_date=auction.published_date +72 hours
        #auction.status="ACT"
        auction.save()

        body = "New Auction has been successfully created!"
        from_email = 'noreply@yaas.com'
        to_email = request.user.email
        send_mail('New Auction Created', body, from_email, [to_email,], fail_silently=False)
        msg = "New auction has been saved"
        return render_to_response('addauctiondone.html',
            {'msg' : msg
                #, 'loggedinUser':request.session["loggedinUser"]
            },
            context_instance=RequestContext(request))
    else:
        error = "Auction was not saved"
        form = createAuction()
        return render_to_response("addauction.html",
            { 'form':form,
              'error' : error
              #'loggedinUser':request.session["loggedinUser"]
            },
            context_instance=RequestContext(request))

@login_required
def editAuction(request, auction_id):
    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    auction = Auction.objects.filter(pk = auction_id)
    if len(auction) >0:
        auction=Auction.getByID(auction_id)
        #if auction.status!="BAN":
        if auction.status=="ACT":
            if auction.user==request.user:
                if request.method=="POST" and request.POST.has_key('description'):
                    description = request.POST["description"].strip()
                    if description!="":
                        auction.description = description
                        auction.version=auction.version+1
                        auction.save()
                        messages.success(request, 'The description of the auction has been successfully updated.')
                        return HttpResponseRedirect('/')
                    else:
                        return render_to_response("editauction.html",
                            {'id':auction_id, 'title':auction.title, 'description':auction.description,
                             'error':'Description cannot be empty'
                             #'loggedinUser':request.session["loggedinUser"]
                            },
                            context_instance=RequestContext(request))
                else:
                    return render_to_response("editauction.html",
                        {'id':auction_id, 'title':auction.title, 'description':auction.description
                         #'loggedinUser':request.session["loggedinUser"]
                        },
                        context_instance=RequestContext(request))
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseNotFound('<h1>Item does not exist</h1>')

def viewAuction(request, auction_id):
    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    auction=Auction.objects.filter(pk = auction_id)
    if len(auction) > 0:
        auction=Auction.getByID(auction_id)
        return render_to_response("viewauction.html",
            {'pk':auction_id, 'title':auction.title, 'description':auction.description,
             'minprice':auction.min_price, 'enddate':auction.deadline_date,
             'seller':auction.user, 'status':auction.status
             #'loggedinUser':request.session["loggedinUser"]
            },
            context_instance=RequestContext(request))
    else:
        return HttpResponseNotFound('<h1>Item does not exist</h1>')

def searchAuction(request):
    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    if request.method=="POST" and request.POST.has_key('searchvalue'):
        if request.POST["searchvalue"].strip()=="":
            #auctions = Auction.objects.all().order_by('-published_date')
            auctions = Auction.objects.all().exclude(status="BAN").order_by('-published_date')
        else:
            auctions = Auction.objects.filter(title__contains=request.POST["searchvalue"].strip()).exclude(status="BAN").order_by('-published_date')
        mp = map(None, auctions)
        #if (request.session.has_key("loggedinUser")==False):
        #    request.session["loggedinUser"]=0
        return render_to_response('index.html',
            {'values':mp
             #'loggedinUser':request.session["loggedinUser"]
            },
            context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect('/')

@login_required
def bidAuction(request, auction_id):
    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    auction = Auction.objects.filter(pk = auction_id)
    if len(auction) >0:
        auction=Auction.getByID(auction_id)
        bids=Bid.objects.filter(auction_id=auction)
        if len(bids)==0:
            curprice=0
        else:
            curprice=auction.current_price
        #seller cannot big on own auctions
        if auction.user==request.user:
            return HttpResponseForbidden()
        #it is not possible to bid on a banned auction
        #if auction.status=="BAN":
        if auction.status!="ACT":
            return HttpResponseForbidden()
        #if the auction is resolved, we cannot bid anymore
        #if auction.winner_bid!=0:
        #    return HttpResponseForbidden()
        if request.method=="POST" and request.POST.has_key("edited_version"):
            form=bidForm(request.POST)
            if form.is_valid():
                bf=form.cleaned_data
                bidprice=bf['price']
                edited_version = int(request.POST["edited_version"])
                if edited_version == auction.version:
                    bids=Bid.objects.filter(auction_id=auction)
                    if len(bids)>0:
                        lastbid=Bid.objects.filter(auction_id=auction).latest('bid_date')
                        #a bidder cannot bid on an auction that is already wining
                        if lastbid.user==request.user:
                            return HttpResponseForbidden()

                    #not possible to bid for an old auction
                    if (auction.deadline_date-timezone.now()).seconds<=1:
                        auction.status="DUE"
                        auction.save()
                        messages.success(request, 'Sorry, the auction is already expired')
                        return HttpResponseRedirect('/')
                    #a new bid should be greater than any previous bid and the minimum price
                    if bidprice>auction.min_price and bidprice>auction.current_price:
                        bid=Bid()
                        bid.user=request.user
                        bid.auction_id=auction
                        bid.price=bidprice
                        bid.save()

                        dt=auction.deadline_date-bid.bid_date
                        if dt.seconds<=5*60:
                            auction.deadline_date= auction.deadline_date + timedelta(seconds=5*60)
                        auction.current_price=bidprice
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
                        messages.success(request, 'Bid was successfully done for auction')
                        return HttpResponseRedirect('/')
                    else:
                        return render_to_response("bidauction.html",
                            { 'form':form,
                              'id':auction_id, 'title':auction.title, 'description':auction.description,
                              'minprice':auction.min_price,'curprice':curprice,
                              'enddate':auction.deadline_date,
                              'edited_version': auction.version,
                              'error':'A new bid should be greater than last bid and the minimum price'
                              #'loggedinUser':request.session["loggedinUser"]
                            },
                            context_instance=RequestContext(request))
                else:
                    return render_to_response("bidauction.html",
                        { 'form':form,
                          'id':auction_id, 'title':auction.title, 'description':auction.description,
                          'minprice':auction.min_price,'curprice':curprice,
                          'enddate':auction.deadline_date,
                          'edited_version': auction.version,
                          'error':'A description of auction has been changed recently'
                          #'loggedinUser':request.session["loggedinUser"]
                        },
                        context_instance=RequestContext(request))
            else:
                return render_to_response("bidauction.html",
                    { 'form':form,
                      'id':auction_id, 'title':auction.title, 'description':auction.description,
                      'minprice':auction.min_price,'curprice':curprice,
                      'enddate':auction.deadline_date,
                      'edited_version': auction.version,
                      'error':'Bid cannot be less than 0.01'
                      #'loggedinUser':request.session["loggedinUser"]
                    },
                    context_instance=RequestContext(request))
        else:
            form=bidForm()
            return render_to_response("bidauction.html",
                { 'form':form,
                  'id':auction_id, 'title':auction.title, 'description':auction.description,
                  'minprice':auction.min_price,'curprice':curprice,
                  'enddate':auction.deadline_date,
                  'edited_version': auction.version
                  #'loggedinUser':request.session["loggedinUser"]
                },
                context_instance=RequestContext(request))
    else:
        return HttpResponseNotFound('<h1>Item does not exist</h1>')

@login_required
def banAuction(request, auction_id):
    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    #only administrator user can ban an active auction
    if request.user.is_superuser:
        auction = Auction.objects.filter(pk = auction_id)
        if len(auction) >0:
            auction=Auction.getByID(auction_id)
            auction.status="BAN"
            auction.save()
            #the seller is notified by email that auction has been banned
            body = "Auction has been banned!"
            from_email = 'noreply@yaas.com'
            to_email = auction.user.email
            send_mail('Auction Banned', body, from_email, [to_email,], fail_silently=False)
            #all the bidders are notified by email that the auction has been banned
            bidsUsers=Bid.objects.filter(auction_id=auction).values('user').distinct()
            for users in bidsUsers:
                thisUser=User.objects.get(pk=users['user'])
                to_email = thisUser.email
                send_mail('Auction Banned', body, from_email, [to_email,], fail_silently=False)
            messages.success(request, 'Auction was successfully banned')
            return HttpResponseRedirect('/')
        else:
            return HttpResponseNotFound('<h1>Item does not exist</h1>')
    else:
        return HttpResponseForbidden()
