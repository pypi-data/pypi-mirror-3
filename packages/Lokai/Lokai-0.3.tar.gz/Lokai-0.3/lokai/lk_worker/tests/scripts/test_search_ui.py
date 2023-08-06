# Name:      lokai/lk_worker/tests/scripts/test_search_ui.py
# Purpose:   Test aspects of the search form
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
import re

from BeautifulSoup import BeautifulSoup

from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_worker.tests.structure_helper import make_initial_nodes_and_users
from lokai.lk_worker.tests.helpers import (
    module_ui_initialise,
    module_close,
    delete_worker_table_content
    )

from lokai.lk_worker.nodes.search import find_in_path

from lokai.lk_worker.tests.ui_helper import (
    basic_login,
    delete_user_table_content,
    check_errors,
    )

#-----------------------------------------------------------------------

setup_module = module_ui_initialise
teardown_module = module_close

#-----------------------------------------------------------------------

def pack(response):
    return '\n'.join([ln for ln in response.response])

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        delete_worker_table_content()
        delete_user_table_content()
        make_initial_nodes_and_users()
        
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t101(self):
        """ test_t101 : error response to date fields
        """
        test_app = basic_login('fred_1', 'useless', 'Fred Manager')
        #
        # fred_1 is allocated as a manager against Lokai
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]

        query_set = {"search___activity___bf_range___bf_range_from":'2010-03-16',
                     "search___activity___bf_range___bf_range_to":'2010-03-15'
                     }
        res = test_app.post(str('/pages/%s/search'%nde_idx), data=query_set)
        self.assertEqual(res.status_code, 200)
        html = BeautifulSoup(pack(res))
        err_set = html.findAll('span', {'class': 'lokai_error'})
        err_text = ''
        for e in err_set:
            if e.string:
                err_text += e.string.strip()
        self.assert_('From date should be less than to date' in err_text,
                     "Error text is %s"%err_text)

        query_set = {"search___activity___bf_range___bf_range_from":'2010-03-54',
                     "search___activity___bf_range___bf_range_to":'2010-03-15'
                     }
        res = test_app.post(str('/pages/%s/search'%nde_idx), data=query_set)
        self.assertEqual(res.status_code, 200)
        html = BeautifulSoup(pack(res))
        err_set = html.findAll('span', {'class': 'lokai_error'})
        err_text = ''
        for e in err_set:
            if e.string:
                err_text += e.string.strip()
        self.assert_('2010-03-54 has too many days for the month' in
                     err_text,
                     "Error text is %s"%err_text)

        query_set = {"search___activity___bf_range___bf_range_from":'2010-03-16',
                     "search___activity___bf_range___bf_range_to":'2010-03-99'
                     }
        res = test_app.post(str('/pages/%s/search'%nde_idx), data=query_set)
        self.assertEqual(res.status_code, 200)
        html = BeautifulSoup(pack(res))
        err_set = html.findAll('span', {'class': 'lokai_error'})
        err_text = ''
        for e in err_set:
            if e.string:
                err_text += e.string.strip()
        self.assert_('2010-03-99 has too many days for the month' in
                     err_text,
                     "Error text is %s"%err_text)

        query_set = {"search___activity___bf_range___bf_range_from":'0987654321',
                     "search___activity___bf_range___bf_range_to":'2010-03-15'
                     }
        res = test_app.post(str('/pages/%s/search'%nde_idx), data=query_set)
        self.assertEqual(res.status_code, 200)
        html = BeautifulSoup(pack(res))
        messages = check_errors(html)
        err_text = ''
        for e in messages:
            if e.string:
                err_text += e.strip()
        self.assert_('0987654321 is not a valid date' in
                     err_text,
                     "Error text is %s"%err_text)

        query_set = {"search___activity___bf_range___bf_range_from":'2010-03-16',
                     "search___activity___bf_range___bf_range_to":'1234567890'
                     }
        res = test_app.post(str('/pages/%s/search'%nde_idx), data=query_set)
        self.assertEqual(res.status_code, 200)
        html = BeautifulSoup(pack(res))
        messages = check_errors(html)
        err_text = ''
        for e in messages:
            if e.string:
                err_text += e.strip()
        self.assert_('1234567890 is not a valid date' in
                     err_text,
                     "Error text is %s"%err_text)

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
