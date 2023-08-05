# Name:      lokai/lk_worker/nodes/data_interface.py
# Purpose:   Handle create/update of node details
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

""" Interfaces to create or update node details in the database:

    The interface uses a dictionary structure that is built up of all
    the elements that make up a complete node.

    The elements are:

        ['nd_node'] = {} for basic node. This can be a mapped object.

        ['message'] = {} for a history entry.

        ['nd_activity'] = {} for associated nd_activity record.


    Other entries may be added as they are identified

    Validation:

        The data is checked against a set of absolute rules and errors
        are raised. There is no gentle return to the calling
        application as the application itself is responsible for
        getting it right. Specifically, user input should be checked
        at source.
"""

#-----------------------------------------------------------------------

from sqlalchemy import or_

import lokai.tool_box.tb_common.dates as dates

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update

from lokai.lk_worker.models import ndNode, ndEdge

from lokai.lk_worker import (ndDataUpdate,
                             ndDataValidation,
                             ndDataRedundantKey,
                             ndNotEmpty,
                             )

from lokai.lk_worker.nodes.graph import child_trees

#-----------------------------------------------------------------------

import pyutilib.component.core as component
from lokai.lk_worker.extensions.data_interface import IWorkerData

data_extensions = component.ExtensionPoint(IWorkerData)

#-----------------------------------------------------------------------

def put_node_dataset(new_data, old_data=None):
    """ Store the data in the data source and return the idx

        Old data is provided so that is can be used in extensions for
        deciding when to delete, update or insert.
    """
    node_set = insert_or_update(ndNode, new_data['nd_node'])
    if len(node_set) == 1:
        engine.session.flush()
        nde_idx = node_set[0].nde_idx
        new_data['nd_node']['nde_idx'] = nde_idx
        for extn in data_extensions():
            extn.nd_write_data_extend(new_data, old_data)

        return nde_idx
    raise ndDataUpdate

#-----------------------------------------------------------------------

def validate_node_dataset(new_data, old_data=None):
    """ Raise errors that represent validation issues with the given
        data.

        Some validations depend on what was, or was not, there
        previously, so we need the old data as well.
    """
    #
    # Node name...
    item = new_data['nd_node'].get('nde_name', None)
    if not item or not item.strip():
        raise ndDataValidation(
            'Missing node name')
    #
    # Description or message
    if not old_data or not old_data['nd_node']:
        # This must be new, so we need a description
        item = new_data['nd_node'].get('nde_description', None)
        if not item or not item.strip():
            raise ndDataValidation(
                'Missing description for new node')
        if len(item.strip()) < 10:
            raise ndDataValidation(
                'Insufficient description for new node')
    else:
        # Let's force a message (not sure about this)
        item = new_data.get(
            'message', {'message': {}}).get('hst_text', None)
        if not item or not item.strip():
            raise ndDataValidation(
                'Missing message for for node update')
        if len(item.strip()) < 10:
            raise ndDataValidation(
                   'Insufficient message for node update')
    #
    # Dates must be given
    dt = new_data['nd_node'].get('nde_date_modify', None)
    if dt:
        try:
            modify_date = dates.strtotime(dt)
        except dates.ErrorInDateString:
            raise ndDataValidation(
                'Bad node modify date: %s'%str(dt))
    else:
        raise ndDataValidation(
            'No node modify date: %s')
    dt = new_data['nd_node'].get('nde_date_create', None)
    if not old_data or not old_data['nd_node']:
        #
        # New node
        if dt:
            try:
                create_date = dates.strtotime(dt)
            except dates.ErrorInDateString:
                raise ndDataValidation(
                    'Bad node create date: %s'%str(dt))
            if modify_date != create_date:
                raise ndDataValidation(
                    'Create date must equal modify date for new node')
        else:
            new_data['nd_node']['nde_date_create'] = (
                new_data['nd_node']['nde_date_modify'])
    else:
        if dt:
            raise ndDataValidation(
                'Cannot update create date')
        
    for extn in data_extensions():
        extn.nd_validate_data_extend(new_data, old_data)

