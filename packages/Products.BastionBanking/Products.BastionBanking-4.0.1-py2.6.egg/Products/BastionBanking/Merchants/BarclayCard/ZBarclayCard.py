#    Copyright (C) 2003-2007  Corporation of Balclutha and contributors.
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
from Shared.DC.Scripts.Script import defaultBindings
from Shared.DC.Scripts.Signature import FuncCode
from Products.PythonScripts.PythonScript import PythonScript
from Products.BastionBanking.interfaces.BastionMerchantInterface import BastionMerchantInterface
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import returncode
from Products.BastionBanking.ZCurrency import CURRENCIES
from Products.BastionBanking.ZCreditCard import ZCreditCard
from Products.BastionBanking.BastionPayment import BastionPayment

from zope.interface import implements

# WAM - zoperl/pyperl is presently borked!!!

#
# we've invoked a perl module to take care of the https connection because httplib doesn't seem
# very well behaved.  We could possibly use something like cryptlib to keep this pure Python ...
#

try:
    from Products.PerlExternalMethod import PerlExtMethod, FuncCode

    class MPIAgent(PerlExtMethod):
        """
        we've invoked a perl module to take care of the https connection
        because httplib doesn't seem very well behaved.  We could possibly use
        something like cryptlib to keep this pure Python ..   
        """
        id = title = meta_type = 'MPIAgent'

        def __init__(self):
            self.module = 'MPI'
            self.function = 'send'
            self.func_code = FuncCode(open(os.path.join(os.path.dirname(__file__),
                                                        'MPI.pm')).read())

    mpi_send = MPIAgent()
except ImportError:
    mpi_send = None
    

preauth = \
"""<EngineDocList xmlns:tal="http://xml.zope.org/namespaces/tal">
 <DocVersion>1.0</DocVersion>
 <EngineDoc>
  <ContentType>OrderFormDoc</ContentType>
  <User>
   <Name tal:content="here/username"/>
   <Password tal:content="here/password"/>
   <ClientId DataType="S32"><span tal:replace="here/clientid"/></ClientId>
  </User>
  <Instructions>
   <Pipeline>PaymentNoFraud</Pipeline>
  </Instructions>
  <OrderFormDoc>
   <Mode>P</Mode>
   <Comments/>
   <Consumer>
    <Email/>
    <PaymentMech>
     <CreditCard>
      <Number tal:content="request/card">4111111111111111</Number>
      <Expires DataType="ExpirationDate" Locale="826">
        <span tal:replace="request/expiry_mm"/>/<span tal:replace="request/expiry_yy"/>
      </Expires>
     </CreditCard>
    </PaymentMech>
   </Consumer>
   <Transaction>
    <Type>Auth</Type>
    <CurrentTotals>
     <Totals>
      <Total DataType="Money" ZCurrency="826"
             tal:attributes="currency here/currencycode">
       <span tal:replace="python: float(request['amount']) * 100">removed (implied) decimal place...</span>
      </Total>
     </Totals>
    </CurrentTotals>
   </Transaction>
  </OrderFormDoc>
 </EngineDoc>
</EngineDocList>"""

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

