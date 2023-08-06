# Name:      lokai/lk_worker/tests/scripts/test_node_permissions.py
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

from lokai.lk_worker.nodes.graph import NodeFamily
from lokai.lk_worker.nodes.node_data_functions import PermittedNodeFamily

from lokai.lk_worker.tests.structure_helper import make_initial_nodes_and_users
from lokai.lk_worker.tests.helpers import (
    module_ui_initialise,
    module_close,
    delete_worker_table_content
    )

from lokai.lk_worker.tests.ui_helper import (
    basic_login,
    delete_user_table_content,
    )

from lokai.lk_worker.nodes.search import find_in_path

#-----------------------------------------------------------------------

def foob(nde_list):
    return ' :: '.join(
        ["%s > %s"% (nde.nde_idx, nde.nde_name) for nde in nde_list])

#-----------------------------------------------------------------------

setup_module = module_ui_initialise
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

    def test_t100(self):
        """ test_t100 - confirm sibling truncation
        """
        # The user fred_3 is allocated to product 2 but not to the
        # sibling, product 1.

        nde_set = find_in_path(['', 'root', 'Lokai'])
        nde_parent = nde_set[0]
        nde_set = find_in_path(['', 'root', 'Lokai', 'product2'])
        nde_idx = nde_set[0]

        # First - the normal situation
        
        nf_normal = NodeFamily(nde_idx)
        self.assert_(len(nf_normal.parents) == 1,
                     "Parents of product 2 "
                     "- expect 1 "
                     "- find %s"% foob(nf_normal.parents))
        self.assertEqual(nf_normal.parents[0].nde_idx, nde_parent)
        self.assert_(len(nf_normal.siblings_right) == 0,
                     "Siblings of product 2, right "
                     "- expect none "
                     "- find %s"% foob(nf_normal.siblings_right))
        self.assert_(len(nf_normal.siblings_left) == 1,
                     "Siblings of product 2, left "
                     "- expect one "
                     "- find %s"% foob(nf_normal.siblings_left))
        
        # Now with permissions

        nf_perm = PermittedNodeFamily(nde_idx,
                                      user='fred_3',
                                      perm=[{'lkw_tasks': 'read'}])
        self.assert_(len(nf_perm.parents) == 0,
                     "Parents of product 2 "
                     "- expect 0 "
                     "- find %s"% foob(nf_normal.parents))
        self.assert_(len(nf_perm.siblings_right) == 0,
                     "Siblings of product 2, right "
                     "- expect none "
                     "- find %s"% foob(nf_normal.siblings_right))
        self.assert_(len(nf_perm.siblings_left) == 0,
                     "Siblings of product 2, left "
                     "- expect none "
                     "- find %s.%s"% (foob(nf_normal.siblings_left),
                                      nf_normal.siblings_left[0].nde_name))

    def test_t200(self):
        """ test_t200 - basic access to key areas
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # Now we can try to display all pages for a node

        # fred_1 is allocated as a manager against Lokai, so product
        # 2 should be OK
        nde_set = find_in_path(['', 'root', 'Lokai', 'product2'])
        
        test_idx = nde_set[0]

        # Default
        res = source.get('/pages/%s/default'%test_idx)
        self.assertEqual(res.status_code, 200)

        # Display
        res = source.get('/pages/%s'%test_idx)
        self.assertEqual(res.status_code, 200)

        # Detail
        res = source.get('/pages/%s/edit'%test_idx)
        self.assertEqual(res.status_code, 200)

        # List
        res = source.get('/pages/%s/list'%test_idx)
        self.assertEqual(res.status_code, 200)

    def test_t210(self):
        """ test_t210 - basic access - access rejected in some areas
        """
        source = basic_login('fred_3', 'useless', 'Fred Manager')
        #
        # Now we can try to display all pages for a node

        # fred_3 is allocated as a viewer against Lokai/product 2,
        # so product 2 should be OK for some and not for others.
        nde_set = find_in_path(['', 'root', 'Lokai', 'product2'])
        
        test_idx = nde_set[0]

        # Default
        res = source.get('/pages/%s/default'%test_idx)
        self.assertEqual(res.status_code, 200)

        # Display
        res = source.get('/pages/%s'%test_idx)
        self.assertEqual(res.status_code, 200)

        # Detail
        res = source.get('/pages/%s/edit'%test_idx)
        self.assertEqual(res.status_code, 404)

        # List
        res = source.get('/pages/%s/list'%test_idx)
        self.assertEqual(res.status_code, 200)

        


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