#-----------------------------------------------------------------------

def compare_node(new_data, old_data=None):
    """ Generate a list of update messages that can go into a history
        object.
    """
    op = []
    if old_data and old_data['nd_node']:
        for k in new_data['nd_node']:
            try:
                if new_data['nd_node'][k] != old_data['nd_node'][k]:
                    op.append("Update %s: from %s: to %s"%
                              (old_data['nd_node'][k],
                               new_data['nd_node'][k]))
            except KeyError:
                raise ndDataRedundantKey(
                    'Compare node: Source key % not found'% k)
    return op

#-----------------------------------------------------------------------

def compare_activity(new_data, old_data):
    """ Generate a list of update messages that can go into a history
        object.
    """
    op = []
    if old_data['nd_activity']:
        for k in new_data['nd_activity']:
            try:
                if (new_data['nd_activity'][k] !=
                    old_data['nd_activity'][k]):
                    op.append("Update %s: from %s: to %s"%
                              (old_data['nd_activity'][k],
                               new_data['nd_activity'][k]))
            except KeyError:
                raise ndDataRedundantKey(
                    'Compare activity: Source key % not found'% k)
    return op

#-----------------------------------------------------------------------

def get_node_dataset(object_reference, given_extensions=None, **kwargs):
    """ Build a dictionary of elements representing a node and some
        (not all) dependent data. Useful for UI work.

        :object_reference: idx of the node

        :given_extensions: one or more specific extension data sets to
            pick up. The default is to pick up all data sets.
        
        The kwargs are passed down to the extension functions for
        interpretation by them. This allows linked data to be
        collected and stored in the data object.
        
    """
    if given_extensions:
        if isinstance(given_extensions, type('')):
            use_extensions = [data_extensions.service(given_extensions)]
        else:
            use_extensions = [data_extensions.service(x) for x in
                              set(given_extensions)]
    else:
        use_extensions = data_extensions()
                          
    main_query = engine.session.query(ndNode).filter(
        ndNode.nde_idx == object_reference
        )

    for extn in use_extensions:
        main_query = extn.nd_read_query_extend(main_query, **kwargs)

    main_data = main_query.one()

    if isinstance(main_data, (list, tuple)):
        node_object = main_data[0]
    else:
        node_object = main_data
    local_obj = {'nd_node' : node_object,
                 'original_result': main_data}

    for extn in use_extensions:
        local_obj.update(extn.nd_read_data_extend(main_data, **kwargs))

    return local_obj

#-----------------------------------------------------------------------

def delete_node_dataset(object_data):
    """ Using the given data object, delete the node and
        all associated data.
    """
    nde_idx = object_data['nd_node']['nde_idx']
    child_set = child_trees(nde_idx)
    if len(child_set) > 0:
        raise ndNotEmpty
    for extn in data_extensions():
        extn.nd_delete_data_extend(object_data)
    engine.session.query(ndNode).filter(
        (ndNode.nde_idx == nde_idx)).delete()
    engine.session.query(ndEdge).filter(
        (ndEdge.nde_child == nde_idx)).delete()
    
#-----------------------------------------------------------------------

def get_node_from_reference(object_reference):
    """ Fetch a node object where the given reference can be either a
        client_reference or an idx.

        If there is an idx somewhere that matches a client reference
        somewhere else then we will get both responses.
    """
    main_query = engine.session.query(ndNode).filter(
        or_((ndNode.nde_idx == object_reference),
            (ndNode.nde_client_reference == object_reference)
        ))
    result_set = main_query.all()
    if len(result_set) == 1:
        return result_set[0].nde_idx # >>>>>>>>>>>>>>>>>>>>
    return None
        
    
#-----------------------------------------------------------------------
