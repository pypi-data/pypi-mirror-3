#!/usr/bin/python
# Name:      lokai/lk_worker/sys_procs/lk_link_node.py
# Purpose:   Link a node from the command line
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

# Link a node from to a new parent. Optionally unlink old.

#-----------------------------------------------------------------------

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_common.configuration import handle_ini_declaration
from lokai.tool_box.tb_common.dates import timetostr

from lokai.lk_worker.extensions.extension_manager import (
    get_all_extensions,
    LK_REGISTER_TYPES_AND_MODELS)

from lokai.lk_worker.models import model

from lokai.lk_worker.nodes.graph import make_link, make_unlink
from lokai.lk_worker.nodes.data_interface import get_node_dataset
from lokai.lk_worker.nodes.search import find_from_string
from lokai.lk_worker.nodes.node_data_functions import NodeFamily

#-----------------------------------------------------------------------

def move_this_node(node_set, parent_id, move_me):
    for nde_idx in node_set:
        if move_me:
            ndf = NodeFamily(node=nde_idx)
            for parent in ndf.parents:
                make_unlink(nde_idx, parent.nde_idx)

        if parent_id:
            make_link(nde_idx, parent_id)

#-----------------------------------------------------------------------

def main_():
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    parser.description = ("Link a node set to new parent. Node set is "
                          "identified by a path, idx or client reference")
    parser.usage = "%prog [options] node_criterion [node_criterion]"
    parser.add_option('-p', '--parent',
                      dest = 'parent_id',
                      help = 'Client reference, IDX or path for the new parent.'
                      ' Default None.',
                      )
    parser.add_option('-v', '--verbose',
                      dest = 'talk_talk',
                      help = "Request some feed back from the process",
                      action = 'count'
                      )
    parser.add_option('-m', '--move',
                      dest = 'move',
                      help = "Set this to move from one parent to another. "
                      "All exiting parents are unlinked",
                      action = 'store_true'
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
        print "Moving         : %s"%' '.join(args)
        print "Options: Parent: %s"%str(options.parent_id)


    # configure these models
    model.init()
    get_all_extensions(LK_REGISTER_TYPES_AND_MODELS)

    if options.parent_id is not None:
        nde_idx = find_from_string(options.parent_id)
        if nde_idx:
            existing_parent = get_node_dataset(nde_idx[0])
            if not existing_parent['nd_node']:
                parser.error("Given parent ID not found")
            target_parent = existing_parent['nd_node']['nde_idx']
        else:
            parser.error("Given parent ID not found")
    else:
        target_parent = None

    candidates = []
    for argstring in args:
        candidates.extend(find_from_string(argstring))

    move_this_node(candidates, target_parent, options.move)
    if options.do_nothing is None:
        engine.session.commit()

    return 0 # Success?

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
