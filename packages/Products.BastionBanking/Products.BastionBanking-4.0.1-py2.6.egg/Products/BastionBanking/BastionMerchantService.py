#    Copyright (C) 2003-2011  Corporation of Balclutha and contributors.
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

# import stuff
import AccessControl, transaction
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from OFS.Image import Image
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.ATContentTypes.content.folder import ATBTreeFolder as BTreeFolder2
from DateTime import DateTime

from Permissions import securityPolicy, operate_bastionbanking
import ZReturnCode
from ZCreditCard import ZCreditCard
from ZCurrency import ZCurrency
from Products.CMFCore.permissions import View

from BastionPayment import BastionPayment
from Exceptions import UnsupportedCurrency, ProcessingFailure


manage_addBastionMerchantServiceForm = PageTemplateFile('zpt/add_merchantservice', globals()) 
def manage_addBastionMerchantService(self, service, title='Bastion Merchant Service', id='BMS', REQUEST=None):
    """ 
    """
    #
    # new up a service ...
    #
    try:
        exec('from Products.BastionBanking.Merchants.%s.Z%s import Z%s' % (service, service, service))
        self._setObject(id,
                        BastionMerchantService(id,
                                               title,
                                               eval('''Z%s('service')''' % service ) ))

    except:
        raise
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/service/manage_workspace' % (REQUEST['URL3'],id))
    return id
                                     
