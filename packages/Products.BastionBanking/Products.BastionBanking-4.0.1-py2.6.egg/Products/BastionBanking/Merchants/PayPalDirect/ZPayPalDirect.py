#    Copyright (C) 2009-2010  Corporation of Balclutha. All rights Reserved.
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

import Globals, os, pycountry
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, access_contents_information
from Products.BastionBanking.interfaces.BastionMerchantInterface import BastionMerchantInterface
from Products.BastionBanking.Exceptions import ProcessingFailure

import returncode

from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionBanking.BastionPayment import BastionPayment
from Products.BastionBanking.ZCreditCard import ZCreditCard

from Products.BastionBanking.Merchants.PayPal.ZPayPal import ZPayPal

from Acquisition import aq_base
from zExceptions import Redirect
from Products.CMFCore.utils import getToolByName

from zope.interface import implements


#
# PayPal config constants
#
PAYPAL_SUPPORTED_CURRENCIES = ('USD', 'GBP',)

PAYPAL_URL = 'https://api-3t.paypal.com/nvp'
PAYPAL_SANDBOX_URL = 'https://api-3t.sandbox.paypal.com/nvp'

COUNTRIES = []
for c in pycountry.countries:
    COUNTRIES.append((c.alpha2, c.name))

#
# our form widget ...
#
form = \
"""
<tal:block metal:define-macro="pay">
<img src="/misc_/BastionBanking/paypaldirect.gif" valign="bottom" alt="PayPal"/>
   <table>
     <tr>
        <td><label>Type</label></td>
        <td><select name="cc_type">
                <option tal:repeat="ct context/card_types" tal:content="ct"/>
            </select></td>
     </tr>
     <tr>
        <td><label>Number</label></td>
        <td><input type="text" size="16" name="cc_number"></td>
     </tr>
     <tr>
        <td><label>Expires</label></td>
        <td><select name="cc_year" tal:define="year python: DateTime().year()">
               <option tal:repeat="yy python: range(0, 4)" tal:content="python: year + yy"/>
            </select>
            <strong>&nbsp;/&nbsp;</strong>
            <select name="cc_month">
               <option tal:repeat="mm python: range(1, 13)" tal:content="python: '%02d' % mm"/>
            </select></td>
      </tr>
     <tr>
        <td><label>First Name</label></td>
        <td><input type="text" size="20" name="cc_firstname"></td>
     </tr>
     <tr>
        <td><label>Last Name</label></td>
        <td><input type="text" size="20" name="cc_lastname"></td>
     </tr>
     <tr>
        <td><label>CVV2</label></td>
        <td><input type="text" size="4" maxlength="4" name="cc_cvv2"></td>
     </tr>
     <tr>
        <td><label>Street Address</label></td>
        <td><input type="text" size="30" name="cc_street"></td>
     </tr>
     <tr>
        <td><label>City</label></td>
        <td><input type="text" size="30" name="cc_city"></td>
     </tr>
     <tr>
        <td><label>State</label></td>
        <td><input type="text" size="30" name="cc_state"></td>
     </tr>
     <tr>
        <td><label>Post Code</label></td>
        <td><input type="text" size="8" name="cc_postcode"></td>
     </tr>
     <tr>
        <td><label>Country</label></td>
        <td><select name="cc_countrycode">
               <option tal:repeat="cc context/countries"
                       tal:attributes="value python: cc[0]"
                       tal:content="python: cc[1]"/>
            </select></td>
     </tr>
   </table>
</tal:block>
"""

error_codes = {'Warning': returncode.WARN,
               'Failure': returncode.ERROR,
               'FailureWithWarning': returncode.ERROR,
               'Success':returncode.OK,
               'SuccessWithWarning': returncode.INFO,}

avs_codes = {
    'A':'Address only (no ZIP)',
    'B':'Address only (no ZIP)',
    'C':'None (declined)',
    'D':'Address and Postal Code',
    'E':'N/a (declined)',
    'F':'Address and Postal Code',
    'G':'Not applicable',
    'I':'Not applicable',
    'N':'None (declined)',
    'P':'Postal Code only (no Address)',
    'R':'Not applicable',
    'S':'Not applicable',
    'U':'Not applicable',
    'W':'Nine-digit ZIP code (no Address)',
    'X':'Address and nine-digit ZIP code',
    'Y':'Address and five-digit ZIP',
    'Z':'Five-digit ZIP code (no Address)',
    # Maestro & Solo
    '0':'All information matched',
    '1':'None (declined)',
    '2':'Partial',
    '3':'N/a',
    '4':'N/a',
    }

cvv2_codes = {
    'M':'Match',
    'N':'No match',
    'P':'Not processed',
    'S':'Service not supported',
    'U':'Service not available',
    'X':'No response',
    # Maestro & Solo
    '0':'Matched',
    '1':'No match',
    '2':'Not implemented by merchant',
    '3':'Merchant indicated no CVV2 on card',
    '4':'Service not available',
}

