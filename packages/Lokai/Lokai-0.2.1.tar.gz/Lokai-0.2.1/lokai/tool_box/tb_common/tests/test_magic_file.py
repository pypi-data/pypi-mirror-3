# Name:      lokai/tool_box/tb_common/tests/test_magic_file.py
# Purpose:   Testing the magic file object
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
import StringIO

from lokai.tool_box.tb_common.helpers import remove_root, make_root
from lokai.tool_box.tb_install.environment_setup import process_setup

import lokai.tool_box.tb_common.magic_file as magic_file

#-----------------------------------------------------------------------

WORK_DIRECTORY = "removable_test_magic_file"
init_txt = (
    "source_dir:\n"
    "  lower_1:\n"
    "    file_1: |\n"
    "      file content\n"
    "  lower_2:\n"
    "    file_2: |\n"
    "      file_2 new content\n"
    "temp_dir:\n"
    "target_dir:\n"
    "  lower_2:\n"
    "    file_2: |\n"
    "      file_2 old content\n"
    "other_dir:\n"
    "  lower_2:\n"
    "    file_2: |\n"
    "      file_2 old content\n"
    )
#-----------------------------------------------------------------------

def setup_module():
    pass
              
#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        remove_root(WORK_DIRECTORY)
        make_root(WORK_DIRECTORY)
        process_setup(StringIO.StringIO(init_txt),
                      working_directory=WORK_DIRECTORY)
        

    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : Open, read, and close an MF object
        """
        mf = magic_file.MagicFile(
            'lower_1/file_1',
            os.path.join(WORK_DIRECTORY, 'source_dir'),
            None,
            'r'
            )
        content = mf.readlines()
        self.assertEqual(content, ["file content\n"])
        mf.close()
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'source_dir', 'lower_1', 'file_1')))
        self.assert_(not
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1')))

    def test_t002(self):
        """ test_t002 : Open and close, with rename
        """
        mf = magic_file.MagicFile(
            'lower_1/file_1',
            os.path.join(WORK_DIRECTORY, 'source_dir'),
            os.path.join(WORK_DIRECTORY, 'target_dir'),
            'r'
            )
        mf.close()
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_1')))
        fd = open(
            os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_1'),
            'r'
            )
        content = fd.readlines()
        self.assertEqual(content, ["file content\n"])
        
        # The original directory exists..
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'source_dir', 'lower_1')))

        # The original file does not..
        self.assert_(not
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'source_dir', 'lower_1', 'file_1')))

    def test_t003(self):
        """ test_t003 : close into multiple directories
        """
        mf = magic_file.MagicFile(
            'lower_1/file_1',
            os.path.join(WORK_DIRECTORY, 'source_dir'),
            [os.path.join(WORK_DIRECTORY, 'target_dir'),
             os.path.join(WORK_DIRECTORY, 'other_dir')],
            'r'
            )
        mf.close()
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_1')))
        fd = open(
            os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_1'),
            'r'
            )
        content = fd.readlines()
        self.assertEqual(content, ["file content\n"])
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'other_dir', 'lower_1', 'file_1')))
        fd = open(
            os.path.join(WORK_DIRECTORY, 'other_dir', 'lower_1', 'file_1'),
            'r'
            )
        content = fd.readlines()
        self.assertEqual(content, ["file content\n"])
        self.assert_(
            len(os.listdir(
                os.path.join(WORK_DIRECTORY, 'source_dir', 'lower_1'))) == 0)

    def test_t004(self):
        """ test_t004 : open new file for output with rename on close
        """
        mf = magic_file.MagicFile(
            os.path.join('lower_1', 'file_2'),
            os.path.join(WORK_DIRECTORY, 'temp_dir'),
            os.path.join(WORK_DIRECTORY, 'target_dir'),
            'w'
            )
        mf.write("file 2 content")
        self.assert_(not
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_2')))
        mf.close()
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_2')))
        fd = open(
            os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_2'),
            'r'
            )
        content = fd.readlines()
        self.assertEqual(content, ["file 2 content"])

    def test_t005(self):
        """ test_t005 : open new file for output - no rename
        """
        mf = magic_file.MagicFile(
            os.path.join('lower_1', 'file_2'),
            os.path.join(WORK_DIRECTORY, 'target_dir'),
            None,
            'w'
            )
        mf.write("file 2 content")
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_2')))
        mf.close()
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_2')))
        fd = open(
            os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_2'),
            'r'
            )
        content = fd.readlines()
        self.assertEqual(content, ["file 2 content"])

    def test_t006(self):
        """ test_t006 : target already exists
        """
        self.assertRaises(
            magic_file.MFError,
            magic_file.MagicFile,
            os.path.join('lower_2', 'file_2'),
            os.path.join(WORK_DIRECTORY, 'source_dir'),
            os.path.join(WORK_DIRECTORY, 'target_dir'),
            'r'
            )
        
    def test_t007(self):
        """ test_t007 : disposition 'o'
        """
        mf = magic_file.MagicFile(
            os.path.join('lower_2', 'file_2'),
            os.path.join(WORK_DIRECTORY, 'source_dir'),
            [os.path.join(WORK_DIRECTORY, 'target_dir'),
             os.path.join(WORK_DIRECTORY, 'other_dir')],
            'r',
            disposition='o')
        content = mf.readlines()
        self.assertEqual(content, ["file_2 new content\n"])
        mf.close()
        # The source no longer exists..
        self.assert_(not
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'source_dir', 'lower_2', 'file_2')))
        # The original destination has been overwritten
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_2', 'file_2')))
        fd = open(
            os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_2', 'file_2'),
            'r'
            )
        content = fd.readlines()
        self.assertEqual(content, ["file_2 new content\n"])
        fd.close()
        # The other original destination has been overwritten
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'other_dir', 'lower_2', 'file_2')))
        fd = open(
            os.path.join(WORK_DIRECTORY, 'other_dir', 'lower_2', 'file_2'),
            'r'
            )
        content = fd.readlines()
        self.assertEqual(content, ["file_2 new content\n"])
        fd.close()
        
    def test_t008(self):
        """ test_t008 : disposition 'k'
        """
        mf = magic_file.MagicFile(
            os.path.join('lower_2', 'file_2'),
            os.path.join(WORK_DIRECTORY, 'source_dir'),
            [os.path.join(WORK_DIRECTORY, 'target_dir'),
             os.path.join(WORK_DIRECTORY, 'other_dir')],
            'r',
            disposition='k')
        content = mf.readlines()
        self.assertEqual(content, ["file_2 new content\n"])
        mf.close()
        # The source no longer exists..
        self.assert_(not
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'source_dir', 'lower_2', 'file_2')))
        # The original destination still exists
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_2', 'file_2')))
        fd = open(
            os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_2', 'file_2'),
            'r'
            )
        content = fd.readlines()
        self.assertEqual(content, ["file_2 old content\n"])
        fd.close()
        # The other original destination still exists
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'other_dir', 'lower_2', 'file_2')))
        fd = open(
            os.path.join(WORK_DIRECTORY, 'other_dir', 'lower_2', 'file_2'),
            'r'
            )
        content = fd.readlines()
        self.assertEqual(content, ["file_2 old content\n"])
        fd.close()

    def test_t009(self):
        """ test_t009 : rename after close
        """
        # open a file
        mf1 = magic_file.MagicFile(
            os.path.join('lower_1', 'file_1'),
            os.path.join(WORK_DIRECTORY, 'source_dir'),
            os.path.join(WORK_DIRECTORY, 'target_dir'),
            'r',
            )
        # other 'process' opens another file and closes it
        mf2 = magic_file.MagicFile(
            os.path.join('lower_1', 'file_1'),
            os.path.join(WORK_DIRECTORY, 'temp_dir'),
            os.path.join(WORK_DIRECTORY, 'target_dir'),
            'w',
            )
        mf2.write('got here first')
        mf2.close()
        # Close the first one - trap the error
        self.assertRaises(magic_file.MFError, mf1.close)
        # We get here with the internal file closed, but the rename
        # still possible.
        self.assertRaises(magic_file.MFError, mf1.readlines)
        mf1.set_rename_target(name=os.path.join('lower_1', 'file_1_retread'))
        mf1.close()
        self.assert_(
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1',
                             'file_1_retread')))
        
    def test_t010(self):
        """ test_t010 : close an empty output file
        """
        mf = magic_file.MagicFile(
            'lower_1/file_2',
            os.path.join(WORK_DIRECTORY, 'temp_dir'),
            os.path.join(WORK_DIRECTORY, 'target_dir'),
            'w'
            )
        temp_file = mf.file_object_path
        self.assert_(os.path.exists(temp_file))
        mf.close()
        self.assert_(not
            os.path.exists(temp_file))
        self.assert_(not
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_2')))
        
    def test_t011(self):
        """ test_t011 : close and delete a used output file
        """
        mf = magic_file.MagicFile(
            'lower_1/file_2',
            os.path.join(WORK_DIRECTORY, 'temp_dir'),
            os.path.join(WORK_DIRECTORY, 'target_dir'),
            'w'
            )
        temp_file = mf.file_object_path
        self.assert_(os.path.exists(temp_file))
        mf.write('put something in')
        mf.close(delete=True)
        self.assert_(not
            os.path.exists(temp_file))
        self.assert_(not
            os.path.exists(
                os.path.join(WORK_DIRECTORY, 'target_dir', 'lower_1', 'file_2')))

    def test_t012(self):
        """ test_t012 : return the name of the open file
        """
        mf = magic_file.MagicFile(
            os.path.join('lower_2', 'file_2'),
            os.path.join(WORK_DIRECTORY, 'source_dir'),
            [os.path.join(WORK_DIRECTORY, 'target_dir'),
             os.path.join(WORK_DIRECTORY, 'other_dir')],
            'r',
            disposition='k')
        self.assertEqual(
            mf.name,
            os.path.abspath(
                os.path.join(WORK_DIRECTORY, 'source_dir', 'lower_2', 'file_2')))
        mf.close()
        self.assertEqual(mf.name, None)
        
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
