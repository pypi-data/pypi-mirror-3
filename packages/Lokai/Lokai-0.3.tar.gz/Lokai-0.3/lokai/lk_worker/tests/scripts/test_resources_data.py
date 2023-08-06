# Name:      lokai/lk_worker/tests/scripts/test_resources_data.py
# Purpose:   Test resource extension code
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
import re

from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_login.db_objects import User, UserRole, Role, Function, RoleFunction
from lokai.lk_worker.models import ndNode, ndEdge, ndParent
from lokai.lk_worker.models.builtin_data_resources import ndRoleAllocation

from lokai.lk_worker.nodes.search import find_in_path
from lokai.lk_worker.models.builtin_data_resources import (
    ResourceList,
    node_add_resource,
    node_del_resource,
    PiResourceData,
    )
from lokai.lk_worker.tests.helpers import (
    module_initialise,
    module_close,
    delete_table_content,
    same,
    )
from lokai.lk_worker.tests.structure_helper import make_initial_nodes_and_users

#-----------------------------------------------------------------------

setup_module = module_initialise
teardown_module = module_close

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        delete_table_content([ndParent, ndEdge, ndNode, ndRoleAllocation])
        delete_table_content([RoleFunction, UserRole, Role, Function, User])
        make_initial_nodes_and_users()
        
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 - add resources
        """
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        resc_query = engine.session.query(ndRoleAllocation).filter(
            ndRoleAllocation.nde_idx == nde_idx)
        resc_set = resc_query.filter(
            ndRoleAllocation.rla_user == 'fred_3').all()
        self.assert_(len(resc_set) == 0,
                     "Found fred_3 already - abandon test")
        history = node_add_resource(nde_idx, 'fred_3', 'undefined')
        engine.session.commit()
        self.assertEqual(history, "Add new resource fred_3, role undefined")
        resc_set = resc_query.filter(
            ndRoleAllocation.rla_user == 'fred_3').all()
        self.assert_(len(resc_set) == 1,
                     "Not found fred_3")
        #
        # Add again
        history = node_add_resource(nde_idx, 'fred_3', 'undefined')
        engine.session.commit()
        self.assertEqual(history, "Add new resource fred_3, role undefined")
        resc_set = resc_query.filter(
            ndRoleAllocation.rla_user == 'fred_3').all()
        self.assert_(len(resc_set) == 1,
                     "Not found fred_3")

    def test_t003(self):
        """ test_t003 - delete a role
        """
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        resc_query = engine.session.query(ndRoleAllocation).filter(
            ndRoleAllocation.nde_idx == nde_idx)
        resc_set = resc_query.filter(
            ndRoleAllocation.rla_user == 'fred_3').all()
        self.assert_(len(resc_set) == 0,
                     "Found fred_3 already - abandon test")
        resc_all = resc_query.all()
        self.assert_(len(resc_all) == 1,
                     "Expect 1 (one) resource already - find %d"%len(resc_all))
        
        history = node_add_resource(nde_idx, 'fred_3', 'undefined')
        engine.session.commit()

        self.assertEqual(history, "Add new resource fred_3, role undefined")
        history = node_del_resource(nde_idx, 'fred_3', 'undefined')
        engine.session.commit()
        self.assertEqual(history,
                         "User %s, role %s has been removed from the resources" %
                         ('fred_3', 'undefined'))
        resc_set = resc_query.filter(
            ndRoleAllocation.rla_user == 'fred_3').all()
        self.assert_(len(resc_set) == 0,
                     "Resource fred_3 not deleted, aparently")
        resc_all = resc_query.all()
        self.assert_(len(resc_all) == 1,
                     "This node should still have 1 (one) resource")
        
    def test_t004(self):
        """ test_t004 - resource query - no assignment
        """
        extn = PiResourceData()
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        base_query = engine.session.query(ndNode).filter(
            ndNode.nde_idx == nde_idx)
        new_query = extn.nd_read_query_extend(base_query)
        self.assert_('nd_user_assignment' in str(new_query),
                     "Expect nd_role_allocation, find %s"%str(new_query))
        data_object = extn.nd_read_data_extend(new_query.one())
        self.assert_('nd_assignment' not in data_object)
        self.assert_('nd_resource' in data_object)
        self.assert_(len(data_object['nd_resource']) == 1,
                     "Expect fred_2 only, find %d"%
                     len(data_object['nd_resource']))
        self.assert_(isinstance(data_object['nd_resource'],
                                ResourceList))
        self.assert_('fred_2' in data_object['nd_resource'].keys())
        
    def test_t005(self):
        """ test_t005 - resource query - no resource
        """
        extn = PiResourceData()
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1', 'data'])[0]
        base_query = engine.session.query(ndNode).filter(
            ndNode.nde_idx == nde_idx)
        new_query = extn.nd_read_query_extend(base_query)
        self.assert_('nd_user_assignment' in str(new_query),
                     "Expect nd_role_allocation, find %s"%str(new_query))
        data_object = extn.nd_read_data_extend(new_query.one())
        self.assert_('nd_resource' in data_object)
        self.assert_(len(data_object['nd_resource']) == 0,
                     "Expect zero resource, find %d"%
                     len(data_object['nd_resource']))
        self.assert_('nd_assignment' in data_object)
        self.assert_(data_object['nd_assignment'].usa_user == 'fred_2')
         
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
