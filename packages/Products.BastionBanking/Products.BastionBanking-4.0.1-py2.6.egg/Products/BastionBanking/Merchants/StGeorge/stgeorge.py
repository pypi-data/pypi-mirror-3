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

SERVER = 'ipg.stgeorge.com.au'
PORT = 443

# TODO - fix linker errors in delivered webpayclient.so :(
try:
    import webpayclient
except:
    pass

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
    This is the transaction class for St. George WebPay Credit Card Gateway
    """
    txnTypes = {
        "PURCHASE"  : ([0,1,2,4,5],[3,9,10,11,12]),
        "REFUND"    : ([0,1,2,4,5,7],[3,9,10,11,12]),
        "PREAUTH"   : ([0,1,2,4,5],[3,9,10,11,12]),
        "COMPLETION": ([0,1,2,4,5,8],[3,9,10,11,12]),
        "STATUS"    : ([0,1,6],[])
    }
    txnResps = [
        "ERROR", "RESPONSECODE", "RESPONSETEXT", "TXNREFERENCE",
        "AUTHCODE", "STAN", "SETTLEMENTDATE"
    ]
    txnReqs = [
        "INTERFACE", "TRANSACTIONTYPE", "TOTALAMOUNT", "TAXAMOUNT",
        "CARDDATA", "CARDEXPIRYDATE", "TXNREFERENCE", "ORIGINALTXNREF",
        "AUTHORISATIONNUMBER", "CLIENTREF", "COMMENT", "TERMINALTYPE",
        "CVC2"
    ]
    codes = [ "DEBUG", "CLIENTID", "DATA" ]
    servArgs = ['server','port','merchant_id','certificate','cert_pass']
    
    def __init__(self, args):
        """
        Initiates the Library API and creates a new bundle
        """
        self.txn = None
        if not webpayclient.init():
            raise txn_error(self,"Could not initialise the WebPay API.")
        for item in self.servArgs[2:]:
            if not args.has_key(item) or not args[item]:
                raise txn_error(self,"Missing arg %s" % item)
        self.txn = webpayclient.newBundle()
        self.server = args
        self._setup()

    def __del__(self):
        """
        Cleans up the transaction and closes it off
        """
        if self.txn:
            webpayclient.cleanup(self.txn)
            if not webpayclient.free():
                raise txn_error(self,"Error freeing the WebPay API.")

    def newTXN(self):
        """
        Starts a new transaction
        """
        self.txn = webpayclient.flushBundle(self.txn)
        self._setup()

    def _setAttr(self,name,value=""):
        """
        Internal method to set request fields
        """
        webpayclient.setAttr(self.txn,name,value)

    def _getAttr(self,name,default=None):
        """
        Internal method to get response fields
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

    def _setup(self):
        """
        Internal method used between transactions to setup the server details
        and after cleaning up the old data from the previous transaction.
        Also called when creating a new transaction instance.
        """
        MerchID = str(self.server.get('merchant_id','???'))
        CertPath = str(self.server.get('certificate','???'))
        CertPass = str(self.server.get('cert_pass','???'))
        host = str(self.server.get('server','www.gwipg.stgeorge.com.au'))
        if host.find(':') > -1:
            host,port = host.split(':')
        else:
            port = str(self.server.get('port','3007'))
        webpayclient.setup(self.txn,host,port,CertPath,CertPass,MerchID)

    def runTest(self,txnType,data):
        """
        Just a wrapper around run
        """
        return self.run(txnType,data,test=1)
    
    def run(self,txnType,data,test=0):
        """
        Runs a CC test using the test interface
        """
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
            self._setAttr(attr,data[attr])
        # Now setup and optional args that are in the data
        for item in self.txnTypes[txnType][1]:
            value = data.get(self.txnReqs[item],None)
            if value:
                self._setAttr(self.txnReqs[item],value)
        # We ignore all other args
        return webpayclient.run(self.txn)

    def getResponse(self):
        """
        Returns a list of response name,result from the transaction
        """
        retList = []
        for item in self.txnResps:
	    res = self._getAttr(item)
            if item == 'RESPONSECODE' and res:
                res = "PG-%s" % res
            retList.append( (item, res) )
        return retList
    
    def getResponseDict(self):
        """
        Returns a list of response name,result from the transaction
        """
        retVal = {}
        for item in self.txnResps:
            res = self._getAttr(item)
            if item == 'RESPONSECODE' and res:
                retVal[item] = "PG-%s" % res
            elif res:
                retVal[item] = res
        return retVal

