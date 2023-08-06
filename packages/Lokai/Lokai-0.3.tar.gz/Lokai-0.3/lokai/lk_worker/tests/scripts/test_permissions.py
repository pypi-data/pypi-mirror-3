# Name:      lokai/lk_worker/tests/scripts/test_permissions.py
# Purpose:   Testing aspects of permission discovery
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

from lokai.lk_worker.models import ndNode
from lokai.lk_worker.nodes.node_data_functions import get_user_node_permissions
from lokai.lk_worker.nodes.data_interface import (get_node_dataset,
                                                  put_node_dataset,
                                                  )
from lokai.lk_worker.nodes.search import find_in_path, search_down
from lokai.lk_worker.models.builtin_data_resources import (
    user_top_trees,
    get_actual_node_resource_list,
    get_full_node_resource_list,
    get_permissions_for,
    ndRoleAllocation,
    )

from lokai.lk_worker.models.node_permission import ndPermission

from lokai.lk_worker.tests.structure_helper import make_initial_nodes_and_users
from lokai.lk_worker.tests.helpers import (
    module_initialise,
    module_close,
    delete_worker_table_content
    )

from lokai.lk_worker.tests.ui_helper import delete_user_table_content

from werkzeug.exceptions import Unauthorized, NotFound
from lokai.lk_worker.ui.local import is_allowed
from lokai.lk_ui.session import SessionRequest

#-----------------------------------------------------------------------

class DummyRequest(object):

    def __init__(self, *args, **kwargs):
        pass

    derived_locals = {}

    user = ''

    referrer = 'dummy_from'

    url = 'dummy_url'
    
    
#-----------------------------------------------------------------------

