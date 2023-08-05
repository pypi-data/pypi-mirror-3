#    Copyright (C) 2008  Corporation of Balclutha. All rights Reserved.
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
import types
from zope import schema
from zope.interface import implements
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.portlet.static import PloneMessageFactory as _
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName

from Products.Zpydoc.config import TOOLNAME

class IZpydocPortlet(IPortletDataProvider):
    """ Zpydoc portlet """

    zpydoc = schema.ASCIILine(title=_(u"Zpydoc Id"),
                              description=_(u"id of the Zpydoc to use (we'll acquire it from here)."),
                              required=True,
                              default=TOOLNAME)
    modules = schema.Text(title=_(u"Python modules"),
                          description=_(u"Module names within the Zpydoc to generate hotlinks to"),
                          required=True,
                          default=u'')


class Renderer(base.Renderer):
    """ Overrides static.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('zpydoc.pt')

    @property
    def available(self):
        return self._tool() is not None

    def _tool(self):
	try:
	    return getattr(self.context, self.data.zpydoc)
	except:
	    return None

    def modules(self):
        # hmmm - we're having problems getting list-like widgets to work ...
	modules = self.data.modules
        if type(modules) in types.StringTypes:
            return modules.split('\n')
        return modules
    
    def zpydoc_url(self):
        tool = self._tool()
        if tool:
            return tool.absolute_url()
        return ''

    def site_url(self):
	return getToolByName(self.context, 'portal_url').getPortalObject().absolute_url()

class Assignment(base.Assignment):
    """ Assigner for portlet. """
    implements(IZpydocPortlet)
    title = _(u'API Doc Portlet')
    
    def __init__(self, zpydoc=TOOLNAME, modules=u''):
        self.zpydoc = zpydoc
        self.modules = modules


class AddForm(base.AddForm):
    form_fields = form.Fields(IZpydocPortlet)
    label = _(u"Add API Doc Portlet")
    description = _(u"This portlet displays links to API documentation.")

    def create(self, data):
        return Assignment(zpydoc=data.get('zpydoc', TOOLNAME),
                          modules=data.get('modules', u''))    

class EditForm(base.EditForm):
    form_fields = form.Fields(IZpydocPortlet)
    label = _(u"Edit API Doc Portlet")
    description = _(u"This portlet displays links to API documentation.")
