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

from lokai.tool_box.tb_common.tb_ccss_cat import Engine

#-----------------------------------------------------------------------

def setup_module():
    pass

#-----------------------------------------------------------------------

T001_IN = """
p:
  font-size: 20px
div.section:
  font-size: 30px
  h1:
    font-size: 40px
h2, h3:
    font-size: 50px
    """

T001_OUT = """p {
  font-size: 20px;
}

div.section {
  font-size: 30px;
}

div.section h1 {
  font-size: 40px;
}

h2,
h3 {
  font-size: 50px;
}"""

T002_IN = """
p:
  font-size: 20px
p:
  text-align: right
p:
  font-size: 30px
"""
T002_OUT = """p {
  font-size: 30px;
  text-align: right;
}"""

class TestObject(unittest.TestCase):

    def setUp(self):
        pass
        

    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : Some selector combinations
        """
        pp = Engine(T001_IN)
        op = pp.to_css()
        self.assertEqual(op, T001_OUT)
    
    def test_t002(self):
        """ test_t002 : Override and merge declarations for same selector
        """
        pp = Engine(T002_IN)
        op = pp.to_css()
        self.assertEqual(op, T002_OUT)
    
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
