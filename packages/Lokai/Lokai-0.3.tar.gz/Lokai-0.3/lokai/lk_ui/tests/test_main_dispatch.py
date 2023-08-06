# Name:      lokai/lk_ui/tests/test_main_dispatch.py
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
from werkzeug import Client, BaseResponse

from lokai.tool_box.tb_common.configuration import (set_global_config_file,
                                              clear_global_config)

import lokai.lk_ui
import lokai.lk_ui.ui_default.default_publisher
from lokai.lk_ui.publisher import get_lokai_consolidating_publisher

#-----------------------------------------------------------------------

def pack(response):
    return '\n'.join([ln for ln in response.response])


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
        lokai.lk_ui.ui_default.default_publisher.DefaultPath = None
    
    #-------------------------------------------------------------------
    
    def tearDown( self ):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : execute a trial application
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
            "application_path = mnt\n"
            "[other]\n"
            "not_used = xxx\n"
            )
        set_global_config_file(StringIO.StringIO(config))
        test_app = Client(get_lokai_consolidating_publisher(), BaseResponse)
        res = test_app.get('/mnt/app1')
        self.assertEqual(res.status_code, 200)
        html = pack(res)
        self.assert_('Lokai test page' in html )

    #-------------------------------------------------------------------

    def test_t002(self):
        """ test_t002 : trigger default application
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
            "application_path = mnt\n"
            "[other]\n"
            "not_used = xxx\n"
            )
        set_global_config_file(StringIO.StringIO(config))
        test_app = Client(get_lokai_consolidating_publisher(), BaseResponse)
        res = test_app.get('/app2')
        self.assertEqual(res.status_code, 404)

    #-------------------------------------------------------------------

    def test_t003(self):
        """ test_t003 : Only one default allowed
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
            "application_path = \n"
            "[other]\n"
            "not_used = xxx\n"
            )
        set_global_config_file(StringIO.StringIO(config))
        self.assertRaises(ValueError, get_lokai_consolidating_publisher)
        
    def test_t004(self):
        """ test_t004 : demonstrate empty path
        """
        config = (
            "[all]\n"
            "not_used = xxx\n"
            "[skin]\n"
            "ignore_this = xxx\n"
            "[default]\n"
            "# Provide a default for when the url is not matched\n"
            "application_publisher = lokai.lk_ui.ui_default.default_publisher.get_default_publisher\n"
            "default_path = leader/MyPage\n"
            "[app1]\n"
            "application_publisher = lokai.lk_ui.tests.trial_publisher.get_trial_publisher\n"
            "application_path = something_else\n"
            "[other]\n"
            "not_used = xxx\n"
            )
        set_global_config_file(StringIO.StringIO(config))
        test_app = Client(get_lokai_consolidating_publisher(), BaseResponse)
        res = test_app.get('')
        self.assertEqual(res.status_code, 301)
        self.assertEqual(res.headers['location'],
                         'http://localhost/leader/MyPage')

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
