# Name:      lokai/tool_box/tb_common/import_helpers.py
# Purpose:   Provides some tools for interpreting module paths
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

import os
from types import ModuleType

#-----------------------------------------------------------------------

def get_base_module(module, module_string):
    """ Run down the module hierarchy to find the rightmost item
    """
    target = module
    for name in module_string.split('.')[1:]:
        target = getattr(target, name)
    return target

def get_module_attribute(module_string, default=None):
    """ Import the module given by module_string and find the
        rightmost attribute.

        If the module string defines a module and the default is given
        then the function returns the default attribute within the
        module.
    """
    module_list = module_string.split('.')
    if len(module_list) == 1:
        raise ImportError(
            "Package %s must have an attribute to search for" % module_string)
    module = __import__('.'.join(module_list[:-1]))
    try:
        candidate = get_base_module(module, module_string)
        if isinstance(candidate, ModuleType):
            raise AttributeError("%s Points to a module" % module_string)
        return candidate
    except AttributeError, e:
        # If module_list[:-1] picks up a package we need to retry...
        module = __import__(module_string)
        candidate = get_base_module(module, module_string)
        if default and isinstance(candidate, ModuleType):
            return getattr(candidate, default)
        raise

def get_module_file(module_string):
    """ Import the module given by module_string and find the full
        path to the file at the rightmost end.
    """
    module = __import__(module_string)
    return get_base_module(module, module_string).__file__

def get_module_path(module_string):
    """ Import the module given by module_string and find the full
        path to the module directory.

        The file name for a given module path should point to a .py or
        .pyc file, so we just need to return the path.
    """
    return os.path.dirname(get_module_file(module_string))

#-----------------------------------------------------------------------
