#    Copyright (C) 2003-2011  Corporation of Balclutha. All rights Reserved.
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

import Globals, Products, os, pydoc, inspect, sys, re, keyword, logging
from pydoc import classname, HTMLDoc, getdoc, allmethods, isdata, ispackage
from string import expandtabs, find, join, lower, split, strip, rfind, rstrip, replace
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.DTMLMethod import DTMLMethod
from OFS.SimpleItem import SimpleItem
from PyDoc import PyDoc
from Products.Zpydoc.inspectors.PythonInfo import PackageInfo
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from AccessControl.Permissions import view

LOG = logging.getLogger('ZpyDoc.renderers.Python')

keyword_re = re.compile('(\W)(%s)(\W)' % join(keyword.kwlist, '|'))
class_re = re.compile('^class ')
space_re = re.compile(' ')

class Python(ObjectManager, PropertyManager, PyDoc):
    """
    Render a standard pydoc page using ZPT's
    """
    meta_type = 'PythonRenderer'

    __ac_permissions__ = ObjectManager.__ac_permissions__ + (
	(view, ('read', 'format')),
    ) + PropertyManager.__ac_permissions__

    #
    # we have an underlying __getattr__ which causes all sorts of problems
    # when we come to override it's methods with visible Zope objects ...
    #
    
    id = 'Python'
    title = 'Customisable Python (ZPT)'

    def __init__(self):
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
                                                            'p_document.zpt') ).read() ))
        self._setObject('standard_template.pt',
                        ZopePageTemplate('standard_template.pt',
                                         open( os.path.join(thisdir,
                                                            'zpt',
                                                            'standard_template.zpt') ).read() ))
                        
        self._setObject('stylesheet.css',
                        DTMLMethod(open( os.path.join(thisdir,
                                                      'zpt',
                                                      'stylesheet.css') ).read(), __name__='stylesheet.css'))

    manage_options = ObjectManager.manage_options + \
                     PropertyManager.manage_options + \
                     SimpleItem.manage_options

    def __getattr__(self, name):
        """
        we seem to be returning a function that ObjectManager confuses with an object ...
        """
        obj = Python.inheritedAttribute('_getattr__')(self, name)
        if obj and hasattr(obj, 'meta_type'):
            return obj
        return None
    
    def __call__(self, object, name):
        """ render page using our Python info object """
        #LOG.debug('__call__(%s)' % (name))
        return self.document( self, self.REQUEST, PackageInfo(object, name) )

    def read(self, filename):
        """
        return the contents of a file

        this just returns raw contents so that you can plug in your own parser ...
        """
        return open(filename, 'r').read()

    def format(self, filename):
        """
        return a basic html rendering of a python source file - this is a *very*
        unsophisticated parser ...
        """
        content = []
        for line in open(filename, 'r').readlines():

            if line.find('#') != -1:
                line,comment = line.split('#', 1)
                comment = '<span class="comment">#%s</span>' % comment
            else:
                comment = ''

            i = 0
            while len(line) > i and line[i] == ' ':
                i += 1
            if i:
                line = re.sub(space_re, '&nbsp;', line, i)

            line = re.sub(keyword_re, r'\1<span class="keyword">\2</span>\3', line)
            line = re.sub(class_re, r'<span class="keyword">class</span>&nbsp;', line)
            content.append('%s%s' % ( line, comment ))

        content = join(content, '<br>')
        return content
        
    
Globals.InitializeClass(Python)

def manage_addPythonRenderer(self, REQUEST=None):
    """ """
    try:
        self._setObject('Python', Python())
    except:
        pass

    if REQUEST:
        return self.manage_main(self, REQUEST)
    return self.Python
