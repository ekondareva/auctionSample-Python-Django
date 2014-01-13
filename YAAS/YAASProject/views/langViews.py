__author__ = 'kate'
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseNotFound, Http404, HttpResponseNotAllowed,HttpResponseForbidden
from django.utils import translation
from django.utils.translation import ugettext as _

from YAASProject.models import *

def fi(request):
    nextTo = request.POST.get('cururlfi', '')
    try:
        request.session["lang"] = "fi"
        translation.activate(request.session["lang"])

        if request.user.is_authenticated():
            up=UserProfile.objects.get(user=request.user)
            up.lang="FI"
            up.save()

    except KeyError:
        request.session["lang"] = "en"
        translation.activate(request.session["lang"])

        if request.user.is_authenticated():
            up=UserProfile.objects.get(user=request.user)
            up.lang="EN"
            up.save()

    if len(nextTo) != 0:
        return HttpResponseRedirect(nextTo)
    else:
        return HttpResponseRedirect('/')

def sv(request):
    nextTo = request.POST.get('cururlsv', '')
    try:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])
        if request.user.is_authenticated():
            up=UserProfile.objects.get(user=request.user)
            up.lang="SV"
            up.save()
    except KeyError:
        request.session["lang"] = "en"
        translation.activate(request.session["lang"])
        if request.user.is_authenticated():
            up=UserProfile.objects.get(user=request.user)
            up.lang="EN"
            up.save()
    if len(nextTo) != 0:
        return HttpResponseRedirect(nextTo)
    else:
        return HttpResponseRedirect('/')

def en(request):
    nextTo = request.POST.get('cururlen', '')

    request.session["lang"] = "en"
    translation.activate(request.session["lang"])
    if request.user.is_authenticated():
        up=UserProfile.objects.get(user=request.user)
        up.lang="EN"
        up.save()

    if len(nextTo) != 0:
        return HttpResponseRedirect(nextTo)
    else:
        return HttpResponseRedirect('/')

