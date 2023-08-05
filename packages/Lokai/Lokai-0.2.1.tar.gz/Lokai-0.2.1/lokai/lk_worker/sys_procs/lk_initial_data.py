#! /usr/bin/python
# Name:      lokai/lk_worker/sys_procs/lk_initial_data.py
# Purpose:   Initialise essential data. This should allow multiple calls.
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

# The program processes a python file that contains certain data sets.
#
# The process can be repeated. Data already in the database is left
# unchanged. New items are added.

#-----------------------------------------------------------------------

# This program is designed to handle setting up nodes in the nb
# database. Nodes are nested (linked to parents) so the setup includes
# handling links.

# The rules:
#
# - The parent of a node can be specified as empty, a single name, or
#   a path (string or list). If not empty, this path must result in a
#   single parent node. The implication is that all expected elements
#   must exist in order for the path to mean anything.
#
#   - The path search works the same way as the UI, using
#     search_filtered. Do not forget the '=' at the beginning of a
#     string with a '/' delimted path.
#
#   - The path search always starts from the top of the forest. That
#     is the previous node in the input data is never assumed to be
#     the parent of the node being processed.
#
# - Nodes are identified by node name. If the incomming data defines a
#   node of name 'xxx' and the database does not already contain a
#   node of name 'xxx' under the given path, then the node is
#   created.
#
#   This process cannot detect nodes that have been renamed, or nodes
#   that have been moved. Conversely, the process does not rename an
#   existing node, nor does it re-link an existing node.
#
# The input data:
#
# - The input uses yaml text formatting.
#
#   See http://yaml.org/spec/1.1/#id857168
#
# - The input may be divided into more than one document (using
#   '---'). This has no actual significance for the data processing.
#
# - Input data is not nested. Each node is specified separately as a
#   new entry in a list.
#
# - Input data follows the data structure required for
#   put_structured_data (q.v.) with an additional entry 'parent'
#   containing the path.
# 
#-----------------------------------------------------------------------

import sys
import os

import logging

import lokai.tool_box.tb_common.notification as notify
import lokai.tool_box.tb_common.configuration as config

from lokai.tool_box.tb_install.yaml_import import YamlImport
from lokai.lk_worker.extensions.extension_manager import (
    get_all_extensions,
    LK_REGISTER_TYPES_AND_MODELS,
    )
from lokai.lk_login.yaml_import import YamlLogin
from lokai.lk_worker.yaml_import import YamlNodes, YamlLinks

#-----------------------------------------------------------------------

# Can be passed on command line as --path=
globals()['default_path'] = './'

#-----------------------------------------------------------------------

# Get the data to process
# Can be passed on command line as --file=
self_dir, self_file = os.path.split(os.path.abspath(__file__))
param_file_default_name = 'lkw_initial_data.yml'
param_file_default = os.path.join(self_dir, param_file_default_name)

#-----------------------------------------------------------------------

class InitialDataSet(YamlImport, YamlLogin, YamlNodes, YamlLinks):

    def __init__(self, options):
        YamlImport.__init__(self, file= options.file, ignore=options.ignore)
        YamlLogin.__init__(self)
        YamlNodes.__init__(self)
        YamlLinks.__init__(self)
        self.process_all()
          
#-----------------------------------------------------------------------

def main_():
    from optparse import OptionParser
    parser = OptionParser(usage = ('usage: %prog [options]'))

    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      help='Be a bit wordy' )

    parser.add_option('-n', '--no-action', dest='ignore', action='store_true',
                      help='Do nothing with the database' )

    parser.add_option('-f', '--file', dest='file', action='store', 
                      help='Read input from this file')

    parser.add_option('--path', dest='path', action='store', 
                      default=None,
                      help='Default base path for folder parameters')

    parser.add_option('--env', dest='env', action='store', 
                      default='nix',
                      help='Environment trigger for predefined base paths')

    (options, args) = parser.parse_args()

    if options.verbose:
        print 'Verbosity set at %s' % str(options.verbose)
        
    config.handle_ini_declaration(prefix='lk')

    log_level = {1:logging.WARNING,
                 2:logging.INFO,
                 3:logging.DEBUG
                 }
    notify.setLogName(
        os.path.splitext(
        os.path.basename(sys.argv[0]))[0])
    level = min(options.verbose, 3)
    logging.basicConfig(level=log_level.get(level,
                                             logging.ERROR))
    this_logger = notify.getLogger()
    this_logger.setLevel(level)
    target_handler = logging.StreamHandler()
    debug_logger = logging.getLogger(notify.getDebugName())
    debug_logger.addHandler(logging.StreamHandler())
    this_logger.addHandler(logging.StreamHandler())
    import lokai.lk_worker.models
    lokai.lk_worker.models.model.init()
    get_all_extensions(LK_REGISTER_TYPES_AND_MODELS)
    
    ids = InitialDataSet(options)

    return 0 # Success?

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
