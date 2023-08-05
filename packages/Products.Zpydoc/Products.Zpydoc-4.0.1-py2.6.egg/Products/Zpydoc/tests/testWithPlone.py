#
#    Copyright (C) 2002-2010  Corporation of Balclutha. All rights Reserved.
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

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import zLOG
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

from Products.Zpydoc.config import TOOLNAME
ztc.installProduct('Zpydoc')

ptc.setupPloneSite(products=['Zpydoc'])


class TestZpydoc(ptc.PloneTestCase):
    """
    Testing with Plone install and Plone skins ...
    """
    def afterSetUp(self):
        ptc.PloneTestCase.afterSetUp(self)
	self.portal.manage_addProduct['Zpydoc'].manage_addZpydoc()
        self.zpydoc = getattr(self.portal, TOOLNAME)

        # register the skins
	self.portal.portal_quickinstaller.installProduct('Zpydoc')


    def testUnsafeZpyDocumentable(self):
	self.zpydoc.manage_addProduct['Zpydoc'].manage_addZpyDocumentable(os.path.dirname(os.path.dirname(__file__)), 'Zope')
	getattr(self.zpydoc, '0')._file_permissions['Zpydoc'] = {'anonymous':1}

        # hmmm - now we need to think up a test ...
        self.failUnless(self.zpydoc.zpydoc_view())

    def testTest(self):
        self.failUnless(TOOLNAME in self.portal.objectIds())
	        
	# f**k knows why it AttributeError's on 'zpydoc_view'...
        self.failUnless(self.zpydoc.zpydoc_view())

if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestZpydoc))
        return suite
