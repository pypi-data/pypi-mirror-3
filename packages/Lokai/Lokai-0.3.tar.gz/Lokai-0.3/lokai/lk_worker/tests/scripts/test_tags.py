# Name:      lokai/lk_worker/tests/scripts/test_tags.py
# Purpose:   Test tag extension code
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

from werkzeug import Client, BaseResponse
from BeautifulSoup import BeautifulSoup

from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_worker.tests.structure_helper import make_initial_nodes_and_users
from lokai.lk_worker.tests.helpers import (
    module_ui_initialise,
    module_close,
    delete_worker_table_content,
    )
from lokai.lk_worker.tests.ui_helper import  delete_user_table_content

from lokai.lk_worker.nodes.search import find_in_path

from lokai.lk_login.db_objects import (
    User,
    Role,
    Function,
    RoleFunction,
    UserRole
    )
from lokai.lk_worker.models.builtin_data_resources import (
    ndRoleAllocation,
    ndUserAssignment,
    )

from lokai.lk_worker.models.builtin_data_activity import (
    ndActivity,
    ndHistory,
    )
from lokai.lk_worker.models import (
    ndNode,
    ndEdge,
    ndParent,
    )
from lokai.lk_worker.tests.ui_helper import (
    basic_login,
    )

from lokai.lk_worker.models.builtin_data_tags import (
    ndNodeTag,
    PiTagData,
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
        delete_user_table_content()
        delete_worker_table_content()
        make_initial_nodes_and_users()
        try:
            os.remove('lokai_ui.log')
        except:
            pass
        
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 - Store tags - no change
        """
        extn = PiTagData()
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        extn.nd_write_data_extend({'nd_node': {'nde_idx': nde_idx},
                               'nd_tags': 'gummy 123456'}
                       )
        engine.session.commit()
        tag_set = engine.session.query(ndNodeTag).filter(
            ndNodeTag.nde_idx == nde_idx).all()
        self.assertEqual(len(tag_set), 2)
        tag_list = [x.nde_tag_text for x in tag_set]
        self.assert_('gummy' in tag_list)
        self.assert_('123456' in tag_list)

    def test_t002(self):
        """ test_t002 - Store tags - then get them back again
        """
        extn = PiTagData()
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        extn.nd_write_data_extend({'nd_node': {'nde_idx': nde_idx},
                               'nd_tags': 'gummy 123456'}
                       )
        engine.session.commit()
        base_query = engine.session.query(ndNode).filter(
            ndNode.nde_idx == nde_idx)
        tag_query =  extn.nd_read_query_extend(base_query)
        self.assertEqual(base_query, tag_query)
        result = tag_query.all()
        data_object = {'nd_node': result[0]}
        data_object.update(extn.nd_read_data_extend(result))
        self.assert_('nd_tags' in data_object)
        tag_list = data_object['nd_tags'].split(' ')
        self.assert_('gummy' in tag_list)
        self.assert_('123456' in tag_list)

    def test_t003(self):
        """ test_t003 - Store tags - then get them back and update
        """
        extn = PiTagData()
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        extn.nd_write_data_extend({'nd_node': {'nde_idx': nde_idx},
                               'nd_tags': 'gummy 123456'}
                       )
        engine.session.commit()
        base_query = engine.session.query(ndNode).filter(
            ndNode.nde_idx == nde_idx)
        tag_query = extn.nd_read_query_extend(base_query)
        result = tag_query.all()
        data_object = {'nd_node': result[0]}
        data_object.update(extn.nd_read_data_extend(result))
        tag_list = data_object['nd_tags'].split(' ')
        extn.nd_write_data_extend({'nd_node': {'nde_idx': nde_idx},
                               'nd_tags': 'gummy 67890'},
                       data_object
                       )
        engine.session.commit()
        tag_set = engine.session.query(ndNodeTag).filter(
            ndNodeTag.nde_idx == nde_idx).all()
        self.assertEqual(len(tag_set), 2)
        tag_list = [x.nde_tag_text for x in tag_set]
        self.assert_('gummy' in tag_list)
        self.assert_('67890' in tag_list)
        
    def test_t004(self):
        """ test_t004 - Store tags - then update with duplicates
        """
        extn = PiTagData()
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        extn.nd_write_data_extend({'nd_node': {'nde_idx': nde_idx},
                               'nd_tags': 'gummy 123456'}
                       )
        engine.session.commit()
        base_query = engine.session.query(ndNode).filter(
            ndNode.nde_idx == nde_idx)
        tag_query = extn.nd_read_query_extend(base_query)
        result = tag_query.all()
        data_object = {'nd_node': result[0]}
        data_object.update(extn.nd_read_data_extend(result))
        tag_list = data_object['nd_tags'].split(' ')
        extn.nd_write_data_extend({'nd_node': {'nde_idx': nde_idx},
                               'nd_tags': 'fred gummy gummy 67890 fred'},
                       data_object
                       )
        engine.session.commit()
        tag_set = engine.session.query(ndNodeTag).filter(
            ndNodeTag.nde_idx == nde_idx).all()
        self.assertEqual(len(tag_set), 3)
        tag_list = [x.nde_tag_text for x in tag_set]
        self.assert_('gummy' in tag_list, "Tag list is %s"% tag_list)
        self.assert_('67890' in tag_list, "Tag list is %s"% tag_list)
        self.assert_('fred' in tag_list, "Tag list is %s"% tag_list)

    def test_t100(self):
        """ test_t100 - basic use of UI
        """
        test_app = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        
        query_set = {'detail_idx': nde_idx,
                     'detail___node_edit___nde_name': 'New Node Name',
                     'detail___activity_data___new_message':
                     "Modify this node for testing",
                     'detail___node_edit___node_type': 'generic',
                     'detail___nd_tags': 'gummy 2468'}
        res = test_app.post(str('/pages/%s/edit'%nde_idx), data=query_set,
                            follow_redirects=True)
        html = BeautifulSoup(pack(res))
        self.assertEqual(res.status_code, 200)
        tag_set = engine.session.query(ndNodeTag).filter(
            ndNodeTag.nde_idx == nde_idx).all()
        self.assertEqual(len(tag_set), 2)
        tag_list = [x.nde_tag_text for x in tag_set]
        self.assert_('gummy' in tag_list)
        self.assert_('2468' in tag_list)
        tag_field = html.findAll(attrs={'name': 'detail___nd_tags'})
        self.assert_(len(tag_field) == 1)
        self.assert_((tag_field[0]['value'] == 'gummy 2468' or
                      tag_field[0]['value'] == '2468 gummy'),
                     "Tag field is %s"% str(tag_field))
        
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
