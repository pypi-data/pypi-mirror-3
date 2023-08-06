#!/usr/bin/env python
# Name:      lokai/packutil/util.py
# Purpose:   
# Copyright: 2011: Database Associates Ltd.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
#    See the License for the specific language governing permissions and
#    limitations under the License.

#-----------------------------------------------------------------------
# These utility routines are partly based on the distutils2 package,
# and partly not.
#-----------------------------------------------------------------------

import os
from fnmatch import fnmatchcase

import lokai.packutil.managers as hg_manager

#-----------------------------------------------------------------------

def convert_path(pathname):
    """Return 'pathname' as a name that will work on the native filesystem.

    i.e. split it on '/' and put it back together again using the current
    directory separator.  Needed because filenames in the setup script are
    always supplied in Unix style, and have to be converted to the local
    convention before we can actually use them in the filesystem.  Raises
    ValueError on non-Unix-ish systems if 'pathname' either starts or
    ends with a slash.
    """
    if os.sep == '/':
        return pathname
    if not pathname:
        return pathname
    if pathname[0] == '/':
        raise ValueError("path '%s' cannot be absolute" % pathname)
    if pathname[-1] == '/':
        raise ValueError("path '%s' cannot end with '/'" % pathname)

    paths = pathname.split('/')
    while os.curdir in paths:
        paths.remove(os.curdir)
    if not paths:
        return os.curdir
    return os.path.join(*paths)



def _is_package(path):
    """Returns True if path is a package (a dir with an __init__ file."""
    if not os.path.isdir(path):
        return False
    return os.path.isfile(os.path.join(path, '__init__.py'))


def _under(path, root):
    path = path.split(os.sep)
    root = root.split(os.sep)
    if len(root) > len(path):
        return False
    for pos, part in enumerate(root):
        if path[pos] != part:
            return False
    return True


def _package_name(root_path, path):
    """Returns a dotted package name, given a subpath."""
    if not _under(path, root_path):
        raise ValueError('"%s" is not a subpath of "%s"' % (path, root_path))
    return path[len(root_path) + 1:].replace(os.sep, '.')


def find_packages(paths=(os.curdir,), exclude=()):
    """Return a list all Python packages found recursively within
    directories 'paths'

    'paths' should be supplied as a sequence of "cross-platform"
    (i.e. URL-style) path; it will be converted to the appropriate local
    path syntax.

    'exclude' is a sequence of package names to exclude; '*' can be used as
    a wildcard in the names, such that 'foo.*' will exclude all subpackages
    of 'foo' (but not 'foo' itself).

    """
    packages = []
    discarded = []

    def _discarded(path):
        for discard in discarded:
            if _under(path, discard):
                return True
        return False

    for path in paths:
        path = convert_path(path)
        for root, dirs, files in os.walk(path):
            for dir_ in dirs:
                fullpath = os.path.join(root, dir_)
                if _discarded(fullpath):
                    continue
                # we work only with Python packages
                if not _is_package(fullpath):
                    discarded.append(fullpath)
                    continue
                # see if it's excluded
                excluded = False
                package_name = _package_name(path, fullpath)
                for pattern in exclude:
                    if fnmatchcase(package_name, pattern):
                        excluded = True
                        break
                if excluded:
                    continue

                # adding it to the list
                packages.append(package_name)
    return packages

#-----------------------------------------------------------------------

def find_hg_version(location='.'):
    """ Use the version frmo the Mercurial repository
    """
    hg = hg_manager.SubprocessManager(location)
    version = hg.get_current_version()
    return version
            
#-----------------------------------------------------------------------
class CfgOut(object):
    """ Output a ditutils2 configuration file """

    meta_list = {'name': 's',
                 'version': 's',
                 'platform': 'm',
                 'supported-platform': 'm',
                 'author': 's',
                 'author-email': 's',
                 'maintainer': 's',
                 'maintainer_email': 's',
                 'summary': 's',
                 'description': 's',
                 'description-file': 's',
                 'keywords': 's',
                 'home_page': 's',
                 'download-url': 's',
                 'license': 's',
                 'classifier': 'm',
                 'requires-dist': 'm',
                 'provides-dist': 'm',
                 'obsoletes-dist': 'm',
                 'requires-python': 'm',
                 'requires-externals': 'm',
                 'project-url': 'm',
                 }

    file_list = {'packages_root': 's',
                 'modules': 'm',
                 'packages': 'm',
                 'scripts': 'm',
                 'extra_files': 'm',
                 'package_data': 'm',
                 'data_files': 'm',
                 }
                 
    def __init__(self, given_file, **kwargs):
        """ Set up the given file as output, and use kwargs to set up
            the data.
        
            Each kwarg sould correspond to a named entry in meta_list
            or file_list.

            Where an entry is marked as 's' the kwarg should be a
            single string.

            Where an entry is marked as 'm' the kwarg should be a
            list.
        """
        if hasattr(given_file, 'write'):
            self.fp = given_file
        else:
            self.fp = open(given_file, 'w')
        self.data = kwargs
        
    def _option(self, name, multi):
        """ output only if there is something to output """
        value = self.data.get(name)
        if value is not None:
            if multi == 's':
                self.fp.write('%s = %s\n' % (name, value))
            else:
                if len(value) > 0:
                    text_out = '%s = %s' % (name, '\n      '.join(value))
                    self.fp.write(text_out)
                    self.fp.write('\n')

    def process(self):
        self.fp.write('[metadata]\n')
        for name, multi in self.meta_list.iteritems():
            self._option(name, multi)

        self.fp.write('[files]\n')
        for name, multi in self.file_list.iteritems():
            self._option(name, multi)
        
#-----------------------------------------------------------------------
