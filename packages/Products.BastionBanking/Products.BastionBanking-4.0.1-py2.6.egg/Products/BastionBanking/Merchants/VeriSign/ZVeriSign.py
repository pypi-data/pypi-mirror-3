#
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

import Globals, os
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from verisign import verisign, Jurisdictions
from Products.BastionBanking.interfaces.BastionMerchantInterface import BastionMerchantInterface
from Products.BastionBanking.ZReturnCode import ZReturnCode
from Products.BastionBanking.ZCreditCard import ZCreditCard
from Products.BastionBanking.BastionPayment import BastionPayment
from Products.BastionBanking.ZCurrency import Supported
from Products.BastionBanking.Exceptions import UnsupportedCurrency
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem

from zope.interface import implements

form = \
"""
<tal:block metal:define-macro="pay">
<img src="" valign="bottom"
     tal:attributes="src string:${request/BASEPATH1}/misc_/BastionBanking/verisign.gif"/>&nbsp;&nbsp;
<span class="form-label">Number</span>&nbsp;
<input type="text" size="16" name="cc_number">&nbsp;&nbsp;
<span class="form-label">Expires</span>&nbsp;
<select name="cc_year" tal:define="year python: DateTime().year()">
    <option tal:repeat="yy python: range(0, 4)" tal:content="python: year + yy"/>
</select>
<strong>&nbsp;/&nbsp;</strong>
<select name="cc_month">
    <option tal:repeat="mm python: range(1, 13)" tal:content="python: '%02d' % mm"/>
</select>
</tal:block>
"""

class ZVeriSign (verisign, ObjectManager, PropertyManager, SimpleItem):
    """
    Zope-wrapped VeriSign PayFlow Merchant
    """
    meta_type = 'ZVeriSign'

    implements( BastionMerchantInterface, )
    _security = ClassSecurityInfo()

    partner = ''

    property_extensible_schema__ = 0
    _properties = (
        {'id': 'account',           'type':'string',             'mode':'w' },
        {'id': 'password',          'type':'string',             'mode':'w' },
        {'id': 'partner',           'type':'string',             'mode':'w' },
        {'id': 'timeout',           'type':'int',                'mode':'w' },
        {'id': 'proxy_host',        'type':'string',             'mode':'w' },
        {'id': 'proxy_port',        'type':'string',             'mode':'w' },
        {'id': 'proxy_account',     'type':'string',             'mode':'w' },
        {'id': 'proxy_password',    'type':'string',             'mode':'w' },
        {'id': 'jurisdiction',      'type':'selection',          'mode':'w',
         'select_variable':'Jurisdictions'},
        {'id': 'currencies',        'type':'multiple selection', 'mode':'w',
         'select_variable':'Currencies'},
        # these aren't yet implemented ...
        {'id': 'decline_avs_failure',   'type':'boolean',            'mode':'r'},
        {'id': 'decline_cvv2_failure',  'type':'boolean',            'mode':'r'},
        )
    
    manage_options = ObjectManager.manage_options + ( {
        'label':'Configuration', 'action':'manage_propertiesForm'},
                       ) + SimpleItem.manage_options

    id = 'VeriSign'
    title = 'VeriSign PayFlow'

    # if address verification or card security code failures, reject payment ...
    decline_avs_failure = decline_cvv2_failure = 0
    
    def __init__(self, id):
        self.account = 'youraccount'
        self.password = 'p@ssw0rd'
        self.timeout = 30
        self.proxy_host = ''
        self.proxy_port = ''
        self.proxy_account = ''
        self.proxy_password = ''
        self.jurisdiction = 'us'
        self.currencies = ['USD']
        self._setObject('widget', ZopePageTemplate('widget', form))

    def Jurisdictions(self):
        """
        return list of VeriSign jurisdictions - whereby we have known meta-data
        """
        return Jurisdictions()

    def supported_currencies(self):
        """
        return list of currencies which your acquiring bank supports
        """
        return self.currencies

    def Currencies(self):
        """
        return list of all known currencies
        """
        return Supported()

    def _generateBastionPayment(self, id, amount, ref, REQUEST):
        """
        this should agree with stuff in our form (excepting amount) ...
        """
        payee = ZCreditCard(REQUEST['cc_number'],
                            DateTime('%s/%s/01' % (REQUEST['cc_year'], REQUEST['cc_month'])),
                            REQUEST.get('cc_type', ''),
                            REQUEST['cc_name'])
        return BastionPayment(id, payee, amount, ref)

    def _pay(self, payment, REQUEST=None):
        """
        make payment, coerce return type 
        """
        if payment.amount.currency() not in self.currencies:
            raise UnsupportedCurrency, payment.amount.currency()
        return verisign._pay(self, payment.payee, payment.amount,
                             self.aq_parent.mode=='test',
                             timeout=self.timeout,
                             street=REQUEST.get('street', ''),
                             zip=REQUEST.get('zip',''))

    def _refund(self, payment, REQUEST=None):
        """
        make refund, coerce return type 
        """
        return verisign._refund(self, payment.payee, payment.amount,
                                payment.returncodes.objectValues()[-1].reference,
                                self.aq_parent.mode=='test', timeout=self.timeout)


Globals.InitializeClass(ZVeriSign)