setup_module = module_initialise
teardown_module = module_close

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        delete_worker_table_content()
        delete_user_table_content()
        make_initial_nodes_and_users()
        
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 examine the resources
        """
        nde_set = find_in_path(['', 'root', 'Lokai', 'product1', 'data'])
        self.assert_(len(nde_set) == 1)
        node_resources = get_actual_node_resource_list(nde_set[0])
        self.assert_(len(node_resources) == 0)
        all_resources = get_full_node_resource_list(nde_set[0])
        self.assert_(len(all_resources) == 2,
                     "Looking for all resources "
                     "- expect 2 "
                     "- find %d"%len(all_resources))
        all_resources = get_full_node_resource_list(nde_set[0],
                                                    user='fred_2',
                                                    )
        self.assert_(len(all_resources) == 1,
                     "Looking for all resources - fred_2 in product 1"
                     "- expect 1 "
                     "- find %d"%len(all_resources))
        
        r_fred_3 = get_full_node_resource_list(nde_set[0],
                                               user='fred_3',
                                               )
        self.assert_(len(r_fred_3) == 0,
                     "Looking for all resources - fred_3 in product 1 "
                     "- expect 0 "
                     "- find %d"%len(r_fred_3))
        
        # Try fred_3 at 'product' level - should have view permission
        # only
        nde_set = find_in_path(['', 'root', 'Lokai', 'product2'])
        r_fred_3 = get_full_node_resource_list(nde_set[0],
                                               user='fred_3',
                                               )
        self.assert_(len(r_fred_3) == 1,
                     "Looking for all resources - fred_3 in product 2 "
                     "- expect 1 "
                     "- find %d"%len(r_fred_3))
        self.assert_('fred_3' in r_fred_3.keys())
        p_fred_3_set = get_permissions_for(r_fred_3)
        self.assert_('fred_3' in p_fred_3_set)
        self.assert_(len(p_fred_3_set) ==1)
        p_fred_3 = p_fred_3_set['fred_3']
        self.assert_('nde_tasks' in p_fred_3)
        self.assertFalse(p_fred_3.test_permit('nde_tasks', 'edit'))
        
        # Try fred_3 at 'data' level - should have edit permission now
        nde_set = find_in_path(['', 'root', 'Lokai', 'product2', 'data'])
        r_fred_3 = get_full_node_resource_list(nde_set[0],
                                                 user='fred_3',
                                                 )
        self.assert_(len(r_fred_3) == 1,
                     "Looking for all resources - fred_3 in product 2 data "
                     "- expect 1 "
                     "- find %d"%len(r_fred_3))
        self.assert_('fred_3' in r_fred_3.keys())
        p_fred_3_set = get_permissions_for(r_fred_3)
        self.assert_('fred_3' in p_fred_3_set)
        self.assert_(len(p_fred_3_set) ==1)
        p_fred_3 = p_fred_3_set['fred_3']
        self.assert_('nde_tasks' in p_fred_3)
        self.assertTrue(p_fred_3.test_permit('nde_tasks', 'edit'))


    def test_t002(self):
        """ test_t002 - get_user_node_permissions
        """
        nde_set = find_in_path(['', 'root', 'Lokai',])
        nde_idx = nde_set[0]
        # fred_0 is not allocated to any node
        p_0 = get_user_node_permissions(nde_idx, 'fred_0')
        self.assertTrue(p_0.test_permit('nde_tasks', 'edit'))
        # fred_1 is a manager on this node
        p_1 = get_user_node_permissions(nde_idx, 'fred_1')
        self.assertTrue(p_1.test_permit('nde_tasks', 'edit'))
        # fred_2 is not given a role here
        p_1 = get_user_node_permissions(nde_idx, 'fred_2')
        self.assertFalse(p_1.test_permit('nde_tasks', 'read'))

    def test_t003(self):
        """ test_t003 - user_top_trees
        """
        nde_set = find_in_path(['', 'root', 'Lokai'])
        nde_lki = nde_set[0]
        nde_set = find_in_path(['', 'root', 'Lokai', 'product2'])
        nde_pr2 = nde_set[0]
        nde_set = find_in_path(['', 'root', 'Lokai', 'product1'])
        nde_pr1 = nde_set[0]
        nde_set = find_in_path(['', 'root', 'Lokai', 'product1', 'data'])
        nde_p1d = nde_set[0]

        #fred_0 has none
        r_set = user_top_trees('fred_0')
        self.assertEqual(len(r_set), 0)
        # fred_1 has Lokai
        r_set = user_top_trees('fred_1')
        self.assertEqual(len(r_set), 1)
        self.assertEqual(r_set[0], nde_lki)
        
        # fred_2 has Lokai.product1, Redolhm.product2 and
        # Lokai.product1.data.
        r_set = user_top_trees('fred_2')
        self.assertEqual(len(r_set), 2)
        self.assert_(nde_pr1 in r_set)
        self.assert_(nde_pr2 in r_set)
        # fred_3 has Redolhm.product2 and Lokai.product2.data and
        # should only see the first one.
        r_set = user_top_trees('fred_3')
        self.assertEqual(len(r_set), 1, "For fred_3, found %s"%r_set)
        self.assert_(nde_pr2 in r_set)

    def test_t100(self):
        """ test_t100 - try search_down using the resource join
        """
        qy = engine.session.query(
        ndRoleAllocation, ndNode).join(
        (ndNode, ndRoleAllocation.nde_idx == ndNode.nde_idx))
        qy = qy.filter(ndRoleAllocation.rla_user == 'fred_3')
        qy = search_down(qy, None)
        res = qy.all()
        self.assertEqual(len(res), 1)

    def test_t200(self):
        """ test_t200 - handle a local permission for a node
        """
        nde_set = find_in_path(['', 'root', 'Lokai', 'product2'])
        nde_pr2 = nde_set[0]
        perm_obj = get_node_dataset(nde_pr2, 'local_permission')
        self.assert_('local_permission' not in perm_obj)
        perm_obj['local_permission'] = 'nde_resource'
        put_node_dataset(perm_obj)
        engine.session.commit()
        res = engine.session.query(
            ndPermission
            ).filter(
            ndPermission.nde_idx == nde_pr2).one()
        self.assertEqual(res.nde_permission, 'nde_resource')
        node_obj = perm_obj['nd_node']
        new_obj = {'nd_node': node_obj}
        new_obj['local_permission'] = ''
        put_node_dataset(new_obj, perm_obj)
        engine.session.commit()
        res = engine.session.query(
            ndPermission
            ).filter(
            ndPermission.nde_idx == nde_pr2).first()
        self.assert_(res is None)

    def test_t300(self):
        """ test_t300 - check the decorator using local permissions
        """
        def responder(request):
            return request

        # Playing with this node
        nde_set = find_in_path(['', 'root', 'Lokai', 'product2'])
        nde_pr2 = nde_set[0]

        # Dummy request to keep innards of is_allowed happy
        request = DummyRequest({})

        # Set the target and a suitable user
        request.derived_locals['object_id'] = nde_pr2
        request.user = 'fred_1'

        # Should be just fine with this one
        rtn = is_allowed({'nde_tasks': 'edit'})(responder)(request)
        self.assert_(rtn == request)

        # Set a local permission that no-one has
        perm_obj = get_node_dataset(nde_pr2, 'local_permission')
        perm_obj['local_permission'] = 'unknown_resource_name'
        put_node_dataset(perm_obj)
        engine.session.commit()

        # Try again
        self.assertRaises(Unauthorized,
                          is_allowed({'nde_tasks': 'edit'})(responder), request)
        
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
