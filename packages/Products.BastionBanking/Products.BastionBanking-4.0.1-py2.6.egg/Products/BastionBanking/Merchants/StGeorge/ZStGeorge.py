#    Copyright (C) 2003-2006  Corporation of Balclutha and contributors.
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

import Globals
from AccessControl import ClassSecurityInfo
from stgeorge import stgeorge
from Products.BastionBanking.interfaces.BastionMerchantInterface import BastionMerchantInterface
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from new import instance
from zope.interface import implements

form = \
"""
<img src="" height="35" width="80" valign="bottom"
     tal:attributes="src string:${request/BASEPATH1}/${container/icon}"/>&nbsp;&nbsp;
<select name="type">
   <option tal:repeat="type python: ('VISA', 'Delta', 'Mastercard', 'JCB')"
           tal:content="type"/>
</select>
<span class="form-label">Number</span>&nbsp;
<input type="text" size="16" name="card">&nbsp;&nbsp;
<span class="form-label">Expires</span>&nbsp;
<strong>&nbsp;/&nbsp;</strong>
<select name="expiry:list:int" tal:define="year python: DateTime().year()">
    <option tal:repeat="yy python: range(0, 4)" tal:content="python: year + yy"/>
</select>
<select name="expiry:list:int">
    <option tal:repeat="mm python: range(1, 13)" tal:content="python: '%02d' % mm"/>
</select>
<input type="hidden" name="expiry:list:int" value="1"/>
"""

class ZStGeorge (stgeorge, ObjectManager, PropertyManager, SimpleItem):
    """
    Zope-wrapped St Georges Bank accessor
    """
    meta_type = 'ZStGeorge'

    implements( BastionMerchantInterface, )
    _security = ClassSecurityInfo()

    property_extensible_schema__ = 0
    _properties = (
        {'id': 'cert_file',   'type':'string', 'mode':'w' },
        {'id': 'merchant_id', 'type':'string', 'mode':'w' },
        {'id': 'user',        'type':'string', 'mode':'w' },
        {'id': 'password',    'type':'string', 'mode':'w' },
        {'id': 'realm',       'type':'string', 'mode':'w' },
        )
    
    manage_options = ObjectManager.manage_options + ( {
        'label':'Configuration', 'action':'manage_propertiesForm'},
                       ) + SimpleItem.manage_options

    id = 'St Georges'
    title = 'St Georges Bank - Australia'
    
    def __init__(self, id):
        self.merchant_id = ''
        self.cert_file = ''
        self.user = 'user'
        self.password = 'password'
        self.realm = 'realm'
        self._setObject('widget', ZopePageTemplate('widget', form))

    def _generateBastionPayment(self, id, amount, ref, REQUEST):
        """
        this should agree with stuff in our form (excepting amount) ...
        """
        payee = ZCreditCard(REQUEST['card'],
                            DateTime('%s/%s/01' % (REQUEST['expiry'][0], REQUEST['expiry'][1])),
                            REQUEST['type'])
        return BastionPayment(id, payee, amount, ref)

    def _pay(self, payment, REQUEST=None):
        return stgeorge._pay(self, payment.payee.number, payment.amount)

    def _refund(self, payment, ref, REQUEST=None):
        return stgeorge._refund(self, payment.payee.number, amount, ref)

    def supported_currencies(self):
	return ('AUD',)

Globals.InitializeClass(ZStGeorge)
