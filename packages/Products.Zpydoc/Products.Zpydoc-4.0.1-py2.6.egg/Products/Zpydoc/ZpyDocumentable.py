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
__version__='$Revision: 108 $'[11:-2]

import AccessControl, os, sys, inspect, logging, copy, string
from pydoc import ispackage
from stat import *
from Acquisition import aq_base
from AccessControl import getSecurityManager
from AccessControl.Permissions import change_configuration, view, \
     view_management_screens, access_contents_information
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from utils import pythonpath, sane_pythonpath

LOG = logging.getLogger('ZPyDocumentable')

class ZpyDocumentable(ObjectManager, PropertyManager, SimpleItem):
    """
    A pseudo-object which we use as a wrapper for introspection and
    to control skinned content views
    """
    meta_type = 'ZpyDocumentable'
    icon = 'www/documentable.gif'

    _properties = (
        { 'id':'title',       'mode':'w', 'type':'string' },
        { 'id':'directory',   'mode':'w', 'type':'selection', 'select_variable': 'directories' },
        { 'id':'renderer_id', 'mode':'w', 'type':'selection', 'select_variable': 'renderers' },
        { 'id':'show_private','mode':'w', 'type':'boolean' },
        )

    __ac_permissions__ = ObjectManager.__ac_permissions__ + \
                         PropertyManager.__ac_permissions__ + \
                         SimpleItem.__ac_permissions__ +(
        (view, ('packages', 'renderer', 'isPermitted')),
        (view_management_screens, ('manage_file_permissions', 'isChecked', 'directories',
                                   'all_modules', 'renderers')),
        (access_contents_information,  ( 'path', 'path_difference'),),
        (change_configuration, ('manage_updateFilePermissions',)),
        )

    manage_options = ObjectManager.manage_options + (
        {'label': 'View', 'action': ''},
        {'label': 'Permissions', 'action': 'manage_file_permissions'},
        ) + PropertyManager.manage_options +  SimpleItem.manage_options
    
    manage_file_permissions = PageTemplateFile('zpt/file_permissions', globals())
    index_html = None
    
    def __init__(self, id, title, directory, renderer):
        self.id = id
        self.title = title
        self.directory = directory
        self.renderer_id = renderer
        self._file_permissions = {}
        self.show_private = 1

    def renderers(self):
        return self.aq_parent.renderers.objectIds()

    def all_modules(self):
        return sane_pythonpath
    
    def renderer(self):
        return self.aq_parent.renderers._getOb(self.renderer_id).__of__(self)

    def packages(self, all=False):
        """
        Returns a list of package/module dictionaries, keyed on name, file, ispackage -
        a package indicator flag.
        """
        modpkgs = []
        seen = {}
        user = getSecurityManager().getUser()
        #
        # hmmm - this bit isn't very OO ...
        #
        if self.directory == 'builtin__':
            if all:
                return map( lambda x: {'name':x, 'file':'', 'ispackage':0},
                            sys.builtin_module_names )
            else:
                return map( lambda x: {'name':x, 'file':'', 'ispackage':0},
                            self._file_permissions.keys() )
                
        def found(name, file, ispackage, modpkgs=modpkgs, seen=seen):
            if not seen.has_key(name):
                modpkgs.append( {'name':name, 'file':file, 'ispackage':ispackage} )
                seen[name] = 1

        # Package spam/__init__.py takes precedence over module spam.py.
        for file in map(lambda x,y=self.directory: '%s/%s' % (y,x),
                        os.listdir(self.directory)):
            LOG.debug('packages doing [%s]' % (file))
            try:
                mode = os.stat(file)[ST_MODE]
            except OSError:
                # hmmm - broken link?
                continue
            if not S_ISDIR(mode) and not file[-3:] == '.py':
                continue
            if ispackage(file):
                directory,name = os.path.split(file) 
                if (all or self.isPermitted(name, user)):
                    found(name, file, 1)

            elif os.path.isfile(file):
                modname = inspect.getmodulename(file)
                if modname and (all or self.isPermitted(modname, user)):
                    found(modname, file, 0)

        modpkgs.sort()
        LOG.debug('packages=%s' % modpkgs)
        return modpkgs

    def manage_updateFilePermissions(self, REQUEST):
        """
        """
        #LOG.debug(REQUEST.form)
        self._file_permissions = copy.deepcopy(REQUEST.form)
            
        REQUEST.set('management_view', 'Permissions')
        REQUEST.set('manage_tabs_message', 'Updated')
        return self.manage_file_permissions(self, REQUEST)

    def isChecked(self, pkg, role):
        """
        see if the file permission is set for this role
        """
        return self._file_permissions.get(pkg, {}).has_key(role)

    def isPermitted(self, pkg, user):
        """
        see if the given user is permitted to the package
        """
        pkg_perm = self._file_permissions.get(pkg, {})
        roles = list(user.getRoles())
        if not 'Anonymous' in roles:
            roles.append('Anonymous')
        #LOG.debug('isPermitted(%s) [%s]' % (pkg, pkg_perm))
        return len( filter( lambda x,y=pkg_perm: y.has_key(x), roles ) )

    def path(self):
        """
        return the specific pythonpath directory this module is rooted to

        (needed for our granular path selection stuff)
        """
        if self.directory == 'builtin__':
            return 'builtin__'
        # try *exact* match
        for path in pythonpath:
            if self.directory == path:
                return '%s/' % path
        # try *closest* match
        rpath = pythonpath[:]
        rpath.reverse()
        for path in rpath:
            if self.directory.startswith(path):
                return '%s/' % path
        
        raise AssertionError, "Couldn't bind path (%s)!!" % self.directory

    def path_difference(self, delimiter='.'):
        """
        return the relative path this directory falls from the PYTHONPATH (needed
        for our granular module selection stuff...)
        """
        if self.directory == 'builtin__':
            return 'builtin__'
        difference = self.directory[len(self.path()[:-1]):]
        if difference:
            return '%s%s' % (difference[1:], delimiter)
        return ''
        
    def directories(self):
        """
        return a list of our sanitised pythonpaths
        """
        return sane_pythonpath

    def _repair(self):
        if not getattr(aq_base(self), 'show_private', None):
            self.show_private = 0

AccessControl.class_init.InitializeClass(ZpyDocumentable)

manage_addZpyDocumentableForm = PageTemplateFile('zpt/add_documentable', globals())

def manage_addZpyDocumentable(self, directory, renderer_id, REQUEST=None):
    """ """
    realself = self.this()
    if not hasattr(aq_base(self.renderers), renderer_id):
        return REQUEST.RESPONSE.redirect('%s/manage_main?manage_tabs_message=Renderer not found!' % REQUEST['URL3'])
    title = directory
    # drop leading underscores so Zope will serve up pages ...
    if directory == '__builtin__':
        directory = 'builtin__'

    if directory in map(lambda x: x.directory, realself.objectValues()):
        return REQUEST.RESPONSE.redirect('%s/manage_main?manage_tabs_message=Already+Exists!' % REQUEST['URL3'])

    if len(realself.objectIds()) == 0:
        id = '0'
    else:
        id = '%i' % ( int( max( realself.objectIds() ) ) + 1 )

    self._setObject( id, ZpyDocumentable(id, title, directory, renderer_id) )
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_file_permissions' % (REQUEST['URL3'], id))
