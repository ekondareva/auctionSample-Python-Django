from django.conf.urls import patterns, include, url
from YAASProject.views.auctionViews import *
from YAASProject.views.userAccountViews import *
from django.views.decorators.csrf import csrf_exempt
from YAASProject.views.langViews import *
from YAASProject.views.webserviceViews import *
from YAASProject.views.toolsView import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home),
    url(r'^fi/$', fi),
    url(r'^sv/$', sv),
    url(r'^en/$', en),
    url(r'^signin/$', signIn),
    url(r'^createuser/$', createUser),
    url(r'^edituseraccount/$', editUserAccount),
    url(r'^logout/$', logoutView),
    url(r'^addauction/$', addAuction),
    url(r'^saveauctionconf/$',saveAuctionConf),
    url(r'^editauction/(?P<auction_id>\d+)/$', editAuction),
    url(r'^viewauction/(?P<auction_id>\d+)/$', viewAuction),
    url(r'^bidauction/(?P<auction_id>\d+)/$', bidAuction),
    url(r'^banauction/(?P<auction_id>\d+)/$', banAuction),
    url(r'^searchauction/$', searchAuction),
    url(r'^gentestdata/$', genTestData),

    # Examples:
    # url(r'^$', 'YAAS.views.home', name='home'),
    # url(r'^YAAS/', include('YAAS.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # RESTful Web Services
    #api/v1/katya/auction/1
    (r'^api/v1/(\w+)/auction/(\d+)$', csrf_exempt(apiauction())),
    #api/v1/katya/search/table
    (r'^api/v1/(\w+)/search/(\w+)$', csrf_exempt(apisearch())),
    #api/v1/katya/browse
    (r'^api/v1/(\w+)/browse$', csrf_exempt(apibrowse())),
    #api/v1/katya/1(auctionid)/12(minprice)
    #http://127.0.0.1:8000/api/v1/katya/1/80.00
    (r'^api/v1/(\w+)/(\d+)/(\d+\.\d{2})$', csrf_exempt(apibid())),

)
