#    Copyright (C) 2003-2011  Corporation of Balclutha.  All rights reserved.
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
import logging
from App.ImageFile import ImageFile
import BastionBankService, BastionMerchantService, ZReturnCode
from Permissions import add_merchant_service, add_bank_service
import Merchants, Banks
import BastionTradeable, CurrencyIndex

# plone stuff
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.DirectoryView import registerDirectory
from config import *

registerDirectory(SKINS_DIR, GLOBALS)

# this is needed for the Zope Security Machinery
import ZCurrency

logger = logging.getLogger('Products.BastionBanking')

def initialize(context): 
    context.registerClass(BastionMerchantService.BastionMerchantService,
                          permission = add_merchant_service,
                          constructors = (BastionMerchantService.manage_addBastionMerchantServiceForm,
                                          BastionMerchantService.manage_addBastionMerchantService),
                          icon='www/visa.gif',
                        )
    context.registerClass(BastionBankService.BastionBankService,
                          permission = add_bank_service,
                          constructors = (BastionBankService.manage_addBastionBankServiceForm,
                                          BastionBankService.manage_addBastionBankService),
                          icon='www/bank.gif',
                        )
    context.registerClass(BastionTradeable.BastionQuote,
                          permission = add_bank_service,
                          visibility = None,
                          constructors = (BastionTradeable.manage_addBastionQuoteForm,
                                          BastionTradeable.manage_addBastionQuote,),
                          icon='www/quote.gif',
                        )

    context.registerClass(CurrencyIndex.CurrencyIndex,
                          permission='Add Pluggable Index',
                          constructors=(CurrencyIndex.manage_addCurrencyIndexForm,
                                        CurrencyIndex.manage_addCurrencyIndex),
                          icon='www/index.gif',
                          visibility=None)
    context.registerHelp()
    #
    # have to explicitly delegate to implementation folders ...
    #
    Merchants.initialize(context)
    Banks.initialize(context)

    try:
        profile_registry.registerProfile('default',
                                         PROJECTNAME,
                                         'bastionbanking',
                                         'profiles/default',
                                         PROJECTNAME,
                                         EXTENSION,
                                         IPloneSiteRoot)
    except KeyError:
        # duplicate entry ...
        pass

misc_ = {}
for icon in ('visa', 'bank', 'currency', 'quote', 'creditcard', 'payment'):
    misc_[icon] = ImageFile('www/%s.gif' % icon, globals())


from AccessControl import ModuleSecurityInfo, allow_module, allow_class
ModuleSecurityInfo('Products').declarePublic('BastionBanking')

ModuleSecurityInfo('Products.BastionBanking').declarePublic('BastionMerchantService')
ModuleSecurityInfo('Products.BastionBanking.BastionMerchantService').declarePublic('BastionMerchantService')
ModuleSecurityInfo('Products.BastionBanking.BastionMerchantService.BastionMerchantService').declarePublic('manage_pay')

ModuleSecurityInfo('Products.BastionBanking').declarePublic('ZReturnCode')
# hmmm - these statics still don't seem to be public according to Zope security machinery ...
ModuleSecurityInfo('Products.BastionBanking.ZReturnCode').declarePublic('DEBUG')
ModuleSecurityInfo('Products.BastionBanking.ZReturnCode').declarePublic('INFO')
ModuleSecurityInfo('Products.BastionBanking.ZReturnCode').declarePublic('WARN')
ModuleSecurityInfo('Products.BastionBanking.ZReturnCode').declarePublic('OK')
ModuleSecurityInfo('Products.BastionBanking.ZReturnCode').declarePublic('FAIL')
ModuleSecurityInfo('Products.BastionBanking.ZReturnCode').declarePublic('ERROR')
ModuleSecurityInfo('Products.BastionBanking.ZReturnCode').declarePublic('FATAL')
ModuleSecurityInfo('Products.BastionBanking.ZReturnCode').declarePublic('ZReturnCode')

ModuleSecurityInfo('Products.BastionBanking').declarePublic('ZCreditCard')
ModuleSecurityInfo('Products.BastionBanking.ZCreditCard').declarePublic('ZCreditCard')
ModuleSecurityInfo('Products.BastionBanking.ZCreditCard').declarePublic('CreditCardException')
ModuleSecurityInfo('Products.BastionBanking.ZCreditCard').declarePublic('CreditCardInvalid')
ModuleSecurityInfo('Products.BastionBanking.ZCreditCard').declarePublic('CreditCardExpired')

ModuleSecurityInfo('Products.BastionBanking').declarePublic('ZCurrency')
ModuleSecurityInfo('Products.BastionBanking.ZCurrency').declarePublic('Supported')
ModuleSecurityInfo('Products.BastionBanking.ZCurrency').declarePublic('widget')
ModuleSecurityInfo('Products.BastionBanking.ZCurrency').declarePublic('ZCurrency')

#
# register currency converter with ZPublisher
#
import Converters
from ZPublisher.Converters import type_converters
from OFS.PropertyManager import PropertyManager, DTMLFile
PropertyManager.manage_propertiesForm = DTMLFile('dtml/properties', globals())
type_converters['currency'] = Converters.field2currency
logging.info('added type converter field2currency')


#
# hmmm - some module aliases are needed for old ZODB stuff
#
import sys
sys.modules['BastionBanking.ZCurrency'] = ZCurrency

