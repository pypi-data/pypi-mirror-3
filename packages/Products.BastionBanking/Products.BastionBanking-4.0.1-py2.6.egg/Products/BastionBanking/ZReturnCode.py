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

import AccessControl, operator, string
from AccessControl import ClassSecurityInfo
from Products.PythonScripts.standard import html_quote
from PortalContent import PortalContent
from returncode import returncode, DEBUG, INFO, WARN, OK, FAIL, ERROR, FATAL


class ZReturnCode(PortalContent, returncode) :
    """
    Encapsulate a return code from a financial institution, making it persistable
    in a ZODB

    It needs this Zope shite to be accessible from Python Scripts ...
    """
    _security = ClassSecurityInfo()
    _security.declareObjectPublic()

    meta_type = 'ZReturnCode'

    _codes = { DEBUG:   'Debug',
               INFO:    'Info',
               WARN:    'Warning',
               OK:      'Ok',
               ERROR:   'Error',
               FATAL:   'Fatal' }

    _properties = (
        {'id':'returncode', 'type':'string', 'mode':'r'},
        {'id':'severity',   'type':'int',    'mode':'r' },
        {'id':'reference',  'type':'string', 'mode':'r' },
        {'id':'amount',     'type':'string', 'mode':'r' },
        {'id':'message',    'type':'string', 'mode':'r' },
        {'id':'response',   'type':'text',   'mode':'r' },
    )

    def __init__(self, id, ref, amount, rc, sev, msg, response=''):
        self.id = id
        returncode.__init__(self, ref, amount, rc, sev, msg, response)

    def prettySeverity(self):
        return self._codes[self.severity]

    def prettyResponse(self):
        return newline_to_br(self.response)

    def __str__(self):
        return '<table>%s</table>' % reduce(operator.add,
                                            map( lambda (x,y): '<tr><th align="left">%s</th><td>%s</td></tr>' % \
                                                                  (x, html_quote(y)), self.__dict__.items()))

AccessControl.class_init.InitializeClass(ZReturnCode)
