#    Copyright (C) 2003-2010  Corporation of Balclutha. All rights Reserved.
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
__doc__ = """$id$"""

import Globals, os, logging
from Products.Zpydoc.renderers.Python import Python
from Products.Zpydoc.inspectors.ZopeInfo import PackageInfo
from OFS.DTMLMethod import DTMLMethod
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

LOG = logging.getLogger('ZpyDoc.renderers.Zope')

class Zope ( Python ):
    """
    Do custom processing for Zope derived objects
    """
    meta_type = 'ZopeRenderer'
    id = 'Zope'
    title = 'Customisable Zope'
    
    _properties = (
        { 'id': 'show_private', 'type':'boolean', 'mode':'w' },
        )

    #manage_options = (
    #    Python.manage_options[0],
    #    { 'label':'Properties', 'action':'manage_propertiesForm',
    #      'help':('Zpydoc.renderers', 'zope.stx') } ) + Python.manage_options[2:]
    
    def __init__(self):
        self.show_private = False
        thisdir = os.path.dirname(__file__)
        self._setObject('index',
                        ZopePageTemplate('index',
                                         open( os.path.join(thisdir,
                                                            'zpt',
                                                            'p_index.zpt') ).read() ))
        
        self._setObject('document',
                        ZopePageTemplate('document',
                                         open( os.path.join(thisdir,
                                                            'zpt',
                                                            'z_document.zpt') ).read() ))
        self._setObject('standard_template.pt',
                        ZopePageTemplate('standard_template.pt',
                                         open( os.path.join(thisdir,
                                                            'zpt',
                                                            'standard_template.zpt') ).read() ))
        self._setObject('stylesheet.css',
                        DTMLMethod(open( os.path.join(thisdir,
                                                      'zpt',
                                                      'stylesheet.css') ).read(), __name__='stylesheet.css' ))

    def __call__(self, object, name):
        """ render page using Zope-specific info object """
        #LOG.debug('__call__(%s)' % (name))
        return self.document( self, self.REQUEST, PackageInfo(object, name) )

Globals.InitializeClass(Zope)


def manage_addZopeRenderer(self, REQUEST=None):
    """ """
    try:
        self._setObject('Zope', Zope())
    except:
        raise
    if REQUEST:
        return self.manage_main(self, REQUEST)
    return self.Zope

