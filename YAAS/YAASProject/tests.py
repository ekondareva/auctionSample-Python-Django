"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from datetime import datetime
from django.core import mail

from YAASProject.models import *

class SimpleTest(TestCase):
    fixtures = ['initial_data.json']

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def testAddAuctionPost(self):
        resp=self.client.get('/addauction/')
        self.failUnlessEqual(resp.status_code, 302)
        self.assertRedirects(resp,'/signin/?next=/addauction/')

        login=self.client.login(username='john2', password='test')
        self.failUnless(login, True)
        self.assertEqual(login, True)

        resp= self.client.get('/addauction/')
        self.failUnlessEqual(resp.status_code, 200)

        #check that title is not null
        resp = self.client.post('/addauction/',
            {'title':'',
             'description':'my description',
             'minprice':10.40
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'addauction.html')
        self.assertContains(resp,"Not valid data")

        #check that descruption is not null
        resp = self.client.post('/addauction/',
            {'title':'my title',
             'description':'',
             'minprice':10.40
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'addauction.html')
        self.assertContains(resp,"Not valid data")

        #check that price is not null
        resp = self.client.post('/addauction/',
            {'title':'my title',
             'description':'my description',
             'minprice':0
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'addauction.html')
        self.assertContains(resp,"Not valid data")

        #check that price is decimal number with 2 decimal places
        resp = self.client.post('/addauction/',
            {'title':'my title',
             'description':'my description',
             'minprice':1.2343
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'addauction.html')
        self.assertContains(resp,"Not valid data")

        #check that price is never less than 0
        resp = self.client.post('/addauction/',
            {'title':'my title',
             'description':'my description',
             'minprice':-100
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'addauction.html')
        self.assertContains(resp,"Not valid data")

        #check the proper case
        resp = self.client.post('/addauction/',
            {'title':'my title',
             'description':'my description',
             'minprice':10.40
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'addauctionconf.html')

    def testAddAuctionConfPost(self):
        resp = self.client.post('/saveauctionconf/',
            {'a_title':'my title',
             'a_description':'my description',
             'a_minprice':10.40,
             'option':'Yes'})

        self.failUnlessEqual(resp.status_code, 302)
        self.assertRedirects(resp,'/signin/?next=/saveauctionconf/')

        login=self.client.login(username='john2', password='test')
        self.failUnless(login, True)
        self.assertEqual(login, True)

        #test when user choose No
        resp = self.client.post('/saveauctionconf/',
            {'a_title':'my title',
             'a_description':'my description',
             'a_minprice':10.40,
             'option':'No'})
        self.assertEqual(resp.status_code,200)
        self.assertContains(resp,"Auction was not saved")
        self.assertTemplateUsed(resp,'addauction.html')

        #test the saving of auction
        resp = self.client.post('/saveauctionconf/',
            {'a_title':'my title',
             'a_description':'my description',
             'a_minprice':10.40,
             'option':'Yes'})

        #test email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'noreply@yaas.com')
        self.assertEqual(mail.outbox[0].to[0], 'smith2@mail.com')
        self.assertEqual(mail.outbox[0].subject,'New Auction Created')

        self.assertEqual(resp.status_code,200)
        self.assertTemplateUsed(resp,'addauctiondone.html')

    def testBidPost(self):
        resp=self.client.get('/bidauction/1/')
        self.failUnlessEqual(resp.status_code, 302)
        self.assertRedirects(resp,'/signin/?next=/bidauction/1/')

        login=self.client.login(username='john2', password='test')
        self.failUnless(login, True)
        self.assertEqual(login, True)

        #if auction does not exist
        resp= self.client.get('/bidauction/1000/')
        self.failUnlessEqual(resp.status_code, 404)

        #if the author tries to bid
        resp= self.client.get('/bidauction/1/')
        self.failUnlessEqual(resp.status_code, 403)

        #check status of auction
        resp= self.client.get('/bidauction/10/')
        self.failUnlessEqual(resp.status_code, 403)
        resp= self.client.get('/bidauction/11/')
        self.failUnlessEqual(resp.status_code, 403)

        login=self.client.login(username='john3', password='test')
        self.failUnless(login, True)
        self.assertEqual(login, True)

        resp= self.client.get('/bidauction/1/')
        self.failUnlessEqual(resp.status_code, 200)

        #versions don't match
        resp = self.client.post('/bidauction/1/',
            {
                'price':10.40,
                'edited_version':1
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'bidauction.html')
        self.assertContains(resp,"A description of auction has been changed recently")

        #the user's bid is already winning ??
        resp = self.client.post('/bidauction/1/',
            {
                'price':11,
                'edited_version':0
            })
        self.failUnlessEqual(resp.status_code, 403)

        login=self.client.login(username='john4', password='test')
        self.failUnless(login, True)
        self.assertEqual(login, True)

        resp= self.client.get('/bidauction/1/')
        self.failUnlessEqual(resp.status_code, 200)

        #minimum bid increment is 0.01
        resp = self.client.post('/bidauction/1/',
            {
                'price':10.005,
                'edited_version':0
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'bidauction.html')
        self.assertContains(resp,"Bid cannot be less than 0.01")

        #check the price
        resp = self.client.post('/bidauction/1/',
            {
                'price':0.40,
                'edited_version':0
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'bidauction.html')
        self.assertContains(resp,"A new bid should be greater than last bid and the minimum price")

        #test proper data
        resp = self.client.post('/bidauction/1/',
            {
                'price':10.40,
                'edited_version':0
            })

        self.assertEqual(len(mail.outbox), 3)
        #to author
        self.assertEqual(mail.outbox[0].from_email, 'noreply@yaas.com')
        self.assertEqual(mail.outbox[0].to[0], 'smith2@mail.com')
        self.assertEqual(mail.outbox[0].subject,'New bid')
        #to current bidder
        self.assertEqual(mail.outbox[1].from_email, 'noreply@yaas.com')
        self.assertEqual(mail.outbox[1].to[0], 'smith3@mail.com')
        self.assertEqual(mail.outbox[1].subject,'New bid')
        #to previous bidder
        self.assertEqual(mail.outbox[2].from_email, 'noreply@yaas.com')
        self.assertEqual(mail.outbox[2].to[0], 'smith4@mail.com')
        self.assertEqual(mail.outbox[2].subject,'New bid')

        self.assertRedirects(resp,'/')

    def testBidConcurrencyPost(self):
        resp=self.client.get('/bidauction/1/')
        self.failUnlessEqual(resp.status_code, 302)
        self.assertRedirects(resp,'/signin/?next=/bidauction/1/')

        #check concurrency for edited description
        c1 = Client()
        c1.login(username='john2', password='test')
        resp = c1.get('/editauction/1/')
        self.failUnlessEqual(resp.status_code, 200)

        c2 = Client()
        c2.login(username='john5', password='test')
        resp = c2.get('/bidauction/1/')
        self.failUnlessEqual(resp.status_code, 200)

        resp = c1.post('/editauction/1/',
            {
             'description':'my edited description'
            })
        self.assertRedirects(resp,'/')

        resp = c2.post('/bidauction/1/',
            {
                'price':120.40,
                'edited_version':0
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'bidauction.html')
        self.assertContains(resp,"A description of auction has been changed recently")

        #check concurrency for higher bidding price
        c1 = Client()
        c1.login(username='john10', password='test')
        resp = c1.get('/bidauction/2/')
        self.failUnlessEqual(resp.status_code, 200)

        c2 = Client()
        c2.login(username='john11', password='test')
        resp = c2.get('/bidauction/2/')
        self.failUnlessEqual(resp.status_code, 200)

        resp = c1.post('/bidauction/2/',
            {
                'price':70,
                'edited_version':0
            })
        self.assertRedirects(resp,'/')

        resp = c2.post('/bidauction/2/',
            {
                'price':30,
                'edited_version':0
            })
        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'bidauction.html')
        self.assertContains(resp,"A new bid should be greater than last bid and the minimum price")
































