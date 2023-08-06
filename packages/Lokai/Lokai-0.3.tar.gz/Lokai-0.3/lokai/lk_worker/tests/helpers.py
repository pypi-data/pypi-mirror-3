# Name:      lokai/lk_worker/tests/helpers.py
# Purpose:   Support testing of node access
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

from sqlalchemy import delete

from lokai.tool_box.tb_common.dates import now
from lokai.tool_box.tb_common.configuration import (handle_ini_declaration,
                                              clear_global_config)
from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update
from lokai.tool_box.tb_common.helpers import check_tests_allowed

import lokai.lk_worker.models as lwm
import lokai.lk_worker.nodes.graph as graph
from lokai.lk_worker.extensions.extension_manager import (
    get_all_extensions,
    LK_REGISTER_TYPES_AND_MODELS,
    LK_REGISTER_CONTROLLERS,
    LK_REGISTER_VIEWS,
    )

from lokai.lk_worker.models import (ndNode,
                                    ndEdge,
                                    ndParent)
from lokai.lk_worker.models.builtin_data_activity import (ndActivity,
                                                          ndHistory)
from lokai.lk_worker.models.builtin_data_resources import (ndRoleAllocation,
                                                           ndUserAssignment)
from lokai.lk_worker.models.builtin_data_tags import ndNodeTag
from lokai.lk_worker.models.builtin_data_attachments import ndAttachment
from lokai.lk_worker.models.builtin_data_subscribers import ndNodeSubscriber
from lokai.lk_worker.models.node_permission import ndPermission
from lokai.lk_worker.models.builtin_data_tags import PiTagData

#-----------------------------------------------------------------------

def module_initialise():

    clear_global_config()
    handle_ini_declaration(prefix='lk')
 
    check_tests_allowed()
    # configure these models
    lwm.model.init()

    get_all_extensions(LK_REGISTER_TYPES_AND_MODELS)

def module_ui_initialise():
    module_initialise()
    get_all_extensions([LK_REGISTER_CONTROLLERS, LK_REGISTER_VIEWS,])

def module_close():

    engine.dispose()
    
#-----------------------------------------------------------------------

def delete_table_content(table_set=None):
    if not table_set:
        table_set = []
    for t in table_set:
        obj = t()
        table = obj.get_mapped_table()
        engine.session.execute(delete(table))
        if hasattr(t, 'set_sequence'):
            t().set_sequence(1)
    engine.session.commit()
    engine.session.expunge_all()

def delete_worker_table_content():
    delete_table_content([
        ndNode,
        ndEdge,
        ndParent,
        ndActivity,
        ndHistory,
        ndRoleAllocation,
        ndUserAssignment,
        ndNodeTag,
        ndAttachment,
        ndNodeSubscriber,
        ndPermission])
    

#-----------------------------------------------------------------------

def create_target_node(set_of_names):
    present_time = now()
    group_node = None
    for s in set_of_names:
        data_set = {
                'nde_date_create': present_time,
                'nde_date_modify': present_time,
                'nde_name': s,
                'nde_description': 'Place holder',
                'nde_type': 'generic',
                }
        node_set = insert_or_update(lwm.ndNode, data_set)
        if len(node_set) > 0:
            node_obj = node_set[0]
            engine.session.flush()
            nde_idx = node_obj['nde_idx']
            if group_node:
                graph.make_link(nde_idx, group_node)
            group_node = nde_idx

#-----------------------------------------------------------------------

def insert_node_data(name, this_date, **kwargs):
    """
        kwargs['tags'] gives a list of tag values
    """
    node_detail = {'nde_date_modify' : this_date,
                   'nde_date_create' : this_date,
                   'nde_name'        : name
                   }
    node_detail.update(kwargs)
    node_set = insert_or_update(lwm.ndNode, node_detail)
    if len(node_set) > 0:
        node_obj = node_set[0]
        engine.session.flush()
        nde_idx = node_obj['nde_idx']
    else:
        nde_idx = None
    tag_list = kwargs.get('tags')
    if nde_idx and tag_list:
        tags = ' '.join(tag_list)
        extn = PiTagData()
        extn.nd_write_data_extend({'nd_node': {'nde_idx': nde_idx},
                               'nd_tags': tags}
                       )
    engine.session.commit()
    return nde_idx

#-----------------------------------------------------------------------

def same(c1, c2):
    """ Compare two lists, where one of them has node objects
    """
    if len(c1) != len(c2):
        return False

    c_switch1 = ' '
    c_switch2 = ' '

    if len(c1) > 0:
        if type(c1[0]) in (type('0'), type(u'0')) :
            c_switch1 = 'c'
        
        if type(c2[0]) in (type('0'), type(u'0')):
            c_switch2 = 'c'
             
        for i in range(len(c1)):
            if c_switch1 == 'c':
                dx1 = c1[i]
            else:
                dx1 = c1[i].nde_idx
            if c_switch2 == 'c':
                dx2 = c2[i]
            else:
                dx2 = c2[i].nde_idx
            if dx1 != dx2:
                return False
    return True

#-----------------------------------------------------------------------