class ZPayPalDirect(ZPayPal):
    """
    Zope-based PayPal interface.
    """
    meta_type = 'ZPayPalDirect'

    implements(BastionMerchantInterface,)

    _security = ClassSecurityInfo()

    # NVP API version
    version = '56.0'
  
    _properties = ZPayPal._properties + (
        {'id':'version',     'type':'string',    'mode':'r'},
        {'id':'currency',    'type':'selection', 'mode':'w', 'select_variable': 'supported_currencies'},
        {'id':'do_maestro',  'type':'boolean',   'mode':'w'},
        )

    def __init__(self, id, account='',password='',signature='',test_account='',test_password='',test_signature=''):
        ZPayPal.__init__(id, account,password,signature,test_account,test_password,test_signature)
        self.currency = 'GBP'
        self.do_maestro = False
        self._setObject('widget', ZopePageTemplate('widget', form))

    def _generateBastionPayment(self, id, amount, ref, REQUEST):
        """
        return a BastionPayment - based upon us knowing what we've stuck in the form ...
        """
        if REQUEST.has_key('cc_expiry'):
            expiry = REQUEST['cc_expiry']
        else:
            expiry = DateTime('%s/%s/28' % (REQUEST['cc_year'], REQUEST['cc_month']))

        return BastionPayment(id, 
                              ZCreditCard(REQUEST['cc_number'],
                                          expiry,
                                          REQUEST['cc_type'],
                                          '%s %s' % (REQUEST['cc_firstname'],
                                                     REQUEST['cc_lastname']),
                                          REQUEST['cc_cvv2']),
                              amount, 
                              ref)
    
    def _pay(self, payment, return_url='', REQUEST=None):
        """
        PayPal expect us to do a POST directly to their site, but that sucks because
        we want to be able to setup a BastionLedger transaction first (and associate it's
        id as the reference for this PayPal).

        So, we're doing a redirect with a GET with our collected and extended parameters!
        """
        if REQUEST is None:
            REQUEST = self.REQUEST

        assert payment.amount.currency() in PAYPAL_SUPPORTED_CURRENCIES, 'doh currency not supported!'

        creditcard = payment.payee
        firstname, lastname = creditcard.name.split(' ')

        url = self.absolute_url()

        tokens, self._nvp("DoDirectPayment", {
                'PAYMENTACTION' : 'Sale',            
                'AMT' : payment.amount.amount(),
                'CURRENCYCODE': payment.amount.currency(),

                'IPADDRESS' : REQUEST['REMOTE_ADDR'],
                
                'ACCT': creditcard.number,
                'EXPDATE' : creditcard.expiry.strftime('%m%Y'),
                'CVV2' : creditcard.cvv2,
                'FIRSTNAME' : firstname,
                'LASTNAME': lastname,
                'CREDITCARDTYPE': creditcard.type,
                'STREET': REQUEST['cc_street'],
                'CITY': REQUEST['cc_city'],
                'STATE': REQUEST['cc_state'],
                'ZIP':REQUEST['cc_postcode'],
                'COUNTRY' : pycountry.countries.get(alpha2=REQUEST['cc_countrycode']).name,
                'COUNTRYCODE': REQUEST['cc_countrycode'],

                'RETURNURL' : '%s/reconcile' % url,
                'CANCELURL' : '%s/cancel' % url,
                })

        if tokens['ACK'] == 'Success':
            payment.setRemoteRef(tokens['TRANSACTIONID'])
            return returncode.returncode(tokens['TRANSACTIONID'],
                                         ZCurrency('%s %s' % (tokens['CURRENCYCODE'], tokens['AMT'])),
                                         0,
                                         returncode.OK,
                                         'AVS=%s, CVV2=%s' % (avs_codes.get(tokens['AVSCODE'], ''),
                                                              cvv2_codes.get(tokens['CVV2MATCH'])),
                                         str(tokens))
        else:
            return returncode.returncode(tokens['CORRELATIONID'],
                                         payment.amount,
                                         tokens['L_ERRORCODE0'],
                                         error_codes[tokens['ACK']],
                                         '%s: %s' % (tokens['L_SHORTMESSAGE0'],
                                                     tokens['L_LONGMESSAGE0']),
                                         str(tokens))

    def _refund(self, payment, REQUEST=None):
        """
        refund a payment
        """
        tokens = self._nvp('RefundTransaction',{'TRANSACTIONID':payment.remote_ref[-1],
                                                'REFUNDTYPE':'Full',})
        if tokens['ACK'] == 'Success':
            payment.setRemoteRef(tokens['TRANSACTIONID'])
            return returncode.returncode(tokens['TRANSACTIONID'],
                                         ZCurrency('%s %s' % (tokens['CURRENCYCODE'], tokens['AMT'])),
                                         0,
                                         returncode.OK,
                                         '',
                                         str(tokens))
        else:
            return returncode.returncode(tokens['CORRELATIONID'],
                                         payment.amount,
                                         tokens['L_ERRORCODE0'],
                                         error_codes[tokens['ACK']],
                                         '%s: %s' % (tokens['L_SHORTMESSAGE0'],
                                                     tokens['L_LONGMESSAGE0']),
                                         str(tokens))


    def reconcile(self, payment, REQUEST=None):
        """
        returns whether or not the payment has cleared funds
        """
        tokens = self.getTransaction(payment.getRemoteRef())
        if tokens['PAYMENTSTATUS'] in ('Canceled-Reversal', 'Completed', 'Processed'):
            return ZCurrency('%s %s'% (tokens['CURRENCYCODE'], tokens['SETTLEAMT'])) == payment.amount
        #elif tokens['PAYMENTSTATUS'] in ('Pending', ):
        #    return ZCurrency('%s %s'% (tokens['CURRENCYCODE'], tokens['AMT'])) == payment.amount
        return False

    def cancel(self, payment_stuff):
        """
        cancel a payment request
        """
        
    def supported_currencies(self):
        return PAYPAL_SUPPORTED_CURRENCIES

    def card_types(self):
        """
        return valid card types
        """
        results = ('Visa', 'MasterCard', 'Discover', 'Amex')
        if self.do_maestro:
            return results + ('Maestro','Solo')
        return results

    def countries(self):
        return COUNTRIES

    def formAction(self, REQUEST={}):
        """
        """
        return 'capture'

Globals.InitializeClass(ZPayPalDirect)