class ZBarclayCard(ObjectManager, PropertyManager, PythonScript):
    """
    Heh - this is kind of complicated - but we want this class to behave like a PythonScript
    because we want to recycle the testing functionality.  But we (i) don't want to edit
    the script - that would breach security; (ii) want to not have to recompile the function
    that is actually file-resident here...

    So, we just trick PythonScript into using the function by setting _v_f ...
    """
    meta_type = 'ZBarclayCard'

    implements( BastionMerchantInterface, )
    _security = ClassSecurityInfo()
    _reserved_names = ('mpi_preauth',)
    
    icon = 'Merchants/www/barclaycard.gif'
    ePDQ = Globals.ImageFile('www/epdq.gif', globals())

    #
    # setting up test tab ...
    #
    _params = 'card,expiry_yy,expiry_mm,amount'
    #func_defaults = None
    #func_code = FuncCode(('card', 'expiry_yy', 'expiry_mm', 'amount','REQUEST'), 5)
    
    manage_options = ( {'label':'Configuration', 'action':'manage_propertiesForm'},
                       {'label':'Advanced', 'action':'manage_main'},
                       {'label':'Test', 'action':'ZScriptHTML_tryForm'}, ) + \
                     SimpleItem.manage_options

    manage_propertiesForm = PageTemplateFile('zpt/properties', globals())
    
    _properties =  (
        {'id':'username',     'type':'string', 'mode': 'w',},
        {'id':'password',     'type':'string', 'mode': 'w',},
        {'id':'clientid',     'type':'string', 'mode': 'w',},
        {'id':'chargetype',   'type':'string', 'mode': 'w',},
        {'id':'currencycode', 'type':'string', 'mode': 'w',},
        {'id':'parameters',   'type':'string', 'mode': 'w',},
        )

    def __setstate__(self, state):
        ZBarclayCard.inheritedAttribute( '__setstate__' )( self, state )
        self._v_f = self._pay
        
    def __init__(self, id):
        self.id = id
        self.manage_edit('ZBarclayCard - ePDQ', '', '', '', '', '')
        self.ZBindings_edit(defaultBindings)
        self._setObject('mpi_preauth', ZopePageTemplate('mpi_preauth', preauth))
        self.mpi_preauth.content_type = 'text/xml'
        self._setObject('widget', ZopePageTemplate('widget', form))
        self._v_f = self._pay
        
    def _generateBastionPayment(self, id, amount, ref, REQUEST):
        """
        this should agree with stuff in our form (excepting amount) ...
        """
        payee = ZCreditCard(REQUEST['card'],
                            DateTime('%s/%s/01' % (REQUEST['expiry'][0], REQUEST['expiry'][1])),
                            REQUEST['type'])
        return BastionPayment(id, payee, amount, ref)

    def _pay(self, payment, REQUEST=None):
        """
        """
        #
        # format and transmit XML txn ...
        #
        request = { 'card': payment.payee.number,
                    'expiry_yy': payment.payee.expiry.year(),
                    'expiry_mm': payment.payee.expiry.month(),
                    'amount': payment.amount.amount() }
        id,total,rc,severity,msg,content = mpi_send( self.mpi_preauth(request) )
        #
        # set right response header (it seems to have got confused with previous call ...)
        #
        if REQUEST:
            REQUEST.RESPONSE.setHeader('Content-Type', 'text/html')

        #
        # bugger, we have detected an HTTP error ...
        #
        try:
            if int(severity) >= 100:
                return returncode.returncode(id, amount, rc, returncode.ERROR, msg, content)
        except:
            # oh well - it's blank, that's ok ...
            pass

        #
        # a severity of 5 or greater is a failed txn from MPI perspective ...
        #
        if int(severity) >= 5:
            return returncode.returncode(id, amount, rc, returncode.ERROR, msg, content)

        return returncode.returncode(id, amount, rc, returncode.OK, msg, content)

    #
    # our test - this stuff doesn't work ...
    #
    #__call__ = manage_pay

    def manage_edit(self, title, username, password, clientid, chargetype, currencycode,
                    REQUEST=None):
        """ """
        self.title = title
        self.username = username
        self.password = password
        self.clientid = clientid
        self.chargetype = chargetype
        self.currencycode = currencycode
        if REQUEST:
            REQUEST.set('management_view', 'Properties')
            REQUEST.set('manage_tabs_message', 'Properties Updated')
            return self.manage_propertiesForm(self, REQUEST)

    def manage_test_preauth(self, REQUEST):
        """ just in case something really f**ked is going on with the XML stuff ...
        """
        return self.mpi_preauth(REQUEST)

    def _refund(self, payment, ref, REQUEST=None):
        raise NotYetImplemented
    
    def supported_currencies(self):
	return CURRENCIES

Globals.InitializeClass(ZBarclayCard)
