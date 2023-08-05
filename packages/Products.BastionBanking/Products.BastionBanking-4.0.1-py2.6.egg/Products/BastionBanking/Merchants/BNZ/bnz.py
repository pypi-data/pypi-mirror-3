#    Copyright (C) 2005-2007  Corporation of Balclutha and contributors.
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
import os, unittest, atexit

# webpayclient libraries are broken on gcc4 environments :(
try:
    import  webpayclient
    if not webpayclient.init_client():
        raise txn_error(self,"Could not initialise the WebPay API.")
    atexit.register(webpayclient.free_client)
except ImportError, NameError:
    pass

#SERVER = 'trans1.buylineplus.co.nz,trans2.buylineplus.co.nz'
SERVER = 'trans2.buylineplus.co.nz'
PORT = '3007'
SUPPORTED_CURRENCIES = ('NZD', 'AUD', 'CAD', 'CHF', 'EUR', 'GBP', 'HKD', 'JPY', 'SGD', 'USD', 'ZAR')

import returncode
try:
    from DateTime import DateTime
except:
    from datetime import datetime as DateTime
    
class txn_error(Exception):
    def __init__(self,txn,exp):
        # We want to reset the transaction in the case of errors. This would
        # allow code to correct itself while keeping the transaction open
        # txn.newTXN()
        self.exp = exp
    def __str__(self):
        return self.exp

class transaction:
    """
    This is the transaction class for eFunds International WebPay Credit Card Gateway
    """
    # this is the types with lists of valid txnReqs/txnResps indexes
    # refer to the "Buy-Line+ Credit Card Transaction Specifications"
    # for detailed field descriptions
    txnTypes = {
        "PURCHASE"  : ((0,1,2,4,5),       (3,6,11,12,13,14,15,16,17,18,19,20)),
        "REFUND"    : ((0,1,2,4,5,8),     (3,6,11,12,13,14,15,16,17,20)),
        "PREAUTH"   : ((0,1,2,4,5),       (3,6,11,12,13,14,15,16,17,18,19,20)),
        "COMPLETION": ((0,1,2,4,5,7,10),  (3,6,11,12,13,14,15,16,17,)),
        "STATUS"    : ((0,1,7),           (3,)),
    }
    txnResps = [
        "RESPONSECODE", "RESPONSETEXT", "TXNREFERENCE",
        "AUTHCODE", "STAN", "SETTLEMENTDATE"
    ]
    txnReqs = [
        "INTERFACE", "TRANSACTIONTYPE", "TOTALAMOUNT", "TAXAMOUNT",
        "CARDDATA", "CARDEXPIRYDATE", "CURRENCY", "TXNREFERENCE", 
	"ORIGINALTXNREF", "AUTHCODE", "AUTHORISATIONNUMBER", 
	"PREAUTHNUMBER", "CLIENTREF", "COMMENT", 
	"MERCHANT_CARDHOLDERNAME", "MERCHANT_DESCRIPTION", 
	"TERMINALTYPE", "CVC2", "CCI", "CAVV", "EXPANDED XID", "ECI" 
    ]
    codes = [ "DEBUG", "CLIENTID", "DATA" ]
    
    def __init__(self, merchant_id, certificate, cert_pass, servers=SERVER,port=PORT, debug=0):
        """
        Initiates the Library API and creates a new bundle
        """
	# TODO - the interface doesn't seem to properly support different servers and ports ...
	if servers.find(':') != -1:
	    self.servers, self.port = servers.split(':')
	else:
            self.servers = servers
	    self.port = port
	self.merchant_id = merchant_id
	self.certificate_path = certificate
	self.certificate_pwd = cert_pass
	self.debug = debug

    def __del__(self):
        """
        Cleans up the transaction and closes it off
        """
        if getattr(self, 'txn', None):
            webpayclient.cleanup(self.txn)

    def newTXN(self):
        """
        sets up a new transaction
        """
	if getattr(self, 'txn', None):
	    webpayclient.cleanup(self.txn)

	self.txn = txn = webpayclient.newBundle()
	webpayclient.setUp(self.txn, self.servers, self.port, self.certificate_path, 
			   self.certificate_pwd, self.merchant_id)
	if self.debug:
	    #webpayclient.put(txn, webpayclient.getLPCTSTR("DEBUG"), webpayclient.getLPCTSTR("ON"))
	    webpayclient.setAttr(txn, "DEBUG", "ON")
	return txn

    def __setitem__(self,name,value=""):
        """
        treat dict context as underlying transaction
        """
        webpayclient.setAttr(self.txn, name, value)

    def __getitem__(self,name,default=None):
        """
        treat dict context as underlying transaction
        """
        if name not in self.txnResps:
            return default
        else:
            # There's a strange class-wrapped thing going on here - sometimes
            # the results come back as something other than a normal string,
            # even tho they really should be.  So, here we str anything that's
            # not a None.  None gets through untouched.
            res = webpayclient.getAttr(self.txn,name)
            if res == None:
                return default
            return str(res)

    def runTest(self,txnType,data):
        """
        Just a wrapper around run
        """
        # according to BNZ, they don't want us testing against test!!!
        return self.run(txnType,data,test=0)
    
    def run(self,txnType,data,test=0):
        """
        Runs a CC test using the test interface
        """
        # get a new webpay transaction each call - there may be the occasional
        # instance whereby attributes haven't been cleared down properly if we
        # recycle this ...
        self.newTXN()
        if txnType not in self.txnTypes.keys():
            raise txn_error(self,"Unsupported transaction type.")
        data["TRANSACTIONTYPE"] = txnType
        if test:
            data["INTERFACE"] = "TEST"
        else:
            data["INTERFACE"] = "CREDITCARD"
        # Setup the required args, erroring if any are missing
        for item in self.txnTypes[txnType][0]:
            attr = self.txnReqs[item]
            if not data.has_key(attr):
                raise txn_error(self,"Missing required attribute for txn: %s" \
                                % attr)
            self[attr] = data[attr]
        # Now setup and optional args that are in the data
        for item in self.txnTypes[txnType][1]:
            value = data.get(self.txnReqs[item],None)
            if value:
                self[self.txnReqs[item]] = value
        # We ignore all other args
        webpayclient.execute(self.txn)
	return self

    def getResponse(self):
        """
        Returns a list of response name,result from the transaction
        """
        retList = []
        for item in self.txnResps:
            retList.append( (item, self[item]) )
        return retList
    
    def getResponseDict(self):
        """
        Returns a list of response name,result from the transaction
        """
        retVal = {}
        for item in self.txnResps:
            retVal[item] = self[item]
        return retVal


