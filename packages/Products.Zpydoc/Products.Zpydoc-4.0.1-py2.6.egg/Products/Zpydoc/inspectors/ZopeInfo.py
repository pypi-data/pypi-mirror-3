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

import Globals, logging, Products, inspect, os, sys, traceback
from Acquisition import Implicit
from pydoc import ispackage
from PythonInfo import structured_text, getmembers, \
     FunctionInfo as FuncInfoBase, ModuleInfo as ModInfoBase, \
     ClassInfo as ClassInfoBase, PackageInfo as PkgInfoBase
from Products.Zpydoc.utils import implementsMethod
from Acquisition import aq_base
import OFS.misc_

from Products.CMFCore.utils import getToolByName

LOG = logging.getLogger('ZpyDoc::ZopeInfo')

# let it recognized PythonMethods as methods
inspect.ismethod= implementsMethod

class FunctionInfo(FuncInfoBase):
    """
    We want to get Zope Permission info into the function info
    """
    def __init__(self, function, permission):
        #LOG.debug(permission)
        FuncInfoBase.__init__(self, function)
        self._permission = permission

    def arguments(self, formatfn=lambda x: '<span style="color:grey; font-size:10pt">=%s</span>' % repr(x)):
        """
        return an html-formatted list of the function arguments
        """
        try:
            return FuncInfoBase.arguments(self, formatfn)
        except:
            # it's probably an interface method
            return '(...)'

    def permission(self):
        """
        return access permission needed to invoke this function
        """
        return self._permission


class ClassInfo(ClassInfoBase):
    """
    We want to place additional functions to access 'Public' and 'Private'
    methods etc
    """
    def __init__(self, cls):
        #LOG.debug('__init__(%s)' % (cls))
        ClassInfoBase.__init__(self, cls)
        #
        # Push Product Registry info into this namespace - well the 'productinfo'
        # namespace anyway.  We want to try and avoid potential name clashes if
        # possible ...
        #
        if hasattr(cls, 'meta_type'):
            self.productinfo = ProductInfo(cls.meta_type)
        else:
            self.productinfo = None
        pm_syms = {}
        if hasattr(self._class, '__ac_permissions__'):
            for perms in getattr(self._class, '__ac_permissions__'):
                for fn in perms[1]:
                    pm_syms[fn] = perms[0]

        #self._methods = map ( lambda x,y=pm_syms: FunctionInfo(x[1].im_func, y.get(x[0], '')),
        #                      getmembers(self._class, inspect.ismethod) )
        self._methods = []
        try:
            methods = getmembers(self._class, inspect.ismethod) 
        except Exception, e:
            methods = []
        for name,method in methods:
            self._methods.append( FunctionInfo( method.im_func, pm_syms.get(name, '') ))

        if hasattr(self._class, '_Interface__attrs'):
            self._methods.extend(map(lambda x,y=pm_syms,self=self: FunctionInfo(x[1], y.get(x[0], '')),
                                     self._class._Interface__attrs.items()))

    def methods(self):
        #LOG.debug('methods: %s' % self._methods)
        return map(lambda x: x.__of__(self), self._methods)

    def public_methods(self):
        """
        methods not beginning with an underscore, and having a docstring and a permission
        assignment (otherwise requiring Manager role to access - which effectively makes
        it private)
        """
        return filter(lambda x: x.id[0] != '_' and hasattr(x, '__doc__') and x.permission,
                      self.methods())

    def private_methods(self):
        """
        methods beginning with an underscore, or without a docstring (or requiring Manager role)
        """
        return filter(lambda x: x.id[0] == '_' or not hasattr(x, '__doc__') or not x.permission,
                      self.methods())

        
class ModuleInfo(ModInfoBase):
    """
    """
    
    def classes(self):
        #LOG.debug('classes')
        results = []
        for k,v in getmembers(self._object, inspect.isclass):
            if (inspect.getmodule(v) or self._object) is self._object:
                results.append((k, v))
        return map(lambda x,self=self: ClassInfo( x[1] ).__of__(self), results)


    
