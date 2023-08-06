#!/usr/bin/python
# Name:      lokai/lk_worker/sys_procs/lk_remove_node.py
# Purpose:   Remove a node, associated data and sub tree - from the command line
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

# Remove an entire subtree, somewhat unconditionally. Use with extreme
# caution. Recommend that nodes are consigned to 'Oblivion' before
# removal.

# Uses same set of command line options as find_node, so can be use as
# a pair:
#
#  find_node xxx
#  remove_node xxx
#
# Or, since find node outputs a stream of nde_idx values:
#
#  remove_node `find_node xxx`
#
# Or, again
#
#  find_node xxx | xargs remove_node

#-----------------------------------------------------------------------

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_common.configuration import handle_ini_declaration
from lokai.tool_box.tb_common.dates import timetostr

from lokai.lk_worker.extensions.extension_manager import (
    get_all_extensions,
    LK_REGISTER_TYPES_AND_MODELS)

from lokai.lk_worker.models import model

from lokai.lk_worker.nodes.data_interface import get_node_dataset
from lokai.lk_worker.nodes.search import find_from_string
from lokai.lk_worker.nodes.node_data_functions import expunge_tree

#-----------------------------------------------------------------------

def main_():
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    parser.description = ("Remove one or more subtrees entirely, "
                          "with no backup. Node set is "
                          "identified by a path, idx or client reference")
    parser.usage = "%prog [options] node_criterion [node_criterion]"
    parser.add_option('-p', '--parent',
                      dest = 'parent_id',
                      help = 'Client reference, IDX or path for parent '
                             'to search down from',
                      )
    parser.add_option('-v', '--verbose',
                      dest = 'talk_talk',
                      help = "Request some feed back from the process",
                      action = 'count'
                      )
    parser.add_option('-n',
                      dest = 'do_nothing',
                      help = 'Do nothing',
                      action = 'store_true'
                      )
    parser.set_defaults(description="Created by make_node from the command line")

    handle_ini_declaration(prefix='lk')
 
    (options, args) = parser.parse_args() 

    if len(args) == 0:
        parser.error("A node name is required")

    if options.talk_talk:
        print "Removing       : %s"%' '.join(args)
        print "Options: Parent: %s"%str(options.parent_id)


    # configure these models
    model.init()
    get_all_extensions(LK_REGISTER_TYPES_AND_MODELS)

    parent_set = None
    if options.parent_id is not None:
        parent_set = find_from_string(options.parent_id)
        if options.talk_talk:
            print "Parents:", parent_set
        if not parent_set:
            parser.error("Parent ID did not find a parent")

    candidates = []
    for argstring in args:
        candidates.extend(find_from_string(argstring, parent_set))

    for nde_idx in candidates:
        if options.talk_talk:
            print "+++", nde_idx
        if options.do_nothing is None:
            # We delete files, so session.commit/rollback is not enough
            expunge_tree(nde_idx)
    if options.do_nothing is None:
        engine.session.commit()

    return 0 # Success?

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
