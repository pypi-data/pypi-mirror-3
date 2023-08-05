#    Copyright (C) 2006-2007  Corporation of Balclutha and contributors.
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
import os, socket, unittest
from httplib import HTTPSConnection, FakeSocket

#from XMLPay import XMLPayRequest, XMLSaleTransaction

# hmmm - this is really going to depend upon whichever acquiring bank you use, but
# the newest VeriSign API seems to be restricted to USA, UK, Australia
SUPPORTED_CURRENCIES = ('USD', 'AUD')

import returncode
try:
    from DateTime import DateTime
except:
    from datetime import datetime as DateTime

#
# hmmm - there are a few different verisign's out there - heres a dict of
# test host, live host, and partner tag's for some ...
# 
VERISIGN = {
    'us':('pilot-payflowpro.verisign.com', 'payflowpro.verisign.com', 'Paypal'),
    'au':('pilot-payflowpro.verisign.com', 'payflowpro.verisign.com', 'VSA'),
    }

PORT = 443
TIMEOUT = 30

def Jurisdictions():
    """ helper to list PayFlow jurisdictions - those for which we hold connectivity metadata """
    return VERISIGN.keys()

def https_connect(self):
    "Connect to a host on a given (SSL) port."

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Python 2.3 has this new feature but it's not exposed in any
    # of the socket API's :(   Also, there's possibly some NAF
    # stuff going on whereby some implementations don't yet have
    # it ...
    timeout = getattr(self, 'timeout', TIMEOUT)
    try:
        sock.settimeout(timeout)
    except:
        pass
    sock.connect((self.host, self.port))
    ssl = socket.ssl(sock, self.key_file, self.cert_file)
    self.sock = FakeSocket(sock, ssl)

# MonkeyPatch HTTPSConnection to get timeouts.
HTTPSConnection.connect = https_connect

