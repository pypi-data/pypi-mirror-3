#
#    Copyright (C) 2003-2009  Corporation of Balclutha.  All rights reserved.
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
__version__='$Revision: 185 $'[11:-2]
import types, re, string

#
# currency is described as:
#     Match Group     Designation
#          1          sign of currency (optional) represented by +, - or enclosed in ( )
#          2          currency code, (optional, if missing, accepts default as per env var)
#          3          fill
#          4          amount, may contain spaces and/or commas which will be parsed out
#          5          optional ) closure for a credit value
#
#                                  1             2                          3    4                    5
currency_match = re.compile(r'^\s*([\(\+\-])?\s*([A-Za-z][A-Za-z][A-Za-z])?(\s*)([-+]?[\d\.\, ]+)?\s*([\)])?\s*$')

#
# A single definitive dictionary of currency information - create global functions
# and then only edit this structure ...
#
# this should be something along the lines of ISO 4217
#
# http://www.iso.org/iso/support/faqs/faqs_widely_used_standards/widely_used_standards_other/currency_codes/currency_codes_list-1.htm
#
_CURRENCY_META = {
    'Afghanistan' : 'AFA',
    'Albania' : 'ALL',
    'Algeria' : 'DZD',
    'American Samoa' : 'USD',
    'Andorra' : 'EUR',
    'Angola' : 'AOA',
    'Anguilla' : 'XCD',
    'Antigua and Barbuda' : 'XCD',
    'Argentina' : 'ARS',
    'Armenia' : 'AMD',
    'Aruba' : 'AWG',
    'Australia' : 'AUD',
    'Austria' : 'EUR',
    'Azerbaijan' : 'AZM',
    'Bahamas, The' : 'BSD',
    'Bahrain' : 'BHD',
    'Bangladesh' : 'BDT',
    'Barbados' : 'BBD',
    'Belarus' : 'BYR',
    'Belgium' : 'EUR',
    'Benin' : 'XOF',
    'Bermuda' : 'BMD',
    'Bhutan' : 'BTN; INR',
    'Bolivia' : 'BOB',
    'Bosnia and Herzegovina' : 'BAM',
    'Botswana' : 'BWP',
    'Brazil' : 'BRL',
    'British Virgin Islands' : 'USD',
    'Brunei' : 'BND',
    'Bulgaria' : 'BGL',
    'Burkina Faso' : 'XOF',
    'Burma' : 'MMK',
    'Burundi' : 'BIF',
    'Cambodia' : 'KHR',
    'Cameroon' : 'XAF',
    'Canada' : 'CAD',
    'Cape Verde' : 'CVE',
    'Cayman Islands' : 'KYD',
    'Central African Republic' : 'XAF',
    'Chad' : 'XAF',
    'Chile' : 'CLP',
    'China' : 'CNY',
    'Christmas Island' : 'AUD',
    'Cocos (Keeling) Islands' : 'AUD',
    'Colombia' : 'COP',
    'Comoros' : 'KMF',
    'Congo, Democratic Republic of the' : 'CDF',
    'Congo, Republic of the' : 'XAF',
    'Cook Islands' : 'NZD',
    'Costa Rica' : 'CRC',
    'Cote dIvoire' : 'XOF',
    'Croatia' : 'HRK',
    'Cuba' : 'CUP',
    'Cyprus' : 'CYP; TRL',
    'Czech Republic' : 'CZK',
    'Denmark' : 'DKK',
    'Djibouti' : 'DJF',
    'Dominica' : 'XCD',
    'Dominican Republic' : 'DOP',
    'East Timor' : 'USD',
    'Ecuador' : 'USD',
    'Egypt' : 'EGP',
    'El Salvador' : 'SVC; USD',
    'Equatorial Guinea' : 'XAF',
    'Eritrea' : 'ERN',
    'Estonia' : 'EEK',
    'Ethiopia' : 'ETB',
    'Falkland Islands (Islas Malvinas)' : 'FKP',
    'Faroe Islands' : 'DKK',
    'Fiji' : 'FJD',
    'Finland' : 'FIM; EUR',
    'France' : 'EUR',
    'French Guiana' : 'EUR',
    'French Polynesia' : 'XPF',
    'Gabon' : 'XAF',
    'Gambia, The' : 'GMD',
    'Gaza Strip' : 'ILS',
    'Georgia' : 'GEL',
    'Germany' : 'EUR',
    'Ghana' : 'GHC',
    'Gibraltar' : 'GIP',
    'Greece' : 'EUR; GRD',
    'Greenland' : 'DKK',
    'Grenada' : 'XCD',
    'Guadeloupe' : 'EUR',
    'Guam' : 'USD',
    'Guatemala' : 'GTQ; USD',
    'Guernsey' : 'GBP',
    'Guinea' : 'GNF',
    'Guinea-Bissau' : 'XOF; GWP',
    'Guyana' : 'GYD',
    'Haiti' : 'HTG',
    'Holy See (Vatican City)' : 'EUR',
    'Honduras' : 'HNL',
    'Hong Kong' : 'HKD',
    'Hungary' : 'HUF',
    'Iceland' : 'ISK',
    'India' : 'INR',
    'Indonesia' : 'IDR',
    'Iran' : 'IRR',
    'Iraq' : 'IQD',
    'Ireland' : 'EUR',
    'Israel' : 'ILS',
    'Italy' : 'EUR',
    'Jamaica' : 'JMD',
    'Japan' : 'JPY',
    'Jersey' : 'GBP',
    'Jordan' : 'JOD',
    'Kazakhstan' : 'KZT',
    'Kenya' : 'KES',
    'Kiribati' : 'AUD',
    'Korea, North' : 'KPW',
    'Korea, South' : 'KRW',
    'Kuwait' : 'KWD',
    'Kyrgyzstan' : 'KGS',
    'Laos' : 'LAK',
    'Latvia' : 'LVL',
    'Lebanon' : 'LBP',
    'Lesotho' : 'LSL; ZAR',
    'Liberia' : 'LRD',
    'Libya' : 'LYD',
    'Liechtenstein' : 'CHF',
    'Lithuania' : 'LTL',
    'Luxembourg' : 'EUR',
    'Macau' : 'MOP',
    'Macedonia, The Former Yugoslav Republic of' : 'MKD',
    'Madagascar' : 'MGF',
    'Malawi' : 'MWK',
    'Malaysia' : 'MYR',
    'Maldives' : 'MVR',
    'Mali' : 'XOF',
    'Malta' : 'MTL',
    'Man, Isle of' : 'GBP',
    'Marshall Islands' : 'USD',
    'Martinique' : 'EUR',
    'Mauritania' : 'MRO',
    'Mauritius' : 'MUR',
    'Mayotte' : 'EUR',
    'Mexico' : 'MXN',
    'Micronesia, Federated States of' : 'USD',
    'Moldova' : 'MDL',
    'Monaco' : 'EUR',
    'Mongolia' : 'MNT',
    'Montserrat' : 'XCD',
    'Morocco' : 'MAD',
    'Mozambique' : 'MZM',
    'Namibia' : 'NAD; ZAR',
    'Nauru' : 'AUD',
    'Nepal' : 'NPR',
    'Netherlands' : 'EUR',
    'Netherlands Antilles' : 'ANG',
    'New Caledonia' : 'XPF',
    'New Zealand' : 'NZD',
    'Nicaragua' : 'NIO',
    'Niger' : 'XOF',
    'Nigeria' : 'NGN',
    'Niue' : 'NZD',
    'Norfolk Island' : 'AUD',
    'Northern Mariana Islands' : 'USD',
    'Norway' : 'NOK',
    'Oman' : 'OMR',
    'Pakistan' : 'PKR',
    'Palau' : 'USD',
    'Panama' : 'PAB; USD',
    'Papua New Guinea' : 'PGK',
    'Paraguay' : 'PYG',
    'Peru' : 'PEN',
    'Philippines' : 'PHP',
    'Pitcairn Islands' : 'NZD',
    'Poland' : 'PLN',
    'Portugal' : 'EUR',
    'Puerto Rico' : 'USD',
    'Qatar' : 'QAR',
    'Reunion' : 'EUR',
    'Romania' : 'ROL',
    'Russia' : 'RUR',
    'Rwanda' : 'RWF',
    'Saint Helena' : 'SHP',
    'Saint Kitts and Nevis' : 'XCD',
    'Saint Lucia' : 'XCD',
    'Saint Pierre and Miquelon' : 'EUR',
    'Saint Vincent and the Grenadines' : 'XCD',
    'Samoa' : 'WST',
    'San Marino' : 'EUR',
    'Sao Tome and Principe' : 'STD',
    'Saudi Arabia' : 'SAR',
    'Senegal' : 'XOF',
    'Seychelles' : 'SCR',
    'Sierra Leone' : 'SLL',
    'Singapore' : 'SGD',
    'Slovakia' : 'SKK',
    'Slovenia' : 'SIT',
    'Solomon Islands' : 'SBD',
    'Somalia' : 'SOS',
    'South Africa' : 'ZAR',
    'Spain' : 'EUR',
    'Sri Lanka' : 'LKR',
    'Sudan' : 'SDD',
    'Suriname' : 'SRG',
    'Svalbard' : 'NOK',
    'Swaziland' : 'SZL',
    'Sweden' : 'SEK',
    'Switzerland' : 'CHF',
    'Syria' : 'SYP',
    'Taiwan' : 'TWD',
    'Tajikistan' : 'SM',
    'Tanzania' : 'TZS',
    'Thailand' : 'THB',
    'Togo' : 'XOF',
    'Tokelau' : 'NZD',
    'Tonga' : 'TOP',
    'Trinidad and Tobago' : 'TTD',
    'Tunisia' : 'TND',
    'Turkey' : 'TRL',
    'Turkmenistan' : 'TMM',
    'Turks and Caicos Islands' : 'USD',
    'Tuvalu' : 'AUD',
    'Uganda' : 'UGX',
    'Ukraine' : 'UAH',
    'United Arab Emirates' : 'AED',
    'United Kingdom' : 'GBP',
    'United States' : 'USD',
    'Uruguay' : 'UYU',
    'Uzbekistan' : 'UZS',
    'Vanuatu' : 'VUV',
    'Venezuela' : 'VEB',
    'Vietnam' : 'VND',
    'Virgin Islands' : 'USD',
    'Wallis and Futuna' : 'XPF',
    'West Bank' : 'ILS; JOD',
    'Western Sahara' : 'MAD',
    'Yemen' : 'YER',
    'Yugoslavia' : 'YUM',
    'Zambia' : 'ZMK',
    'Zimbabwe' : 'ZWD',
}

