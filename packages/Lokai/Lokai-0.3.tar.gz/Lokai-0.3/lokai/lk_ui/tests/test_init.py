# Name:      lokai/lk_ui/tests/test_init.py
# Purpose:   Testing initialise from config file
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
from lokai.tool_box.tb_common.import_helpers import get_module_path
from lokai.lk_ui.publisher import build_skin, build_application_mounts
import lokai.lk_ui
from lokai.lk_ui.ui_default.make_ident import make_ident
from lokai.lk_ui.ui_default.make_menu import make_menu
from lokai.lk_ui.ui_default.default_publisher import (
    get_default_publisher as def_pub)
from lokai.lk_ui.tests.trial_publisher import publisher as trial_pub

#-----------------------------------------------------------------------

def setup_module():
    pass

#-----------------------------------------------------------------------

class TestObject( unittest.TestCase ):

    def setUp( self ):
        clear_global_config()
        lokai.lk_ui.PageTemplate = None
        lokai.lk_ui.TemplatePath = None
        lokai.lk_ui.MakeIdent = None
        lokai.lk_ui.MakeMenu = None
    
    #-------------------------------------------------------------------
    
    def tearDown( self ):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : read skin and set up global links
        """
        config = (
            "[all]\n"
            "not_used = xxx\n"
            "[skin]\n"
            "page_template = main_page.html\n"
            "templates = lokai.lk_ui.ui_default\n"
            "template_cache = lk_template_cache\n"
            "static = lokai.lk_ui.ui_default\n"
            "ident_builder = lokai.lk_ui.ui_default.make_ident.make_ident\n"
            "menu_builder = lokai.lk_ui.ui_default.make_menu.make_menu\n"
            "ignore_this = xxx\n"
            "[other]\n"
            "not_used = xxx\n"
            )
        
        set_global_config_file(StringIO.StringIO(config))
        build_skin()
        self.assertEqual(lokai.lk_ui.PageTemplate, 'main_page.html')
        self.assertEqual(lokai.lk_ui.TemplatePath,
                         [os.path.abspath(
                             os.path.join(
                                 get_module_path(
                                     'lokai.lk_ui.ui_default'), 'templates'))])
        self.assertEqual(lokai.lk_ui.TemplatePath[0][-25:],
                         os.path.join('lk_ui', 'ui_default', 'templates')[-25:])
        self.assertEqual(lokai.lk_ui.TemplateCachePath, 'lk_template_cache')
        self.assertEqual(lokai.lk_ui.StaticPath[-22:],
                         os.path.join('lk_ui', 'ui_default', 'static')[-22:])
        self.assertEqual(lokai.lk_ui.MakeMenu, make_menu)
        self.assertEqual(lokai.lk_ui.MakeIdent, make_ident)

    def test_t002(self):
        """ test_t002 : read the skin and use the defaults
        """
        config = (
            "[all]\n"
            "not_used = xxx\n"
            "[skin]\n"
            "ignore_this = xxx\n"
            "[other]\n"
            "not_used = xxx\n"
            )
        
        set_global_config_file(StringIO.StringIO(config))
        build_skin()
        self.assertEqual(lokai.lk_ui.PageTemplate, 'main_page.html')
        self.assertEqual(lokai.lk_ui.TemplatePath,
                         [os.path.abspath(
                             os.path.join(
                                 get_module_path(
                                     'lokai.lk_ui.ui_default'), 'templates'))])
        self.assertEqual(lokai.lk_ui.TemplateCachePath, None)
        self.assertEqual(lokai.lk_ui.MakeMenu, make_menu)
        self.assertEqual(lokai.lk_ui.MakeIdent, make_ident)

    def test_t101(self):
        """ test_t101 : Set up application mounts
        """
        config = (
            "[all]\n"
            "not_used = xxx\n"
            "[skin]\n"
            "ignore_this = xxx\n"
            "[default]\n"
            "# Provide a default for when the url is not matched\n"
            "application_publisher = lokai.lk_ui.ui_default.default_publisher.get_default_publisher\n"
            "[app1]\n"
            "application_publisher = lokai.lk_ui.tests.trial_publisher.get_trial_publisher\n"
            "application_path = prefix_text\n"
            "[other]\n"
            "not_used = xxx\n"
            )
        set_global_config_file(StringIO.StringIO(config))
        default_app, mount_set = build_application_mounts()
        self.assertEqual(type(default_app), type(def_pub()))
        self.assertEqual(mount_set,
                         {'/prefix_text': trial_pub})
                         
    def test_t102(self):
        """ test_t102 : Set up application mount with a default prefix
        """
        config = (
            "[all]\n"
            "not_used = xxx\n"
            "[skin]\n"
            "ignore_this = xxx\n"
            "[default]\n"
            "# Provide a default for when the url is not matched\n"
            "application_publisher = lokai.lk_ui.ui_default.default_publisher.get_default_publisher\n"
            "[app1]\n"
            "application_publisher = lokai.lk_ui.tests.trial_publisher.get_trial_publisher\n"
            "[other]\n"
            "not_used = xxx\n"
            )
        set_global_config_file(StringIO.StringIO(config))
        default_app, mount_set = build_application_mounts()
        self.assertEqual(type(default_app), type(def_pub()))
        self.assertEqual(mount_set,
                         {'/app1': trial_pub})
          
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
