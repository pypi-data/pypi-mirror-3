# Name:      lokai/lk_worker/tests/scripts/test_views_resources.py
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
import os

from werkzeug import Client, BaseResponse
from BeautifulSoup import BeautifulSoup

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.lk_worker.tests.structure_helper import make_initial_nodes_and_users
from lokai.lk_worker.tests.helpers import (
    module_ui_initialise,
    module_close,
    delete_table_content,
    delete_worker_table_content,
    )

from lokai.lk_worker.nodes.search import find_in_path
from lokai.lk_worker.models.builtin_data_resources import (
    ndRoleAllocation,
    get_full_node_resource_list
    )
from lokai.lk_worker.tests.ui_helper import (
    basic_login,
    delete_user_table_content,
    pack,
    check_errors,
    )

#-----------------------------------------------------------------------

setup_module = module_ui_initialise
teardown_module = module_close

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        delete_worker_table_content()
        delete_user_table_content()
        make_initial_nodes_and_users()
        if os.path.exists('lokai_ui.log'):
            os.remove('lokai_ui.log')
        
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 - find a detail form and check the fields
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        
        res = source.get(str('/pages/%s/edit'%nde_idx))
        self.assertEqual(res.status_code, 200)
        # Expect fields like empty assignment field, one resource
        # field and a link for adding a new user.
        html = BeautifulSoup(pack(res))
        fieldset_set = html.findAll('fieldset'
                                         )
        find_string = ''
        for fieldset in fieldset_set:
            legend = fieldset.legend
            if legend:
                label = legend.string
                if label and 'user' in label:
                    # Found the right place
                    find_string = 'Resource fieldset found'
                    assign_field_set = fieldset.findAll(
                        attrs={'name': 'detail___user_detail___active_resource'})
                    self.assert_(len(assign_field_set) == 1,
                                 "Expect one assign field")
                    self.assert_('disabled' not in assign_field_set[0].attrMap)
                    other_field_set = fieldset.findAll(
                        attrs={'name': 'detail___user_detail___row001'})
                    self.assert_(len(other_field_set) == 1,
                                 "Expect one row_1 field")
                    self.assert_('disabled' not in other_field_set[0].attrMap)
                    new_field_set = fieldset.findAll(
                        attrs={'name': 'detail___user_detail___newresource'})
                    self.assertEqual(len(new_field_set), 1,
                                     "Expect one new resource field")
        self.assertEqual(find_string, 'Resource fieldset found')
        
    def test_t002(self):
        """ test_t002 - find a detail form and check the fields for readonly
        """
        source = basic_login('fred_2', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product2'])[0]
        
        res = source.get(str('/pages/%s/edit'%nde_idx))
        self.assertEqual(res.status_code, 200)
        # Expect fields like empty assignment field, one resource
        # field and a link for adding a new user.
        html = BeautifulSoup(pack(res))
        fieldset_set = html.findAll('fieldset'
                                         )
        find_string = ''
        for fieldset in fieldset_set:
            legend = fieldset.legend
            if legend:
                label = legend.string
                if label and 'user' in label:
                    # Found the right place
                    find_string = 'Resource fieldset found'
                    assign_field_set = fieldset.findAll(
                        attrs={'name': 'detail___user_detail___active_resource'})
                    self.assert_(len(assign_field_set) == 1,
                                 "Expect one assign field")
                    self.assert_('disabled' in assign_field_set[0].attrMap)
                    other_field_set = fieldset.findAll(
                        attrs={'name': 'detail___user_detail___row001'})
                    self.assert_(len(other_field_set) == 1,
                                 "Expect one row_1 field")
                    self.assert_('disabled' in other_field_set[0].attrMap)
                    new_field_set = fieldset.findAll(
                        attrs={'name': 'detail___user_detail___newresource'})
                    self.assertEqual(len(new_field_set), 0,
                                     "Expect zero new resource field")
                    
        self.assertEqual(find_string, 'Resource fieldset found')
        
    def test_t003(self):
        """ test_t003 - avoid duplicate entries in resource drop-down
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product2', 'data'])[0]
        
        res = source.get(str('/pages/%s/edit'%nde_idx))
        self.assertEqual(res.status_code, 200)
        # Expect fields like empty assignment field, three resource
        # fields and a link for adding a new user.
        available_resources = get_full_node_resource_list(nde_idx)
        # Expect a duplicate of fred_3 without changing the length of the user set
        self.assertEqual(len(available_resources), 3)
        html = BeautifulSoup(pack(res))
        fieldset_set = html.findAll('fieldset'
                                         )
        find_string = ''
        for fieldset in fieldset_set:
            legend = fieldset.legend
            if legend:
                label = legend.string
                if label and 'user' in label:
                    # Found the right place
                    find_string = 'Resource fieldset found'
                    assign_field_set = fieldset.findAll(
                        attrs={'name': 'detail___user_detail___active_resource'})
                    self.assert_(len(assign_field_set) == 1,
                                 "Expect one assign field")
                    self.assert_(
                        assign_field_set[0].attrMap.get('disabled') is None)
                    option_set = assign_field_set[0].findAll('option')
                    self.assertEqual(len(option_set), 4)
                    self.assertEqual(
                        option_set[0].string,
                        "Select user to assign")
                    fred_list = [opt.attrMap.get('value') for
                                 opt in option_set[1:]]
                    fred_list.sort()
                    self.assertEqual(fred_list, ['fred_1', 'fred_2', 'fred_3'])
        self.assertEqual(find_string, 'Resource fieldset found')

    def test_t004(self):
        """ test_t004 - add a new resource
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product2', 'data'])[0]

        query_set = {
            'detail___node_edit___nde_name': 'Anything',
            'detail___node_edit___nde_type': 'generic',
            'detail___user_detail___newresource': 'fred_2'
            }
        res = source.post(str('/pages/%s/edit'%nde_idx), data=query_set)
        html = BeautifulSoup(pack(res))
        msg = check_errors(html)
        self.assertEqual(msg, [])
        self.assertEqual(res.status_code, 302)

        # The following must run without error
        res = engine.session.query(
            ndRoleAllocation
            ).filter(
            ndRoleAllocation.nde_idx == nde_idx
            ).filter(
            ndRoleAllocation.rla_user == 'fred_2'
            ).one()
        
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
