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

import os, sys, logging
from Products.Zpydoc.Permissions import manage_zpydoc

LOG = logging.getLogger('Zpydoc.renderers')

def _renderers():
    thisdir = os.path.dirname(__file__)
    return map(lambda x: x[:-3],
               filter( lambda x: x[-3:] == '.py' and x not in ['__init__.py'],
                       os.listdir( thisdir ) ) )

def initialize(context):
    iconPath = os.path.dirname( os.path.dirname(__file__) )
    iconPath =  os.path.join(iconPath, 'www', 'renderer.gif')
    for renderer in _renderers():
        command = '''
import %s
context.registerClass(%s.%s,
                      permission=manage_zpydoc,
                      visibility=None,
                      constructors = (%s.manage_add%sRenderer,),
                      icon=%r)

LOG.info('Registered Renderer: %s')
''' % (renderer, renderer, renderer,renderer, renderer, iconPath, renderer )
        exec( command )
    context.registerHelp()