class verisign:
    """
    pure python VeriSign transactor
    """
    def supported_currencies(self):
        return SUPPORTED_CURRENCIES

    def __init__(self, jurisdiction, account, password):
        assert VERISIGN.has_key(jurisdiction), 'Unsupported Jurisdiction: %s' % jurisdiction
        self.jurisdiction = jurisdiction
        self.account = account
        self.password = password
        self.proxy_host = ''
        self.proxy_port = ''
        self.proxy_account = ''
        self.proxy_password = ''

    def _refund(self, card, amount, ref='', test_mode=False, *args, **kw):
        """
        refund (credit) card 
        """
        host, partner = self._get_host_partner(test_mode)
        headers = {
            'TRXTYPE':'C',
            'TENDER':'C',
            'PARTNER':partner,
            'VENDOR':self.account,
            'USER':self.account,
            'PWD':self.password,
            'AMT': amount.amount_str(),
            }

        #
        #  hmmm - despite the documentation's indication otherwise, I seem to REQUIRE
        #  passing a reference!!
        #
        if ref:
            headers['ORIGID'] = ref
        else:
            headers['ACCT'] = card.number
            headers['EXPDATE'] = card.expiry.strftime('%m%y')

        try:
             return self._send(test_mode, amount, **headers)
        except Exception, e:
             return self._parse_result(str(e), amount)
            
    def _pay(self, card, amount, test_mode=False, *args,**kw):
        """
        clear funds on card - full sale, not auth + capture
        """
        host, partner = self._get_host_partner(test_mode)

        headers = {
            'TRXTYPE':'S',
            'TENDER':'C',
            'PARTNER':partner,
            'VENDOR':self.account,
            'USER':self.account,
            'PWD':self.password,
            'ACCT':card.number,
            'EXPDATE':card.expiry.strftime('%m%y'),
            'AMT': amount.amount_str(),
            }

        # hmmm - need to do some xml ...
        #request = XMLPayRequest( Vendor=self.account,
        #                         Partner=partner,
        #                         User=self.account,
        #                         Timeout = TIMEOUT,
        #                         Password=self.password,
        #                         transactions=[XMLSaleTransaction(TotalAmount = amount.amount_str(),
        #                                                           CardType=card.type,
        #                                                           ExpDate=card.expiry.strftime('%Y%m'),
        #                                                           )] )
        #pfpro.process(str(request), host, PORT, TIMEOUT)

        # AVS processing uses street/zip and is necessary to receive lowest transaction charges
        # street processing actually only does checking on the street number, not even the name ...
        street = kw.get('street', '')
        zip = kw.get('zip', '')
        if street:
            headers['STREET'] = street
        if zip:
            headers['ZIP'] = zip

        # Card Security Code validation
        if card.cvv2:
            headers['CVV2'] = card.cvv2

        if card.name:
            headers['NAME'] = card.name
            name = '&NAME=%s' % card.name

        try:
            return self._send(test_mode, amount, **headers)
        except Exception, e:
            return self._parse_result(str(e), amount)

    def _verify(self, card, amount, test_mode=False):
        """
        this looks like work in progress for now ...
        """
        raise NotImplementedError

    def _send(self, test_mode, amount, request_id='', **kw):
        """
        helper to post a request to verisign - returns a returncode ...
        set txn_id to retry/rerun a request
        """
        host, partner = self._get_host_partner(test_mode)
        conn = HTTPSConnection(host, PORT)

        #conn.set_debuglevel(9)
        if kw.has_key('timeout'):
            conn.timeout = kw['timeout']

        if not request_id:
            request_id = os.popen("/usr/bin/uuidgen").read().rstrip().replace('-', '')

        body = '&'.join(map(lambda x: '%s[%i]=%s' % (x[0], len(x[1]), x[1]), kw.items()))

        # headers are as specified at:
        # http://www.pdncommunity.com/pdn/board/message?board.id=payflow&message.id=610
        conn.request('POST',
                     '/transaction',
                     body,
                     {'Content-Type':'text/namevalue',
                      'X-VPS-REQUEST-ID':request_id,
                      'X-VPS-CLIENT-TIMEOUT':TIMEOUT,
                      'X-VPS-VIT-CLIENT-CERTIFICATION-ID':'BastionBanking',
                      'X-VPS-VIT-INTEGRATION-PRODUCT': 'BastionBanking',
                      'X-VPS-VIT-INTEGRATION-VERSION': '2.1.1',
                      'X-VPS-VIT-OS-NAME':'BastionLinux',
                      'X-VPS-VIT-OS-VERSION':'6.0',
                      'X-VPS-VIT-RUNTIME-VERSION':'6.0'})

        response = conn.getresponse()
        data = response.read()
        
        if response.status > 400:
            return returncode.returncode(request_id,
                                         amount,
                                         response.reason,
                                         returncode.FATAL,
                                         response.reason,
                                         data)
        
        return self._parse_result(data, amount)
    
    def _parse_result(self, responsestr, amount):
        """
        helper to parse VeriSign return string into a returncode
        """
        #print responsestr
        response = {}
        if responsestr.find('&') != -1:
            for k,v in map(lambda x: x.split('='), responsestr.split('&')):
                if k == 'RESULT':
                    response[k] = int(v)
                else:
                    response[k] = v
            if response['RESULT'] == 0:
                rc = returncode.OK
            elif response['RESULT'] < 0:
                # a comms error
                rc = returncode.FATAL
            else:
                # a decline or error
                rc = returncode.ERROR
        else:
            # hmmm it's a comms error - we never got to VeriSign ...
            rc = returncode.FATAL

        # NOTE: bank's do not decline based upon CSC or AVS discrepancies - this is left
        # up to the merchant.  Since we'd have to do a reversal as we're not first doing an authorise,
        # we're ignoring this stuff for now (excepting trapping the info in the message

        # CSC processing
        if response.has_key('CVV2MATCH'):
            # valid values are 'Y', 'N', 'X' (unsupported by customer's bank)
            if response['CVV2MATCH'] == 'N':
                response['RESPMSG'] = '%s (%s)' % (response['RESPMSG'], 'failed CSC')

        # AVS processing
        if response.has_key('AVSADDR') and response.has_key('AVSZIP'):
            if response['AVSADDR'] == 'N':
                response['RESPMSG'] = '%s (%s)' % (response['RESPMSG'], 'failed street')
            if response['AVSZIP'] == 'N':
                response['RESPMSG'] = '%s (%s)' % (response['RESPMSG'], 'failed zip')
        try:
            # no PNREF for comms errors ...
            return returncode.returncode(response.get('PNREF', ''),
                                         amount,
                                         response.get('RESULT', ''),
                                         rc,
                                         response.get('RESPMSG', ''),
                                         responsestr)
        except Exception, e:
            raise Exception, '%s\n%s' % (str(e), responsestr)

    def _get_host_partner(self, test_mode):
        """
        helper to retrieve host and partner from our verisign metadata - or if it's overridden
        """
        if test_mode:
            host = VERISIGN[self.jurisdiction][0]
        else:
            host = VERISIGN[self.jurisdiction][1]
        return host, getattr(self, 'partner', VERISIGN[self.jurisdiction][2])
                            
class verisigntest(unittest.TestCase):
    """
    A wrapper containing the prescribed tests for verisign merchant facilies
    """

    gateway = verisign('au', 'lastbastion', 'bastion01')

    mcard  = '5555555555554444'
    visa   = '4111111111111111'
    amex   = '378282246310005'
    diners = '30569309025904'	

    def XtestPay(self):
        from creditcard import creditcard
        from currency import currency
        cc = creditcard(self.mcard, DateTime() + 180, 'MasterCard')
        self.assertEqual(self.gateway._pay(cc, currency('AUD 10.00'), 1).severity, returncode.OK)

    def XtestRefund(self):
        from creditcard import creditcard
        from currency import currency
        cc = creditcard(self.mcard, DateTime() + 180, 'MasterCard')
        self.assertEqual(self.gateway._refund(cc, currency('AUD 10.00'), '', 1).severity, returncode.OK)

    def testPayRefund(self):
        import time
        from creditcard import creditcard
        from currency import currency
        cc = creditcard(self.mcard, DateTime() + 180, 'MasterCard')
        rc = self.gateway._pay(cc, currency('AUD 10.00'), 1)
        self.assertEqual(rc.severity, returncode.OK)

        # hmmm paypal is f**ked ...
        time.sleep(1)
        
        rc = self.gateway._refund(cc, currency('AUD 10.00'), rc.reference, 1)
        self.assertEqual(rc.severity, returncode.OK)
        
#
if __name__ == '__main__':
    unittest.main()   