class stgeorge:
    """
    pure python StGeorge's Bank interface

    """

    def __init__(self):
        self.cert_file = 'bla'
        self.merchant_id = 'crap'
        self.user = 'user'
        self.password = 'password'
        self.realm = 'realm'
        self.test_mode = 0


    def _pay(self, card, amount):
        """
        connect to St Georges and pay ...
        """
        try:
            txn = transaction( { 'server' : SERVER,
                                 'port'   : PORT,
                                 'certificate' : self.cert_file,
                                 'cert_pass' : self.password,
                                 'merchant_id' : self.merchant_id, } )
        except txn_error, e:
            raise e

        try:
            rc = txn.run('PURCHASE', { "CARDDATA"      : card.number,
                                       "CARDEXPIRYDATE": card.expiry.strftime('%m%y'),
                                       "TOTALAMOUNT"   : str(amount.amount()),
                                       "CLIENTREF"     : "User: %s, Realm: %s" % (str(self.user),str(self.realm)),
                                       "COMMENT"       : "CardHolder: unknown, Invoice #",
                                       "CVC2"          : '' }, self.test_mode)
        except txn_error, e:
            return returncode.returncode(card.number, amount, rc, returncode.FATAL, str(e), '')

        try:
            rc = txn.getResponseDict()
            if rc.has_key('AUTHCODE'):
                ref = '%s - %s' % (rc['TXNREFERENCE'], rc['AUTHCODE'])
            else:
                ref = rc.get('TXNREFERENCE', '')                             
            return returncode.returncode(ref,
                              amount,
                              rc.get('RESPONSECODE', 0),
                              returncode.OK,
                              rc.get('RESPONSETEXT', ''),
                              rc.get('RESPONSETEXT', ''))
        except txn_error, e:
            return returncode.returncode(card.number, amount, rc, returncode.FATAL, str(e), '')

    def _refund(self, card, amount, ref):
        """
        refund card
        """
        try:
            txn = transaction( { 'server' : SERVER,
                                 'port'   : PORT,
                                 'certificate' : self.cert_file,
                                 'cert_pass' : self.password,
                                 'merchant_id' : self.merchant_id, } )
        except txn_error, e:
            raise e

        try:
            rc = txn.run('REFUND', { "CARDDATA"      : card.number,
                                     "CARDEXPIRYDATE": card.expiry.strftime('%m%y'),
                                     "TOTALAMOUNT"   : str(amount.amount()),
                                     "CLIENTREF"     : "User: %s, Realm: %s" % (str(self.user),str(self.realm)),
                                     "COMMENT"       : "CardHolder: unknown, Invoice #",
                                     "CVC2"          : '', }, self.test_mode)
        except txn_error, e:
            return returncode.returncode(card.number, amount, rc, returncode.FATAL, str(e), '')

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
            return returncode.returncode(card.number, amount, rc, returncode.FATAL, str(e), '')


    def _verify(self, card, amount):
        """
        """
        try:
            txn = transaction( { 'server' : SERVER,
                                 'port'   : PORT,
                                 'certificate' : self.cert_file,
                                 'cert_pass' : self.password,
                                 'merchant_id' : self.merchant_id, } )
        except txn_error, e:
            raise e

        try:
            rc = txn.run('STATUS', { "CARDDATA"      : card.number,
                                     "CARDEXPIRYDATE": card.expiry.strftime('%m%y'),
                                     "TOTALAMOUNT"   : str(amount.amount()),
                                     "TXNREFERENCE"  :'hmmm',
                                     "CLIENTREF"     : DateTime().strftime("%d/%m/%Y %H:%M:%S"),
                                     "COMMENT"       : "CardHolder: unknown, Invoice #",
                                     "CVC2"          : '', }, self.test_mode)
        except txn_error, e:
            return returncode.returncode(card.number, amount, rc, returncode.FATAL, str(e), '')

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
            return returncode.returncode(card.number, amount, rc, returncode.FATAL, str(e), '')
 

#
# Running this file will run a test by default..
#
if __name__ == '__main__':
    from currency import currency
    from creditcard import creditcard
        
    merchant = stgeorge()

    rc = merchant._pay(creditcard("4565456545654565",
                                  DateTime() + 365),
                       currency('AUD', 1.00))

    print rc