#
# a global of defined currency codes
#
CURRENCIES = []

#from ISO 4217
_CURRENCY_DECIMALS = {
    'BHD':3, 'BIF':0, 'BYR':0, 'CLP':0, 'DJF':0, 'GNF':0, 'IQD':3,
    'JOD':3, 'JPY':0, 'KMF':0, 'KRW':0, 'KWD':3, 'LYD':3, 'OMR':3,
    'PYG':0, 'RWF':0, 'TND':3, 'VUV':0, 'XAF':0,
    'XDR':5, # Special Drawing Rights
    'XOF':0,    'XPF':0,
}

for code in _CURRENCY_META.values():
    # hmmm - maybe we should use a more informed structure for the meta data ...
    if code.find(';') != -1:
        for c in  code.split(';'):
            c = c.strip()
            if not c in CURRENCIES:
                CURRENCIES.append(c)
    else:
        if not code in CURRENCIES:
            CURRENCIES.append(code)
    CURRENCIES.sort()

class UnsupportedCurrency(TypeError):
    """
    An unsupported currency
    """
    pass


# global functions

def valid_currency(code):
    """
    returns whether the currency code is a valid currency code
    """
    return code in CURRENCIES

def decimals(code):
    """
    returns the number of decimal places for a currency code
    """
    if not valid_currency(code):
        raise UnsupportedCurrency, code
    return _CURRENCY_DECIMALS.get(code, 2)

