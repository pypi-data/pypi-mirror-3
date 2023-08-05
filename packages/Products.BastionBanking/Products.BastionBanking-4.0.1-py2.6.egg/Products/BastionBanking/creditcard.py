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
import operator
try:
    from DateTime import DateTime
except ImportError:
    from datetime import datetime as DateTime

class CreditCardException(Exception): pass
class CreditCardInvalid(CreditCardException): pass    
class CreditCardExpired(CreditCardException): pass

class creditcard:
    """
    A creditcard object.

    Type should be derivable from number shouldn't it ???

    The cvv2 field is the 3 or 4 digit code printed on the back of the card
    used as partial assurance the card is in the purchaser's possession.
    
    This class is attempting to be both Python and Zope friendly ...
    """
    def __init__(self, number, expiry, typ='', name='', cvv2=''):
        # expiry could be a complex object coerceable into a DateTime ...
        if isinstance(expiry, DateTime):
            self.expiry = expiry
        else:
	    # oh well, lets try and coerce it ...
            self.expiry = DateTime(expiry)
        self.type = typ
	for special in (' ', '-'):
            number = number.replace(special,'')
        self.number = number
        if not self.number.isdigit() or len(self.number) < 13 or len(self.number) > 16:
            raise CreditCardInvalid, 'card number contains alphabet chars or is incorrect length'
        self.name = name
        self.cvv2 = cvv2

    def __str__(self):
        """
        mask card - this is as specified by VISA International in
        http://usa.visa.com/download/business/accepting_visa/ops_risk_management/cisp_PCI_Data_Security_Standard.pdf
        """
        if self.name:
            return '%s-%sXX-XXXX-%s (%s)' % (self.number[0:4], self.number[4:6], self.number[-4:], self.name)
        else:
            return '%s-%sXX-XXXX-%s' % (self.number[0:4], self.number[4:6], self.number[-4:])

    def __repr__(self):
        return '<creditcard %s (%s)>' % (self.number, self.expiry)
    
    def validate(self, date=None):
        """
        hmmm - do some modulus checking etc etc ... - throw exceptions with
        appropriate messages if there's a problem ...
        """
        # hmmm - we might not be called within the context of Zope, convert to datetime ...
        # also we need to make the date the end-of-month ...
        if not date:
            try:
                today = DateTime()
                if today.mm() == 12:
                    date = DateTime('%s/12/31: 23:59' % today.year())
                else:
                    date = DateTime('%s/%s/01: 23:59' % (today.year(), today.mm())) - 1
            except:
                # TODO - fix none Zope DateTime ...
                date = DateTime.now()
                
        if self.expiry < date:
            raise CreditCardExpired, 'card expired'

        try:
            if self.luhn_checksum():
                raise CreditCardInvalid, 'failed checksum'
        except Exception, e:
            raise CreditCardInvalid, str(e)

    def luhn_checksum(self):
        """
        return the luhn checksum of this card number
        """
        digits = map(int, self.number)
        odds, evens = digits[-2::-2], digits[-1::-2]
        return reduce(operator.add, map(lambda digit: sum(divmod( digit*2, 10 )), odds) + evens) % 10
