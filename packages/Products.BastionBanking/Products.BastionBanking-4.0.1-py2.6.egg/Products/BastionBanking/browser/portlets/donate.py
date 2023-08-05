#    Copyright (C) 2010  Corporation of Balclutha. All rights Reserved.
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
from zope import schema
from zope.interface import implements
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.portlet.static import PloneMessageFactory as _
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

TOOLNAME='BMS'  # the default ...

class IDonatePortlet(IPortletDataProvider):
    """  a Donations portlet """
    bms = schema.ASCIILine(title=_(u"Bastion Merchant Serice Id"),
                              description=_(u"id of the BMS to use (we'll acquire it from here)."),
                              required=True,
                              default=TOOLNAME)
    desc = schema.Text(title=_(u"User Message"),
                          description=_(u"Any text to include in the portlet"),
                          required=False,
                          default=u'')
    donation = schema.ASCIILine(title=_(u"A minimum suggest donation amount"),
                          description=_(u"Please include currency code!!"),
                          required=True,
                          default='USD 10.00')


class Renderer(base.Renderer):
    """ Overrides static.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('donate.pt')

    @property
    def available(self):
        return self._tool() is not None
    
    def suggestedAmount(self):
       """
       returns a suggested minimum amount to donate
       """
       return self.data.donation

    def merchantURL(self):
	"""
        return the URL of the BMS processing any donation
	"""
        tool = self._tool()
        if tool:
            return tool.absolute_url()
        return ''

    def referenceURL(self):
	"""
        return the URL of the calling portlet
	"""
        return self.context.absolute_url()

    def serviceIcon(self):
        """
        """
        tool = self._tool()
        if tool:
            return tool.serviceIcon()
        return ''
        
    def Description(self):
	"""
	A site-defined message to display in the donations portlet
	"""
        return self.data.desc

    def _tool(self):
	try:
	    return getattr(self.context, self.data.bms)
	except:
	    return None

class Assignment(base.Assignment):
    """ Assigner for Donations portlet. """
    implements(IDonatePortlet)
    title = _(u'Donations')

    def __init__(self, bms, donation, desc=u''):
        self.bms = bms
        self.donation = donation
        self.desc = desc
    
class AddForm(base.AddForm):
    """ Make sure that add form creates instances of our custom portlet instead of the base class portlet. """
    form_fields = form.Fields(IDonatePortlet)
    label = _(u"Accept Donations Portlet")
    description = _(u"This portlet allows you to accept donations.")

    def create(self, data):
        return Assignment(bms=data.get('BMS', TOOLNAME),
                          donation=data.get('donation', 'USD 10.00'),
                          desc=data.get('desc', u''))

class EditForm(base.EditForm):
    """ edit Donations portlet"""
    form_fields = form.Fields(IDonatePortlet)
    label = _(u"Edit Donations Portlet")
    description = _(u"This portlet allows you to accept donations.")
