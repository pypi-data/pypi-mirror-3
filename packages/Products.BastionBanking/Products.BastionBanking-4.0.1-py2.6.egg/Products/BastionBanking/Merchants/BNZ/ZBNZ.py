#    Copyright (C) 2005-2007  Corporation of Balclutha and contributors.
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
from bnz import bnz
from Products.BastionBanking.interfaces.BastionMerchantInterface import BastionMerchantInterface
from Products.BastionBanking.ZReturnCode import ZReturnCode
from Products.BastionBanking.ZCreditCard import ZCreditCard
from Products.BastionBanking.BastionPayment import BastionPayment
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from new import instance
from zope.interface import implements

form = \
"""
<img src="" height="16" width="16" valign="bottom"
     tal:attributes="src string:${request/BASEPATH1}/${container/icon}"/>&nbsp;&nbsp;
<select name="cc_type">
   <option tal:repeat="type python: ('VISA', 'Delta', 'Mastercard', 'JCB')"
           tal:content="type"/>
</select>
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
"""

class ZBNZ (bnz, ObjectManager, PropertyManager, SimpleItem):
    """
    Zope-wrapped Bank of New Zealand accessor
    """
    meta_type = 'ZBNZ'

    implements( BastionMerchantInterface, )
    _security = ClassSecurityInfo()

    property_extensible_schema__ = 0
    _properties = (
        {'id': 'cert_file',       'type':'string', 'mode':'w' },
        {'id': 'cert_password',   'type':'string', 'mode':'w' },
        {'id': 'merchant_id',     'type':'string', 'mode':'w' },
        {'id': 'user',            'type':'string', 'mode':'w' },
        {'id': 'realm',           'type':'string', 'mode':'w' },
        )
    
    manage_options = ObjectManager.manage_options + ( {
        'label':'Configuration', 'action':'manage_propertiesForm'},
                       ) + SimpleItem.manage_options

    id = 'BNZ'
    title = 'Bank of New Zealand'
    
    def __init__(self, id):
        self.merchant_id = '12341234'
        self.cert_file = os.path.join(os.path.dirname(__file__), 'gateway.cer')
        self.cert_password = 'a5de3fsA'
        self.user = 'user'
        self.realm = 'realm'
        self._setObject('widget', ZopePageTemplate('widget', form))

    def _generateBastionPayment(self, id, amount, ref, REQUEST):
        payee = ZCreditCard(REQUEST['cc_number'],
                            DateTime('%s/%s/01' % (REQUEST['cc_year'], REQUEST['cc_month'])),
                            REQUEST.get('cc_type', ''), REQUEST.get('cc_name', ''))
        return BastionPayment(id, payee, amount, ref)

    def _pay(self, payment, REQUEST=None):
        """
        make payment, coerce return type 
        """
        return bnz._pay(self, payment.payee, payment.amount,
                        self.aq_parent.mode=='test')

    def _refund(self, payment, REQUEST=None):
        """
        make refund, coerce return type 
        """
        return bnz._refund(self, payment.payee, payment.amount,
                           payment.reference, self.aq_parent.mode=='test')


Globals.InitializeClass(ZBNZ)
