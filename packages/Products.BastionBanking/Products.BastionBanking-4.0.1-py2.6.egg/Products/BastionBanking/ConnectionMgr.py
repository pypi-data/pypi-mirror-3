#
#    Copyright (c) 2004, Corporation of Balclutha.
#
#    Please report any bugs or errors in this program to our bugtracker
#    at http://www.last-bastion.net/HelpDesk
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
#
#
from time import time
from httplib import HTTPConnection, HTTPSConnection, FakeSocket, _CS_IDLE
from urllib import urlencode
import cPickle, re, sys, traceback, socket, base64
from threading import Lock

url_re = re.compile(r'^([a-z]+)://([A-Za-z0-9._-]+)(:[0-9]+)?')

#
# note each boundary in the body has -- prepended, and another -- ending the set
# the LF's are also important, but may also need \r if dealing with M$
#
#
# monkey patch connection to include timeouts ...
#

def http_connect(self):
    """Connect to the host and port specified in __init__."""
    msg = "getaddrinfo returns an empty list"
    for res in socket.getaddrinfo(self.host, self.port, 0,
                                  socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            self.sock = socket.socket(af, socktype, proto)
            # Python 2.3 has this new feature but it's not exposed in any
            # of the socket API's :(   Also, there's possibly some NAF
            # stuff going on whereby some implementations don't yet have
            # it ...
            try:
                self.sock.settimeout(30)
            except:
                pass
            if self.debuglevel > 0:
                print "connect: (%s, %s)" % (self.host, self.port)
            self.sock.connect(sa)
        except socket.error, msg:
            if self.debuglevel > 0:
                print 'connect fail:', (self.host, self.port)
            if self.sock:
                self.sock.close()
            self.sock = None
            continue
        break
    if not self.sock:
        raise socket.error, msg

def https_connect(self):
    "Connect to a host on a given (SSL) port."

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Python 2.3 has this new feature but it's not exposed in any
    # of the socket API's :(   Also, there's possibly some NAF
    # stuff going on whereby some implementations don't yet have
    # it ...
    try:
        self.sock.settimeout(30)
    except:
        pass
    sock.connect((self.host, self.port))
    ssl = socket.ssl(sock, self.key_file, self.cert_file)
    self.sock = FakeSocket(sock, ssl)


HTTPConnection.connect = http_connect
HTTPSConnection.connect = https_connect
 
# this is for easy manipulation of headers and future extensibility
headers = {
    "Content-type": "application/x-www-form-urlencoded",
    "Accept-Encoding":"identity",
    "Connection":"close",
    "keep-alive": 0,
    "User-Agent": 'BastionBanking'
    }

class Transport:
    """
    Python's httplib SSL layer is generally fucked, so we're providing a wrapper
    for it here.
    """
    _lock = Lock()

    def __init__(self, url, user='', password=''):
        '''
        setup a request to a URL.  If user/password supplied, then set up
        basic http authentication headers
        '''
        self.url = url
        if user:
            self.headers = dict(headers)
            self.headers["Authorization"] = "Basic %s" % base64.encodestring("%s:%s" % (user, password))
        else:
            self.headers = headers
            
        try:
            proto,host,port=url_re.match(url).groups()
            if port:
                port = int(port[1:])   # remove the ':' ...
        except:
            raise AttributeError, 'Invalid URL: %s' % url

        assert proto in ('http', 'https'), 'Unsupported Protocol: %s' % proto
        if proto == 'http':
            self._v_conn = HTTPConnection(host, port or 80)
        else:
            self._v_conn = HTTPSConnection(host, port or 443)

    def __call__(self, body='', headers={}, action="POST"):
        """
        make the request, returns the response packet contents, and response code as
        a tuple
        """
        req_hdrs = dict(self.headers)
        req_hdrs.update(headers)
        try:
            self._lock.acquire()
            try:
                self._v_conn.request(action,
                                     self.url,
                                     body,
                                     req_hdrs)
                response = self._v_conn.getresponse()
            except:
                raise
            return response
            data = response.read()
            if response.status >= 400:
                msg = '%s: %i - %s\n%s' % (self.url, response.status, response.reason, data)
                raise IOError, msg
            return (data,response.status)
        finally:
            # force connection state - think there could be a bug in httplib ...
            try:
                self._v_conn._HTTPConnection__state = _CS_IDLE
                #self._v_conn._HTTPConnection__response.close()
            except:
                pass
            self._lock.release()

    def __del__(self):
        try:
            self._v_conn.close()
        except:
            pass
