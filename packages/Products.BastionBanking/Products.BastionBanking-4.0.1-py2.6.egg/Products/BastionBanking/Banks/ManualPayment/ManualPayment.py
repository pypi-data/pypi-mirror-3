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

import Globals
from AccessControl import ClassSecurityInfo
from Products.BastionBanking.interfaces.BastionBankInterface import BastionBankInterface
from Products.BastionBanking.PortalContent import PortalContent
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from DateTime import DateTime
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from returncode import returncode, OK

from zope.interface import implements

class Cheque( PortalContent ):
    """ describe a manual transaction ... """
    meta_type = portal_content = 'Cheque'
    icon = 'Banks/ManualPayment/www/cheque.gif'
    
    property_extensible_schema__ = 0
    _properties = (
        { 'id'   : 'id',          'type' : 'string', 'mode' : 'r' },
        { 'id'   : 'date',        'type' : 'date',   'mode' : 'r' },
        { 'id'   : 'payee',       'type' : 'string', 'mode' : 'r' },
        { 'id'   : 'amount',      'type' : 'string', 'mode' : 'r' },
        { 'id'   : 'reference',   'type' : 'string', 'mode' : 'r' },
        )
    
    def __init__(self, id, payee, amount, reference):
        self.id = id
        self.date = DateTime()
        self.payee = payee
        self.amount = amount
        self.reference = reference

Globals.InitializeClass(Cheque)

class ManualPayment(ObjectManager, PropertyManager):
    """ """
    meta_type = 'ManualPayment'

    implements( BastionBankInterface, )
    _security = ClassSecurityInfo()

    all_meta_types=[]
    dontAllowCopyAndPaste = 1

    id = 'ManualPayment'
    title = 'Payment Schedule'
    
    manage_options = ( {'label':'Payments', 'action':'manage_main'},
                       {'label':'Properties', 'action':'manage_propertiesForm'}, ) + \
                     SimpleItem.manage_options

    _properties = ( )
    manage_main = PageTemplateFile('zpt/payments', globals())
    
    def __init__(self): pass
    
    def _pay(self, amount, account, reference, REQUEST=None):
        """ """
        # TODO - fix this id ...
        id = str(DateTime().timeTime())
        id.replace('.', '')
        self._setObject(id, Cheque(id, account.payee, amount, reference))
        return returncode(id, amount, OK, 0, '', '')

Globals.InitializeClass(ManualPayment)
