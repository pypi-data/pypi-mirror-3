# Name:      lokai/tool_box/tb_common/tests/test_file_walk.py
# Purpose:   Testing ordered_walk
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

from lokai.tool_box.tb_common.helpers import remove_root, make_root
from lokai.tool_box.tb_install.environment_setup import process_setup

import lokai.tool_box.tb_common.file_handling as file_handling

#-----------------------------------------------------------------------

WORK_DIRECTORY = "removable_test_file_walk"
init_txt = (
    "aaa:\n"
    "  aaa_aaa:\n"
    "    aaa_aaa_aaa:\n"
    "    aaa_aaa_aab: |\n"
    "      aaa_aaa_aab\n"
    "    aaa_aaa_aac:\n"
    "      aaa_aaa_aac_aaa: |\n"
    "        aaa_aaa_aac_aaa\n"
    "  aaa_aab: |\n"
    "    aaa_aab\n"
    "  aaa_aac:\n"
    "    aaa_aac_aaa: |\n"
    "      aaa_aac_aaa\n"
    "aab:\n"
    "  aab_aaa: |\n"
    "    aab_aaa\n"
    "aac: |\n"
    "  aac\n"
    "aad: |\n"
    "  aad\n"
    "\n"
    )

expected_set = [
    "aaa/aaa_aaa/aaa_aaa_aac/aaa_aaa_aac_aaa",
    "aaa/aaa_aaa/aaa_aaa_aab",
    "aaa/aaa_aac/aaa_aac_aaa",
    "aaa/aaa_aab",
    "aab/aab_aaa",
    "aac",
    "aad",
    ]

# for the reversed set remember that directories are sorted before files
expected_reversed = [
    "aab/aab_aaa",
    "aaa/aaa_aac/aaa_aac_aaa",
    "aaa/aaa_aaa/aaa_aaa_aac/aaa_aaa_aac_aaa",
    "aaa/aaa_aaa/aaa_aaa_aab",
    "aaa/aaa_aab",
    "aad",
    "aac",
    ]
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
        """ test_t001 : extract an ordered list
        """
        for given, found in zip(
            file_handling.ordered_walk(WORK_DIRECTORY),
            expected_set):
            self.assertEqual(given, found)

        self.assertEqual(
            len(expected_set),
            len(list(file_handling.ordered_walk(WORK_DIRECTORY)))
            )

    def test_t002(self):
        """ test_t002 : extract a reverse ordered list
        """
        for given, found in zip(
            file_handling.ordered_walk(WORK_DIRECTORY, reverse=True),
            expected_reversed):
            self.assertEqual(given, found)

        self.assertEqual(
            len(expected_reversed),
            len(list(file_handling.ordered_walk(WORK_DIRECTORY, reverse=True)))
            )
        
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
