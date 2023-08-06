# Name:      lokai/lk_worker/yaml_import.py
# Purpose:   Initialise node data from a yaml file
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
#-----------------------------------------------------------------------

import copy
import csv
from sqlalchemy import and_
import lokai.tool_box.tb_common.notification as notify
from lokai.tool_box.tb_database.orm_interface import engine

import lokai.lk_worker
from lokai.lk_worker.nodes.graph import make_link
from lokai.lk_worker.nodes.data_interface import put_node_dataset
from lokai.lk_worker.nodes.search import find_in_path
from lokai.lk_worker.models.builtin_data_resources import (ndRoleAllocation,
                                                           ndUserAssignment)

#-----------------------------------------------------------------------

def find_node(path_1, name = None):
    """ Tack the paths together and do a search.

        Always search forrest.

        Force a text path to start with '=' to avoid unlooked for
        wildcard searches.
    """
    if isinstance(path_1, list):
        path_0 = path_1
    elif path_1 == None:
        path_0 = []
    else:
        # Assume string
        if path_1[0] == "=":
            reader = csv.reader([path_1[1:]], delimiter='/')
        else:
            reader = csv.reader([path_1], delimiter='/')
        path_0 = []
        for element in reader.next():
            path_0.append(element)
    if name != None:
        path_0.append(name)
    
    res = find_in_path(path_0)
    return res

#-----------------------------------------------------------------------

class YamlNodes(object):
    """ Class built on YamlImport to handle node content data

        Designed to be used as a mixin
    """

    def __init__(self, **kwargs):
        self.register('node', self.process_nodes)

    #-------------------------------------------------------------------
    
    def process_nodes(self, data_set):
        # A node set is a list of nodes
        for item in data_set:
            self._base_process_node(item)

    #-------------------------------------------------------------------

    def _base_process_node(self, item):
        """ Place a node and link to parents
        """

        node_data_exclude_list = ['parent']
        
        node_str = "Node - %s with %s" % (str(item['nd_node']['nde_name']),
                                          str(item))
        item_parent = item.get('parent')
        # check the parent
        parent_idx = None
        if item_parent != None:
            parent_idx_set = find_node(item_parent)
            if len(parent_idx_set) > 1:
                notify.warn(
                    "Error: found more than one parent %s for %s"%
                    (item['parent'], item['nd_node']['nde_name']))
                return False
            if len(parent_idx_set) == 0:
                notify.warn(
                    "Error: found no parent %s for %s"%
                    (item['parent'], item['nd_node']['nde_name']))
                return False
            parent_idx = parent_idx_set[0]
        nde_set = find_node(item_parent, item['nd_node']['nde_name'])
        if len(nde_set) == 1:
            nde_idx = nde_set[0]
            notify.info("Found %s" % node_str)
            nde_obj = copy.deepcopy(item)
            nde_obj['nd_node']['nde_date_modify'] = self.time_now
            nde_obj['message'] = item.get('message',{})
            if not 'hst_text' in nde_obj['message']:
                nde_obj['message']['hst_text'] = (
                    "Automatic update from data file")
            nde_obj['message']['hst_user'] = 'auto'
            nde_obj['message']['hst_type'] = 'auto'
            nde_obj['message']['hst_time_entry'] = self.time_now

            nde_idx = put_node_dataset(nde_obj, nde_set[0])
            
        elif len(nde_set) == 0:
            nde_obj = copy.deepcopy(item)
            nde_obj['nd_node']['nde_date_create'] = self.time_now
            nde_obj['nd_node']['nde_date_modify'] = self.time_now
            nde_obj['message'] = item.get('message',{})
            if not 'hst_text' in nde_obj['message']:
                nde_obj['message']['hst_text'] = (
                    "Automatic creation from data file")
            nde_obj['message']['hst_user'] = 'auto'
            nde_obj['message']['hst_type'] = 'auto'
            nde_obj['message']['hst_time_entry'] = self.time_now

            nde_idx = put_node_dataset(nde_obj)
            notify.info("Stored %s" % node_str)
            if parent_idx:
                try:
                    make_link(nde_idx, parent_idx)
                    notify.info(
                        "Linked %s to %s"%(nde_idx, parent_idx))
                except lokai.lk_worker.ndGraphCycle:
                    notify.warn(
                        "Error: parent %s leads to cycle for %s"%
                        (item['parent'], item['nd_node']['nde_name']))
                    return False
        return True

#-----------------------------------------------------------------------

class YamlLinks(object):
    """ Class built on YamlImport to handle additional node links

        Designed to be used as a mixin
    """

    def __init__(self, **kwargs):
        self.register('link', self.process_links) 

    def process_links(self, data_set):
        # A link set is a list of links
        if not data_set:
            return
        for item in data_set:
            self._base_process_link(item)

    def _base_process_link(self, item):
        """ Identify child and parent, and make the link """

        child_path = item[0]
        parent_path = item[1]

        child_idx_set = find_node(child_path)
        if len(child_idx_set) != 1:
            if len(child_idx_set) > 1:
                notify.warn("Error: found more than one node for path %s"%
                    (child_path))
                return False
            else:
                notify.warn("Error: failed to find node for path %s"%
                    (child_path))
                return False
                        
        parent_idx_set = find_node(parent_path)
        if len(parent_idx_set) != 1:
            if len(parent_idx_set) > 1:
                notify.warn("Error: found more than one node for path %s"%
                    (cparent_path))
                return False
            else:
                notify.warn("Error: failed to find node for path %s"%
                    (parent_path))
                return False
        make_link(child_idx_set[0], parent_idx_set[0])
        return True

#-----------------------------------------------------------------------
                
