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
import Globals, os, pydoc, inspect, sys, logging
from pydoc import classname, HTMLDoc, getdoc, allmethods, isdata, ispackage
from string import expandtabs, find, join, lower, split, strip, rfind, rstrip
from OFS.SimpleItem import SimpleItem
import Acquisition
from Products.Zpydoc.interfaces.IRenderer import IZpydocRenderer
from Products.Zpydoc.utils import pydoc_encode, pydoc_decode, implementsMethod

from zope.interface import implements

LOG = logging.getLogger('ZpyDoc.renderers.PyDoc')

# let it recognized PythonMethods as methods
inspect.ismethod= implementsMethod

class PyHTMLDoc(HTMLDoc, SimpleItem):
  """
  we need implicit acquistion for this ...
  """
  def index(self):
    """
    coping with function signature changes ...
    """
    seen = {}
    LOG.debug(self.aq_parent.directory())
    return HTMLDoc.index(self, self.aq_parent.directory(), seen)
  
  def page(self, title, contents):
    """
    Format an HTML page - inserted base tag!!
    """
    #LOG.debug('page(%s)' % title)
    return '''
<!doctype html public "-//W3C//DTD HTML 4.0 Transitional//EN">
<html><head><title>Python: %s</title>
<style type="text/css"><!--
TT { font-family: lucidatypewriter, lucida console, courier }
--></style><base href="%s"></head><body bgcolor="#f0f0f8">
%s
</body></html>''' % (title,
                     self.aq_parent.aq_parent.absolute_url(1),
                     contents)

Globals.InitializeClass(PyHTMLDoc)
  
class PyDoc(SimpleItem):
    """
    Render a standard pydoc page by delegating to pydoc

    We have to be very careful about not explicitly defining methods here because
    then they do not become overrideable via ObjectManager objects in derivations.
    This is why we have used containment of the pydoc object.
    """
    implements( IZpydocRenderer, )

    meta_type = 'pydocRenderer'
    icon = 'www/renderer.gif'
    id = 'PyDoc'
    title = 'Vanilla pydoc'

    # Zope stuff f**s with HTMLDoc so we can't inherit from it ...
    _renderer = PyHTMLDoc()

    def __call__(self, object, name):
      """
      do page publishing
      """
      #LOG.debug('__call__(%s)' % (name))
      return self._renderer.document(object)
    
    def builtins(self):
        """ return the builtin functions """
        def bltinlink(name):
            return '<a href="%s.html">%s</a>' % (pydoc_encode(name), name)
        names = filter(lambda x: x != '__main__',
                       map( lambda x: x['name'], self.aq_parent.packages() ))
        contents = self._renderer.multicolumn(names, bltinlink)
        indices = ['<p>' + self._renderer.bigsection(
            'Built-in Modules', '#ffffff', '#ee77aa', contents)]
        return join(indices, '')

    def directory(self):
      """
      needed to homogenise function signature in PyHTMLDoc::index()
      """
      return self.aq_parent.directory
    
    def __getitem__(self, name):
        """
        delegate all unfound to HTMLDOC ...
        """
        return getitem(self._renderer, name)
    
Globals.InitializeClass(PyDoc)

def manage_addPyDocRenderer(self, REQUEST=None):
    """ """
    try:
        self._setObject('pydoc', PyDoc())
    except:
        pass

    if REQUEST:
        return self.manage_main(self, REQUEST)
    return self.pydoc

