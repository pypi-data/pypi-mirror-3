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

import AccessControl, string, inspect, pydoc, os, sys, types, logging
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.Permissions import change_configuration, view, view_management_screens
from AccessControl.unauthorized import Unauthorized
from Acquisition import aq_base
try:
    from Products.CMFPlone.PloneFolder import PloneFolder as Folder
except:
    try:
        from Products.OrderedFolder.OrderedFolder import OrderedFolder as Folder
    except:
        from OFS.Folder import Folder
    
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import REPLACEABLE
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from utils import pydoc_decode, locate, sane_pythonpath, all_modules
from ZpydocRenderer import RendererFolder
from Permissions import *
from config import TOOLNAME

#
# Plone skins are optional ...
#
try:
    from Products.CMFCore.DynamicType import DynamicType
    from Products.CMFCore.permissions import ModifyPortalContent
    # need DynamicType for skins, and SimpleItem for context/path info etc
    class PortalContent ( DynamicType, SimpleItem ): pass
    DO_PLONE = 1
except:
    class PortalContent ( SimpleItem ): pass
    DO_PLONE = 0
    ModifyPortalContent = 'Modify Portal Content'

# do we have SilverCity (for sytax high-lighting)
try:
    from Products.PloneSilverCity.source import generate_html
    HAS_SILVERCITY = True
except ImportError:
    HAS_SILVERCITY = False

LOG = logging.getLogger('ZpyDoc')

# cache points for global module list - we have to delay instantiation until the entire Zope
# server has loaded ...

all_modules = None
modules_tree = None

class ModuleTree(dict):
    """
    manage a dict of modules ...
    """
    def __init__(self, module_list):
        dict.__init__(self)
        for module in module_list:
            if not self.has_key(module):
                self[module] = []
            if module.find('.') != -1:
                parent, leaf = module.rsplit('.', 1)
                #print "%s: %s -> %s" % (module, parent, leaf)
                if not self.has_key(parent):
                    self[parent] = [leaf]
                else:
                    self[parent].append(leaf)

    def subModules(self, module):
        return self[module]

    def hasSubModules(self, module):
        return len(self[module]) > 0
    
    def keys(self, name='', depth=0):
        if name:
            return filter(lambda x,n=name,d=depth + name.count('.'):
                          x.startswith(n) and x.count('.') == d,
                          dict.keys(self))
                       
        else:
            return filter(lambda x,d=depth: x.count('.') == d, dict.keys(self))


class ZpydocPage( PortalContent ):
    """
    a publishable unit (required for ZPublisher ...)

    note - this is not persisted !!
    """
    isPortalContent = 1
    meta_type = portal_type = 'ZpydocPage'

    _security = ClassSecurityInfo()
    _security.declareObjectPublic()

    __ac_permissions__ = PortalContent.__ac_permissions__ + (
        (view, ('getPackageInfo', 'isfile',),),
        (view_zpydoc_source, ('render_source',)),
        )

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, object, name, documentable=None):
        """
        pass in a ZpyDocumentable for old-style/expert behaviour
        """
        #LOG.debug('__init__')
        self.id = name
        self.title = name.split('.')[-1]
        self.object = object
        self.name = name
        self.documentable = documentable

    # force __call__ - we don't want aquisition of parents ...
    index_html = None

    def __call__(self, REQUEST, *args, **kw):
        """
        this will get invoked by ZPublisher to render the page
        """
        #LOG.debug('__call__()')
        if self.documentable:
            return self.documentable.renderer( self.object, self.name )
        # plone-style rendering ...
        return self(self, self.REQUEST)
          

    def isfile(self):
        """
        return true if is a file (otherwise we need security assertions on os ...)
        """
        return getattr(aq_base(self.object), '__file__', None)


    def render_source(self,plain=False):
        """
        render html source text
        """
        # file IO is private ;) - and we're going to be safe and calculate it, not
        # trusting our user to pass it in ...
        filename = inspect.getsourcefile(self.object)
        if plain:
            return open(filename,'r').read()
        if HAS_SILVERCITY:
            return generate_html(open(filename,'r').read(),'python')[0]
        return getattr(self, 'renderSource')(lines=open(filename, 'r').readlines())

    def getPackageInfo(self):
        """
        we need to wrap PackageInfo's in an acquisition context for permissions to work
        """
        # delegate to skin so end-user can additionally embellish result
        info = self.createPackageInfo(self.object, self.name).__of__(self)

        # TODO - run this through our module permissions and knock out anything
        # not permissioned
        return info

    def nameParts(self):
        """
        return a listing of all the sub-modules constituting this name
        this function is for creating anchor paths (breadcrumbs)
        """
        results = []
        if self.name.find('.') != -1:
            parts = self.name.split('.')
            for index in xrange(0, len(parts)):
                results.append( (parts[index], '.'.join(parts[0:index + 1])))
        else:
            results = [(self.name, self.name)]
        return results

