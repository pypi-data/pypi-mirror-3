#    Copyright (C) 2004-2010  Corporation of Balclutha. All rights Reserved.
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

import Globals, os, logging, re
from urllib import urlencode, unquote
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.BastionBanking.ConnectionMgr import Transport
import returncode
from Products.BastionBanking.interfaces.BastionMerchantInterface import BastionMerchantInterface
from Products.BastionBanking.BastionPayment import BastionPayment
from Products.BastionBanking.Exceptions import ProcessingFailure
from Products.BastionBanking.Permissions import operate_bastionbanking
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

from zope.interface import implements

logger = logging.getLogger('BastionBanking.ZPayPal')

TENMINUTES = 10.0 * 60 / 86400

#
# PayPal config constants
#
PAYPAL_SUPPORTED_CURRENCIES = ('USD', 'JPY', 'GBP', 'EUR', 'CAD', 'AUD')
PAYPAL_URL = 'https://www.paypal.com/cgi-bin/webscr'
PAYPAL_SANDBOX_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
PAYPAL_PAYMENT_STATUSES=('Cancelled_Reversed', 'Completed', 'Pending', 'Denied',
                         'Failed', 'Refunded', 'Reversed')
PAYPAL_PENDING_REASONS=('address', 'echeck', 'intl', 'multi_currency', 'unilateral',
                        'upgrade', 'verify', 'other')
PAYPAL_REASON_CODES=('buyer_complaint', 'chargeback', 'guarantee', 'refund', 'other')

TRANSACTION_ID_RE = re.compile(r"""'TRANSACTIONID': '(.+?)'""")

#
# our form widget ...
#
form = \
"""
<tal:block metal:define-macro="pay">
<img src="" valign="bottom"
     tal:attributes="src string:${request/BASEPATH1}/misc_/BastionBanking/paypal.gif"/>&nbsp;&nbsp;
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



#
# this stub was generated with the PayPal Sandbox's 'buy now' forms and should be
# 'definitive' - whatever that means in the world of PayPal ...
#
#  <form action="https://www.sandbox.paypal.com/cgi-bin/webscr" method="post">
#     <input type="hidden" name="cmd" value="_xclick">
#     <input type="hidden" name="business" value="test-merchant@last-bastion.net">
#     <input type="hidden" name="amount" value="10.00">
#     <input type="hidden" name="no_note" value="1">
#     <input type="hidden" name="currency_code" value="GBP">
#     <input type="image" src="https://www.sandbox.paypal.com/en_US/i/btn/x-click-but23.gif" border="0" name="submit" alt="Make payments with PayPal - it's fast, free and secure!">
#  </form>
#
#


#
# We're using eBL, PayPal's WSDL mark-up for direct communications
# These will get turned in ZPT's (type text/xml)
#
AuthenticationHeader = """
<RequesterCredentials xmlns="urn:ebay:api:PayPalAPI"
                      xsi:type="ebl:CustomSecurityHeaderType">
  <Credentials xmlns="urn:ebay:apis:eBLBaseComponents" xsi:type="ebl:UserIdPasswordType">
    <Username xsi:type="xs:string">usename</Username>
    <Password xsi:type="xs:string">password</Password>
  </Credentials>
</RequesterCredentials>
"""

AbstractRequestType = """
<xs:complexType name="AbstractRequestType" abstract="true">
  <xs:annotation>
    <xs:documentation>
       Base type definition of request payload that can carry any type
       of payload content with optional versioning information and
       detail-level requirements.
    </xs:documentation>
  </xs:annotation>
  <xs:sequence>
    <xs:any processContents="lax" minOccurs="0"/>
  </xs:sequence>
  <xs:attribute name="detailLevel" type="xs:token" use="optional"/>
  <xs:attribute name="errorLanguage" type="xs:string" use="optional"/>
    <xs:annotation>
      <xs:documentation>
         This shoudl be the standard RFC 3066 language identification
         tag, e.g., en_US.
      </xs:documentation>
    </xs:annotation>
  </xs:attribute>
  <xs:attribute name="version" type="xs:string" use="required">
    <xs:annotation>
      <xs:documentation>
         This refers to the version of the request payload schema.
      </xs:documentation>
    </xs:annotation>
  </xs:attribute>
