##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""PluginIndexes z3 interfaces.

$Id: interfaces.py 33294 2005-07-13 10:56:36Z yuppie $
"""

from zope.interface import Interface
from zope.schema import Bool, Choice

from Products.BastionBanking.ZCurrency import CURRENCIES

class ICurrencyIndex(Interface):

    """Index for currencies.
    """

    base_currency = Choice(title=u'Base currency - only used if convert_to_base',
                           values=CURRENCIES)
    convert_to_base = Bool(title=u'Convert to base currency on input?')


