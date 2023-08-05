#
# Copyright (c) 2004, Corporation of Balclutha
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are NOT permitted.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
import os, sys, urllib
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase  # this fixes up PYTHONPATH :)
from Products.BastionBanking.tests import BankingTestCase
from ZPublisher.tests.testHTTPRequest import ProcessInputsTests
from Acquisition import aq_base
from Products.BastionLedger.Ledger import manage_addLedger
import Globals
from OFS.SimpleItem import SimpleItem
from AccessControl.Permissions import view

ZopeTestCase.installProduct('BastionLedger')

# and some dependencies ...
ZopeTestCase.installProduct('ZCTextIndex')

paypal_response = {'last_name':'Erwin',
                   'txn_id':'55W11734P4916400C',
                   'receiver_email':'test-merchant@last-bastion.net',
                   'payment_status':'Completed',
                   'payment_gross':'',
                   'tax':'0.00',
                   'invoice':'T000000000029',
                   'address_state':'Queensland',
                   'payer_status':'unverified',
                   'txn_type':'web_accept',
                   'address_country':'Australia',
                   'payment_date':'03:56:21 Nov 27, 2004 PST',
                   'first_name':'Steve',
                   'item_name':'',
                   'address_street':'Crocodile Park',
                   'custom':'T000000000029',
                   'notify_version':'1.6',
                   'address_name':'Steve Erwin',
                   'test_ipn':	'1',
                   'item_number':'',
                   'receiver_id':'HXCQVTXNXRWMU',
                   'business':'test-merchant@last-bastion.net',
                   'payer_id':'BN3WAWPGNCKPJ',
                   'verify_sign':'AN280UdvyCKt4zzLfJHXQDE1MWkqAur0Js0-fBW8PAUoFw99z5sZYv3R',
                   'address_zip':'5332',
                   'payment_fee':'',
                   'address_city':'Brisbane',
                   'address_status':'unconfirmed',
                   'mc_fee':'0.24',
                   'mc_currency':'GBP',
                   'payer_email':'usd-customer@last-bastion.net',
                   'payment_type':'instant',
                   'mc_gross':'1.00',
                   'quantity':'1',
                   }

# kludge up an HTTPRequest ...
pit = ProcessInputsTests(methodName='_processInputs')    
paypalRequest = pit._processInputs(paypal_response.items())

from Products.BastionBanking.Merchants.PayPal import ZPayPal

# Create the error_log object
app = ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog(app)
ZopeTestCase.close(app)
 
# Start the web server
host, port = ZopeTestCase.utils.startZServer(4)
 

class DummyPayPal(SimpleItem):
    """
    Fake PayPal site
    """
    id = title = meta_type = 'PayPal'
    __ac_permissions__ = (
        (view, ('verified', 'invalid')),
        )

    def verified(self, REQUEST):
        """
        """
        raise AssertionError, 'I got called'
        REQUEST.RESPONSE.write('VERIFIED')

    def invalid(self, REQUEST):
        """
        """
        REQUEST.REPSONSE.write('INVALID')

Globals.InitializeClass(DummyPayPal)

class TestPayPal(BankingTestCase.BankingTestCase):

    def afterSetUp(self):
        BankingTestCase.BankingTestCase.afterSetUp(self)
        self.app.manage_addProduct['BastionBanking'].manage_addBastionMerchantService('PayPal')
        self.app._setObject('PayPal', DummyPayPal())
        self.paypal_url =  self.app.PayPal.absolute_url()
        self.bms = self.app.BastionMerchantService
        print "port = %s" % port

    def testIPNVerified(self):
        ZPayPal.PAYPAL_SANDBOX_URL = '%s/verified' % self.paypal_url
        self.bms.service.ipn(*paypal_response.values())

    def testIPNInvalid(self):
        print os.popen('netstat -l', 'r').read()
        ZPayPal.PAYPAL_SANDBOX_URL = 'http://localhost:%s' % port  # % self.paypal_url
        urllib.urlopen('http://localhost/BastionMerchantService/service/ipn?%s' % urllib.urlencode(paypal_response))
        self.bms.service.ipn(*paypal_response.values())
    

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestPayPal))
        return suite

