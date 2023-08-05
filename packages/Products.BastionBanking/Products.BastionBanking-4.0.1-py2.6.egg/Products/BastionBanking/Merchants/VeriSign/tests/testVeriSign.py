#    Copyright (C) 2006-2007  Corporation of Balclutha and contributors.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.BastionBanking.tests import BankingTestCase

from Products.BastionBanking.ZCurrency import ZCurrency
from DateTime import DateTime

class TestVeriSign(BankingTestCase.BankingTestCase):

    def afterSetUp(self):
        BankingTestCase.BankingTestCase.afterSetUp(self)
        self.app.manage_addProduct['BastionBanking'].manage_addBastionMerchantService('VeriSign')
        self.bms = self.app.BastionMerchantService

    def testPay(self):
        expiry = DateTime() + 180
        self.bms.manage_pay(ZCurrency('USD 10.00'),
                            {'cc_number':'4111111111111111',
                             'cc_name':'John Doe',
                             'cc_type':'Visa',
                             'cc_year': expiry.strftime('%y'),
                             'cc_month':expiry.strftime('%m')})
        
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestVeriSign))
        return suite

