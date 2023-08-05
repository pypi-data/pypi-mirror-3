#
#    Copyright (C) 2007  Corporation of Balclutha. All rights reserved.
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

from AccessControl import ClassSecurityInfo
from ZCurrency import ZCurrency, CURRENCIES
from Products.Archetypes.Widget import TypesWidget, registerWidget
from Products.Archetypes.Field import Field, ObjectField, registerField, registerPropertyType
from Products.Archetypes.utils import DisplayList

class AmountWidget(TypesWidget):
    """
    Widget to capture currency-based amounts
    """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "widgets_amount",
        'size' : '12',
        'maxlength' : '20',
        })

    security = ClassSecurityInfo()

registerWidget(AmountWidget,
               title='Amount',
               description=('Render a widget to a base currency and an amount.'),
               used_for=('Products.BastionBanking.Archetypes.AmountField',)
               )


class AmountField(ObjectField):
    """A field that stores currency-based amounts"""

    _properties = Field._properties.copy()
    _properties.update({
        'type' : 'currency',
        'base' : 'USD',
        'widget' : AmountWidget,
        })

    security  = ClassSecurityInfo()
   
    security.declarePrivate('validate_required')
    def validate_required(self, instance, value, errors):
        try:
            ZCurrency(value)
        except:
            result = False
        else:
            result = True
        return ObjectField.validate_required(self, instance, result, errors)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        Check if value is an actual currency value. If not, attempt
        to convert it to one. Assign all properties passed as kwargs to object.
        """
        if not value:
            value = None
        elif not isinstance(value, ZCurrency):
            __traceback_info__ = (self.getName(), instance, value, kwargs)
            value = ZCurrency(value)

        ObjectField.set(self, instance, value, **kwargs)

registerField(AmountField,
              title='Amount',
              description='Used for storing currency-based amounts')
registerPropertyType('default', 'currency', AmountField)

_vocabulary = []
for code in CURRENCIES:
    _vocabulary.append((code, code, 'label_cur_%s' % code))
CurrencyList = DisplayList(_vocabulary)

class CurrencyField(ObjectField):
    """
    A pull-down to select a currency
    """
    _properties = Field._properties.copy()
    _properties.update({
        'default' : 'USD',
        })

    security  = ClassSecurityInfo()

    def __init__(self, name=None, **kw):
        ObjectField.__init__(self, name, **kw)
        # enforce vocabulary ...
        self.vocabulary = CurrencyList

            
    security.declarePrivate('validate_required')
    def validate_required(self, instance, value, errors):
        if not value in CURRENCIES:
            result = False
        else:
            result = True
        return ObjectField.validate_required(self, instance, result, errors)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        Check if value is an actual currency. If not, set it to USD.
        Assign all properties passed as kwargs to object.
        """
        if not value or not value in CURRENCIES:
            value = self.default

        ObjectField.set(self, instance, value, **kwargs)

registerField(CurrencyField,
              title='Currency',
              description='Used for storing currency codes')
