#!/usr/bin/python
# Name:      lokai/lk_worker/sys_procs/lk_import_node.py
# Purpose:   Find a node and export it
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

# Find one or more nodes and print a serialisation to stdout

#-----------------------------------------------------------------------

import yaml
import base64
import StringIO

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_common.configuration import handle_ini_declaration
from lokai.tool_box.tb_common.dates import timetostr

from lokai.lk_worker.extensions.extension_manager import (
    get_all_extensions,
    LK_REGISTER_TYPES_AND_MODELS)

from lokai.lk_worker.models import model
from lokai.lk_worker.models.builtin_data_attachments import make_version
from lokai.lk_worker.nodes.data_interface import get_node_dataset
from lokai.lk_worker.nodes.search import find_from_string
from lokai.lk_worker.nodes.graph import make_link
from lokai.lk_worker.models import ndNode
from lkoai.lk_worker.models.builtin_data_activity import (
    ndHistory,
    ndActivity,
    )
from lkoai.lk_worker.models.builtin_data_attachments import NodeAttachment

#-----------------------------------------------------------------------

table_map = {'ndNode': ndNode,
             'ndActivity': ndActivity
             }

def populate_row(table, data_set):
    """ create a table object and put some data into it
    """
    table_object = table_map[table]()
    for item,value in data_set.iteritems():
        table_object[item] = value
    return table_object

def import_node(source, parent):
    """ Import from source and use parent where needed
    """
    # Keep a record of nde_idx values read in from source and mapped
    # to the new idx values as we progress.
    idx_map={}
    node_list = yaml.load(source)
    for node_data in node_list:
        print node_data
        table_set = node_data['nd_node']
        data_set = table_set['ndNode']
        node_object = populate_row('ndNode', data_set)
        old_nde_idx = node_object['nde_idx']
        new_nde_idx = node_object.get_next_in_sequence()
        idx_map[old_nde_idx] = new_nde_idx
        node_object['nde_idx'] = new_nde_idx
        engine.session.add(node_object)
        for table, data_set in table_set.iteritems():
            if table != 'ndNode':
                table_object = populate_row(table, data_set)
                table_object['nde_idx'] = new_nde_idx
                engine.session.add(table_object)
        if 'attachments' in node_data:
            for nda_data in node_data['attachments']:
                nda_data['other_location'] = new_nde_idx
                nda = NodeAttachment('node',
                                     new_nde_idx,
                                     nda_data['file_name'])
                nda.set_from_object(nda_data)
                
                nda.store(StringIO.StringIO(
                    base64.b64decode(nda_data['file_content'])))
        if 'parent' in node_data:
            parent_idx = node_data['parent']
            if parent_idx:
                make_link(new_nde_idx, idx_map[parent_idx])
            else:
                make_link(new_nde_idx, parent)
        engine.session.flush()
    engine.session.commit()

#-----------------------------------------------------------------------

def main_():
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    parser.description = ("Import one or more nodes under a parent. "
                          )
    parser.usage = "%prog [options] node_criterion [node_criterion]"
    parser.add_option('-p', '--parent',
                      dest = 'parent_id',
                      help = 'Client reference, IDX path for the parent.'
                      ' Default None.',
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
        print "Using        : %s"%' '.join(args)
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

    for argstring in args:
        source_file = argstring.open()
        import_data(source_file, target_parent)

    return 0 # Success?

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
