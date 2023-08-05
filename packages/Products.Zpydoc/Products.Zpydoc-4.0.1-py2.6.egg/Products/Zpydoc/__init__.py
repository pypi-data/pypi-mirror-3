#    Copyright (C) 2003-2008  Corporation of Balclutha. All rights Reserved.
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

from App.ImageFile import ImageFile
from config import *

# register rendering options ...
import renderers

from Permissions import manage_zpydoc

#
# optionally install plone skins
#
try:
    from Products.CMFCore.DirectoryView import registerDirectory
    from Products.CMFCore import utils as coreutils
    from Products.GenericSetup import EXTENSION
    from Products.GenericSetup import profile_registry
    from Products.CMFPlone.interfaces import IPloneSiteRoot
    registerDirectory(SKINS_DIR, GLOBALS)
    DO_PLONE=1
except:
    DO_PLONE=0

import Zpydoc, ZpyDocumentable

def initialize(context): 
    context.registerClass(Zpydoc.Zpydoc,
                          constructors = (Zpydoc.manage_addZpydoc,),
                          icon='www/pydoc.gif',
                          permission=manage_zpydoc,
                          )
    context.registerClass(ZpyDocumentable.ZpyDocumentable,
                          constructors = (ZpyDocumentable.manage_addZpyDocumentableForm,
                                          ZpyDocumentable.manage_addZpyDocumentable),
                          visibility=None,
                          icon='www/documentable.gif',
                          permission=manage_zpydoc,
                          )
    #
    # have to explicitly delegate to implementation folders ...
    #
    renderers.initialize(context)
    context.registerHelp()

    if DO_PLONE:
        coreutils.ContentInit(PROJECTNAME + ' Content',
                          content_types = (Zpydoc.Zpydoc,
                                           ZpyDocumentable.ZpyDocumentable),
                          extra_constructors = (Zpydoc.manage_addZpydoc,),
                          permission = manage_zpydoc,
                          fti = (),).initialize(context)

        # Register the extension profile
        try:
            profile_registry.registerProfile('default',
                                             PROJECTNAME,
                                             'Zpydoc',
                                             'profiles/default',
                                             PROJECTNAME,
                                             EXTENSION,
                                         IPloneSiteRoot)
        except KeyError:
            # duplicate entry ...
            pass

misc_ = {}
for icon in ('pydoc', 'documentable', 'renderer'):
    misc_[icon] = ImageFile('www/%s.gif' % icon, globals())

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products').declarePublic('Zpydoc')

ModuleSecurityInfo('Products.Zpydoc').declarePublic('utils')
ModuleSecurityInfo('Products.Zpydoc.utils').declarePublic('pydoc_encode', 'pydoc_decode', 'all_modules')

ModuleSecurityInfo('Products.Zpydoc').declarePublic('inspectors')

ModuleSecurityInfo('Products.Zpydoc.inspectors').declarePublic('ZopeInfo')
ModuleSecurityInfo('Products.Zpydoc.inspectors.ZopeInfo').declarePublic('PackageInfo')
ModuleSecurityInfo('Products.Zpydoc.inspectors.ZopeInfo').declarePublic('InterfaceInfo')
ModuleSecurityInfo('Products.Zpydoc.inspectors.ZopeInfo').declarePublic('ClassInfo')
ModuleSecurityInfo('Products.Zpydoc.inspectors.ZopeInfo').declarePublic('FunctionInfo')
ModuleSecurityInfo('Products.Zpydoc.inspectors.ZopeInfo').declarePublic('ModuleInfo')
ModuleSecurityInfo('Products.Zpydoc.inspectors.ZopeInfo').declarePublic('ProductInfo')

ModuleSecurityInfo('Products.Zpydoc.inspectors').declarePublic('PythonInfo')
ModuleSecurityInfo('Products.Zpydoc.inspectors.PythonInfo').declarePublic('PackageInfo')
ModuleSecurityInfo('Products.Zpydoc.inspectors.PythonInfo').declarePublic('ClassInfo')
ModuleSecurityInfo('Products.Zpydoc.inspectors.PythonInfo').declarePublic('FunctionInfo')
ModuleSecurityInfo('Products.Zpydoc.inspectors.PythonInfo').declarePublic('ModuleInfo')
