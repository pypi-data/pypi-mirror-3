#    Copyright (C) 2004-2008  Corporation of Balclutha. All rights Reserved.
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

import AccessControl

from AccessControl.Permissions import view
from Products.CMFCore.DynamicType import DynamicType
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Permissions import add_bank_service
from ZCurrency import ZCurrency

manage_addBastionQuoteForm = PageTemplateFile('zpt/add_quote', globals())
def manage_addBastionQuote(self, amount, quantity='', expires='', REQUEST=None):
    """ """
    id = str(len(self.objectIds()))

    try:
        qty = float(quantity)
    except:
        qty = 0.0
    if expires:
        expires = DateTime(expires)
    else:
        expires = DateTime(0)
    
        
    self._setObject(id, BastionQuote(id, ZCurrency(amount), qty, expires))

    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/manage_main' % REQUEST['URL3'])

class BastionQuote(PropertyManager, SimpleItem, CMFCatalogAware):
    """
    """
    meta_type="BastionQuote"

    _properties = (
        {'id':'amount',         'type':'currency',  'mode':'w'},
        {'id':'quantity',       'type':'float',     'mode':'w'},
        {'id':'expires',        'type':'date',      'mode':'w'},
        )

    __ac_permissions = PropertyManager.__ac_permissions__ + \
                       SimpleItem.__ac_permissions__ + \
                       CMFCatalogAware.__ac_permissions__
    
    manage_options = PropertyManager.manage_options + SimpleItem.manage_options
    
    def __init__(self, id, amount, quantity, expires):
        self.id = id
        self.amount = amount
        self.quantity = quantity
        self.expires = expires

    def title(self):
        return "%s / %s" % (self.amount, self.quantity)

AccessControl.class_init.InitializeClass(BastionQuote)

class BastionQuotesFolder(ObjectManager, SimpleItem):
    meta_type = title = 'QuoteFolder'

    manage_options = (
        {'label':'Quotes', 'action':'manage_main'},
        ) + SimpleItem.manage_options

    def all_meta_types(self):
        return  ( { 'action' : 'manage_addProduct/BastionBanking/add_quote'
                 , 'permission' : add_bank_service
                 , 'name' : 'Tradeable Quote'
                 , 'Product' : 'BastionBanking'
                 , 'instance' : BastionQuote
                 },
               )

    def best(self):
        if not self.objectIds():
            return None
        else:
            return self._getOb('0').amount  # heh - just return the first ...

AccessControl.class_init.InitializeClass(BastionQuotesFolder)


class BastionTradeable(PropertyManager, DynamicType, SimpleItem, CMFCatalogAware):
    """
    A tradeable wraps an underlying object with buy/sell/trade info ...
    """
    meta_type = 'BastionTradeable'
    isPortalContent = 1
    _isPortalContent = 1  # More reliable than 'isPortalContent'.
    property_extensible_schema__ = 1

    __ac_permissions__ =  PropertyManager.__ac_permissions__ + (
        (view, ('bidPrice', 'askPrice')),
        ) + SimpleItem.__ac_permissions__ + CMFCatalogAware.__ac_permissions__

    Statuses = ('Open', 'Offered', 'Traded',)
    _properties = PropertyManager._properties + (
        {'id':'path',   'type':'string', 'mode':'w'},
        )

    manage_options =  PropertyManager.manage_options + (
        {'label':'View', 'action':''},
        {'label':'Bids', 'action':'manage_bids'},
        {'label':'Asks', 'action':'manage_offers'}
        ) +  SimpleItem.manage_options

    def __init__(self, id, title,  path):
        self.id = id
        self.title = ''
        self.path = path
        self.bidlist = BastionQuotesFolder('bidlist')
        self.asklist = BastionQuotesFolder('asklist')

    def manage_bids(self, REQUEST):
        """
        """
        REQUEST.RESPONSE.redirect('bidlist/manage_workspace')
    
    def manage_offers(self, REQUEST):
        """
        """
        REQUEST.RESPONSE.redirect('asklist/manage_workspace')
    
    def bidPrice(self):
        return self.bidlist.best()

    def askPrice(self):
        return self.asklist.best()

    def _getPortalTypeName(self):
        """
        needed for the portal type view mechanism ...
        """
        return self.meta_type

    def __str__(self):
	return '<%s bid=%s ask=%s at %s>' % (self.meta_type,
                                             self.bidPrice(),
                                             self.askPrice(),
                                             self.absolute_url())

AccessControl.class_init.InitializeClass(BastionTradeable)


