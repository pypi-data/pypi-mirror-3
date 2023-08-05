#
#    Copyright (C) 2003-2007  Corporation of Balclutha. All rights reserved.
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
__doc__ = """$id$"""
__version__='$Revision: 202 $'[11:-2]
import AccessControl, os
from currency import currency as base, CURRENCIES, UnsupportedCurrency
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from new import instance

__roles__ = None
__allow_access_to_unprotected_subobjects__ = 1

#
# TODO - get our component.xml stuff into zope conf
# 
# it appears this cannot be done - we've got to do our own ZConfig in isolation
# from zope.conf :(
#
# we could think about doing that via an etc/bastionbanking.conf file perhaps ...
#

if os.environ.has_key('DEFAULT_CURRENCY'):
    DEFAULT_CURRENCY = os.environ['DEFAULT_CURRENCY']
else:
    # force user to enter this always ...
    DEFAULT_CURRENCY = ''


def Supported():
    return CURRENCIES

#
# hmmm - having big problems unpacking complex structures using :currency tag
#    ( but this does work with text types... )
#
def widget(tag, currencies, value):
    return """<input type="text" name="%s:currency" value="%s" size="12">\n""" % (tag, str(value))
                                                                                  
class ZCurrency (base):
    """
    A Zope Currency Type

    You can set a default currency via the DEFAULT_CURRENCY environment variable
    """
    meta_type = 'ZCurrency'

    __ac_permissions__ = (
        (view, ('widget',)),
    )

    _currency = DEFAULT_CURRENCY

    # For security machinery:
    __roles__ = None
    __allow_access_to_unprotected_subobjects__ = 1

    _security = ClassSecurityInfo()
    #_security.declareObjectProtected(view)
    _security.declareObjectPublic()

    # override underlying return by value types (there's probably something
    # more cunning that could be done here ...
    def __add__(self, other): return instance(ZCurrency, base.__add__(self, other).__dict__)
    def __mul__(self, other): return instance(ZCurrency, base.__mul__(self, other).__dict__)
    def __div__(self, other): return instance(ZCurrency, base.__div__(self, other).__dict__)
    def __neg__(self): return ZCurrency(self._currency, -self._amount)
    def __abs__(self): return ZCurrency(self._currency, abs(self._amount))

    # this method is deprecated and you should use the :currency mutator instead ...
    def widget(self, tag, currencies=CURRENCIES):
        # TODO - do value ...
        return widget(tag, currencies, self)

    # this shite is necessarily declared here for Zope security machinery to include
    amount = base.amount
    currency = base.currency
    strfcur = base.strfcur

    _security.declarePublic('amount')
    _security.declarePublic('currency')
    _security.declarePublic('strfcur')
    

    def X__cmp__(self, other):
        try:
            return base.__cmp__(self, other)
        except UnsupportedError:
            # hmmm - we need to convert bases
            try:
                currency_service = self.Control_Panel.CurrencyTool
            except:
                raise
            rate = currency_service.getQuote(other.currency)
            if rate:
                return base.__cmp__(self, currency(self._currency, other._amount * rate))
            else:
                rate = currency_service.getQuote(self.currency)
                if rate:
                    return base.__cmp__(other, currency(other._currency, self._amount * rate))
            # bummer - no conversion possible
            raise

AccessControl.class_init.InitializeClass(ZCurrency)
