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

# import stuff
import AccessControl
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from BastionBankLog import BastionBankServiceLog
import returncode
from ZReturnCode import ZReturnCode
from Permissions import securityPolicy
from new import instance

manage_addBastionBankServiceForm = PageTemplateFile('zpt/add_bank', globals()) 
def manage_addBastionBankService(self, service, title='', REQUEST=None):
    """ """
    #
    # new up a service ...
    #
    try:
        exec('from Products.BastionBanking.Banks.%s.%s import %s' % (service, service, service))
        self._setObject('BastionBankService',
                        BastionBankService('BastionBankService',
                                    title,
                                    eval('''%s()'''% service ) ))

    except:
        raise
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/BastionBankService/manage_workspace' % REQUEST['URL3'] )
    

class ServicesFolder( Folder ):
    """
    house our services ...
    """
    meta_type = 'ServicesFolder'

    def all_meta_types(self):
        return []

    def __init__(self, id, title='ServicesFolder'):
        self.id = id
        self.title = title

AccessControl.class_init.InitializeClass( ServicesFolder )


class BastionBankService( ObjectManager, PropertyManager, SimpleItem ):
    """
    An encapsulation of a banking service provider.
    """
    meta_type = 'BastionBankService'
    _security = ClassSecurityInfo()

    manage_options = ObjectManager.manage_options + \
                     PropertyManager.manage_options + \
                     ( { 'label': 'Services', 'action':'manage_services' },
                       { 'label': 'Log',     'action':'log/manage_workspace'}, ) + \
                     SimpleItem.manage_options

    def all_meta_types(self):
   	return []
 
    def manage_services(self, REQUEST):
        """ """
        REQUEST.RESPONSE.redirect('services/manage_workspace')

    def __init__(self, id, title, imp):
        self.id = id
        self.title = title
        self.services = ServicesFolder('services', 'Banking Service Provision')
        self.services._setObject(imp.id, imp)
        self.log = BastionBankServiceLog('log', 'Audit Log')
        self._setObject('banner', ZopePageTemplate('banner', ''))

    def manage_afterAdd(self, item, container):
        securityPolicy(self)
        self.log.manage_afterAdd(self.log, self)
        
    def manage_pay(self, account, amount, reference, REQUEST=None):
        """
        pass additional parameters in REQUEST ?? ...
        """
	# hmmm - ...
	service = self.services.objectValues()[0]
        rc = service.pay(amount, account, reference, REQUEST)
        
        if rc.severity <= returncode.OK:
            self.log.log(returncode.INFO, account.getId(), str(rc.__dict__))
        else:
            self.log.log(returncode.ERROR, account.getId(), str(rc.__dict__))

        # upgrade to Zope version ...
        return instance(ZReturnCode, rc.__dict__)
       
    _security.declarePublic('widget')
    def widget(self, *args, **kw):
        return self.service.widget(args, kw)


AccessControl.class_init.InitializeClass(BastionBankService)