</xs:complexType>
"""

AbstractResponseType = """
<xs:complexType name="AbstractResponseType" abstract="true">
  <xs:annotation>
    <xs:documentation>
       Base type definition of response payload that can carry any 
       type of payload content with following optional elements:
         - typestamp of response message,
         - application-level acknowledgement, and
         - applicaiton-level errors and warnings.
    </xs:documentation>
  </xs:annotation>
  <xs:sequence>
    <xs:element name="Timestamp" type="xs:dateTime" minOccurs="0">
      <xs:annotation>
        <xs:documentation>
           This value represents the date and time (GMT) when the
           response was generated by a service provider (as a result of
           processing of a request).
        </xs:documentation>
      </xs:annotation>
    </xs:element>
    <xs:element ref="ns:Ack">
      <xs:annotation>
        <xs:documentation>
           Application level acknowledgement code
           response was generated by a service provider (as a result of
           processing of a request).
        </xs:documentation>
      </xs:annotation>
    </xs:element>
    <xs:element ref="ns:CorrelationId" minOccurs="0">
      <xs:annotation>
        <xs:documentation>
           CorrelationId may be used optionally with an application
           level acknowledgement.
        </xs:documentation>
      </xs:annotation>
    </xs:element>
    <xs:element name="Errors" type="ns:ErrorType" minOccurs="0" maxOccurs="unbounded"/>
    <xs:any processContents="lax" minOccurs="0"/>
  </xs:sequence>
  <xs:attribute name="version" type="xs:string" use="required">
    <xs:annotation>
      <xs:documentation>
         This refers to the version of the response payload schema.
      </xs:documentation>
    </xs:annotation>
  </xs:attribute>
  <xs:attribute name="build" type="xs:string" use="required">
    <xs:annotation>
      <xs:documentation>
         This refers to the specific software build that was used in the
         deployment for processing the request and generating the 
         response.
      </xs:documentation>
    </xs:annotation>
  </xs:attribute>
