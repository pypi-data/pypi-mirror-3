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
import lokai.tool_box.tb_common.dates as dates
from lokai.lk_worker.nodes.data_interface import get_node_dataset, put_node_dataset
from lokai.lk_worker.tests.structure_helper import make_initial_nodes_and_users
from lokai.lk_worker.tests.helpers import (
    module_ui_initialise,
    module_close,
    delete_table_content,
    delete_worker_table_content,
    )

from lokai.lk_worker.nodes.search import find_in_path
from lokai.lk_worker.models.builtin_data_resources import (
    get_full_node_resource_list
    )
from lokai.lk_worker.tests.ui_helper import (
    basic_login,
    delete_user_table_content,
    )

from lokai.lk_worker.models.builtin_data_activity import ndHistory

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
        if os.path.exists('lokai_ui.log'):
            os.remove('lokai_ui.log')
        
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : find a detail form and check the fields
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        # Need an activity data type
        nde_obj = get_node_dataset(nde_idx)
        nde_obj['nd_node']['nde_type'] = 'activity'
        put_node_dataset(nde_obj)
        engine.session.commit()
        
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
            find_string = 'Fieldset %s' % str(legend)
            if legend:
                label = legend.string
                find_string = 'Fieldset name %s' % label
                if label and 'activity' in label:
                    # Found the right place
                    find_string = 'Activity fieldset found'
                    # The following excludes tests for 'act_type',
                    # 'act_sub_type' and 'act_date_work'. The first
                    # because it is only used conditionally, the last
                    # two are just not used.
                    for field in ['act_date_range___start_date',
                                  'act_date_range___finish_date',
                                  'remind_date', 'priority',
                                  'status']:
                        full_field = 'detail___activity_data___%s'%field
                        assign_field_set = fieldset.findAll(
                            attrs={'name': full_field})
                        self.assert_(len(assign_field_set) == 1,
                                     "Expect field %s" % field)
                        self.assert_('disabled' not in assign_field_set[0].attrMap)
                    # Testing for something that does not exist is
                    # slightly spurious. There are too many reasons
                    # why that might be so. This test will fail,
                    # however, if sub_type and work are brought into
                    # play, so at least we know.
                    for field in ['act_type', 'act_sub_type', 'act_date_work']:
                        full_field = 'detail___activity_data___%s'%field
                        assign_field_set = fieldset.findAll(
                            attrs={'name': full_field})
                        self.assert_(len(assign_field_set) == 0,
                                     "Do not expect field %s" % field)
                    break
        self.assertEqual(find_string, 'Activity fieldset found')

    def test_t002(self):
        """ test_t002 : Update some stuff
        """
        print
        print "========================================"
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        # Need an activity data type
        nde_obj = get_node_dataset(nde_idx)
        nde_obj['nd_node']['nde_type'] = 'activity'
        put_node_dataset(nde_obj)
        engine.session.commit()

        query_set = {
            'detail___node_edit___nde_name': 'product1',
            'detail___node_edit___node_type': 'activity',
            'detail___activity_data___new_message':
            "Modify this node for testing",
            'detail___activity_data___act_date_range___start_date': '2009-01-01',
            'detail___activity_data___act_date_range___finish_date': '2009-10-01',
            'detail___activity_data___priority': '050',
            'detail___activity_data___status': '100',
            }
        res = source.post(str('/pages/%s/edit'%nde_idx), data=query_set)
        self.assertEqual(res.status_code, 302)

        nde_obj = get_node_dataset(nde_idx)
        act_obj = nde_obj['nd_activity']
        self.assertEqual(act_obj['act_date_start'], dates.strtotime('2009-01-01'))
        self.assertEqual(act_obj['act_date_finish'], dates.strtotime('2009-10-01'))
        self.assertEqual(act_obj['act_priority'], '050')
        self.assertEqual(act_obj['act_status'], '100')

        # Now make some changes
        query_set = {
            'detail___node_edit___nde_name': 'product1',
            'detail___node_edit___node_type': 'activity',
            'detail___activity_data___new_message':
            "Modify this node for testing",
            'detail___activity_data___act_date_range___start_date': '2009-02-01',
            'detail___activity_data___act_date_range___finish_date': '2009-11-01',
            'detail___activity_data___priority': '090',
            'detail___activity_data___status': '900',
            }
        res = source.post(str('/pages/%s/edit'%nde_idx), data=query_set)
        self.assertEqual(res.status_code, 302)

        nde_obj = get_node_dataset(nde_idx)
        act_obj = nde_obj['nd_activity']
        self.assertEqual(act_obj['act_date_start'], dates.strtotime('2009-02-01'))
        self.assertEqual(act_obj['act_date_finish'], dates.strtotime('2009-11-01'))
        self.assertEqual(act_obj['act_priority'], '090')
        self.assertEqual(act_obj['act_status'], '900')

        hist = engine.session.query(
            ndHistory
            ).filter(
            ndHistory.nde_idx == nde_idx
            ).all()
        
        self.assertEqual(len(hist), 4)
        found = False
        for hrec in hist:
            msg = hrec['hst_text']
            if 'act_date_start' in msg:
                found = True
                msg_parts = msg.split('\n')
                # get non-empty lines
                msg_parts = [x for x in msg_parts if x]
                self.assertEqual(len(msg_parts), 5)
        self.assert_(found)

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
