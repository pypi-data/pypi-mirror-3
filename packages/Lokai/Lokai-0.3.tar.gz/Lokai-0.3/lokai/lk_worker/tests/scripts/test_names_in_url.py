# Name:      lokai/lk_worker/tests/scripts/test_names_in_url.py
# Purpose:   Test finding a node by using client reference in url
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
        """ test_t100 - Look for something we expect.
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        
       
        res = source.get(str('/pages/%s'%'ProductOne'))
        self.assertEqual(res.status_code, 200)

    def test_t101(self):
        """ test_t101 - Look for the node id
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        
       
        res = source.get(str('/pages/%s'%nde_idx))
        self.assertEqual(res.status_code, 200)

    def test_t200(self):
        """ test_t200 - Look for something we do not expect.
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        
        res = source.get(str('/pages/%s'%'ProductXYZ'))
        self.assertEqual(res.status_code, 404)

    def test_t201(self):
        """ test_t101 - Look for unknown node id
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        
       
        res = source.get(str('/pages/%s'%'1234567890'))
        self.assertEqual(res.status_code, 404)

    def test_t202(self):
        """ test_t101 - Look for neither one thing nor the other
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        
       
        res = source.get(str('/pages/%s'%'123456-7890'))
        self.assertEqual(res.status_code, 404) 
       
    
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
