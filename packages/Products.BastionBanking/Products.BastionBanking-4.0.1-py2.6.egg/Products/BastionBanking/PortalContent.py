#
# Copyright 2004-2011 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
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
import AccessControl

from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.DynamicType import DynamicType
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base, aq_get
from AccessControl.Permissions import view, view_management_screens, access_contents_information

#
# We're being a bit particular about not quite describing our Plone stuff
# as portal content because we don't want to stick stuff in the PortalCatalog
# etc etc ...
#

class PortalContent(DynamicType, DefaultDublinCoreImpl, PropertyManager, SimpleItem, CMFCatalogAware):
    """
    Sort out our default views ...
    """
    isPortalContent = 1
    _isPortalContent = 1  # More reliable than 'isPortalContent'.

    # force CMFCore stuff to defer to portal_types in copy/paste/rename ops
    __factory_meta_type__ = None

    __ac_permissions__ = DefaultDublinCoreImpl.__ac_permissions__ + \
        PropertyManager.__ac_permissions__ + (
        (view, ('status', 'actions', 'getTypeInfo')),
        (access_contents_information, ('getStatusOf', 'getActionsFor', 'instigator')),
    ) + SimpleItem.__ac_permissions__ + CMFCatalogAware.__ac_permissions__


    manage_options = PropertyManager.manage_options + (
        {'label':'View', 'action':'' },
        ) + SimpleItem.manage_options

    def _getPortalTypeName(self):
        """
        needed for the portal type view mechanism ...
        """
        return self.meta_type

    def status(self):
        """
        return workflow status
        """
        try:
            return getToolByName(self, 'portal_workflow').getInfoFor(self, 'review_state')
        except:
            return ''

    def _status(self, status, wftool=None, wf=None, wf_var='review_state'):
        """
        set workflow status without calling workflow transition (use content_modify_status
        method if you want to do this ...
        """
        wftool = wftool or getToolByName(self, 'portal_workflow')

        # TODO - figure out how to get the correct workflow ...
        wf = wf or wftool.getWorkflowsFor(self)[0]
        assert status in wf.states.objectIds(), 'unknown state: %s (not in %s)' % (status, wf.states.objectIds())

        wftool.setStatusOf(wf.getId(), self, {'review_state':status})

    def actions(self):
        """
        return  a list of valid transitions for the object
        """
        return getToolByName(self, 'portal_actions').listFilteredActionsFor(self)['workflow']

    def getStatusOf(self, workflow):
        """
        return the status of ourselves in the context of this workflow (the corresponding
        WorkflowTool function is strangely declared private ...
        """
        try:
            return getToolByName(self, 'portal_workflow').getInfoFor(self, workflow.state_var)
        except WorkflowException:
            return 'Doh'

    def getActionsFor(self, workflow):
        """
        return a list of valid transition states
        """
        state = workflow._getWorkflowStateOf(self)
        return state.getTransitions()

    def instigator(self):
        """
        return who owns (ie enacted) the content
        """
        try:
            return self.getOwnerTuple()[1]
        except:
            return ''

    def indexObject(self):
        # acquire catalog ...
        self.catalog_object(self,  '/'.join(self.getPhysicalPath()))

    def unindexObject(self):
        # acquire catalog ...
        self.uncatalog_object('/'.join(self.getPhysicalPath()))

    def reindexObject(self, idxs=[]):
        self.unindexObject()
        self.indexObject()

    def manage_afterAdd(self, item, container):
        self.indexObject()

    def manage_beforeDelete(self, item, container):
        self.unindexObject()

AccessControl.class_init.InitializeClass(PortalContent)