class BastionMerchantService( BTreeFolder2, ZCatalog, PropertyManager, SimpleItem ):
    """
    An encapsulation of a card merchant service provider.
    """
    meta_type = portal_type = 'BastionMerchantService'

    modes = ('live', 'test')
    retentions = ('none', 'mangled', 'full')
    default_page = 'bastionmerchant_view'

    description = ''
    store_name = ''
    store_identifier = ''

    __ac_permissions__ = BTreeFolder2.__ac_permissions__ + ZCatalog.__ac_permissions__ + (
        (View, ('serviceIcon', 'widget', 'manage_pay', 'manage_payTransaction', 'manage_payment')),
        (view_management_screens, ('manage_service',)),
        (operate_bastionbanking, ('getSearchTerm', 'saveSearch', 'paymentResults','manage_refund', 
                                  'manage_reconcile', 'manage_accept', 'manage_reject', )),
        ) + PropertyManager.__ac_permissions__ + SimpleItem.__ac_permissions__

    manage_options = ( 
        { 'label':'Payments', 'action':'manage_main',
          'help':('BastionBanking', 'search.stx') },
        { 'label':'View',       'action':'' },
        { 'label':'Pay',        'action':'manage_payment',
          'help':('BastionBanking', 'merchantview.stx')},
        { 'label':'Service',    'action':'manage_service' },
        ) + ZCatalog.manage_options[1:]

    def manage_service(self, REQUEST):
        """ """
        REQUEST.RESPONSE.redirect('service/manage_workspace')

    manage_main = PageTemplateFile('zpt/merchant_search', globals())
    manage_payment = PageTemplateFile('zpt/merchant_view', globals())

    _properties = PropertyManager._properties + (
        {'id':'description',      'type':'text',      'mode':'w',},
        {'id':'mode',             'type':'selection', 'mode':'w', 'select_variable':'modes' },
        {'id':'number_retention', 'type':'selection', 'mode':'w', 'select_variable':'retentions'},
        {'id':'store_name',       'type':'string',    'mode':'w' },
        {'id':'store_identifier', 'type':'string',    'mode':'w' },
        )

    def __init__(self, id, title, imp):
        BTreeFolder2.__init__(self, id)
        ZCatalog.__init__(self, id)
        self.title = title
        self.service = imp
        self.mode='test'
        self.number_retention='full'
        for id in ('status', 'number'):
            self.addIndex(id, 'FieldIndex')
        self.addIndex('submitted', 'DateIndex')
	try:
            self.addIndex('reference', 'TextIndexNG3')
	except:
	    self.addIndex('reference', 'TextIndex')
        self.addColumn('meta_type')

    def manage_afterAdd(self, item, container):
        securityPolicy(self)

    def supported_currencies(self):
	"""
	return a tuple of the currency codes supported by the underlying transport
	"""
	return self.service.supported_currencies()


    def displayContentsTab(self):
        """
        we're not Plone-based ...
        """
        return False

    def manage_pay(self, amount, reference='', return_url='', REQUEST={}, txn=None):
        """
        the parameters explicitly defined reflect those defined in the widgets - and
        indeed the minimum required for any merchant txn, additional parameters will
        be in the request.
        
        return a returncode object containing results of interaction ...

        the REQUEST *must* contain appropriate fields to instantiate a creditcard object
        for the service you've configured

        """
        if not isinstance(amount, ZCurrency):
            amount = ZCurrency(amount)
        
        if amount == 0:
            raise ValueError,  'zero amount!'

        id = self.generateId()

        # our ref is blank
        self._setObject(id, self.service._generateBastionPayment(id, amount, reference, REQUEST))

        #
        # we become paranoid about ensure Zope keeps as much of this on record as possible from here ...
        #
        transaction.get().commit()

        payment = self._getOb(id)
        
        if txn:
            payment.setTransactionRef(txn)

        rc, redirect_url = self.service._pay(payment, 
                                             return_url or '%s/pay' % self.absolute_url(), 
                                             REQUEST)

        zrc = payment._setReturnCode(rc)

        # mangle card details as necessary ...
        if payment.payee:
            self._mask_payee(payment.payee)

        # automagically do state changes if we're not redirecting (don't use workflows directly - they could have
        # stronger permissions settings!!)
        if not redirect_url:
            if rc.severity == ZReturnCode.OK:
                payment._status('paid')
            elif rc.severity in (ZReturnCode.FAIL, ZReturnCode.ERROR, ZReturnCode.FATAL):
                payment._status('rejected')

        transaction.get().commit()

        # we could be called from anywhere, only display html if from merchant service
        url = redirect_url or return_url or REQUEST.get('HTTP_REFERER','')
        if url:
            if url.endswith('manage_payment'):
                REQUEST.RESPONSE.redirect('%s/manage_workspace' % payment.getId())
            REQUEST.RESPONSE.redirect(url)
        return payment

    def widget(self, *args, **kw):
        """
        return the html-generated widget from the service
        """
        if getattr(aq_base(self.service), 'widget', None):
            return self.service.widget(args, kw)
        return ''

    def manage_payTransaction(self, txn, reference='', payee=None, return_url='', REQUEST={}):
        """
        BastionLedger-aware payment mechanism.

        Since some payment methods can return success/failure asynchronously,
        this leaves us in a bind about when to post transactions.

        This method allows us to pass this responsibility on to the service,
        which knows this.
        """
	amount = txn.debitTotal()

        return self.manage_pay(amount, reference, return_url, REQUEST or self.REQUEST, txn)

    def manage_refund(self, payment, REQUEST=None):
        """
        delegate to service to refund payment - this is called via workflow - don't set returncode, that happens afterwards
        """
        if self.service._reconcile(payment):

            rc = self.service._refund(payment)
            payment._setReturnCode(rc)
            transaction.get().commit()

            if not rc.severity == ZReturnCode.OK:
                raise ProcessingFailure, rc.message

            txn = payment.getTransactionRef()
            if txn:
                try:
                    txn.manage_reverse('Reversal: BMS ref %s' % payment.getId())
                except:
                    pass
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Refunded')
        else:
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Not reconciled, unable to refund')
            else:
                raise ValueError, 'Cannot refund until payment confirmation'

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_reconcile(self, payment, REQUEST=None):
        """
        delegate to service to reconcile payment
        """
        status = payment.status()
        if status in ('paid', 'pending', 'refunded', 'reconciled', 'rejected') and self.service._reconcile(payment):
            if status != 'reconciled':
                payment._status('reconciled')
        elif status == 'cancelled':
            pass
        elif status != 'rejected':
            payment._status('rejected')
        payment.reindexObject()
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_accept(self, payment, REQUEST=None):
        """
        cool - if it's a BLTransaction, then post it ...
        """
        txn = payment.getTransactionRef()
        if txn:
            txn.manage_post()

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_reject(self, payment, REQUEST=None):
        """
        uncool - if it's a BLTransaction, then cancel it
        """
        txn = payment.getTransactionRef()
        if txn:
            try:
                txn.manage_cancel()
            except:
                pass

        if REQUEST:
            return self.manage_main(self, REQUEST)

    def paymentResults(self, REQUEST):
        """
        return a list of pure payment objects reflecting the sort criteria
        """
        results = []
        for ob in map(lambda x: x.getObject(),
                      self.searchResults(REQUEST=REQUEST, sort_on='submitted', sort_order='descending')):
            if ob.meta_type == 'BastionPayment':
                pmt = ob
            elif ob.meta_type == 'ZReturnCode':
                pmt = ob.aq_parent.aq_parent
            elif ob.meta_type == 'ZCreditCard':
                pmt = ob.aq_parent
            if not pmt in results:
                results.append(pmt)
        return results
        
    def saveSearch(self, REQUEST=None):
        """
        save search parameters in session object
        """
        if not REQUEST:
            REQUEST=self.REQUEST
        REQUEST.SESSION['bastionbanking'] = REQUEST.form

    def getSearchTerm(self, field, default, REQUEST=None):
        """
        return search term results for field
        """
        if not REQUEST:
            REQUEST = self.REQUEST
        if not REQUEST.has_key('SESSION'):
            return default
        return REQUEST.SESSION.get('bastionbanking', {}).get(field, default)


    def serviceIcon(self):
        """
        """
        return self.service.icon

    def _getPortalTypeName(self):
        """
        needed for the portal type view mechanism ...
        """
        return self.meta_type

    def _mask_payee(self, payee):
        """
        returns a card number based upon card number retention policy
        """
        payee.cvv2 = '' # always clear down this ...
        if self.number_retention == 'none':
            payee.number = 'XXXXXXXXXXXXXXXX'
            payee.expiry = DateTime(0)  # reset date to EPOCH
        if self.number_retention == 'mangled':
            payee.number = '%sXXXXXX%s' % (payee.number[0:7], payee.number[-4:])

    def manage_repair(self, REQUEST=None):
        """
        Upgrade any underlying datastructure modifications between releases
        """
        if not getattr(aq_base(self), 'number_retention', None):
            self.number_retention = 'full'
        for pmt in self.objectValues('BastionPayment'):
            if not getattr(aq_base(pmt), 'returncodes', None):
                pmt.returncodes = BTreeFolder2('returncodes')
        self.refreshCatalog(clear=1)

        try:
            self.addIndex('reference', 'TextIndexNG3')
            self.manage_reindexIndex(['reference'])
        except:
            pass

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'repaired')
            return self.manage_main(self, REQUEST)

    def manage_fixupIndexes(self, REQUEST=None):
        """
        resurrect screwed up indexes
        """
        for pmt in self.objectValues('BastionPayment'):
            map(lambda x: x.reindexObject(),
                map(lambda x: x[1], pmt.getReturnCodes()))
            pmt.reindexObject()

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Reindexed ...')
            return self.manage_main(self, REQUEST)

AccessControl.class_init.InitializeClass(BastionMerchantService)
