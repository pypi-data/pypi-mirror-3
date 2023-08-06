# Name:      lokai/tool_box/tb_common/tests/test_file_helper.py
# Purpose:   Testing test helper functions
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

from lokai.tool_box.tb_common.helpers import can_remove_root, remove_root, make_root

#-----------------------------------------------------------------------

def setup_module():
    pass

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        pass
        

    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001: Try combinations of good and bad paths
        """
        test_root_name = 'a long name that we will not use anywhere else'
        self.assertRaises(SystemExit, can_remove_root, '~/foobar')
        self.assertRaises(SystemExit, can_remove_root, '/foobar')
        self.assertRaises(SystemExit, can_remove_root, './')
        self.assertRaises(SystemExit, can_remove_root, os.getcwd())
        self.assert_(can_remove_root(test_root_name))
        # Basic removal
        remove_root(test_root_name) # just in case
        self.failIf(os.path.exists(test_root_name))
        make_root(test_root_name)
        self.failIf(not os.path.exists(test_root_name))
        remove_root(test_root_name) # just in case
        self.failIf(os.path.exists(test_root_name))
        # Get nested
        make_root(os.path.join(test_root_name, 'p1', 'p1.1'))
        self.failIf( not os.path.exists(os.path.join(test_root_name, 'p1', 'p1.1')))
        test_file = os.path.join(test_root_name, 'p1', 'p1.1', 'my final file')
        fp = file(test_file, 'w')
        fp.close() # should leave an empty file
        self.failIf( not os.path.exists(test_file))
        remove_root(test_root_name)
        self.failIf(os.path.exists(test_file))
        self.failIf(os.path.exists(test_root_name))

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
