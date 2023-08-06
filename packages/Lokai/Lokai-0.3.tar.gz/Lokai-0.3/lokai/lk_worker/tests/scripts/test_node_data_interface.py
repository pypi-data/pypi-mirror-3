# Name:      lokai/lk_worker/tests/scripts/test_node_data_interface.py
# Purpose:   Testing aspects of node data with extensions
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

import sys
import unittest
import logging

from lokai.tool_box.tb_common.dates import strtotime
from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update

from lokai.lk_worker.models import (ndNode,
                                    ndEdge,
                                    ndParent,
                                    )

from lokai.lk_worker.models.builtin_data_activity import (
    ndActivity,
    ndHistory)

from lokai.lk_worker.models.builtin_data_tags import (
    ndNodeTag)

from lokai.lk_worker.models.builtin_data_resources import (
    ndRoleAllocation,
    ndUserAssignment)

from lokai.lk_worker.models.builtin_data_attachments import (
    ndAttachment
    )

from lokai.lk_worker.nodes.data_interface import put_node_dataset

from lokai.lk_worker.tests.helpers import (
    module_initialise,
    module_close,
    delete_table_content,
    same
    )

#-----------------------------------------------------------------------

setup_module = module_initialise
teardown_module = module_close
                         
#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        delete_table_content([ndNode,
                              ndEdge,
                              ndParent,
                              ndActivity,
                              ndHistory,
                              ndNodeTag,
                              ndRoleAllocation,
                              ndUserAssignment,
                              ndAttachment,
                              ])

    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : Create a node with all the trimmings
        """
        date_today = '2009-10-04'
        obj = {'nd_node': {'nde_name': 'node_1'},
               'nd_activity': {'act_user': 'user_1'},
               'message': {'hst_user': 'user_1',
                           'hst_type': 'xxx',
                           'hst_text' : 'some message',
                           'hst_time_entry' : date_today},
               'nd_tags': 'tag1 tag2 tag3',
               'nd_assignment': {'usa_user': 'user_2'},
               'nd_resource': [('user_3', 'manager',),
                               ('user_4', 'serf',),
                               ],
               }
        
        nde_idx = put_node_dataset(obj)
        engine.session.commit()
        qt = engine.session.query(ndNode).filter(
            ndNode.nde_idx == nde_idx).one()
        self.assertEqual(qt.nde_name, 'node_1')
        qt = engine.session.query(ndActivity).filter(
            ndActivity.nde_idx == nde_idx).one()
        self.assertEqual(qt.act_user, 'user_1')
        qt = engine.session.query(ndHistory).filter(
            ndHistory.nde_idx == nde_idx).one()
        self.assertEqual(qt.hst_user, 'user_1')
        qt = engine.session.query(ndNodeTag).filter(
            ndNodeTag.nde_idx == nde_idx).all()
        self.assertEqual(len(qt), 3)
        t_list = [itm.nde_tag_text for itm in qt]
        t_list.sort()
        self.assertEqual('tag1 tag2 tag3', ' '.join(t_list))
        qt = engine.session.query(ndUserAssignment).filter(
            ndUserAssignment.nde_idx == nde_idx).one()
        self.assertEqual(qt.usa_user, 'user_2')
        qt = engine.session.query(ndRoleAllocation).filter(
            ndRoleAllocation.nde_idx == nde_idx).all()
        self.assertEqual(len(qt), 2)

#-----------------------------------------------------------------------

if __name__ == "__main__":

    import lokai.tool_box.tb_common.helpers as tbh
    options, test_set = tbh.options_for_publish()
    tbh.logging_for_publish(options)
    setup_module() 
    try:
        tbh.publish(options, test_set, TestObject)
    finally:
        try:
            teardown_module()
        except NameError:
            pass

#-----------------------------------------------------------------------