class bnz:
    """
    pure python BNZ interface

    """
    def supported_currencies(self):
        return SUPPORTED_CURRENCIES

    def __init__(self):
        self.cert_file = os.path.join(os.path.dirname(__file__), 'gateway.cer')
	self.cert_password = 'asewewwd'
        self.merchant_id = '12341234'
        self.user = 'user'
        self.realm = 'realm'

    def _transaction(self):
	"""
	singleton transaction manager function
	"""
	if not getattr(self, '_v_txn', None):
	    self._v_txn = transaction(self.merchant_id, self.cert_file, self.cert_password)
	return self._v_txn

    def _pay(self, card, amount, test_mode=0):
        """
        connect to BNZ and pay ... (BNZ ignores test mode)
        """
	txn = self._transaction()
        try:
            txn.run('PURCHASE', { "CARDDATA"      : card.number,
                                  "CARDEXPIRYDATE": card.expiry.strftime('%m%y'),
                                  "TOTALAMOUNT"   : amount.amount_str(),
                                  "CURRENCY"      : amount.currency(),
                                  "CLIENTREF"     : "User: %s, Realm: %s" % (self.user, self.realm),
                                  "COMMENT"       : "CardHolder: unknown, Invoice #",
                                  "CVC2"          : '' }, 0)
        except txn_error, e:
            return returncode.returncode('', amount, -99, returncode.FATAL, str(e), '')

        try:
            rc = txn.getResponseDict()
            if rc.has_key('AUTHCODE'):
                ref = '%s (%s)' % (rc.get('TXNREFERENCE', ''), rc['AUTHCODE'])
            else:
                ref = rc.get('TXNREFERENCE', '')                             
            return returncode.returncode(ref,
                              amount,
                              rc.get('RESPONSECODE', 0),
                              returncode.OK,
                              rc.get('RESPONSETEXT', ''),
                              rc.get('RESPONSETEXT', ''))
        except txn_error, e:
            return returncode.returncode('', amount, -99, returncode.FATAL, str(e), '')

    def _refund(self, card, amount, ref, test_mode=0):
        """
        refund card - BNZ ignore's test mode ...
        """
	txn = self._transaction()
        try:
            txn.run('REFUND', { "CARDDATA"      : card.number,
                                "CARDEXPIRYDATE": card.expiry.strftime('%m%y'),
                                "TOTALAMOUNT"   : amount.amount_str(),
                                "CURRENCY"      : amount.currency(),
                                "CLIENTREF"     : "User: %s, Realm: %s" % (self.user,self.realm),
                                "COMMENT"       : "CardHolder: unknown, Invoice #",
                                "CVC2"          : '', }, 0)
        except txn_error, e:
            return returncode.returncode('', amount, -99, returncode.FATAL, str(e), '')

        try:
            rc = txn.getResponseDict()
            if rc.has_key('AUTHCODE'):
                ref = '%s - %s' % (rc.get('TXNREFERENCE', ''), rc.get('AUTHCODE', ''))
            else:
                ref = rc.get('TXNREFERENCE', '')                             
            return returncode.returncode(ref,
                              amount,
                              rc.get('RESPONSECODE', 0),
                              returncode.OK,
                              rc.get('RESPONSETEXT', ''),
                              rc.get('RESPONSETEXT', ''))
        except txn_error, e:
            return returncode.returncode('', amount, -99, returncode.FATAL, str(e), '')


    def _verify(self, card, amount, test_mode=0):
        """
        this looks like work in progress for now ...
        """
	txn = self._transaction()

        try:
            txn.run('STATUS', { "CARDDATA"      : card.number,
                                "CARDEXPIRYDATE": card.expiry.strftime('%m%y'),
                                "TOTALAMOUNT"   : str(amount.amount()),
                                "TXNREFERENCE"  :'hmmm',
                                "CLIENTREF"     : DateTime().strftime("%d/%m/%Y %H:%M:%S"),
                                "COMMENT"       : "CardHolder: unknown, Invoice #",
                                "CVC2"          : '', }, 0)
        except txn_error, e:
            return returncode.returncode('', amount, -99, returncode.FATAL, str(e), '')

        try:
            rc = txn.getResponseDict()
            if rc.has_key('AUTHCODE'):
                ref = '%s - %s' % (rc.get('TXNREFERENCE', ''), rc.get('AUTHCODE', ''))
            else:
                ref = rc.get('TXNREFERENCE', '')                          
            return returncode.returncode(ref,
                              amount,
                              rc.get('RESPONSECODE', 0),
                              returncode.OK,
                              rc.get('RESPONSETEXT', ''),
                              rc.get('RESPONSETEXT', ''))
        except txn_error, e:
            return returncode.returncode('', amount, rc, returncode.FATAL, str(e), '')
 

