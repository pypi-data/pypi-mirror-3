#    Copyright (C) 2003-2011  Corporation of Balclutha and contributors.
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
# add services here so they get auto-included in Banks.* ... 
#
import os, os.path
directory = os.path.dirname(__file__)
_services = filter( lambda x: os.path.isdir(os.path.join(directory, x)) and x not in ['CVS', '.svn'],
                    os.listdir(directory) )

# make a copy ...
def services() : return list(_services)

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products').declarePublic('BastionBanking')
ModuleSecurityInfo('Products.BastionBanking').declarePublic('Banks')
ModuleSecurityInfo('Products.BastionBanking.Banks').declarePublic('services')

from Products.BastionBanking.Permissions import add_bank_service
from App.ImageFile import ImageFile
misc_ = {}

#
# we really only want the icon available - but how to do this otherwise ??
#
def initialize(context):
    for provider in services():
        exec('''
from Products.BastionBanking.Banks.%s.%s import %s
context.registerClass(%s,
                      permission=add_bank_service,
                      visibility=None,
                      constructors = (%s,),
                      icon='Banks/%s/www/%s.gif')
context.registerHelp()''' % (provider, provider, provider, provider,
                             provider, provider, provider.lower()))


