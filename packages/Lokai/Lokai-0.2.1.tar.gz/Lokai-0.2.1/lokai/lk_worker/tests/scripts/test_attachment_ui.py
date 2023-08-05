# Name:      lokai/lk_worker/tests/scripts/test_attachment_ui.py
# Purpose:   Testing aspects of attachments through the UI
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
import StringIO

from BeautifulSoup import BeautifulSoup

from lokai.tool_box.tb_database.orm_interface import engine
import lokai.tool_box.tb_common.configuration as config

from lokai.lk_worker.tests.structure_helper import make_initial_nodes_and_users
from lokai.lk_worker.tests.helpers import (
    module_ui_initialise,
    module_close,
    delete_worker_table_content
    )

from lokai.lk_worker.nodes.search import find_in_path

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
    delete_user_table_content,
    )

from lokai.tool_box.tb_common.helpers import remove_root, make_root

from lokai.lk_worker.models.builtin_data_attachments import (
    ndAttachment,
    AttachmentCollection,
    NodeAttachment
    )

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

setup_module = module_ui_initialise
teardown_module = module_close

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        delete_worker_table_content()
        delete_user_table_content()
        remove_root(find_attachment_root())
        make_root(find_attachment_root())
        make_initial_nodes_and_users()
        
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t100(self):
        """ test_t100 - Post something to the form
        """
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_set = find_in_path(['', 'root', 'Lokai'])
        
        query_set = {
            'detail_idx': nde_set[0],
            'detail___attachments___attach_description': 'uploaded file',
            'detail___activity_data___new_message':
            "Upload a file for testing",
            'detail___node_edit___nde_name': 'Lokai',
            'detail___upd_btns___update': 'Update',
            'detail___attachments___attach_file': (
                StringIO.StringIO("This is the content for test_upload_file"),
                'test_upload_file',
                ),
            }

        res = source.post(str('/pages/%s/edit'%nde_set[0]), data=query_set)
        nda = AttachmentCollection(NodeAttachment, 'node', nde_set[0])
        self.assertEqual(len(nda), 1,
                         "Attachment posted - expect 1"
                         " - find %d"%len(nda))

    def test_t200(self):
        """ test_t200 - Download an existing file
        """
        make_root(find_attachment_root())
        nde_set = find_in_path(['', 'root', 'Lokai'])
        att = NodeAttachment('node',
                             nde_set[0],
                             'test_upload_file',
                             descripton = 'a file called 1',
                             user_name = 'fred'
                             )
        att.store(example_file)
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        file_back = source.get('/pages/%s/file/%s'% (
            nde_set[0], 'test_upload_file_000'))
        self.assertEqual(file_back.status, "200 OK")

    def test_t201(self):
        """ test_t201 - Download an existing file without version
        """
        make_root(find_attachment_root())
        nde_set = find_in_path(['', 'root', 'Lokai'])
        att = NodeAttachment('node',
                             nde_set[0],
                             'test_upload_file',
                             descripton = 'a file called 1',
                             user_name = 'fred'
                             )
        att.store(example_file)
        source = basic_login('fred_1', 'useless', 'Fred Manager')
        file_back = source.get('/pages/%s/file/%s'% (
            nde_set[0], 'test_upload_file'))
        self.assertEqual(file_back.status, "200 OK")

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