class currency:
    """
    A Builtin-Python Currency Type

    A Currency is described by a base and an amount.  A base is a three-letter country
    code, and the amount should probably be a float ...
    """

    # there's a few currencies that don't have cents, but we're going to force *all*
    # mathematical operations on currencies to return 100% truncated cents values ...
    decimal_places = 2

    # allow a base currency to be set in a derived class ...
    _currency = ''

    def __init__(self, *args):
        self._amount = 0.0
        for arg in args:
            # if we get this from our form widget, then it's a list of strings :(
            try:
                arg = round(float(arg), self.decimal_places)
            except:
                pass
            if type(arg) == types.StringType:
                if len(arg) == 3:
                    self._currency = arg.upper()
                else:
                    match = currency_match.match(arg)
                    if match:
                        self._currency = match.group(2).upper()
			amount = match.group(4)
			amount = amount.replace(',','') # remove commas
			amount = amount.replace(' ','') # remove spaces
                        if amount:
                            try:
                                amount = round(float(amount), self.decimal_places)
                            except:
                                raise TypeError, "cannot coerce amount: %s" % amount
                        if match.group(1) == '+':
                            amount = abs(amount)
                        elif match.group(1) == '-' or match.group(1) == '(' and match.group(5) == ')' :
                            amount = abs(amount) * -1
                        self._amount = amount
                    else:
                        raise TypeError, "cannot coerce string to currency: %s" % arg
            elif type(arg) in ( types.FloatType, types.IntType, types.LongType):
                self._amount = round(float(arg), self.decimal_places)
            elif hasattr(arg, '_currency') and hasattr(arg, '_amount'):
                self._currency = arg._currency
                # coerce amount again just in case this wasn't a currency  type ...
                self._amount = round(float(arg._amount), self.decimal_places)
            else:
                raise UnsupportedCurrency, "(%s) [%s]" % (str(arg), 
                                                       getattr(arg, '__dict__', {}))
        if self._currency not in CURRENCIES:
            raise AttributeError, "Invalid Currency Code: %s" % self._currency
        
    def __add__(self, other):
        if type(other) in ( types.FloatType, types.IntType, types.LongType):
            return currency(self._currency, self._amount + other)
        elif isinstance(other, currency) or hasattr(other, '_currency') and hasattr(other, '_amount'):
            if self._currency == other._currency:
                return currency(self._currency, self._amount + other._amount)
            elif other._amount == 0:
	        return self
            raise ArithmeticError, "Currency Code Mismatch %s != %s" % (self, other)
        else:
            try:
                # attempted coercion
                tmp = currency(other)
                return self + tmp # note we're returning a self's currency base ...
            except:
                raise
                raise UnsupportedCurrency, type(other)

    def __sub__(self, other):
        return self.__add__(-(other))

    def __cmp__(self, other):
        """
        comparisons are a little ridiculous as these are face-value, and really should
        only be used for equality checking
        """
        if type(other) in ( types.FloatType, types.IntType, types.LongType):
            return cmp(self._amount, other)
        elif isinstance(other, currency) or hasattr(other, '_currency') and hasattr(other, '_amount'):
            if self._currency != other._currency and (self._amount != 0 or other._amount != 0):
                raise UnsupportedCurrency, other.currency()
            return cmp(self._amount, other._amount)
        else:
            # hmmm - this must work for inequalities, tests against None etc etc ...
            #raise TypeError, "Not supported for this type: %s (%s)" % (type(other), other)
            return -1

    def __mul__(self, other):
        if type(other) in [types.FloatType, types.IntType, types.LongType]:
            #print "currency::__mul__ %s * %s %s = %s" % (str(self._amount), str(other), type(other), str(self._amount * other))
            return currency(self._currency, self._amount * other)
        elif isinstance(other, currency) or hasattr(other, '_currency') and hasattr(other, '_amount'):
            if self._currency != other._currency and other._amount != 0:
                raise ArithmeticError, 'cannot multiply unequal currency bases: %s, %s' % (self, other)
            return currency(self._currency, self._amount * other._amount)
        else:
            raise TypeError, "Not supported for this type (%s)" % type(other)
        
    def __div__(self, other):
        if type(other) in ( types.FloatType, types.IntType, types.LongType):
            return currency(self._currency, self._amount / other)
        elif isinstance(other, currency) or hasattr(other, '_currency') and hasattr(other, '_amount'):
            if self._currency != other._currency :
                raise ArithmeticError, 'cannot divide unequal currency bases: %s, %s' % (self, other)
            
            return currency(self._currency, self._amount / other._amount)
        else:
            raise TypeError, type(other)

    def __neg__(self):
        return currency(self._currency, -self._amount)

    def __abs__(self):
        return currency(self._currency, abs(self._amount))

    def __pos__(self):
        return self

    def __len__(self):
        return 1

    def __str__(self):
        return self.strfcur()

    def __repr__(self):
        return self.strfcur()

    def __hash__(self):
        return str(self).__hash__()

    def strfcur(self, fmt="%a"):
        """
        Format a currency - of form XXX 9,999.00 ...

        %a  comma-separated with brackets representing a credit amount

        %c  the ISO 4217 currency code

        anything else is passed to sprintf to format the amount
        """
        #
        # TODO: implement this ...
        #
        # want to support %$ %c %f for symbol, tag, amount format ...
        #
        # the _currency attribute is a currencyType with all the formatting info known ...
        #
        if fmt.find('%a') != -1:
            amt = self.amount_str()
            commas = []
            length = len(amt)
            for i in xrange(0, length):
                commas.append(amt[i])
                index = length - i - 6  # six for last three chars + dec pt + cents
                if index > 0 and index % 3 == 1:
                    commas.append(',')

            if self < 0:
                return "(%s %s)" % (self._currency, string.join(commas, ''))
            else:
                return " %s %s " % (self._currency, string.join(commas, ''))

        if fmt.find('%c') != -1:
            result = fmt.replace('%c', self._currency)
        else:
            result = fmt

        # we've resolved everything - return ...
        if result.find('%') == -1:
            return result

        # ok throw it over to sprintf - hope it doesn't barf ...
        return result % self._amount

        
    # hmmm - this is needed to implement rounding - hope it does not cause bizarre coercion
    # side effects ...
    def __float__(self):
        return self._amount

    def currency(self): return self._currency
    def amount(self): return self._amount
    # TODO - store decimal place currency metadata ...
    def amount_str(self): return "%0.2f" % abs(self._amount)

    def decimals(self):
        """ returns the number of decimal places """
        return _CURRENCY_DECIMALS.get(self._currency, 2)
