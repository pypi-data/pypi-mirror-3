#!/usr/bin/python
# Name:      lokai/lk_worker/sys_procs/lk_make_node.py
# Purpose:   Create a node from the command line
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

# Very basic create generic node. Useful for quick fix when using
# other command line programs.

#-----------------------------------------------------------------------

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_common.configuration import handle_ini_declaration
from lokai.tool_box.tb_common.dates import timetostr, now

from lokai.lk_worker.nodes.data_interface import put_node_dataset

from lokai.lk_worker.extensions.extension_manager import (
    get_all_extensions,
    LK_REGISTER_TYPES_AND_MODELS)

from lokai.lk_worker.models import model

from lokai.lk_worker.nodes.data_interface import get_node_dataset
from lokai.lk_worker.nodes.search import find_from_string
from lokai.lk_worker.nodes.graph import make_link

#-----------------------------------------------------------------------

def make_this_node(node_name, parent_id, options):
    time_stamp = now()
    node_data = {'nde_name': node_name,
                 'nde_type': 'generic',
                 'nde_date_create': time_stamp,
                 'nde_date_modify': time_stamp}
    if options.description:
        node_data['nde_description'] = options.description
    if options.client_reference:
        node_data['nde_client_reference'] = options.client_reference
    nde_idx = put_node_dataset({'nd_node': node_data})
    if parent_id:
        make_link(nde_idx, parent_id)

#-----------------------------------------------------------------------

def main_():
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    parser.description = "Create a generic node"
    parser.usage = "%prog [options] node_name"
    parser.add_option('-p', '--parent',
                      dest = 'parent_id',
                      help = 'Client reference, IDX or path for the parent.'
                      ' Default None.',
                      )
    parser.add_option('-r', '--reference',
                      dest = 'client_reference',
                      help = 'Unique client reference for the new node'
                      )
    parser.add_option('-d', '--description',
                      dest = 'description',
                      help = 'Description text for the new node',
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
        print "Creating          : %s"%' '.join(args)
        print "Options: reference: %s"%str(options.client_reference)
        print "       Description: %s"%str(options.description)
        print "            Parent: %s"%str(options.parent_id)


    # configure these models
    model.init()
    get_all_extensions(LK_REGISTER_TYPES_AND_MODELS)

    if options.client_reference is not None:
        nde_idx = get_node_from_reference(options.client_reference)
        if nde_idx is not None:
            existing_data = get_node_dataset(nde_idx)
            if existing_data['nd_node']:
                parser.error("Given client reference is already used")

    if options.parent_id is not None:
        nde_idx = find_from_string(options.parent_id)
        if nde_idx is not None:
            existing_parent = get_node_dataset(nde_idx[0])
            if not existing_parent['nd_node']:
                parser.error("Given parent ID not found")
            target_parent = existing_parent['nd_node']['nde_idx']
        else:
            parser.error("Given parent ID not found")
    else:
        target_parent = None

    make_this_node(' '.join(args), target_parent, options)
    if options.do_nothing is None:
        engine.session.commit()

    return 0 # Success?

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
