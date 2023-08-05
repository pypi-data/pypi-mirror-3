#    Copyright (C) 2003-2006  Corporation of Balclutha and contributors.
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

DEBUG = -500
INFO  = -300
WARN  = -100
OK    = 0
FAIL  = 100
ERROR = 400
FATAL = 900

class returncode:
    """
    Encapsulate a return code from a financial institution

    It needs this Zope shite to be accessible from Python Scripts ...
    """
    _codes = { DEBUG:   'Debug',
               INFO:    'Info',
               WARN:    'Warning',
               FAIL:    'Failure',
               OK:      'Ok',
               ERROR:   'Error',
               FATAL:   'Fatal' }
    
    def __init__(self, ref, amount, rc, sev, msg, response):
        assert self._codes.has_key(sev), "Unknown Severity: %s" % str(sev)
        self.reference = ref     # the bank's unique identifier for this response
        self.amount = amount     # the financial amount involved
        self.returncode = rc     # this may not be an integer value
        self.severity = int(sev) # mapping of returncode to our severity ratings
        self.message = msg       # any human-readable message component
        self.response = response # the raw return data

    def prettySeverity(self):
        """
        return the string-version of the severity code
        """
        return self._codes[self.severity]

    def __str__(self):
        return '<returncode %s>' % self.__dict__.items()
