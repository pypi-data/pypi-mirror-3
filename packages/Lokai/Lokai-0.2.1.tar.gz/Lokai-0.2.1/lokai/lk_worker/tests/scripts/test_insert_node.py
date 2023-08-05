# Name:      lokai/lk_worker/tests/scripts/test_insert_node.py
# Purpose:   Test insert a new node through the insert controller
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
import os
import re

from BeautifulSoup import BeautifulSoup

from lokai.lk_worker.nodes.graph import NodeFamily
from lokai.lk_worker.nodes.search import find_in_path
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

#-----------------------------------------------------------------------

setup_module = module_ui_initialise
teardown_module = module_close

#-----------------------------------------------------------------------

def pack(response):
    return '\n'.join([ln for ln in response.response])

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        delete_worker_table_content()
        delete_user_table_content()
        make_initial_nodes_and_users()
        try:
            os.remove('lokai_ui.log')
        except:
            pass

    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t100(self):
        """ test_t100 - insert a new node and expect it to appear in
            the graph.
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai'])[0]
        query_set = {'detail___node_edit___nde_name': 'New Node',
                     'detail___activity_data___new_message':
                     "Create a new node for testing",
                     'detail___node_edit___nde_type': 'generic',}

        res = source.post(str('/pages/**new**/add?up=%s'%nde_idx), data=query_set)
        self.assertEqual(res.status_code, 302)
        
        self.assert_('edit' in res.headers['location'])
        target_match = re.compile(
            "/pages/([0-9]{10})/edit").search(
            res.headers['location'])
        self.assert_(target_match is not None,
                     "Failed to find a 10 digit node id in the redirect")
        target_idx = target_match.group(1)
        tfl = NodeFamily(target_idx)
        self.assert_(len(tfl.parents) == 1,
                     "Inserted node has parents %s"%str(tfl.parents))
        self.assertEqual(tfl.parents[0].nde_idx, nde_idx)

    def test_t200(self):
        """ test_t200 - insert a new node with errors.
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai'])[0]
        #
        # query with no name will produce an error
        query_set = {'detail___node_edit___nde_name': '',
                     'detail___activity_data___new_message': "Create a new node for testing",
                     'detail___node_edit___nde_type': 'generic',}

        res = source.post(str('/pages/**new**/add?up=%s'%nde_idx), data=query_set)
        self.assertEqual(res.status_code, 200)
        html = BeautifulSoup(pack(res))
        err_set = html.findAll('span', {'class': 'lokai_error'})
        err_text = ''
        for e in err_set:
            if e.string:
                err_text += e.string.strip()
        self.assert_('Name must be given' in err_text,
                     "Error text is %s"%err_text)
    
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
