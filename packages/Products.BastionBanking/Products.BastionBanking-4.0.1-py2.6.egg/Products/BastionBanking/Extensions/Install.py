#    Copyright (C) 2004-2011  Corporation of Balclutha. All rights Reserved.
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
from StringIO import StringIO
from Products.CMFPlone.utils import getFSVersionTuple
from Products.CMFCore.utils import getToolByName

from Products.BastionBanking.config import *


def install(portal):                                       
    out = StringIO()

    setup_tool = getToolByName(portal, 'portal_setup')

    if getFSVersionTuple()[0]>=3:
        setup_tool.runAllImportStepsFromProfile(
                "profile-BastionBanking:default",
                purge_old=False)
    else:
        plone_base_profileid = "profile-CMFPlone:plone"
        setup_tool.setImportContext(plone_base_profileid)
        setup_tool.setImportContext("profile-BastionBanking:default")
        setup_tool.runAllImportSteps(purge_old=False)
        setup_tool.setImportContext(plone_base_profileid)

    out.write('registered skins and types and workflows')

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile('profile-BastionBanking:default')

    return "Successfully uninstalled %s" % PROJECTNAME