class PackageInfo(PkgInfoBase):
    """
    """

    def __init__(self, object, name, onelevel=True):
        """
        This is the same as it's parent, but the scope of the Info's is different ...
        """
        #LOG.debug('__init__(%s) -->%s' % (name, object))
        self.id = object.__name__
        self.title = name
        self._object = object
        self._modpkgs = []

        if onelevel:
            for name, module in getmembers(object, inspect.ismodule):
                if hasattr(module, '__path__'):
                    self._modpkgs.append(PackageInfo(module, name, onelevel=False).__of__(self))
                else:
                    self._modpkgs.append(ModuleInfo(module, name).__of__(self))
        #LOG.debug('modules=%s' % self._modpkgs)
        self._modpkgs.sort()

    def getIcon(self):
        """
        dynamically figure out if we're a package or module and produce the
        correct icon path
        """
        portal_url = getToolByName(self, 'portal_url').getPortalObject().absolute_url()
        if self.packages():
            return '%s/package.png' % portal_url
        else:
            return '%s/file.png' % portal_url

    def classes(self):
        """
        return a list of class meta data objects in this module/package
        """
        #LOG.debug('classes()')
        if inspect.isclass(self._object):
            return [ ClassInfo(self._object).__of__(self) ]
        results = []
        for k,v in getmembers(self._object, inspect.isclass):
            #LOG.debug('classes(%s)' % v)
            if inspect.getmodule(v) == self._object:
                results.append(v)
        return map(lambda x,self=self: ClassInfo(x).__of__(self), results)


    def __getitem__(self, name):
        """
        check for python builtin's before 'normal' zope objects ...
        """
        return PkgInfoBase.__getitem__(self, name) or getattr(aq_base(self._object), name, '')



class ProductInfo(Implicit):
    """
    product={'visibility': 'Global',
             'interfaces': [<Interface webdav.EtagSupport.EtagBaseInterface at 83fa108>],
             'container_filter': None,
             'action': 'manage_addProduct/Zpydoc/manage_addZpydoc',
             'permission': 'Manage Zpydocs',
             'name': 'Zpydoc',
             'product': 'Zpydoc',
             'instance': <extension class Products.Zpydoc.Zpydoc.Zpydoc at 922f208>}

    instance={'icon': 'misc_/Zpydoc/renderer.gif',
            'id': 'PyDoc', '_renderer': <PyHTMLDoc at 0x965a288>,
            '__call__': <function __call__ at 0x965a0e4>,
            '__implements__': (<Interface Products.Zpydoc.ZpydocRenderer.IZpydocRenderer at 92576c0>,),
            'meta_type': 'pydocRenderer',
            'directory': <function directory at 0x9659c14>,
            '__getattr__': <function __getattr__ at 0x9659c4c>,
            'title': 'Vanilla pydoc',
            'builtins': <function builtins at 0x965a164>,
            '__doc__': '\n    Render a standard pydoc page by delegating to pydoc\n\n    We have to be very careful about not explicitly defining methods here because\n    then they do not become overrideable via ObjectManager objects in derivations.\n    This is why we have used containment of the pydoc object.\n    ',
            '__module__': 'Products.Zpydoc.renderers.PyDoc'}

    """
    __allow_access_to_unprotected_subobjects__ = 1


    def __init__(self, meta_type):
        #LOG.debug('__init__(%s)' % meta_type)
        self.id = meta_type
        self._product = None
        #
        # unfortunately, cls has a different address to the instance in Products.meta_types :(
        # and there's something naf where full module path resolution doesn't exist ...
        #
        # we should cache this maybe ???
        #
        for p in Products.meta_types:
            product =  p.get('instance', None)
            if product and hasattr(product, 'meta_type') and product.meta_type == meta_type:
                self._product = p
                break

        if self._product and self._product.has_key('interfaces'):
            interfaces = []
            for interface in self._product['interfaces']:
                    interfaces.append( InterfaceInfo(interface) )
            # cunninly mask the hash table with an attribute ...
            self._interfaces = interfaces
        else:
            self._interfaces = []
    
        #LOG.debug(self._product)

    def iconpath(self):
        try:
            return self._product['instance'].icon
        except:
            return None
        
    def icon(self):
        #
        # hmmm - think this is brokrn ...
        #
        try:
            name=os.path.split(self.iconpath())[1]
            return getattr(OFS.misc_.misc_, self._product['product'])[name]
        except:
            return None

    def interfaces(self):
        """
        return list of interface classes
        """
        return map(lambda x,y=self: x.__of__(y), self._interfaces)
    
    def doc(self, structured=False):
        """
        return the document string
        """
        msg = getattr(self._product, '__doc__').strip()
        if msg:
            if structured:
                return structured_text( msg )
            return msg
        return ''
        
    def __getitem__(self, name):
        #LOG.debug('__getitem__(%s)' % name)
        item = self._product.get(name, None)
        return item

       
class InterfaceInfo(ClassInfo):
    """
    a Zope Interface object
    '_Interface__attrs': {'http__etag': <Method instance at 8379c78>, 'http__refreshEtag': <Method instance at 8450790>},
    '__doc__': '    Basic Etag support interface, meaning the object supports generating\n
                    an Etag that can be used by certain HTTP and WebDAV Requests.\n    ',
    '__bases__': (<Interface Interface._Interface.Interface at 82d5b70>,),
    '__module__': 'webdav.EtagSupport',
    '__name__': 'EtagBaseInterface'
    """
    def name(self):
        return self['name']

    def module(self):
        return self['module']
    
    def methods(self):
        return map ( lambda x,self=self: FunctionInfo(x[1], '').__of__(self),
                     self._class._Interface__attrs.items() )

