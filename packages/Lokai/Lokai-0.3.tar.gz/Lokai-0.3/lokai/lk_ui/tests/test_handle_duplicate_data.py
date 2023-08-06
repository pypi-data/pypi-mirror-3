# Name:      lokai/lk_ui/tests/test_handle_duplicate_data.py
# Purpose:   Testing publisher response retry on duplicate data values
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

from mock import patch
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from werkzeug import (
    Client,
    BaseResponse,
    Response,
    Local,
    LocalManager,
    )
from werkzeug.routing import Map, Rule

from lokai.tool_box.tb_common.configuration import (
    set_global_config_file,
    clear_global_config,
    )

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.lk_login.db_objects import (
    model,
    User,
    Role,
    Function,
    RoleFunction,
    UserRole,
    )
from lokai.lk_ui.base_publisher import BasePublisher

#-----------------------------------------------------------------------

loop_number = 0
def action_function(request):
    """ This is going to handle the request

        The code always tries to store the value from loop_number. If
        the tester resets this to zero before consecutive calls to the
        publisher then there will always be a duplicate key error on
        the second such call. The publisher should retry, up to some
        maximum, and loop_counter will be incremented. At some point
        the loop_counter value will exceed the value reached by the
        previous call and success and calmness will ensue.
    """
    global loop_number
    loop_number += 1
    obj = User()
    obj.user_uname = '%d' % loop_number
    engine.session.add(obj)
    engine.session.flush()
    return Response('got here')

#-----------------------------------------------------------------------
local = Local()
local_manager = LocalManager([local])

url_map = Map()
url_adapter = None

def get_adapter():
    global url_adapter
    if not url_adapter:
        global APPLICATION_PATH
        APPLICATION_PATH = '/'
        APPLICATION_SCHEME = 'http'
        url_adapter = url_map.bind('',
                                   APPLICATION_PATH,
                                   None,
                                   APPLICATION_SCHEME,
                                   )
    return url_adapter

class HandlerMap(object):
    """ An empty class that can have functions added as attributes.

        Adding a function reference as an attribute makes an unbound
        reference, so it acts the same way as a module for our
        purposes.
    """
    pass

handler_map = HandlerMap()

url_map.add(Rule('/action', endpoint='action_function'))

setattr(handler_map, 'action_function', action_function)

#-----------------------------------------------------------------------

def delete_table_content(table_set=None):
    if not table_set:
        table_set = []
    for t in table_set:
        obj = t()
        table = obj.get_mapped_table()
        engine.session.execute(delete(table))
        if hasattr(t, 'set_sequence'):
            t().set_sequence(1)
    engine.session.commit()
    engine.session.expunge_all()

#-----------------------------------------------------------------------
def setup_module():
    pass

def teardown_module():
    pass

#-----------------------------------------------------------------------

config = (
    "[all]\n"
    "not_used=xxx\n"
    "[login]\n"
    "login_db.url = postgresql:///unit_lokai\n"
    "login_db.convert_unicode = True\n"
    )
#-----------------------------------------------------------------------

class TestObject( unittest.TestCase ):

    def setUp( self ):
        clear_global_config()
        set_global_config_file(StringIO.StringIO(config))
        model.init()
        delete_table_content([UserRole, RoleFunction, Role, Function, User])

    #-------------------------------------------------------------------
    
    def tearDown( self ):
        pass

    #-------------------------------------------------------------------

    @patch('lokai.lk_ui.base_publisher.notify')
    @patch('lokai.lk_ui.base_publisher.render_template')
    @patch('lokai.lk_ui.base_publisher.render_error')
    def test_t001(self, *args):
        """ test_t001 : execute a trial application
        """
        test_app = Client(
            BasePublisher(
                handler_map,
                get_adapter,
                local,
                local_manager,
                ),
            BaseResponse)
        global loop_number
        loop_number = 0
        res = test_app.post('/action', data={'n':1})
        loop_number = 0
        res = test_app.post('/action', data={'n':2})
        loop_number = 0
        res = test_app.post('/action', data={'n':3})
        loop_number = 0
        res = test_app.post('/action', data={'n':4})
        loop_number = 0
        res = test_app.post('/action', data={'n':5})
        loop_number = 0
        res = test_app.post('/action', data={'n':6})
        loop_number = 0
        res = test_app.post('/action', data={'n':7})
        loop_number = 0
        res = test_app.post('/action', data={'n':8})
        loop_number = 0
        res = test_app.post('/action', data={'n':9})
        self.assertEqual(res.status_code, 200)
        loop_number = 0
        res = test_app.post('/action', data={'n':10})
        self.assertEqual(res.status_code, 200)
        loop_number = 0
        res = test_app.post('/action', data={'n':11})
        self.assertEqual(res.status_code, 400)
        
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
