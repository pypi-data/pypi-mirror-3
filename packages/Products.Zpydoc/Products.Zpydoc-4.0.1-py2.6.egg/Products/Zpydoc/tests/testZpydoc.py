#    Copyright (C) 2002-2008  Corporation of Balclutha. All rights Reserved.
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

from Testing.ZopeTestCase import installProduct, ZopeTestCase
from AccessControl import getSecurityManager


# hmmm - BastionLinux assures us of this!!
PRODUCTS='/usr/lib/zope/lib/python/Products'


installProduct('Zpydoc')


# hmmm some experimental introspection
from pydoc import ispackage
import inspect

class TestZpydoc(ZopeTestCase):
    """
    Bog standard Zope only test
    """
    def afterSetUp(self):
        ZopeTestCase.afterSetUp(self)
	self.folder.manage_addProduct['Zpydoc'].manage_addZpydoc()
        self.zpydoc = self.folder.zpydoc

    def testCreation(self):
        self.assertEqual(self.folder.objectIds(), ['acl_users', 'zpydoc'])
	self.failUnless(self.zpydoc.index_html())

    def testRendererMetaTypes(self):
	tnames = map(lambda x: x['name'], self.zpydoc.renderers.all_meta_types())
        tnames.sort()
        self.assertEqual(tnames, ['PythonRenderer', 'pydocRenderer'])

    def testModuleTree(self):
        self.failUnless('Products' in map(lambda x: x[0],
                                          self.zpydoc.module_tree(depth=0)))
        #self.assertEqual(map(lambda x:x[0],
        #                     self.zpydoc.module_tree(depth=1)), [])
        self.failUnless('Products.Zpydoc' in map(lambda x: x[0],
                                                 self.zpydoc.module_tree(depth=1)))
        #self.assertEqual(self.zpydoc._modules_tree().keys(depth=2), [])
        zpydoc_tree = self.zpydoc.module_tree(name='Products.Zpydoc', depth=1)
        zpydoc_tree.sort()
        self.assertEqual(zpydoc_tree,
                         [('Products.Zpydoc.browser', True),
                          ('Products.Zpydoc.inspectors', False),
                          ('Products.Zpydoc.interfaces', False),
                          ('Products.Zpydoc.renderers', False),
                          ('Products.Zpydoc.tests', False)])

    def testGetDocumentableNames(self):
        self.assertEqual(self.zpydoc.getDocumentableNames(), [])
        # test user has only Authenticated permission ...
        self.zpydoc._updateModulePermissions('', {'Products':{'Anonymous':1, 'Authenticated':1}})
        self.assertEqual(self.zpydoc.getDocumentableNames(), ['Products'])
        self.assertEqual(self.zpydoc.getDocumentables(),[('Products', True, False)])

    def testInfo(self):
        from Products.Zpydoc.inspectors.ZopeInfo import PackageInfo
        info = PackageInfo(sys.modules['Products.Zpydoc'], 'Zpydoc')

        self.assertEqual(info['name'], 'Products.Zpydoc')

        self.assertEqual(info.id, 'Products.Zpydoc')
        self.assertEqual(info.shortname(), 'Zpydoc')

        module = info._modpkgs[2]
        self.assertEqual(module.id, 'Products.Zpydoc.ZpyDocumentable')
        self.assertEqual(module.title, 'ZpyDocumentable')
        self.assertEqual(module.name(), 'Products.Zpydoc.ZpyDocumentable')
        self.assertEqual(module.shortname(), 'ZpyDocumentable')
        
    def testPermissions(self):
	self.zpydoc.manage_addProduct['Zpydoc'].manage_addZpyDocumentable(PRODUCTS, 'Zope')
        documentable = getattr(self.zpydoc, '0')
	documentable._file_permissions['Zpydoc'] = {'Authenticated':1}


        self.failUnless(documentable.packages(all=True))

        self.login()
        user = getSecurityManager().getUser()
        self.assertEqual(user.getRoles(), ('test_role_1_', 'Authenticated'))
        
        #self.assertEqual(documentable.isPermitted('Zpydoc', user), True)
        self.assertEqual(documentable.packages(),
                         [{'ispackage': 1, 'name': 'Zpydoc', 'file': '/usr/lib/zope/lib/python/Products/Zpydoc'}])

        self.logout()
        user = getSecurityManager().getUser()
        self.assertEqual(user.getRoles(), ('Anonymous',))
        self.assertEqual(documentable.isPermitted('Zpydoc', user), False)
        self.assertEqual(documentable.packages(), [])
        
if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestZpydoc))
        return suite
