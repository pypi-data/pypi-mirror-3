# Name:      lokai/lk_worker/extensions/extension_manager.py
# Purpose:   Pick up and save any extensions
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
import glob

import lokai.tool_box.tb_common.configuration as config

#-----------------------------------------------------------------------

LK_REGISTER_TYPES = 'lk_register_types'
LK_REGISTER_MODELS = 'lk_register_models'
LK_REGISTER_CONTROLLERS = 'lk_register_controllers'
LK_REGISTER_VIEWS = 'lk_register_views'
LK_REGISTER_TYPES_AND_MODELS = [LK_REGISTER_TYPES, LK_REGISTER_MODELS]
LK_REGISTER_ALL = [LK_REGISTER_TYPES, LK_REGISTER_MODELS,
                   LK_REGISTER_CONTROLLERS, LK_REGISTER_VIEWS]

#-----------------------------------------------------------------------

def get_base_module(module, module_string):
    """ Run down the module hierarchy to find the rightmost item
    """
    target = module
    for name in module_string.split('.')[1:]:
        target = getattr(target, name)
    return target

def get_module_file(module_string):
    """ Import the module given by module_string and find the full
        path to the file at the rightmost end.
    """
    module = __import__(module_string)
    return get_base_module(module, module_string).__file__
    
def get_register_extensions(module_string, file_path_set, load_function):
    """ Try to import everything in file_name_set
    """
    for file_path in file_path_set:
        file_name = os.path.basename(file_path)
        mod_name, ext = os.path.splitext(file_name)
        module_string = '.'.join([module_string, mod_name])
        module = __import__(module_string)
        base_module = get_base_module(module, module_string)
        if isinstance(load_function, (type(()), type([]))):
            load_set = load_function
        else:
            load_set = [load_function]
        for function in load_set:
            if hasattr(base_module, function):
                # Execute the required registration module
                getattr(base_module, function)()

def get_package_extensions(package, load_function):
    """ Get the actual package extension files and pass the results to
        be registered.
    """
    pack_file = get_module_file(package)
    pack_path = os.path.dirname(pack_file)
    try_1 = glob.glob(os.path.join(pack_path, 'lk_register_extensions.py'))
    get_register_extensions(package, try_1, load_function)
    try_2 = glob.glob(os.path.join(pack_path, 'lk_register_*_extensions.py'))
    get_register_extensions(package, try_2, load_function)

        
def get_all_extensions(load_function):
    """ Get the package_xxx entries from the ini file, find the target
        extension files, import them.
    """
    # Start with the essentials
    get_package_extensions('lokai.lk_worker.models', load_function)
    get_package_extensions('lokai.lk_worker.ui', load_function)
    # Now look for other stuff
    cs = config.get_global_config()
    cs_worker = cs.get('lk_worker', {})
    package_set = cs_worker.get('package', {})
    for package in package_set.itervalues():
        get_package_extensions(package, load_function)
        
#-----------------------------------------------------------------------