</xs:complexType>
"""


class ZPayPal(ObjectManager, PropertyManager, SimpleItem):
    """
    Zope-based PayPal interface.
    """
    meta_type = 'ZPayPal'
    implements( BastionMerchantInterface, )
    _security = ClassSecurityInfo()
    __ac_permissions__ = ObjectManager.__ac_permissions__ + (
        (view, ('url', 'business', 'formAction', 'SetExpressCheckout', 'DoExpressCheckoutPayment',)),
        (operate_bastionbanking, ('RefundTransaction', 'GetExpressCheckoutDetails', 'GetTransactionDetails')),
        ) + PropertyManager.__ac_permissions__ + SimpleItem.__ac_permissions__
    __allow_access_to_unprotected_subbojects__ = 1

    # US is the default at PayPal ...
    Locales = ('AU', 'AT', 'BE', 'CA', 'CH', 'CN', 'DE', 'ES', 'GB', 'FR', 'IT', 'NL', 'PL', 'US')

    manage_options = (
        {'label':'Configuration', 'action':'manage_propertiesForm'},
        {'label':'Advanced', 'action':'manage_main'},
        ) + SimpleItem.manage_options

    #
    # signatures are generated from the 'profile' in your account, then 'Request API credentials'
    #
    _properties = PropertyManager._properties + (
        {'id':'account',         'type':'string',    'mode':'w',},
        {'id':'password',        'type':'string',    'mode':'w',},
        {'id':'signature',       'type':'string',    'mode':'w' },
        {'id':'test_account',    'type':'string',    'mode':'w',},
        {'id':'test_password',   'type':'string',    'mode':'w',},
        {'id':'test_signature',  'type':'string',    'mode':'w' },
        {'id':'locale',          'type':'selection', 'mode':'w', 'select_variable':'Locales'},
        )

    def __init__(self, id, account='',password='',signature='',test_account='',test_password='',test_signature=''):
        self.id = id
        self.title = self.meta_type
        self.account = account
        self.password = password
        self.signature = signature
        self.test_account = test_account
        self.test_password = test_password
        self.test_signature = test_signature
        self.locale = 'US'
        self._setObject('widget', ZopePageTemplate('widget', form))
        #self._setObject('picon', Image('picon', 'icon', open('%s/www/paypal.gif' % os.path.dirname(__file__))))

    def url(self):
        if self.aq_parent.mode == 'live':
            return PAYPAL_URL
        else:
            return PAYPAL_SANDBOX_URL

    def business(self):
        if self.aq_parent.mode == 'live':
            return self.account
        else:
            return self.test_account

    def _generateBastionPayment(self, id, amount, ref, REQUEST):
        """
        return a BastionPayment - based upon us knowing what we've stuck in the form ...
        """
        return BastionPayment(id, None, amount, ref)
    
    def _pay(self, payment, return_url, REQUEST=None):
        """
        PayPal expect us to do a POST directly to their site, but that sucks because
        we want to be able to setup a BastionLedger transaction first (and associate it's
        id as the reference for this PayPal).

        So, we're doing a redirect with a GET with our collected and extended parameters!
        """
        if REQUEST is None:
            REQUEST = self.REQUEST

        amount = payment.amount

        assert amount.currency() in PAYPAL_SUPPORTED_CURRENCIES, 'doh currency not supported!'

        token = self.SetExpressCheckout(amount, return_url)
        
        payment.setRemoteRef(token)
        rc = returncode.returncode(token, amount, 0, 0, 'SetExpressCheckout', '')

        request = {'cmd':'_express-checkout',
                   'token': token}

        # we don't actually know what's going to happen from here, so give it the OK ...
        return rc, '%s?%s' % (self.url(), urlencode(request))

    
    def _refund(self, payment, REQUEST=None):
        """
        we're doing full refunds - or nothing ...
        """
        txn_id = self._getTransactionId(payment)
        if txn_id:
            rc = self.RefundTransaction(txn_id, payment.amount, 'Full')
            return returncode.returncode(rc['REFUNDTRANSACTIONID'],
                                         payment.amount,
                                         0, 0,
                                         'RefundTransaction',
                                         str(rc))
        else:
            raise ValueError, 'No TRANSACTIONID!'

    def _reconcile(self, payment, REQUEST=None):
        """
        go complete payment on PayPal side (if necessary) 
        """
        tid = self._getTransactionId(payment)

        if not tid:
            return False

        remote_info = self.GetTransactionDetails(tid)

        return remote_info.get('AMT','') == '%0.2f' % payment.amount.amount() and \
                remote_info.get('CURRENCYCODE','') == payment.amount.currency() and \
                remote_info.get('PAYMENTSTATUS','') in ('Processed', 'Completed')
                
    def _doExpressCheckout(self, token, payerid, payment):
        """
        helper to do express checkout and record the results for posterity ...
        """
        results = self.DoExpressCheckoutPayment(token, payerid, payment.amount, payment.getId())
        rc = returncode.returncode(token, payment.amount, 0, 0, 'DoExpressCheckoutPayment', str(results))
        payment._setReturnCode(rc)
        payment.manage_changeStatus('accept')
        return results

    _security.declarePublic('ipn')
    def ipn(self, REQUEST):
        """
        process payment notification

        Note we have to do the whole workflow thing here as the MerchantService
        has no idea about this function ...
        """
        # they want us to send back their same shite (and we've just nicely
        # deblocked it from the REQUEST...)
        request = dict(REQUEST.form)
        logger.debug('ipn() %s' % str(request))
        request['cmd'] = '_notify-validate'

        transport = Transport(self.url())
        response = transport(urlencode(request))

        data = response.read()

        logger.debug('ipn() response %s, %s, %s' % (response.status, response.reason, data))

        if response.status >= 400:
            msg = '%s: %i - %s\n%s' % (self.url(), response.status, response.reason, data)
            logger.error(msg)
            raise IOError, msg

        # restore acquisition context of transaction
        pmt_id = request['custom']
        try:
            payment = self.aq_parent._getOb(pmt_id)
        except:
            logger.error('unknown payment id: %s' % pmt_id)
            return

        rc = returncode.returncode(request.get('txn_id', ''), payment.amount, 0, 0, 'ipn', str(request))
        payment._setReturnCode(rc)
        
        wftool = getToolByName(self, 'portal_workflow')
        wf = wftool.getWorkflowsFor(payment)[0]

        if data == 'INVALID':
            wf._executeTransition(payment, wf.transitions.reject)
        elif data == 'VERIFIED':
            wf._executeTransition(payment, wf.transitions.accept)
        else:
            logger.error('Unknown return type, expected INVALID/VERIFIED, got: %s' % data)

    def supported_currencies(self):
        return PAYPAL_SUPPORTED_CURRENCIES

    def SetExpressCheckout(self, amount, url, email=''):
        """
        calls PayPal SetExpressCheckout function and returns the express checkout token
        """
        params = {'NOSHIPPING':'1',
                  'PAYMENTACTION':'Sale',      # same as DoExpressCheckoutPayment ...
                  'RETURNURL':url,
                  'CANCELURL':url,
                  'LOCALECODE':self.locale,
                  'CHANNELTYPE':'Merchant',
                  'CURRENCYCODE': amount.currency(),
                  'AMT': amount.amount(),
                  'ITEMAMT': amount.amount(),
                  'L_AMT0': amount.amount(),
                  #'L_QTY0':'1',               # these don't seem to work ...
                  #'L_NUMBER0': '111',
                  #'L_DESC0':'test desc',
                  #'L_NAME0':'test name',
                  }

        # auto-prime PayPal member login info
        if email:
            params['EMAIL'] = email

        #
        # bollicks - this feature isn't implemented!!
        # https://www.x.com/thread/41272
        #
        brandname = self.aq_parent.store_name
        if brandname:
            params['BRANDNAME'] = brandname

        identifier = self.aq_parent.store_identifier
        if identifier:
            params['CUSTOM'] = identifier

        results = self._nvp('SetExpressCheckout', params)

        if results.has_key('TOKEN'):
            return results['TOKEN']

        raise ValueError, (params, results)

    def DoExpressCheckoutPayment(self, token, payerid, amount, custom=''):
        """
        we set the custom field so that ipn can find the ticket ...
        """
        params = {'CURRENCYCODE': amount.currency(),
                  'AMT': amount.amount(),
                  'CUSTOM': custom,
                  'NOTIFYURL':'%s/ipn' % self.absolute_url(),
                  'TOKEN':token,
                  'PAYERID':payerid,
                  'PAYMENTACTION':'Sale'}

        results = self._nvp('DoExpressCheckoutPayment', params)
        
        if results['ACK'] == 'Failure':
            raise ValueError, (params, results)

        return results

    def GetExpressCheckoutDetails(self, token):
        """
        """
        params = {'TOKEN':token}
        try:
            results = self._nvp('GetExpressCheckoutDetails', params)
        except ProcessingFailure, e:
            # it's probably a normal failure :)
            return e[1]
        return results

    def GetTransactionDetails(self, tid):
        """
        """
        params = {'TRANSACTIONID':tid}
        results = self._nvp('GetTransactionDetails', params)

        return results


    def RefundTransaction(self, tid, amount, refund_type='Full'):
        """
        refund_type is Full, Partial, Other
        """
        params = {'TRANSACTIONID':tid,
                  'CURRENCY':amount.currency(),
                  'REFUNDTYPE': refund_type,}

        if refund_type != 'Full':
            params['AMOUNT'] = amount.amount()

        results = self._nvp('RefundTransaction', params)

        # results is 
        # REFUNDTRANSACTIONID Unique transaction ID of the refund.
        # FEEREFUNDAMT Transaction fee refunded to original recipient of payment.
        # GROSSREFUNDAMT Amount of money refunded to original payer.
        # NETREFUNDAMT Amount subtracted from PayPal balance of original recipient of payment to make this refund

        return results

    def _nvp(self, methodname, args={}):
        """
        do a PayPal NVP gateway API call
        """
        params = {'METHOD': methodname,
                  'VERSION': '52.0' }

        if self.aq_parent.mode == 'live':
            url = 'https://api-3t.paypal.com/nvp'
            params.update({'USER':self.account,
                           'PWD':self.password,
                           'SIGNATURE':self.signature})
        else:
            url = 'https://api-3t.sandbox.paypal.com/nvp'
            params.update({'USER':self.test_account,
                           'PWD':self.test_password,
                           'SIGNATURE':self.test_signature})

        if args:
            params.update(args)

        logger.debug('_nvp(%s) %s' % (methodname,str(params)))

        transport = Transport(url)
        response = transport(urlencode(params))

        data = response.read()

        if response.status >= 400:
            msg = '%s: %i - %s\n%s' % (url, response.status, response.reason, data)
            logger.error('_nvp() %s' % msg)
            raise IOError, msg

        results = {}
        for k, v in map(lambda x: x.split('='), data.split('&')):
            results[k] = unquote(v)

        logger.debug('_nvp(%s) %s' % (methodname, str(results)))

        if results['ACK'] == 'Failure':
            raise ProcessingFailure, (args, results)

        return results

    def formAction(self, REQUEST={}, force=False):
        """
        determine what kind of processing should be done on the form - and we cheat and
        use this to kick off DoExpressCheckoutPayment to complete the payment on PayPal.

        if force is set, we do a complete catalog-scan
        """
        if REQUEST.has_key('token'):
            token = REQUEST['token']
            if REQUEST.has_key('PayerID'):
                # OK - we're going to hook the form-stub into transaction completion - eek!!
                now = DateTime()
                if force:
                    pmts = filter(lambda x: x.getRemoteRef() == token, 
                                  self.aq_parent.paymentResults({'status':('pending', 'rejected')}))
                else:
                    pmts = filter(lambda x: x.getRemoteRef() == token,
                                  self.aq_parent.paymentResults({'status':'pending',
                                                                 'submitted':{'query': (now, now - TENMINUTES),
                                                                              'range':'minmax'}}))
                if pmts:
                    # there should be only one ...
                    self._doExpressCheckout(token, REQUEST['PayerID'], pmts[0])
                return 'thank'
            return 'rejected'
        return 'capture'

    def formHidden(self, amount, url, REQUEST={}):
        """
        return a dict of necessary hidden fields
        """
        return {'token':self.SetExpressCheckout(amount, url)}

    def getTransaction(self, pmt):
        """
        returns PayPal's transaction info on the payment.  If we've got far enough
        to get a TRANSACTIONID, we get the details on this, otherwise we get the
        Express Checkout details based on the TOKEN
        """
        tid = self._getTransactionId(pmt)
        if tid:
            return self.GetTransactionDetails(tid)

        token = pmt.getRemoteRef()
        return self.GetExpressCheckoutDetails(token)

    def _getTransactionId(self, pmt):
        """
        trawl through the returncodes looking for TRANSACTIONID's ...
        """
        tid = ''

        codes = list(pmt.returncodes.objectValues())
        codes.reverse()

        for rc in codes:
            match = TRANSACTION_ID_RE.search(rc.response)
            if match:
                return match.groups()[0]

        return ''


Globals.InitializeClass(ZPayPal)
