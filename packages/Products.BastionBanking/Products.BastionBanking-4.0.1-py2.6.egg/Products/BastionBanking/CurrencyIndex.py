#
#    Copyright (C) 2008-2011  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from types import IntType
import logging
logger = logging.getLogger('UnIndex')

import BTrees.Length
from BTrees.IIBTree import IISet, union, intersection, multiunion
from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree
from ZCurrency import CURRENCIES, ZCurrency, UnsupportedCurrency
from App.special_dtml import DTMLFile
from OFS.PropertyManager import PropertyManager
from ZODB.POSException import ConflictError
from zope.interface import implements

from Products.PluginIndexes.common import safe_callable
from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.PluginIndexes.common.util import parseIndexRequest
from Products.BastionBanking.interfaces.ICurrencyIndex import ICurrencyIndex

_marker = []

try:
    import Products.BastionCurrencyTool
    MULTI_CURRENCY_SUPPORT=True
except ImportError:
    MULTI_CURRENCY_SUPPORT=False

class CurrencyIndex(UnIndex, PropertyManager):
    """
    Index for currencies (ie ordered amounts).
    """

    implements(ICurrencyIndex)

    meta_type = 'CurrencyIndex'
    query_options = ['query', 'range']

    base_currency = 'USD'
    convert_to_base = True


    _properties=(
        {'id':'base_currency',   'type':'selection', 'mode':'w', 'select_variable': 'currencies'},
        {'id':'convert_to_base', 'type':'boolean',   'mode':'w'},
        )

    manage = manage_main = DTMLFile( 'dtml/manageCurrencyIndex', globals() )
    manage_browse = DTMLFile('dtml/browseIndex', globals())

    manage_main._setName( 'manage_main' )
    manage_options = ( { 'label' : 'Settings'
                       , 'action' : 'manage_main'
                       },
                       {'label': 'Browse',
                        'action': 'manage_browse',
                       },
                     ) + PropertyManager.manage_options

    def __init__(self, id, ignore_ex=None, call_methods=None, extra=None, caller=None):
        UnIndex.__init__(self, id, ignore_ex, call_methods, extra, caller)
        if extra:
            if extra.has_key('base_currency'):
                self.base_currency = extra['base_currency']
        
    def currencies(self):
        """
        property manager helper
        """
        return CURRENCIES

    def clear( self ):
        """ Complete reset """
        self._index = OOBTree()
        self._unindex = IOBTree()
        self._length = BTrees.Length.Length()

    def index_object( self, documentId, obj, threshold=None ):
        """index an object, normalizing the indexed value to an integer

           o Normalized value has granularity of one minute.

           o Objects which have 'None' as indexed value are *omitted*,
             by design.
        """
        returnStatus = 0

        try:
            currency_attr = getattr( obj, self.id )
            if safe_callable( currency_attr ):
                currency_attr = currency_attr()
            converted = self._convert(value=currency_attr, default=_marker)
        except AttributeError:
            converted = _marker

        old = self._unindex.get( documentId, _marker )

        if converted != old:
            if old is not _marker:
                self.removeForwardIndexEntry(old, documentId)
                if converted is _marker:
                    try:
                        del self._unindex[documentId]
                    except ConflictError:
                        raise
                    except:
                        logger.error(
                            ("Should not happen: ConvertedDate was there,"
                             " now it's not, for document with id %s" %
                             documentId))

            if converted is not _marker:
                self.insertForwardIndexEntry( converted, documentId )
                self._unindex[documentId] = converted

            returnStatus = 1

        return returnStatus

    def _apply_index( self, request, cid='', type=type ):
        """Apply the index to query parameters given in the argument
        """
        record = parseIndexRequest( request, self.id, self.query_options )
        if record.keys == None:
            return None

        keys = map(self._convert, record.keys)

        index = self._index
        r = None
        opr = None

        #experimental code for specifing the operator
        operator = record.get( 'operator', self.useOperator )
        if not operator in self.operators :
            raise RuntimeError, "operator not valid: %s" % operator

        # depending on the operator we use intersection or union
        if operator=="or":
            set_func = union
        else:
            set_func = intersection

        # range parameter
        range_arg = record.get('range',None)
        if range_arg:
            opr = "range"
            opr_args = []
            if range_arg.find("min") > -1:
                opr_args.append("min")
            if range_arg.find("max") > -1:
                opr_args.append("max")

        if record.get('usage',None):
            # see if any usage params are sent to field
            opr = record.usage.lower().split(':')
            opr, opr_args = opr[0], opr[1:]

        if opr=="range":   # range search
            if 'min' in opr_args:
                lo = min(keys)
            else:
                lo = None

            if 'max' in opr_args:
                hi = max(keys)
            else:
                hi = None

            if hi:
                setlist = index.values(lo,hi)
            else:
                setlist = index.values(lo)

            #for k, set in setlist:
                #if type(set) is IntType:
                    #set = IISet((set,))
                #r = set_func(r, set)
            # XXX: Use multiunion!
            r = multiunion(setlist)

        else: # not a range search
            for key in keys:
                # TODO - do some funky MultiCurrency conversion using BastionCurrencyTool!!!
                set = index.get(key, None)
                if set is not None:
                    if type(set) is IntType:
                        set = IISet((set,))
                    r = set_func(r, set)

        if type(r) is IntType:
            r = IISet((r,))

        if r is None:
            return IISet(), (self.id,)
        else:
            return r, (self.id,)

    def _convert( self, value, default=None ):
        """Convert ZCurrency value to our base currency type so that equality comparisons make
        some sense.  A reindex in effect revalues the """
        if not isinstance(value, ZCurrency):
            value = ZCurrency(value)

        if value.currency() != self.base_currency:
            if not MULTI_CURRENCY_SUPPORT:
                # bummer - currency compare will kill us!!
                return default

            currency_tool = self.Control_Panel.CurrencyTool
            try:
                rate = currency_tool.getCrossQuote(value.currency(), self.base_currency).mid
            except UnsupportedCurrency:
                # doh - no rate
                return default
            
            return ZCurrency(self.base_currency, rate * value.amount())
            
        return value

manage_addCurrencyIndexForm = DTMLFile( 'dtml/addCurrencyIndex', globals() )

def manage_addCurrencyIndex( self, id, REQUEST=None, RESPONSE=None, URL3=None):
    """Add a Date index"""
    return self.manage_addIndex(id, 'CurrencyIndex', extra=None, \
                    REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
