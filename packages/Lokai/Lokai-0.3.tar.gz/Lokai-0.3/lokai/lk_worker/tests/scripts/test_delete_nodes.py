# Name:      lokai/lk_worker/tests/scripts/test_delete_nodes.py
# Purpose:   Testing the extendable deletion facilities
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
import os
import unittest
import logging
import StringIO

from lokai.tool_box.tb_common.helpers import remove_root, make_root
import lokai.tool_box.tb_common.configuration as config
from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_worker.nodes.search import find_in_path
from lokai.lk_worker.nodes.data_interface import (
    put_node_dataset,
    get_node_dataset,
    )
from lokai.lk_worker.nodes.node_data_functions import expunge_tree

from lokai.lk_worker.models import ndNode, ndEdge, ndParent
from lokai.lk_worker.models.builtin_data_activity import ndActivity
from lokai.lk_worker.models.builtin_data_tags import ndNodeTag
from lokai.lk_worker.models.builtin_data_attachments import (
    ndAttachment,
    NodeAttachment,
    AttachmentCollection,
    )
from lokai.lk_worker.tests.structure_helper import make_initial_nodes_and_users
from lokai.lk_worker.tests.helpers import (
    module_initialise,
    module_close,
    delete_worker_table_content
    )
from lokai.lk_worker.tests.ui_helper import delete_user_table_content


#-----------------------------------------------------------------------

setup_module = module_initialise
teardown_module = module_close

#-----------------------------------------------------------------------

def find_attachment_root():
    root_path = config.get_global_config()['lk_worker']['attachment_path']
    return root_path

example_content = (
    "We only need a small file for basic testing\n"
    "Large files that go round the read loop are "
    "another matter altogether.\n"
    )

example_file = StringIO.StringIO(example_content)

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        delete_worker_table_content()
        delete_user_table_content()
        make_initial_nodes_and_users()
        remove_root(find_attachment_root())
        
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t100(self):
        """ test_t100 : Full scope test to catch anything
        """
        # for attachments
        target_path = find_attachment_root()
        make_root(find_attachment_root())
        
        nde_set = find_in_path(['', 'root', 'Lokai', 'product1', 'data'])
        nde_data_1 = nde_set[0]
        nde_set = find_in_path(['', 'root', 'Lokai', 'product1'])
        nde_product_1 = nde_set[0]
        nde_set = find_in_path(['', 'root', 'Lokai'])
        nde_target = nde_set[0]
        nde_set = find_in_path(['', 'root'])
        nde_top = nde_set[0]
        nde_set = find_in_path(['', 'root', 'Other Path'])
        nde_other = nde_set[0]
        # Add some data to an intermediate node
        original_obj = get_node_dataset(nde_product_1)
        local_obj = {'nd_node': {'nde_idx': original_obj['nd_node']['nde_idx']}}
        local_obj['nd_activity'] = {'nde_idx': nde_product_1,
                                    'act_user': 'defined'}
        local_obj['message'] = {'nde_idx': nde_product_1,
                                'hst_time_entry': '2010-01-01',
                                'hst_type': 'not empty',
                                'hst_user': 'defined',
                                'hst_text': 'A test node is brought into being'}
        local_obj['nd_tags'] = 'tag1 tag2'
        put_node_dataset(local_obj)
        nda = NodeAttachment('node',
                             nde_product_1,
                             'file1.ext',
                             descripton = 'a file called 1',
                             user_name = 'fred'
                             )
        nda.store(example_file)
        
        engine.session.commit()
        # check stuff is there to delete
        edge_test = engine.session.query(ndEdge).filter(
            ndEdge.nde_child.in_([nde_target, nde_product_1, nde_data_1])
            ).all()
        self.assertEqual(len(edge_test), 3)
        parent_test = engine.session.query(ndParent).filter(
            ndParent.nde_idx.in_([nde_target, nde_product_1, nde_data_1])
            ).all()
        self.assertEqual(len(parent_test), 6)
        activity_test = engine.session.query(ndActivity).filter(
            ndActivity.nde_idx.in_([nde_target, nde_product_1, nde_data_1])
            ).all()
        self.assertEqual(len(activity_test), 1)
        tags_test = engine.session.query(ndNodeTag).filter(
            ndNodeTag.nde_idx.in_([nde_target, nde_product_1, nde_data_1])
            ).all()
        self.assertEqual(len(tags_test), 2)
        att_coll = AttachmentCollection(NodeAttachment,
                                        'node',
                                        nde_product_1)
        self.assertEqual(len(att_coll), 1)
        nda = att_coll['file1.ext']['_000']
        att_path = nda.get_target_path()
        self.assert_(os.path.exists(att_path),
                     "Failed to find %s"%att_path)
        # delete it
        expunge_tree(nde_target)
        engine.session.commit()
        nde_set = find_in_path(['', 'root'])
        self.assertEqual(nde_set[0], nde_top)
        nde_set = find_in_path(['', 'root', 'Other Path'])
        self.assertEqual(nde_set[0], nde_other)
        nde_set = find_in_path(['', 'root', 'Lokai'])
        self.assertEqual(len(nde_set), 0)
        edge_test = engine.session.query(ndEdge).filter(
            ndEdge.nde_child.in_([nde_target, nde_product_1, nde_data_1])
            ).all()
        self.assertEqual(len(edge_test), 0)
        parent_test = engine.session.query(ndParent).filter(
            ndParent.nde_idx.in_([nde_target, nde_product_1, nde_data_1])
            ).all()
        self.assertEqual(len(parent_test), 0)
        activity_test = engine.session.query(ndActivity).filter(
            ndActivity.nde_idx.in_([nde_target, nde_product_1, nde_data_1])
            ).all()
        self.assertEqual(len(activity_test), 0)
        tags_test = engine.session.query(ndNodeTag).filter(
            ndNodeTag.nde_idx.in_([nde_target, nde_product_1, nde_data_1])
            ).all()
        self.assertEqual(len(tags_test), 0)
        att_coll = AttachmentCollection(NodeAttachment,
                                        'node',
                                        nde_product_1)
        self.assertEqual(len(att_coll), 0)
        self.assert_(not os.path.exists(att_path),
                     "Failed to _not_ find %s"%att_path)
 
       
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
