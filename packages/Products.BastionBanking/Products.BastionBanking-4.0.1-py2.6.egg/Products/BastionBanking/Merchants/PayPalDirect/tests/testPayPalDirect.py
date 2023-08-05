#
# Copyright (c) 2009, Corporation of Balclutha
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
from Products.PloneTestCase.PloneTestCase import PloneTestCase, setupPloneSite
from ZPublisher.tests.testHTTPRequest import ProcessInputsTests
from Acquisition import aq_base
from Products.BastionLedger.Ledger import manage_addLedger
import Globals
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionBanking.BastionPayment import BastionPayment
from OFS.SimpleItem import SimpleItem
from AccessControl.Permissions import view


from Products.BastionBanking.Merchants.PayPalDirect.ZPayPalDirect import PAYPAL_SANDBOX_URL

ZopeTestCase.installProduct('BastionBanking')

setupPloneSite(products=['BastionBanking'])


class TestPayPalDirect(PloneTestCase):

    def afterSetUp(self):
        PloneTestCase.afterSetUp(self)
        self.portal.manage_addProduct['BastionBanking'].manage_addBastionMerchantService('PayPalDirect')
        self.bms = self.portal.BastionMerchantService

        # as per PP NVP API Developer Guide ...
        # we've got to make it USD otherwise processing is delayed because it's multi-currency ...
        self.bms.service.manage_changeProperties(api_endpoint=PAYPAL_SANDBOX_URL,
                                                 username='sdk-three_api1.sdk.com',
                                                 password='QFZCWN5HZM8VBG7Q',
                                                 signature='A-IzJhZZjhg29XQ2qnhapuwxIDzyAZQ92FRP5dqBzVesOkzbdUONzmOU',
                                                 currency='USD')

    def testPayRefund(self):
        expiry = DateTime() + 300
        amount = ZCurrency('USD 10.12')
        pmt = self.bms.manage_pay(amount, 'bla',
                                  {'cc_number':'5404630449028682',
                                   'cc_expiry':expiry,
                                   'cc_type':'Visa',
                                   'cc_firstname':'John',
                                   'cc_lastname':'Doe',
                                   'cc_cvv2':'123',
                                   'cc_street':'123 Park Lane',
                                   'cc_city':'London',
                                   'cc_state':'Buckinghamshire',
                                   'cc_postcode':'W2 1AJ',
                                   'cc_countrycode':'GB',
                                   'REMOTE_ADDR':'123.4.5.67'})
        self.assertEqual(pmt.amount, amount)
        self.assertEqual(pmt.status(), 'paid')

        #self.assertEqual(self.bms.service.reconcile(pmt), True)

        self.bms.manage_refund(pmt)

        #self.assertEqual(pmt.status(), 'refunded')
        #self.assertEqual(self.bms.service.reconcile(pmt), False)

        
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestPayPalDirect))
        return suite

