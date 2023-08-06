#!/usr/bin/python
# Name:      lokai/lk_worker/sys_procs/lk_find_node.py
# Purpose:   Find a node from the command line
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

# Find one or more nodes and return either just the IDX set, or some
# more detail

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
from lokai.lk_worker.nodes.node_data_functions import NodeFamily

#-----------------------------------------------------------------------

def print_node_full(nde_idx):
    if nde_idx is not None:
        node_data = get_node_dataset(nde_idx)
        print "------------------------------"
        if 'nd_node' in node_data and node_data['nd_node']:
            detail = node_data['nd_node']
            print detail['nde_idx'], detail['nde_name']
            print "Reference", detail['nde_client_reference']
            print "Type", detail['nde_type']
            print "Created", timetostr(detail['nde_date_create'])
            print "Modified", timetostr(detail['nde_date_modify'])

def print_node_part(nde_idx):
    if nde_idx is not None:
        node_data = get_node_dataset(nde_idx)
        if 'nd_node' in node_data and node_data['nd_node']:
            detail = node_data['nd_node']
            if detail['nde_client_reference']:
                out_text = detail['nde_client_reference']
                if ' ' in out_text:
                    if "'" in out_text:
                        out_text = '"%s"'%out_text
                    else:
                        out_text = "'%s'"%out_text
                print out_text,
            else:
                print nde_idx,

def parent_of(nde_idx):
    ndf = NodeFamily(node=nde_idx)
    if ndf.parents:
        return ndf.parents[0].nde_idx
    else:
        return None

#-----------------------------------------------------------------------

def main_():
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    parser.description = ("Find one or more nodes using node name "
                          "(with wild cards) or a path. Use a parent "
                          "node to search down from")
    parser.usage = "%prog [options] node_criterion [node_criterion]"
    parser.add_option('-p', '--parent',
                      dest = 'parent_id',
                      help = 'Client reference, IDX path for the parent.'
                      ' Default None.',
                      )
    parser.add_option('-l', '--full',
                      dest = 'full',
                      help = "Output some details for each node",
                      action = 'store_true'
                      )
    parser.add_option('-u', '--up',
                      dest = 'up',
                      help = "Output details of parent (full or otherwise)",
                      action = 'store_true'
                      )
    parser.add_option('-v', '--verbose',
                      dest = 'talk_talk',
                      help = "Request some feed back from the process",
                      action = 'count'
                      )
    parser.set_defaults(description="Created by make_node from the command line")

    handle_ini_declaration(prefix='lk')
 
    (options, args) = parser.parse_args() 

    if options.talk_talk:
        print "Seeking        : %s"%' '.join(args)
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

    for candidate in candidates:
        if options.up:
            nde_idx = parent_of(candidate)
        else:
            nde_idx = candidate
        if options.full:
            print_node_full(nde_idx)
        else:
            print_node_part(nde_idx)

    return 0 # Success?

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
