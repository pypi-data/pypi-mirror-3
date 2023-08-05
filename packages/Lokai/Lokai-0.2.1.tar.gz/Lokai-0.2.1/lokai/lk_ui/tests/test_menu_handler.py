# Name:      lokai/lk_ui/tests/test_menu_handler.py
# Purpose:   Testing top level dispatch process
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

import unittest
import sys
import os
import StringIO

from lokai.tool_box.tb_common.configuration import (set_global_config_file,
                                              clear_global_config)

import lokai.lk_ui
from lokai.lk_ui.publisher import get_lokai_consolidating_publisher

from lokai.lk_ui.menu_handler import MenuHandler

#-----------------------------------------------------------------------

def get_permission(arg0, arg1):
    if arg1 != 'response arg':
        raise TypeError("response arg is %s"%arg1)
    return arg0 != 'x'

#-----------------------------------------------------------------------

def setup_module():
    pass

#-----------------------------------------------------------------------

class TestObject( unittest.TestCase ):

    def setUp( self ):
        clear_global_config()
        lokai.lk_ui.PageTemplate = None
        lokai.lk_ui.TemplatePath = None
        lokai.lk_ui.StaticPath = None
        lokai.lk_ui.MakeIdent = None
        lokai.lk_ui.MakeMenu = None
    
    #-------------------------------------------------------------------
    
    def tearDown( self ):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : Post into a menu from config
        """
        config = (
            "[all]\n"
            "not_used = xxx\n"
            "[skin]\n"
            "ignore_this = xxx\n"
            "[app1]\n"
            "application_publisher = lokai.lk_ui.tests.trial_publisher.publisher\n"
            "menu_publisher = lokai.lk_ui.tests.trial_publisher\n"
            "[other]\n"
            "not_used = xxx\n"
            )
        set_global_config_file(StringIO.StringIO(config))
        mh = MenuHandler('response arg')
        self.assertEqual(mh.menu_list[0]['title'], 'Main Menu')
        self.assertEqual(mh.menu_list[0]['children'][0]['title'], 'Sub Menu 1')
        self.assertEqual(mh.menu_list[0]['children'][0]['link'], '/u/r/l/1')
        self.assertEqual(mh.menu_list[0]['children'][1]['title'], 'Sub Menu 2')

        # Add something
        mh.process_submenu([
            {'title': 'At Level 0',
             }
            ])
        self.assertEqual(mh.menu_list[0]['title'], 'Main Menu')
        self.assertEqual(mh.menu_list[1]['title'], 'At Level 0')
        self.assertEqual(mh.menu_list[0]['children'][0]['title'], 'Sub Menu 1')
        self.assertEqual(mh.menu_list[0]['children'][0]['link'], '/u/r/l/1')
        self.assertEqual(mh.menu_list[0]['children'][1]['title'], 'Sub Menu 2')

        # Remove something
        mh.process_submenu([
            {'title': 'Sub Menu 1',
             'action': 'delete',
             'parent': ['Main Menu']
             }
            ])
        self.assertEqual(mh.menu_list[0]['title'], 'Main Menu')
        self.assertEqual(mh.menu_list[1]['title'], 'At Level 0')
        self.assertEqual(mh.menu_list[0]['children'][0]['title'], 'Sub Menu 2')
        self.assertEqual(len(mh.menu_list[0]['children']), 1)

        # Add to lower level
        mh.process_submenu([
            {'title': 'Sub Menu 2.1',
             'link': '/u/r/l',
             'parent': ['Main Menu', 'Sub Menu 2'],
             'children': [
                 {'title': 'Sub Menu 2.1.1',
                  'link':  '/u/r/l/2/1/1'
                  },
                 {'title': 'Sub Menu 2.1.2',
                  'link':  '/u/r/l/2/1/2',
                  'position': 20
                  },
                 ]
             }
            ])
        self.assertEqual(mh.menu_list[0]['title'], 'Main Menu')
        self.assertEqual(mh.menu_list[1]['title'], 'At Level 0')
        self.assertEqual(mh.menu_list[0]['children'][0]['title'], 'Sub Menu 2')
        self.assertEqual(len(mh.menu_list[0]['children']), 1)
        self.assertEqual(mh.menu_list[0]['children'][0]
                         ['children'][0]['children'][0]['title'],
                         'Sub Menu 2.1.1')
        self.assertEqual(mh.menu_list[0]['children'][0]
                         ['children'][0]['children'][1]['title'],
                         'Sub Menu 2.1.2')
        
        # Sort
        mh._sort_menu(mh.menu_list)
        self.assertEqual(mh.menu_list[0]['children'][0]
                         ['children'][0]['children'][0]['title'],
                         'Sub Menu 2.1.2')
        self.assertEqual(mh.menu_list[0]['children'][0]
                         ['children'][0]['children'][1]['title'],
                         'Sub Menu 2.1.1')

        # Parents
        mh._identify_parents(mh.menu_list)
        level3_parents = (mh.menu_list[0]['children'][0]
               ['children'][0]['children'][0]['parent'])
        print level3_parents
        for l3p, given in zip(level3_parents,
                              ['Main Menu', 'Sub Menu 2', 'Sub Menu 2.1']):
            self.assertEqual(l3p, given)
                         
        # Permission
        mh.process_submenu([
            {'title': 'Sub Menu x',
             'permission': 'x',
             'permission_tester': get_permission,
             'parent': ['At Level 0']
             }
            ])
        self.assertEqual(mh.menu_list[0]['title'], 'Main Menu')
        self.assertEqual(mh.menu_list[1]['title'], 'At Level 0')
        self.assertEqual(mh.menu_list[0]['children'][0]['title'], 'Sub Menu 2')
        self.assertEqual(mh.menu_list[1]['children'][0]['title'], 'Sub Menu x')
        self.assertEqual(len(mh.menu_list), 2)
        self.assertEqual(len(mh.menu_list[1]['children']), 1)
        mh._reduce_under_permissions(mh.menu_list)
        self.assertEqual(len(mh.menu_list[1]['children']), 0)

        mh._remove_dangling_elements(mh.menu_list)
        self.assertEqual(len(mh.menu_list), 1)
        
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