AccessControl.class_init.InitializeClass(ZpydocPage)


class Zpydoc(Folder):
    """
    Run's pydoc within the Zope HTTP server environment

    If you have the *OrderedFolder* product installed, you can control the order in
    which your documentables appear in the index_html

    If you want to customise the documentation, or want to do cool stuff with Zope
    documentation, then you're at the right place!
    """
    meta_type = portal_type = 'Zpydoc'

    icon = 'www/pydoc.gif'
    __replaceable__ = REPLACEABLE
    _reserved_names = ('index_html',)
    default_page = 'zpydoc_view'

    description = 'API Documentation'

    #
    # there are major security issues with the old way of defining paths and
    # specifying packages with ZpyDocumentable.  The import step prior to
    # introspection could run some very nasty globals on the Zope instance.
    #
    # if you know *exactly* what these classes are doing and they're not
    # imported by your Zope as matter of course, then you can set this flag
    # and also ZpyDoc these ...
    #
    expert_mode = False

    # some of the data sections are very messy, they also potentially show
    # details from modules you're trying to hide
    show_data = False
    
    property_extensible_schema__ = 1

    _properties = Folder._properties + (
        {'id':'description', 'type':'text',    'mode':'w'},
        {'id':'show_data',   'type':'boolean', 'mode':'w'},
        {'id':'expert_mode', 'type':'boolean', 'mode':'w'},
        )
    
    __ac_permissions__ = Folder.__ac_permissions__ + (
        (view, ('render', 'module_permitted', 'module_role',
                'module_roles', 'getDocumentableNames', 'isBuiltin', 'isPackage',
                'isModule', 'getDocumentables', 'getModule')),
        (change_configuration, ('manage_repair', 'manage_purgePermissions')),
        (view_management_screens, ('manage_renderers', 'manage_modules')),
        (manage_zpydoc, ('pythonpaths', 'modules', 'module_tree',
                         'manage_updateModulePermissions',))
        )

    manage_options = (
        {'label':'Contents',    'action':'manage_main', 'help':('Zpydoc', 'pydoc.stx') },
        {'label':'View',        'action':'' },
        {'label':'Modules',     'action':'manage_modules'},
        {'label':'Renderers',   'action':'renderers/manage_workspace' },
        ) + Folder.manage_options[2:-2]

    manage_modules = PageTemplateFile('zpt/modules', globals())
    index_html = PageTemplateFile('zpt/index_html', globals())

    def __init__(self, id, title):
        Folder.__init__(self, id, title)
        self.renderers = RendererFolder('renderers')
        self._module_permissions = {}

    def manage_afterAdd(self, item, container):
        """
        let's give it a default renderer
        """
        # if we're copying then this may already be present
        if not getattr(aq_base(self.renderers), 'Zope', None):
            self.renderers.manage_addProduct['Zpydoc'].manage_addZopeRenderer()
    
    def manage_renderers(self, REQUEST):
        """
        Redirect to renderers folder
        """
        REQUEST.RESPONSE.redirect('renderers/manage_main')

    def manage_delObjects(self, ids=[], REQUEST=None):
	"""
	this doesn't seem to properly route ...
	"""
	if ids:
	    Folder.manage_delObjects(self, ids)
	if REQUEST:
	    return self.manage_main(self, REQUEST)

    def all_meta_types(self):
        """
        If you think you know what you're doing, you can define stuff right off the
        file-system PYTHONPATH, but the module import of such modules may well be
        unsafe and eat your Zope instance!!
        """
        if self.expert_mode:
            return [ { 'action' : 'manage_addProduct/Zpydoc/add_documentable'
                       , 'permission' : manage_zpydoc
                       , 'name' : 'ZpyDocumentable'
                       , 'Product' : 'Zpydoc'
                       , 'instance' : None
                       }, ]
        return []

    def pythonpaths(self):
        """
        all the paths (adjusted) where python modules may be located
        """
        return sane_pythonpath

    def module_tree(self, **kw):
        """
        all the loaded (and thus 'safe') python modules in this Zope installation

        parameters:

        name:  a string containing a specific module name
        depth: an integer saying what level of submodules to return
        """
        global modules_tree

        if not modules_tree:
            modules_tree = ModuleTree(self.modules())

        m = modules_tree.keys(name=kw.get('name', ''),
                              depth=kw.get('depth', 0))
        m.sort()
        return map(lambda x, subs=modules_tree.hasSubModules: (x, subs(x)), m)

    def modules(self):
        """
        all the loaded (and thus 'safe') python modules in this Zope installation
        """
        global all_modules

        if not all_modules:
            all_modules = map(lambda x: x.__name__,
                              filter(lambda x: hasattr(x, '__path__'),
                                     sys.modules.values())) + list(sys.builtin_module_names)

        return all_modules

    def module_permitted(self, module, user=None):
        """
        see if the given module is allowed to be displayed, and optionally if
        the given user is permitted to the module
        """
        # we only do package-level permissioning ...
        if self.isPackage(module):
            pkg = module
        elif module.find('.') != -1:
            pkg = '.'.join(module.split('.')[:-1])
        else:
            return False

        module_perm = self._module_permissions.get(pkg, {})

        # not found ...
        if not module_perm:
            return False
        
        if user:
            if 'Manager' in user.getRoles():
                return True
            roles = list(user.getRoles())
            if not 'Anonymous' in roles:
                roles.append('Anonymous')
            #LOG.debug('isPermitted(%s) [%s]' % (pkg, pkg_perm))
            return len( filter( lambda x,y=module_perm: y.has_key(x), roles ) ) > 0
        
        return not not module_perm

    def module_role(self, module, role):
        """
        see if the module permission is set for this role
        """
        return self._module_permissions.get(module, {}).has_key(role)

    def module_roles(self, module, roles):
        """
        see if the module permission is set for these roles
        """
        role_map = self._module_permissions.get(module, {})
        if not role_map:
            return False
        for role in roles:
            try:
                if role_map.has_key(role):
                    return True
            except Exception, e:
                raise Exception, (e, role_map, role, module)
        return False
        
    def manage_updateModulePermissions(self, REQUEST, name=''):
        """
        update the permission mappings for the modules
        """
        self._updateModulePermissions(name, REQUEST.form)
        REQUEST.set('management_view', 'Modules')
        REQUEST.set('manage_tabs_message', 'Updated %s' % name)
        return self.manage_modules(self, REQUEST)

    def manage_purgePermissions(self, REQUEST=None):
        """
        over time as you uninstall products etc, Zpydoc can retain permissions
        no longer needed.  While this isn't a problem at all, these can be
        cleaned out with this function
        """
        deleted = 0
        perms = self._module_permissions
        known = self.modules()
        # hmmm we've overridden keys in ModuleInfo ...
        for k in map(lambda x: x[0], perms.items()):
            if k not in known:
                del perms[k]
                deleted += 1
        self._p_changed = 1
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Purged %i permissions' % deleted)
            return self.manage_main(self, REQUEST)
        

    def _updateModulePermissions(self, name, map):
        """
        do some *very* basic checking and then saving of permission info
        """
        # remove old values
        for k, subs_flag in self.module_tree(name=name, depth=1):
            if self._module_permissions.has_key(k):
                del self._module_permissions[k]
            
        for k,v in map.items():
            #LOG.debug('permission map %s=%s (%s)' % (k, v, type(v)))
            if type(v) != type(''):
                self._module_permissions[k] = v
        self._p_changed = 1

    def getDocumentableNames(self):
        """
        return all the displayable module names at the first (index) level
        """
        names = filter(lambda x: x.find('.') == -1,
                       self._module_permissions.keys())
        user = getSecurityManager().getUser()
        roles = list(user.getRoles())
        if not 'Anonymous' in roles:
            roles.append('Anonymous')
        names = filter(lambda x,roles=roles,fn=self.module_roles: fn(x,roles), names)

        if self.expert_mode:
            for documentable in self.objectValues('ZpyDocumentable'):
                for pkg in documentable.packages():
                    if pkg['name'] not in names and documentable.isPermitted(pkg['name'], user):
                        names.append(pkg['name'])
        
        names.sort()
        return names

    def isBuiltin(self, module):
        """
        returns whether or not this is a built-in module
        """
        return module in sys.builtin_module_names

    def isPackage(self, module):
        """
        returns whether or not this module is a package (ie contains
        other packages and modules)
        """
        return not self.isBuiltin(module) and hasattr(self.getModule(module), '__path__')

    def isModule(self, module):
        """
        returns whether or not this package/module is a module 
        """
        return not self.isBuiltin(module) and not hasattr(self.getModule(module), '__path__')

    def getDocumentables(self):
        """
        return name, isbuiltin, ispackage, ismodule  tuples of first (index) level modules
        """
        return map(lambda x,p=self.isPackage,m=self.isModule: (x, p(x), m(x)),
                   self.getDocumentableNames())

    def getModule(self, module):
        """
        returns the python module object associated with this, if allowed
        """
        return sys.modules.get(module, None)

    def _get_documentable(self, obj, do_permissions=1):
	"""
	determine if this package is ZpyDocumentable and optionally that the user is 
        permissioned to	do so, returning the ZpyDocumentable (or None)
	"""
	if hasattr(obj, '__path__'):
            # it's a file system package ...
            path = getattr(obj, '__path__')
            if type(path) == type([]):
                path = path[0]
                directory,file = os.path.split( path )
        else:
            try:
                # it's a module ...
                directory,file = os.path.split( inspect.getsourcefile(obj) )
            except TypeError:
                # ok - it's a builtin (we could 100% verify this but ...)
                directory = 'builtin__'
            except:
                raise

        # step thru directory looking for a ZpyDocumentable to bind to ...
        zpydoc = None
        while not zpydoc and directory and directory != '/':
            try:
                zpydoc = filter( lambda x, y=directory: x.directory == y,
                                 self.objectValues('ZpyDocumentable') )[0]
            except:
                directory,file = os.path.split( directory )
            for documentable in self.objectValues('ZpyDocumentable'):
                if documentable.path() == directory:
                    zpydoc = documentable
                    break
        
	if zpydoc:
            difference = zpydoc.path_difference('.')
            if difference and difference != 'builtin__':
                pkg = string.replace(obj.__name__, difference, '', 1).split('.')[0]
            else:
                pkg = obj.__name__.split('.')[0]
            if do_permissions and not zpydoc.isPermitted(pkg, getSecurityManager().getUser()):
	        zpydoc = None

	return zpydoc

    def render(self):
        #
        # driver for index_html
        #
        modules = []
        seen = {}
        for documentable in self.objectValues():
            if documentable.directory == 'builtin__':
                modules.append( documentable.renderer().builtins() )
            else:
                # TODO - no parameters into index() ...
                modules.append( documentable.renderer().index(documentable.directory, seen) )
        return string.join(modules, '')

    def __getitem__(self, name):
        """
        this is where all the magic resides - it's a factory binding mechanism:
         * parsing the 'url'
         * binding to our ZpyDocumentable directory for rendering and access permissions
         * assembling a ZpydocPage for authorising and publishing
        """
        name = pydoc_decode(name)
        if name[-5:] == '.html': name = name[:-5]
        if name[:1] == '/': name = name[1:]

        #LOG.debug('__getitem__(%s)' % name)
        if name and name != '.':
            # see if we know about it, then security check it ...
            if self.module_permitted(name):
                if self.module_permitted(name, getSecurityManager().getUser()):
                    return ZpydocPage(sys.modules[name], name).__of__(self)
                else:
                    raise Unauthorized, name
            elif self.expert_mode:
                # hmmm - go do the dangerous old stuff!!!
                try:
                    obj = locate(name, forceload=0)
                except pydoc.ErrorDuringImport, value:
                    #return html_quote( str(value) )
                    LOG.debug('pyDoc.ErrorDuringImport(%s)' % value)
                    raise ImportError, value
                if obj:
                    zpydoc = self._get_documentable(obj, 0)
                    if zpydoc:
		        LOG.debug('rendering %s with %s' % (name, zpydoc.renderer()))
                        return ZpydocPage(obj, name , zpydoc).__of__(self)
                    else:
                        LOG.debug('no renderer %s [%s] ' % (obj, name))
                        raise AttributeError, 'no renderer for %s [%s]' % (obj, name)

        return Folder.__getitem__(self, name)
                

    def manage_repair(self, REQUEST=None):
        """
        if we change the underlying structure of Zpydoc, then you can apply this method
        to repair an instance - this is designed to be rerunnable ...
        """
        if not getattr(aq_base(self), 'renderers', None):
            self.renderers = RendererFolder('renderers', '')

        if not getattr(aq_base(self), '_module_permissions', None):
            self._module_permissions = {}

        if not getattr(aq_base(self), 'id', None):
            self.id = TOOLNAME
        if not getattr(aq_base(self), 'title', None):
            self.title = 'API documentation'

        for ob in self.objectValues('ZpyDocumentable'):
            ob._repair()

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Object Repaired')
            return self.manage_main(self, REQUEST)

AccessControl.class_init.InitializeClass(Zpydoc)

def manage_addZpydoc(self, id=TOOLNAME, title='API Documentation', REQUEST=None):
    """
    Add a Zpydoc autogenerating Python/Zope documentation tool
    """
    self._setObject(id, Zpydoc(id, title))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], TOOLNAME))

