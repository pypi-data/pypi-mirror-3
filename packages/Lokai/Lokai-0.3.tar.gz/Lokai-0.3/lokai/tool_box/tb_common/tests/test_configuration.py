# Name:      lokai/tool_box/tb_common/tests/test_configuration.py
# Purpose:   Testing the interface to Configobj
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

from lokai.tool_box.tb_common.configuration import (handle_ini_declaration,
                                     get_global_config,
                                     clear_global_config,
                                     )

#-----------------------------------------------------------------------

ini_trial = (
    '[global]\n'
    'var1 = 1\n'
    '[section 1]\n'
    'var2 = a\n'
    'var1 = 2\n'
    'section 1_1.var3 = 1.2\n'
    'section 1_1.var1 = 3\n'
    )

ini_extend = (
    '[global]\n'
    'g1.v1 = g1_v1\n'
    '[section 2]\n'
    's2value = s2v\n'
    '[section 1]\n'
    'var1 = 3\n'
    )

#-----------------------------------------------------------------------

def setup_module():
    pass

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        clear_global_config()
        

    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 - Open and parse a file
        """
        handle_ini_declaration(StringIO.StringIO(ini_trial))
        obj = get_global_config()
        self.assertEqual(obj['global']['var1'], '1')
        self.assertEqual(obj['section 1']['var1'], '2')
        self.assertEqual(obj['section 1']['var2'], 'a')
        self.assertEqual(obj['section 1']['section 1_1']['var1'], '3')
        self.assertEqual(obj['section 1']['section 1_1']['var3'], '1.2')

    def test_t002(self):
        """ test_t002 - Open and parse a file and then extend
        """
        handle_ini_declaration(StringIO.StringIO(ini_trial))
        obj = get_global_config()
        obj.extend(StringIO.StringIO(ini_extend))
        
        self.assertEqual(obj['global']['var1'], '1')
        self.assertEqual(obj['global']['g1']['v1'], 'g1_v1')
        self.assertEqual(obj['section 1']['var1'], '3')
        self.assertEqual(obj['section 1']['var2'], 'a')
        self.assertEqual(obj['section 1']['section 1_1']['var1'], '3')
        self.assertEqual(obj['section 1']['section 1_1']['var3'], '1.2')
        self.assertEqual(obj['section 2']['s2value'], 's2v')

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
