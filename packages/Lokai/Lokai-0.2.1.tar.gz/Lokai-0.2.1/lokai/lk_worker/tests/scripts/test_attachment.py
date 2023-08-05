# Name:      lokai/lk_worker/tests/scripts/test_attachment.py
# Purpose:   Testing aspects of atachment class
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
import os

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update
import lokai.tool_box.tb_common.configuration as config

from lokai.lk_worker.models.builtin_data_attachments import (
    ndAttachment,
    NodeAttachment,
    AttachmentCollection,
    AttachmentNotFound,
    unpack_version,
    )

from lokai.tool_box.tb_common.helpers import remove_root, make_root
from lokai.lk_worker.tests.helpers import (
    module_initialise,
    module_close,
    delete_table_content,
    )

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
    
    def assertSamePath(self, expected, actual):
        """ OS-independent path comparison
        """
        self.assertEqual(
                    os.path.normpath(os.path.normcase(expected)),
                    os.path.normpath(os.path.normcase(actual)))

    def setUp(self):
        delete_table_content([ndAttachment],
                             )
        remove_root(find_attachment_root())
        example_file.seek(0)
        

    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001: create an attachment entry - look at paths
        """
        target_path = find_attachment_root()
        make_root(find_attachment_root())
        att = NodeAttachment('node',
                             '1234567890',
                             'file1.ext',
                             descripton = 'a file called 1',
                             user_name = 'fred'
                             )
        self.assertSamePath(att.get_target_path(),
                         os.path.join(target_path,
                                      '12/34/56/78/90/file1_000.ext'))
        att = NodeAttachment('node',
                             '1234567890',
                             'file1.',
                             descripton = 'a file called 1',
                             user_name = 'fred'
                             )
        self.assertSamePath(att.get_target_path(),
                         os.path.join(target_path,
                                      '12/34/56/78/90/file1_000.'))
        att = NodeAttachment('node',
                             '1234567890',
                             'file1',
                             descripton = 'a file called 1',
                             user_name = 'fred'
                             )
        self.assertSamePath(att.get_target_path(),
                         os.path.join(target_path,
                                      '12/34/56/78/90/file1_000'))
        
    def test_t002(self):
        """ test_t002: create an attachment entry - store the data
        """
        target_path = find_attachment_root()
        make_root(find_attachment_root())
        att = NodeAttachment('node',
                             '1234567890',
                             'file1.ext',
                             descripton = 'a file called 1',
                             user_name = 'fred'
                             )
        avn = att.get_latest_version()
        self.assertEqual(avn, -1)
        att.store(example_file)
        fpt = att.open_file()
        chunk = fpt.read(4096)
        self.assertEqual(chunk, example_content)
        fpt.close()
        engine.session.commit()
        atx = NodeAttachment('node',
                             '1234567890',
                             'file1.ext'
                             )
        avn = atx.get_latest_version()
        self.assertEqual(avn, 0)
        atx.set_version(0)
        atx.get_detail()
        fpx = atx.open_file()
        chunk = fpx.read(4096)
        self.assertEqual(chunk, example_content)
        fpx.close()
        
    def test_t003(self):
        """ test_t003: Missing main directory - created automatically
        """
        target_path = find_attachment_root()
        self.assert_(not os.path.exists(target_path))
        att = NodeAttachment('node',
                             '1234567890',
                             'file1.ext',
                             descripton = 'a file called 1',
                             user_name = 'fred'
                             )
        att.store(example_file)
        self.assert_(os.path.exists(target_path))
        

    def test_t004(self):
        """ test_t004: Store multiple versions and then delete an entry
        """
        target_path = find_attachment_root()
        make_root(find_attachment_root())
        att1 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              descripton = 'a file called 1',
                              user_name = 'fred1'
                              )
        att1.store(example_file)
        att2 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              descripton = 'a file called 1',
                              user_name = 'fred2'
                              )
        att2.store(example_file)
        engine.session.commit()
        ntt1 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              )
        avn = ntt1.get_latest_version()
        self.assertEqual(avn, 1)
        ntt1.set_version(0)
        ntt1.get_detail()
        self.assertEqual(ntt1.user_name, u'fred1')
        ntt2 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              )
        avn = ntt2.get_latest_version()
        self.assertEqual(avn, 1)
        ntt2.set_version(1)
        ntt2.get_detail()
        self.assertEqual(ntt2.user_name, u'fred2')
        #
        ntt1.delete()
        ntt3 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              )
        avn = ntt3.get_latest_version()
        self.assertEqual(avn, 1)
        ntt3.set_version(0)
        self.assertRaises(AttachmentNotFound, ntt3.get_detail)

    def test_t100(self):
        """ test_t100 - use the collection
        """
        target_path = find_attachment_root()
        make_root(find_attachment_root())
        att1 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              descripton = 'a file called 1',
                              user_name = 'fred1'
                              )
        att1.store(example_file)
        att2 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              descripton = 'a file called 1',
                              user_name = 'fred2'
                              )
        att2.store(example_file)
        target_path = find_attachment_root()
        make_root(find_attachment_root())
        att3 = NodeAttachment('node',
                              '1234567890',
                              'file2.ext',
                              descripton = 'a file called 2',
                              user_name = 'fred1'
                              )
        att3.store(example_file)
        att4 = NodeAttachment('node',
                              '1234567890',
                              'file3.ext',
                              descripton = 'a file called 3',
                              user_name = 'fred2'
                              )
        att4.store(example_file)
        engine.session.commit()
        coll = AttachmentCollection(NodeAttachment,
                                    'node',
                                    '1234567890')
        self.assertEqual(len(coll), 4)
        file_set = [u'file1.ext', u'file1.ext', u'file2.ext', u'file3.ext']
        file_set_p = 0
        for nda in coll.get_in_sequence():
            self.assertEqual(nda.file_name, file_set[file_set_p])
            file_set_p += 1

    def test_t102(self):
        """ test_t102 : delete a collection
        """
        # Repeat t101 so we get some data.
        target_path = find_attachment_root()
        make_root(find_attachment_root())
        att1 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              descripton = 'a file called 1',
                              user_name = 'fred1'
                              )
        att1.store(example_file)
        att2 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              descripton = 'a file called 1',
                              user_name = 'fred2'
                              )
        att2.store(example_file)
        target_path = find_attachment_root()
        make_root(find_attachment_root())
        att3 = NodeAttachment('node',
                              '1234567890',
                              'file2.ext',
                              descripton = 'a file called 2',
                              user_name = 'fred1'
                              )
        att3.store(example_file)
        att4 = NodeAttachment('node',
                              '1234567890',
                              'file3.ext',
                              descripton = 'a file called 3',
                              user_name = 'fred2'
                              )
        att4.store(example_file)
        engine.session.commit()
        coll = AttachmentCollection(NodeAttachment,
                                    'node',
                                    '1234567890')
        self.assertEqual(len(coll), 4)
        file_set = [u'file1.ext', u'file1.ext', u'file2.ext', u'file3.ext']
        file_set_p = 0
        for nda in coll.get_in_sequence():
            self.assertEqual(nda.file_name, file_set[file_set_p])
            file_set_p += 1
        # Tha's alright then - now delete it (individual nda delete is
        # tested elsewhere)
        coll.delete_data()
        engine.session.commit()
        coll_check = AttachmentCollection(NodeAttachment,
                                          'node',
                                          '1234567890')
        self.assertEqual(len(coll_check), 0)
       
    def test_t201(self):
        """ test_t201 - unpack for maximum
        """
        (name, version, extension) = unpack_version('file_name.txt')
        self.assertEqual(name, 'file_name')
        self.assertEqual(version, None)
        self.assertEqual(extension, '.txt')
        (name, version, extension) = unpack_version('file_name____.txt')
        self.assertEqual(name, 'file_name')
        self.assertEqual(version, None)
        self.assertEqual(extension, '.txt')
        (name, version, extension) = unpack_version('file_name_000.txt')
        self.assertEqual(name, 'file_name')
        self.assertEqual(version, '_000')
        self.assertEqual(extension, '.txt')
        (name, version, extension) = unpack_version('file_name___.txt')
        self.assertEqual(name, 'file_name___')
        self.assertEqual(version, None)
        self.assertEqual(extension, '.txt')

    def test_t202(self):
        """ test_t202 - request latest version
        """
        # Set up a few versions of one file, plus spoilers
        target_path = find_attachment_root()
        make_root(find_attachment_root())
        att1 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              descripton = 'a file called 1',
                              user_name = 'fred1'
                              )
        att1.store(example_file)
        att2 = NodeAttachment('node',
                              '1234567890',
                              'file1.ext',
                              descripton = 'a file called 1',
                              user_name = 'fred2'
                              )
        att2.store(example_file)
        target_path = find_attachment_root()
        make_root(find_attachment_root())
        att3 = NodeAttachment('node',
                              '1234567890',
                              'file2.ext',
                              descripton = 'a file called 2',
                              user_name = 'fred1'
                              )
        att3.store(example_file)
        att4 = NodeAttachment('node',
                              '1234567890',
                              'file3.ext',
                              descripton = 'a file called 3',
                              user_name = 'fred2'
                              )
        att4.store(example_file)
        engine.session.commit()
        nda_1 = NodeAttachment('node',
                               '1234567890',
                               'file1.ext',
                               unpack = True)
        self.assertEqual(nda_1.version, 1)
        nda_1 = NodeAttachment('node',
                               '1234567890',
                               'file2.ext',
                               unpack = True)
        self.assertEqual(nda_1.version, 0)
        nda_1 = NodeAttachment('node',
                               '1234567890',
                               'file3____.ext',
                               unpack = True)
        self.assertEqual(nda_1.version, 0)

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
