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
from zope.interface import Interface

class IZpydocRenderer( Interface ):
    """
    this is our renderer quasi-ZClass

    note that each renderer MUST implement this interface, and MUST
    supply a global function of the form manage_add<__classname__>Renderer(self, REQUEST=None)
    for our factory generator
    """
    def __init__(self):
        """
        a default ctor IS required ie no parameters ...
        """
    def page(self, object):
        """
        handle publishing a package/module...
        """

    def builtins(self):
        """
        handle publishing builtin functions
        """

    def index(self, path, seen):
        """
        build a list of package modules for the main index page
        """
