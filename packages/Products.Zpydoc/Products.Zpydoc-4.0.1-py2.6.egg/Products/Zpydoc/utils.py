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

import string, os, pydoc, sys, inspect, types, __builtin__

all_paths = pydoc.pathdirs

# cache this
pythonpath = all_paths()

#
# we wish to add granular module selection in our python path selections
#
# at the least for Zope ...  (TODO generalise this ...)
#

zopepath = [ os.path.join(os.environ.get('SOFTWARE_HOME'), 'Products'),
             os.path.join(os.environ.get('INSTANCE_HOME'), 'Products') ]


sane_pythonpath = ['builtin__'] + pythonpath + zopepath

# we need a coherent ordering to determine relative paths ...
sane_pythonpath.sort()

#
# cache all the known (safe as in already imported) module names in this server/installation
#
# note this is filtering them to where they were initially defined, not referenced in other
# modules
#
# if it's not referenced and imported into the server already, it may not be safe to
# import later!!
#
all_modules = map(lambda x: x.__name__,
                  filter(lambda x: hasattr(x, '__path__'),
                                           sys.modules.values()))
all_modules.sort()



#
# anything beginning with '_' is considered private and unservable by Zope ...
#
def pydoc_encode(name):
    if name[0] == '_': return '-%s' % name[1:]
    return name

def pydoc_decode(name):
    if name[0] =='-': return '_%s' % name[1:]
    return name


def implementsMethod(object):
    try:
        return isinstance(object, types.MethodType) or \
             (hasattr(object,'__doc__') \
              and hasattr(object,'__name__') \
              and hasattr(object,'im_class') \
              and hasattr(object,'im_func') \
              and hasattr(object,'im_self') \
              and inspect.isfunction(object.im_func) \
             )
    except:
        raise

def locate(path, forceload=0):
    """
    find and wrecklessly import a module a module if we don't already have it!!
    """
    parts = [part for part in string.split(path, '.') if part]
    module, n = None, 0
    while n < len(parts):
        nextmodule = pydoc.safeimport(string.join(parts[:n+1], '.'), forceload)
        if nextmodule: module, n = nextmodule, n + 1
        else: break
    if module:
        object = module
        for part in parts[n:]:
            try: object = getattr(object, part)
            except AttributeError: return None
        return object
    else:
        if hasattr(__builtin__, path):
            return getattr(__builtin__, path)