class bnztest(unittest.TestCase):
    """
    A wrapper containing the prescribed tests for BNZ merchant facilies
    """

    bnz = bnz()

    mcard  = '5537501010109112'
    visa   = '4564456445644564'
    invalid = '4564456445644569'
    amex   = '376000000000006'
    diners = '36123456780913'	

    def getResponseCard(self, amt, card, expiry, comment, txn_type, currency='NZD'):
        txn = self.bnz._transaction().runTest(txn_type, 
                                           {"CARDDATA"      : card,
                                            "CARDEXPIRYDATE": expiry,
                                            "TOTALAMOUNT"   : amt,
                                            "CURRENCY"      : currency,
                                            "CLIENTREF"     : "User: %s, Realm: %s" % (self.bnz.user,self.bnz.realm),
                                            "COMMENT"       : comment,
                                            "CVC2"          : ""})

	# this is a bit grubby but we're actually storing the return code ...
	self.rc = txn.getResponseDict()
        return self.rc['RESPONSECODE']

    def getResponseRef(self, amt, card, expiry, txn_type, ref,comment, currency='NZD'):
        txn = self.bnz._transaction().runTest(txn_type, 
					      {"CARDDATA"      : card,
                                               "CARDEXPIRYDATE": expiry,
                                               "CLIENTREF"     : "User: %s, Realm: %s" % (self.bnz.user,self.bnz.realm),
                                               "CURRENCY"      : currency,
					       "TXNREFERENCE":ref, 
					       "TOTALAMOUNT":amt, "COMMENT":comment})

	# this is a bit grubby but we're actually storing the return code ...
	self.rc = txn.getResponseDict()
        return self.rc['RESPONSECODE']	

    def getResponseCompletion(self, amt, card, expiry, ref, authcode, comment, currency='NZD'):
	txn = self.bnz._transaction().runTest('COMPLETION', 
	 			        {"TXNREFERENCE":ref,
					"CARDDATA"      : card,
                                        "CARDEXPIRYDATE": expiry,
                                        "TOTALAMOUNT"   : amt,
                                        "CURRENCY"      : currency,
                                        "CLIENTREF"     : "User: %s, Realm: %s" % (self.bnz.user,self.bnz.realm),
                                        "MERCHANT_CARDHOLDERNAME": "Optional Optional",
                                        "COMMENT"       : comment,
                                        "AUTHORISATIONNUMBER"      : authcode,
                                        "CVC2"          : ""})
	self.rc = txn.getResponseDict()
        return self.rc['RESPONSECODE']
        
    def getResponseCompletionCurr(self, amt, card, expiry, ref, authcode, comment, currency):
       txn = self.bnz._transaction().runTest('COMPLETION',
                                       {"TXNREFERENCE":ref,
                                       "CARDDATA"      : card,
                                       "CARDEXPIRYDATE": expiry,
                                       "TOTALAMOUNT"   : amt,
                                       "CURRENCY"      : currency,
                                       "CLIENTREF"     : "User: %s, Realm: %s" % (self.bnz.user,self.bnz.realm),
                                       "MERCHANT_CARDHOLDERNAME": "Optional Optional",
                                       "COMMENT"       : comment,
                                       "AUTHORISATIONNUMBER"      : authcode,
                                       "CVC2"          : ""})

    def getResponseRefund(self, amt, card, expiry,comment, ref, currency='NZD'):
	txn = self.bnz._transaction().runTest('REFUND', 
	 			        {"ORIGINALTXNREF":ref,
					"CARDDATA"      : card,
                                        "CARDEXPIRYDATE": expiry,
                                        "TOTALAMOUNT"   : amt,
                                        "CURRENCY"      : currency,
                                        "CLIENTREF"     : "User: %s, Realm: %s" % (self.bnz.user,self.bnz.realm),
                                        "MERCHANT_CARDHOLDERNAME": "Optional Optional",
                                        "COMMENT"       : comment,
                                        "CVC2"          : ""})
	self.rc = txn.getResponseDict()
        return self.rc['RESPONSECODE']

    def testPreauthVisa1(self):
	self.assertEqual(self.getResponseCard("1.00", self.visa, "0108", "Approved", 'PREAUTH'), "00")

    def testPreauthVisa2(self):
	self.assertEqual(self.getResponseCard("2.00", self.visa, "0108", "Approved", 'PREAUTH'), "00")

    def testPreauthAmex(self):
	self.assertEqual(self.getResponseCard("1.00", self.amex, "0108", "Approved", 'PREAUTH'), "00")

    def testPreauthInvalidCard(self):
	self.assertEqual(self.getResponseCard("1.00", self.invalid, "0108", "Invalid Card", 'PREAUTH'), "VA")

    def testPreauthInvalidAmount(self):
	self.assertEqual(self.getResponseCard("0.99", self.visa, "0108", "Under minimum txn limit", 'PREAUTH'), "Y3")

    def testCompletionOK(self):
	self.getResponseCard("1.00", self.visa, "0108", "Approved", 'PREAUTH')
	self.assertEqual(self.getResponseCompletion("1.00", self.visa, "0108",  self.rc['TXNREFERENCE'], "Approved", self.rc['AUTHCODE']), "00")

    def testCompletionDupd(self):
        # ok do a preauth ...
	self.getResponseCard("1.00", self.visa, "0108", "Approved", 'PREAUTH')
        # get it's transaction ref and do a completion ...
        self.getResponseCompletion("1.00", self.visa, "0108", self.rc['TXNREFERENCE'], self.rc['AUTHCODE'], "Approved")
        # now try to do the completion again ...
	self.assertEqual(self.getResponseCompletion("1.00", self.visa, "0108", self.rc['TXNREFERENCE'], self.rc['AUTHCODE'], "Invalid Completion"), "0T")

    def testCompletionCurrency(self):
	self.getResponseCard("1.00", self.visa, "0108", "Invalid Currency", 'PREAUTH', "036")
        self.assertEqual(self.getResponseCompletionCurr("1.00", self.visa, "0108", self.rc['TXNREFERENCE'], "Invalid Currency", self.rc['AUTHCODE'], '036'), "0M")

    def testPurchaseAmex(self):
	self.assertEqual(self.getResponseCard("1.00", self.amex, "0108", "Approved", 'PURCHASE'), "00")

    def testPurchaseMCard(self):
	self.assertEqual(self.getResponseCard("1.00", self.mcard, "0108", "Approved", 'PURCHASE'), "00")

    def testPurchaseVisa(self):
	self.assertEqual(self.getResponseCard("1.00", self.visa, "0108", "Approved", 'PURCHASE'), "00")
        # strangely, the response dict contains only the following, when we were promised much more:
        # {'SETTLEMENTDATE': '2006-02-01 00:00:00',
        #  'RESPONSETEXT': 'APPROVED (TEST TRANSACTION ONLY)',
        #  'AUTHCODE': '963577', 'TXNREFERENCE': '6446',
        #  'RESPONSECODE': '00', 'ERROR': None, 'STAN': '137072'}
	self.assertEqual(self.rc['COMMENT'], "Approved")
	self.assertEqual(self.rc['CLIENTREF'], "User: %s, Realm: %s" % (str(self.user),str(self.realm)),)
	self.assertEqual(self.rc['CARDHOLDERNAME'], "name reqd!")

    def testPurchaseYenNoDecimal(self):
	self.assertEqual(self.getResponseCard("1000", self.mcard, "0108", "Invalid Decimal in amount", 'PREAUTH', "392"), "0C")

    def testPurchaseYenDecimal(self):
	self.assertEqual(self.getResponseCard("1000.00", self.visa, "0108", "Approved", 'PREAUTH', "392"), "00")

    def testRefundAmex(self):
	purchase = self.getResponseCard("3.00", self.amex, "0108", "Approved", 'PURCHASE')
	self.assertEqual(self.getResponseRefund("3.00", self.amex, "0108", "Approved", self.rc['TXNREFERENCE']), "00")

    def testRefundMCard(self):
	purchase = self.getResponseCard("1.00", self.mcard, "0108", "Approved", 'PURCHASE')
	self.assertEqual(self.getResponseRefund("1.00", self.mcard, "0108", "Approved", self.rc['TXNREFERENCE']), "00")

    def testRefundVisa(self):
	purchase = self.getResponseCard("2.00", self.visa, "0108", "Approved", 'PURCHASE')
	self.assertEqual(self.getResponseRefund("2.00", self.visa, "0108", "Approved", self.rc['TXNREFERENCE']), "00")
        # this is crap - it appears there IS NO COMMENT, CLIENTREF - why are we being asked about checking it ...
	#self.assertEqual(self.rc['COMMENT'], "Approved")
	#self.assertEqual(self.rc['CLIENTREF'], "User: %s, Realm: %s" % (str(self.bnz.user),str(self.bnz.realm)),)
	#self.assertEqual(self.rc['CARDHOLDERNAME'])

#
# Running this file will run the test suite
#
if __name__ == '__main__':
    unittest.main()   


