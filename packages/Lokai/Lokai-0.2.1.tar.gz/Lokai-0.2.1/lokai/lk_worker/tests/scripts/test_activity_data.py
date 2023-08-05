# Name:      lokai/lk_worker/tests/scripts/test_activity_data.py
# Purpose:   Testing aspects of node+activity data manipulation
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

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update

from lokai.lk_worker.models import (ndNode,
                                    ndEdge)
from lokai.lk_worker.models.builtin_data_activity import (
    ndHistory,
    ndActivity)

from lokai.lk_worker.models.builtin_data_activity import (
    PiActivityData,
    get_allocated_resources)

from lokai.lk_worker.tests.helpers import (
    module_initialise,
    module_close,
    delete_table_content,
    same,
    )

#-----------------------------------------------------------------------

setup_module = module_initialise
teardown_module = module_close

#-----------------------------------------------------------------------

def insert_some_data(name, this_date, message, parent_set=[], **kwargs):
    node_detail = {'nde_date_modify' : this_date,
                   'nde_date_create' : this_date,
                   'nde_name'        : name
                   }
    node_set = insert_or_update(ndNode, node_detail)
    if len(node_set) > 0:
        node_obj = node_set[0]
        engine.session.flush()
        nde_idx =node_obj['nde_idx']
        #
        # Add in the history
        hst_detail = {'nde_idx' : nde_idx,
                      'hst_user' : 'test user',
                      'hst_text' : message,
                      'hst_time_entry' : this_date,
                      'hst_type' : 'test type'
                      }
        hst_set = insert_or_update(ndHistory, hst_detail)
        #
        # Activity data
        act_detail = {'nde_idx' : nde_idx,
                      'act_user' : kwargs.get('act_user')
            }
        act_set = insert_or_update(ndActivity, act_detail)
        engine.session.flush()
        #
        # Now the parents
        for p in parent_set:
            edge_detail = {'nde_parent' : p,
                           'nde_child' : nde_idx
                           }
            edge_set = insert_or_update(ndEdge, edge_detail)
    engine.session.commit()
    return nde_idx

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        delete_table_content([ndNode, ndEdge, ndHistory, ndActivity])
                             
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ t001 - Searching for assigned users
        """
        date_today = '2009-10-04'
        user_name_1 = 'user 1'
        insert_some_data('node 1', date_today,
                         "a node with a person",
                         parent_set = [],
                         act_user = user_name_1)
        u1 = get_allocated_resources()
        self.assert_(len(u1) == 1,
                     "1 - Number of users found %d, expected 1"%len(u1))
        self.assert_(u1[0][0] == user_name_1,
                     "1 - User name found %s, expected %s"%(u1[0][0], user_name_1))

    def test_t201(self):
        """ test_t201 : Delete activity data
        """
        extn = PiActivityData()
        date_today = '2009-10-04'
        user_name_1 = 'user 1'
        node_1 = insert_some_data('node 1', date_today,
                                  "a node with a person",
                                  parent_set = [],
                                  act_user = user_name_1)
        date_today = '2009-11-04'
        user_name_1 = 'user 2'
        node_2 = insert_some_data('node 2', date_today,
                                  "a node with a person",
                                  parent_set = [],
                                  act_user = user_name_1)
        full_result_a = engine.session.query(ndActivity).all()
        self.assertEqual(len(full_result_a), 2)
        full_result_h = engine.session.query(ndHistory).all()
        self.assertEqual(len(full_result_h), 2)
        extn.nd_delete_data_extend({'nd_node': {'nde_idx': node_1}})
        engine.session.commit()
        full_result_a = engine.session.query(ndActivity).all()
        self.assertEqual(len(full_result_a), 1)
        full_result_h = engine.session.query(ndHistory).all()
        self.assertEqual(len(full_result_h), 1)
        self.assertEqual(full_result_a[0].nde_idx, node_2)
        self.assertEqual(full_result_h[0].nde_idx, node_2)

    def test_t202(self):
        """ test_t202 : query and read
        """
        extn = PiActivityData()
        date_today = '2009-10-04'
        user_name_1 = 'user 1'
        node_1 = insert_some_data('node 1', date_today,
                                  "a node with a person",
                                  parent_set = [],
                                  act_user = user_name_1)
        date_today = '2009-11-04'
        user_name_1 = 'user 2'
        node_2 = insert_some_data('node 2', date_today,
                                  "a node with a person",
                                  parent_set = [],
                                  act_user = user_name_1)
        query = engine.session.query(ndNode).filter(
            ndNode.nde_idx == node_1)
        query = extn.nd_read_query_extend(query)
        result_obj = {'nd_node': node_1}
        act_obj = extn.nd_read_data_extend(query.one())
        self.assert_('nd_activity' in act_obj)

    def test_t203(self):
        """ test_t203 : write data
        """
        extn = PiActivityData()
        date_today = '2009-10-04'
        user_name_1 = 'user 1'
        node_1 = '0000000099'
        data_obj = {'nd_node': {'nde_idx': node_1},
                    'nd_activity': {'act_user': user_name_1},
                    'message': {'hst_user': user_name_1,
                                'hst_type': 'xxx',
                                'hst_text' : 'some message',
                                'hst_time_entry' : date_today}}
        node_set = insert_or_update(ndNode, data_obj['nd_node'])
        extn.nd_write_data_extend(data_obj)
        engine.session.commit()
        qt1 = engine.session.query(ndActivity).filter(
            ndActivity.nde_idx == node_1)
        obj1 = qt1.one()
        self.assertEqual(obj1.act_user, user_name_1)
        qt2 = engine.session.query(ndHistory).filter(
            ndHistory.nde_idx == node_1)
        obj2 = qt2.one()
        self.assertEqual(obj2.hst_text, 'some message')
        
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
