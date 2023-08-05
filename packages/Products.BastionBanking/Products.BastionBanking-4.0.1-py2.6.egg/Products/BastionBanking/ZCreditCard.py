#    Copyright (C) 2003-2008  Corporation of Balclutha and contributors.
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
from AccessControl import ClassSecurityInfo
from PortalContent import PortalContent
from creditcard import creditcard, CreditCardException, CreditCardInvalid, CreditCardExpired


class ZCreditCard(creditcard, PortalContent):
    """
    A persistent creditcard ...

    This is supposed to be a first-class Zope object ...
    """
    meta_type = portal_type = 'ZCreditCard'
    icon = 'misc_/BastionBanking/creditcard'

    __ac_permissions__ = PortalContent.__ac_permissions__ + (
        (view, ('number_str', 'masked')),
        )
    
    property_extensible_schema__ = 0
    _properties = (
        {'id': 'title',  'type':'string', 'mode':'w' },
        {'id': 'number', 'type':'string', 'mode':'r' },
        {'id': 'expiry', 'type':'date',   'mode':'r' },
        {'id': 'type',   'type':'string', 'mode':'r' },
        {'id': 'name',   'type':'string', 'mode':'r' },
        # it may be forbidden to hold this ...
        {'id': 'cvv2',   'type':'string', 'mode':'r' }
        )
    _security = ClassSecurityInfo()

    def __init__(self, number, expiry, type='', name='', cvv2=''):
        self.id = number
        self.title = name     # for want of anything better ...
        creditcard.__init__(self, number, expiry, type, name, cvv2)

    def _repair(self):
        for attr in ('name', 'cvv2'):
            if not getattr(aq_base(self), attr, none):
                setattr(self, attr, '')

    def number_str(self):
        """
        return the formatted cardnumber
        """
        return '%s-%s-%s-%s' % (self.number[0:4],
                                self.number[4:8],
                                self.number[8:12],
                                self.number[12:])

    def masked(self):
        """
        returns a card number based upon card number retention policy
        """
        return '%sXXXXXX%s' % (self.number[0:7], self.number[-4:])

AccessControl.class_init.InitializeClass(ZCreditCard)
