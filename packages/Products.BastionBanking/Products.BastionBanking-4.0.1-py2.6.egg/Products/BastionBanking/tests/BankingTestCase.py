#    Copyright (C) 2004-2009  Corporation of Balclutha. All rights Reserved.
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
#
import transaction
from Testing import ZopeTestCase
from OFS.Folder import manage_addFolder

from Products.BastionLedger.Ledger import manage_addLedger

ZopeTestCase.installProduct('ZScheduler')
ZopeTestCase.installProduct('BastionLedger')
ZopeTestCase.installProduct('BastionBanking')

# and some dependencies ...
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('ZCTextIndex')

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
import time

ledger_name = 'ledger'
ledger_owner = 'ledger_owner'
default_user = ZopeTestCase.user_name

class BankingTestCase(ZopeTestCase.ZopeTestCase):
    """ Base test case for testing BastionLedger functionality """

    def XafterSetUp(self):
        """ hmmm - forcing setup of self.ledger """
        if not getattr(self.app, ledger_name, None):
            manage_addLedger(self.app, ledger_name, 'default', 'test ledger','GBP')
        self.ledger = getattr(self.app, ledger_name)
        # we can't set up a BastionMerchantService because we don't know which one we want ...

    def X_setupFolder(self):
        # we don't have one of these ...
        pass

    def X_setupUserFolder(self):
        # we don't have one of these ...
        pass

    def X_setupUser(self):
        # we don't have one of these ...
        pass

    def X_login(self):
        # hmmm - we've got to think lots more about user/role testing ...
        pass

def setupBastionLedger(app=None, id=ledger_name, quiet=0):
    if not hasattr(aq_base(app), id):
        _start = time.time()
        if not quiet: ZopeTestCase._print('Adding BastionLedger instance... ')
        manage_addLedger(app, id, 'test ledger', currency='GBP')
        assert getattr(app, id), 'doh ledger not created!'
        if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
setupBastionLedger(app)
transaction.get().commit()
ZopeTestCase.close(app)

