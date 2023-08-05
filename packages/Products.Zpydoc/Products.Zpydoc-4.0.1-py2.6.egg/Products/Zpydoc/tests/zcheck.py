#
# To run the ZChecker on all skins in this instance type
#
#   $ python zcheck.py [-q]
#

__version__ = '0.2.0'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Suppress DeprecationWarnings, we really don't want any in these tests
import warnings
warnings.simplefilter('ignore', DeprecationWarning, append=1)

from Testing import ZopeTestCase
from Testing.ZopeTestCase import _print

ZopeTestCase.installProduct('PlacelessTranslationService')
ZopeTestCase.installProduct('ZChecker')

from Products.CMFPlone.tests import PloneTestCase


class TestSkins(PloneTestCase.PloneTestCase):
    # Note: This looks like a unit test but isn't

    def afterSetUp(self):
        factory = self.portal.manage_addProduct['ZChecker']
        factory.manage_addZChecker('zchecker')
        self.verbose = not '-q' in sys.argv

    def testSkins(self):
        '''Runs the ZChecker on skins'''
        dirs = self.portal.portal_skins.objectValues()
        for dir in dirs:
            # filter out certain skin layers
            #print self._skinpath(dir)
            if self._skinpath(dir) in ['portal_skins/zpydoc']:
                results = self.portal.zchecker.checkObjects(dir.objectValues())
                for result in results:
                    self._report(result)
        if self.verbose:
            _print('\n')

    def testZMI(self):
	''' WAM trying this ...'''
	pass

    def _report(self, result):
        msg = result['msg']
        obj = result['obj']
        if msg:
            if self.verbose:
                _print('\n')
            _print('------\n%s\n' % self._skinpath(obj))
            for line in msg:
                _print('%s\n' % line)
        else:
            if self.verbose:
                _print('.')

    def _skinpath(self, obj):
        path = obj.absolute_url(1)
        path = path.split('/')
        return '/'.join(path[1:])


if __name__ == '__main__':
    TestRunner(verbosity=0).run(test_suite())
