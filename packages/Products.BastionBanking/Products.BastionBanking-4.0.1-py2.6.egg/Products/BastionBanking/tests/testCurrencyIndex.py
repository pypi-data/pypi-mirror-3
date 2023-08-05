#
#    Copyright (C) 2008  Corporation of Balclutha. All rights Reserved.
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

import os, sys, unittest
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing.ZopeTestCase import installProduct, ZopeTestCase
from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionBanking.CurrencyIndex import CurrencyIndex, MULTI_CURRENCY_SUPPORT

installProduct('BastionBanking')
installProduct('PluginIndexes')

if MULTI_CURRENCY_SUPPORT:
    installProduct('BastionCurrencyTool')

class Dummy:

    def __init__(self, name, currency):

        self._name  = name
        self._currency = currency

    def name(self):
        return self._name

    def currency(self):
        return self._currency

    def __str__(self):
        return "<Dummy %s, currency %s>" % (self._name, str(self._currency))



class CI_Tests(ZopeTestCase):
    def afterSetUp(self):
        self._values = [
            (1, Dummy('b', ZCurrency('AUD 10.00'))),
            (2, Dummy('c', ZCurrency('AUD 20.00'))), 
            (3, Dummy('d', ZCurrency('AUD 30.00'))),
        ]
        self.app._setObject('currency',
                            CurrencyIndex('currency',extra={'base_currency':'AUD'}))

        self._index = self.app.currency
        
        self._noop_req  = {'bar': 123}
        self._request   = {'currency': {'query': ZCurrency('AUD 20.00')}}
        self._min_req   = {'currency': {'query': ZCurrency('AUD 30.00'),
                                        'range': 'min'}}
        self._max_req   = {'currency': {'query': ZCurrency('AUD 10.00'),
                                        'range': 'max'}}
        self._range_req = {'currency': {'query':(ZCurrency('AUD 10.00'),
                                                 ZCurrency('AUD 20.00')),
                                        'range': 'min:max'}}

    def _populateIndex( self ):
        for k, v in self._values:
            self._index.index_object(k, v)

    def _checkApply(self, req, expectedValues):
        result, used = self._index._apply_index(req)
        if hasattr(result, 'keys'):
            result = result.keys()
        self.failUnlessEqual(used, ('currency',))
        self.failUnlessEqual(len(result), len(expectedValues),
            '%s | %s' % (result, expectedValues))
        for k, v in expectedValues:
            self.failUnless(k in result)

    def testBaseCurrency(self):
        self.assertEqual(self._index.getProperty('base_currency'), 'AUD')

    def test_z3interfaces(self):
        from Products.BastionBanking.interfaces.ICurrencyIndex import ICurrencyIndex
        from Products.PluginIndexes.interfaces import IPluggableIndex
        from Products.PluginIndexes.interfaces import ISortIndex
        from Products.PluginIndexes.interfaces import IUniqueValueIndex
        from zope.interface.verify import verifyClass

        verifyClass(ICurrencyIndex, CurrencyIndex)
        verifyClass(IPluggableIndex, CurrencyIndex)
        verifyClass(ISortIndex, CurrencyIndex)
        verifyClass(IUniqueValueIndex, CurrencyIndex)

    def test_empty(self):
        empty = self._index

        self.failUnlessEqual(len(empty), 0)
        self.failUnlessEqual(len(empty.referencedObjects()), 0)

        self.failUnless(empty.getEntryForObject(1234) is None)
        marker = []
        self.failUnless(empty.getEntryForObject(1234, marker) is marker)
        empty.unindex_object(1234) # shouldn't throw

        self.failUnless(empty.hasUniqueValuesFor('currency'))
        self.failIf(empty.hasUniqueValuesFor('foo'))
        self.failUnlessEqual(len(empty.uniqueValues('currency')), 0)

        self.failUnless(empty._apply_index({'zed': 12345}) is None)

        self._checkApply(self._request, [])
        self._checkApply(self._min_req, [])
        self._checkApply(self._max_req, [])
        self._checkApply(self._range_req, [])

    def test_retrieval( self ):
        self._populateIndex()
        values = self._values
        index = self._index

        self.failUnlessEqual(len(index), len(values))
        self.failUnlessEqual(len(index.referencedObjects()), len(values))

        self.failUnless(index.getEntryForObject(1234) is None)
        marker = []
        self.failUnless(index.getEntryForObject(1234, marker) is marker)
        index.unindex_object(1234) # shouldn't throw

        for k, v in values:
            if v.currency():
                self.failUnlessEqual(self._index.getEntryForObject(k),
                                     v.currency())

        self.failUnlessEqual(len(index.uniqueValues('currency')), len(values))
        self.failUnless(index._apply_index(self._noop_req) is None)

        self._checkApply(self._request, values[1:2])
        self._checkApply(self._min_req, values[2:])
        self._checkApply(self._max_req, values[:1])
        self._checkApply(self._range_req, values[:2] )


    def test_removal(self):
        """ DateIndex would hand back spurious entries when used as a
            sort_index, because it previously was not removing entries
            from the _unindex when indexing an object with a value of
            None. The catalog consults a sort_index's
            documentToKeyMap() to build the brains.
        """
        values = self._values
        index = self._index
        self._populateIndex()
        index.index_object(3, None)
        self.failIf(3 in index.documentToKeyMap().keys())

class MultiCurrencyTest(CI_Tests):
    """
    TODO - we need to figure out how to hook BastionCurrencyTool into this
    """

    # this sets us up just fine, but we've got to figure out where to manage
    # the currency conversion in CurrencyTool
    def afterSetUp(self):
        CI_Tests.afterSetUp(self)
        ct = self.app.Control_Panel.CurrencyTool
        ct._updateProperty('automagic', True)
        ct._updateProperty('base', 'AUD')
        # let's say $1 USD buys $1.1001 Aussie dollars 
        ct._addQuote('USD', None, None, 1.1001, DateTime(0))

        self.usd = Dummy('z', ZCurrency('USD 50.00'))
        
    def testMultiCurrency(self):

        self._populateIndex()
        self._index.index_object(4, self.usd)

        values = self._values
        values.append((4, self.usd))
        
        # make sure we stuffed our converted currency into the index
        self.failUnlessEqual(len(self._index.uniqueValues('currency')), 4)

        self._checkApply(self._request, values[1:2])
        self._checkApply(self._min_req, values[2:])
        self._checkApply(self._max_req, values[:1])
        self._checkApply(self._range_req, values[:2] )

    def testCrossRate(self):
        self.assertEqual(self.app.Control_Panel.CurrencyTool.getCrossQuote('USD', 'AUD').mid, 1.1001)

        self.assertEqual(self._index._convert(ZCurrency('AUD 10.00')), ZCurrency('AUD 10.00'))
        self.assertEqual(self._index._convert(ZCurrency('USD 10.00')), ZCurrency('AUD 11.00'))

    def testReindexRevalues(self):

        self._index.index_object(4, self.usd)

        self.assertEqual(self._index.uniqueValues('currency'),
                         (ZCurrency('AUD 55.01'),))

        # double the exchange rate some time later ...
        self.app.Control_Panel.CurrencyTool._addQuote('USD', None, None, 2.0001, DateTime())

        self._index.index_object(4, self.usd)

        self.assertEqual(self._index.uniqueValues('currency'),
                         (ZCurrency('AUD 100.01'),))
        
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( CI_Tests ) )
    if MULTI_CURRENCY_SUPPORT:
        suite.addTest( unittest.makeSuite( MultiCurrencyTest ) )
        
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
