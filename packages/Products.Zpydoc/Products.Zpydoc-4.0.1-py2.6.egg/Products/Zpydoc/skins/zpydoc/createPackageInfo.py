## Script (Python) "createPackageInfo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object,name
##title=create/embellish introspection object
##
from Products.Zpydoc.inspectors.ZopeInfo import PackageInfo

return PackageInfo(object, name)
