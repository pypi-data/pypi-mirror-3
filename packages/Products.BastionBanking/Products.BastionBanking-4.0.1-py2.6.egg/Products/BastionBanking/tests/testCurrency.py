import unittest


# run setup.py first !!
from currency import currency, currency_match

class CurrencyTest(unittest.TestCase):

    def testRE(self):
        self.failUnless(currency_match.match(' GBP '))
        self.failUnless(currency_match.match(' 12.34 '))
        self.failUnless(currency_match.match(' -12.34 '))

    def testStringFirst(self):
        self.failUnless( currency('GBP', 12.34) )

    def testAmountFirst(self):
        self.failUnless( currency(-12.34, 'GBP') )

    def testString(self):
        self.failUnless( currency('GBP12.34') )

    def testStringCommas(self):
        self.failUnless( currency('GBP12,444,445.34') )

    def testStringGap(self):
        self.failUnless( currency('GBP -12.34') )

    def testArithmeticSign(self):
        self.failUnless( currency('-GBP 12.34') )
        self.failUnless( currency('+GBP 12.34') )
        self.assertEqual( currency('GBP 12.34'), currency('+GBP -12.34') )
        self.assertEqual( currency('GBP 12.34'), currency('+GBP +12.34') )
        self.assertEqual( currency('-GBP 12.34'), currency('GBP -12.34') )
        self.assertEqual( currency('-GBP 12.34'), currency('-GBP -12.34') )

    def testBracketSign(self):
        self.failUnless( currency('(GBP 12.34)') )
        self.assertEqual( currency('(GBP 12.34)'), currency('-GBP 12.34'))

    def testAmountStr(self):
        # verify it retains the trailing zero ..
        self.assertEqual( currency('GBP 0.10').amount_str(), '0.10')

    def testAdd(self):
        amt = currency('GBP12.34')
        self.assertEqual(amt+amt, currency('GBP24.68'))

    def testAddBadCurrencies(self):
        amt = currency('GBP12.34')
	self.assertRaises(ArithmeticError, amt.__add__, currency('USD 12.34'))

    def testAddZero(self):
        amt = currency('GBP12.34')
	self.assertEqual(amt + currency('USD 0.00'), amt)

    def testSub(self):
        amt = currency('GBP12.34')
        self.assertEqual(amt-amt, currency('GBP0.00'))

    def testSubBadCurrencies(self):
        amt = currency('GBP12.34')
	self.assertRaises(ArithmeticError, amt.__sub__, currency('USD 12.34'))

    def testSubZero(self):
        amt = currency('GBP12.34')
	self.assertEqual(amt-currency('USD 0.00'), amt)

    def testMul(self):
        amt = currency('GBP12.34')
        self.assertEqual(amt*2, currency('GBP24.68'))

    def testMulBadCurrencies(self):
        amt = currency('GBP12.34')
	self.assertRaises(ArithmeticError, amt.__mul__, currency('USD 12.34'))

    def teststrfcur(self):
        self.assertEqual(currency('GBP-1.00').strfcur(), '(GBP 1.00)')
        self.assertEqual(currency('GBP1.00').strfcur(), ' GBP 1.00 ')
        self.assertEqual(currency('GBP10.00').strfcur(), ' GBP 10.00 ')
        self.assertEqual(currency('GBP100.00').strfcur(), ' GBP 100.00 ')
        self.assertEqual(currency('GBP1000.00').strfcur(), ' GBP 1,000.00 ')
        self.assertEqual(currency('GBP10000.00').strfcur(), ' GBP 10,000.00 ')
        self.assertEqual(currency('GBP100000.00').strfcur(), ' GBP 100,000.00 ')
        self.assertEqual(currency('GBP1000000.00').strfcur(), ' GBP 1,000,000.00 ')
        self.assertEqual(currency('GBP10000000.00').strfcur(), ' GBP 10,000,000.00 ')
        self.assertEqual(currency('GBP100000000.00').strfcur(), ' GBP 100,000,000.00 ')

        self.assertEqual(currency('GBP 1.00').strfcur('%c'), 'GBP')
        self.assertEqual(currency('GBP 1.00').strfcur('%c %0.2f'), 'GBP 1.00')
        self.assertEqual(currency('GBP 1.00').strfcur('%c %0.5f'), 'GBP 1.00000')
        self.assertEqual(currency('(GBP 1.00)').strfcur('%c %+0.0f'), 'GBP -1')
        
    def testEquality(self):
        a = currency('GBP10.00')
        b = currency('GBP', 10.00)
        self.assertEqual(a, b)

    def testInequality(self):
        a = currency('AUD10.01')
        b = currency('AUD', 10.00)
        c = currency('AUD', -10.00)
        self.failUnless(a != b)
        self.failUnless(b != c)

    def testGreaterLessThan(self):
        a = currency('AUD10.00')
        b = currency('AUD12.00')
        c = currency('AUD0.00')
        self.failUnless(a < b)
        self.failUnless(b > a)
        self.failUnless(a > 0)
        self.failUnless(c == 0)

    def testHash(self):
        my_dict = { currency('AUD10.00'):'yahooo!' }
        self.failUnless(1)

    def testRound(self):
        self.assertEqual( round(currency('AUD10.50')), currency('AUD11.00'))
        self.assertEqual( round(currency('AUD10.49')), currency('AUD10.00'))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(CurrencyTest))
    return suite
        
if __name__ == '__main__':
    unittest.main()

