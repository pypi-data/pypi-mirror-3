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
import AccessControl, Products, inspect
from AccessControl.Permissions import change_configuration, view_management_screens, \
     manage_properties, change_permissions, undo_changes, access_contents_information

try:
    from Products.OrderedFolder.OrderedFolder import OrderedFolder
    Folder = OrderedFolder
except:
    from OFS.Folder import Folder

from zope.interface import classImplements
from interfaces.IRenderer import IZpydocRenderer

class RendererFolder(Folder):
    """ """
    meta_type = 'RendererFolder'

    id = 'renderers'
    title = ''

    # don't want 'View'
    manage_options = ( Folder.manage_options[0], ) + Folder.manage_options[2:]
    index_html = None
    
    def all_meta_types(self):
        #possibles = []
        #for module in inspect.getmembers(Products, inspect.ismodule):
        #    for klass in inspect.getmembers(module, inspect.isclass):
        #        if classImplements(klass, (IZpydocRenderer,)):
        #            possibles.append(iface)
        possibles = filter(lambda x: x['name'] in ['pydocRenderer', 'PythonRenderer', 'ZopeRenderer'],
                           Products.meta_types)
        definites = map(lambda x: x.meta_type, self.objectValues())
        return filter(lambda x,y=definites: x['name'] not in y, possibles)

AccessControl.class_init.InitializeClass(RendererFolder)
