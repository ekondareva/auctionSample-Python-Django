__author__ = 'kate'

# Create your views here.
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseNotFound, Http404
from django.contrib.sessions.models import Session
from datetime import datetime
from django.template.loader import get_template
from django.contrib import messages
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import translation
from django.utils.translation import ugettext as _

from YAASProject.models import *
from YAASProject.forms import *

def signIn(request):
    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    if not request.user.is_authenticated():
        if request.method == 'POST':
            username=request.POST['login']
            password=request.POST['password']
            nextTo = request.GET.get('next', '')            #retrieving the url to redirect after successful login
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    #print("User is valid, active and authenticated")
                    auth.login(request, user)
                    #request.session["loggedinUser"]=1
                    request.session["userLogin"]=username

                    up = UserProfile.objects.filter(user = user)
                    if len(up)==0:
                        up=UserProfile()
                        up.user=user
                        up.lang="EN"
                        up.save()
                    else:
                        up=UserProfile.objects.get(user=user)

                    request.session["lang"]=up.lang
                    try:
                        translation.activate(request.session["lang"])
                    except KeyError:
                        request.session["lang"] = "sv"
                        translation.activate(request.session["lang"])

                    if len(nextTo) != 0:
                        return HttpResponseRedirect(nextTo)
                    else:
                        return HttpResponseRedirect('/')
                else:
                    #print("The password is valid, but the account has been disabled!")
                    error = 'The password is valid, but the account has been disabled!'
                    return render_to_response('signin.html', {'error':error},context_instance = RequestContext(request))
            else:
                error = 'User login or password is incorrect. Please, try again.'
                return render_to_response('signin.html', {'error':error},context_instance = RequestContext(request))
        return render_to_response('signin.html', {}, context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect('/')

def createUser(request):
    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    if not request.user.is_authenticated():
        if request.method == 'POST':
            form =UserRegisterForm(request.POST)
            if form.is_valid():
                new_user = form.save()
                up=UserProfile()
                up.user=new_user
                up.save()
                messages.success(request, 'New User is created. Please Login')
                return HttpResponseRedirect('/')
        else:
            form =UserRegisterForm()
        return render_to_response('createuser.html', {'form': form},
            context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect('/')

@login_required
def logoutView(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s'%request.path)
    else:
        auth.logout(request)
        #request.session["loggedinUser"]=0
        request.session["userLogin"]=""
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])
        return HttpResponseRedirect('/')

@login_required
def editUserAccount(request):
    try:
        if not request.session["lang"]:
            request.session["lang"] = "sv"
            translation.activate(request.session["lang"])
        else:
            translation.activate(request.session["lang"])
    except KeyError:
        request.session["lang"] = "sv"
        translation.activate(request.session["lang"])

    if request.method == 'POST':
        form = EditUserAccountForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            thisUser=User.objects.get(username=request.user)
            edit_useraccount_form=form.cleaned_data

            newpassword=edit_useraccount_form['newpassword']
            confirmation=edit_useraccount_form['confirmation']
            if (newpassword!="" and newpassword!=confirmation):
                error = 'New Password and Confirmation does not match'
                return render_to_response('edituseraccount.html',
                    {'form': form,
                     #'loggedinUser':request.session["loggedinUser"],
                     'error':error
                    },
                    context_instance = RequestContext(request))

            if (edit_useraccount_form['email']==""):
                error = 'Email cannot be empty'
                return render_to_response('edituseraccount.html',
                    {'form': form,
                     #'loggedinUser':request.session["loggedinUser"],
                     'error':error
                    },
                    context_instance = RequestContext(request))

            if (newpassword!=""):
                thisUser.set_password(newpassword)
            if (edit_useraccount_form['email']!=""):
                thisUser.email=edit_useraccount_form['email']
            thisUser.first_name = edit_useraccount_form['firstname']
            thisUser.last_name = edit_useraccount_form['lastname']
            thisUser.save()
            messages.success(request, 'User Account was successfully updated')
            return HttpResponseRedirect('/')

        else:
            form = EditUserAccountForm(request.POST)
            error = 'Incorrect data'
            return render_to_response('edituseraccount.html',
                {'form': form,
                 #'loggedinUser':request.session["loggedinUser"],
                 'error':error
                 },
                context_instance = RequestContext(request))
    else:
        thisUser=User.objects.get(username=request.user)
        form = EditUserAccountForm(initial={'firstname': thisUser.first_name,
                                            'lastname': thisUser.last_name,
                                            'email': thisUser.email
                                            })
        return render_to_response('edituseraccount.html',
            {'form': form
             #'loggedinUser':request.session["loggedinUser"]
            },
            context_instance = RequestContext(request))


