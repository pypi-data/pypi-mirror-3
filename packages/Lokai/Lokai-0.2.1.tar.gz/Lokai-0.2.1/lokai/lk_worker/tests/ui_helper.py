# Name:      lokai/lk_worker/tests/ui_helper.py
# Purpose:   Support basic login for testing UI aspects.
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

from werkzeug import Client, BaseResponse
from BeautifulSoup import BeautifulSoup

from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_ui import set_use_form_token
from lokai.lk_ui.publisher import build_skin
import lokai.lk_ui

from lokai.lk_login.db_objects import (User,
                                       Function,
                                       RoleFunction,
                                       Role,
                                       UserRole,
                                       )

from lokai.lk_worker.tests.helpers import delete_table_content

from lokai.lk_ui.publisher import make_app

#-----------------------------------------------------------------------

class LoginFailure(Exception):

    pass

#-----------------------------------------------------------------------

def delete_user_table_content():
    delete_table_content( [RoleFunction,
                           UserRole,
                           User,
                           Function,
                           Role,
                           ]
                          )

#-----------------------------------------------------------------------

def make_a_user(uname, password, lname):
    u = User()
    u.user_uname = uname
    u.user_pword = password
    u.user_lname = lname
    engine.session.add(u)
    engine.session.commit()

    v = UserRole()
    v.user_idx = engine.session.query(User).filter(
        User.user_uname == uname).one().user_idx
    v.role_idx = engine.session.query(Role).filter(
        Role.role_text == 'sys admin').one().role_idx
    v.role_scope = 'site'
    engine.session.add(v)
    engine.session.commit()

#-----------------------------------------------------------------------

def make_basic_roles():
    for fcn_idx, fcn_text in [('nde_tasks', 'Node management'),
                               ('nde_search_full', 'Allow search')
                              ]:
        x = Function()
        x.fcn_idx = fcn_idx
        x.fcn_text = fcn_text
        engine.session.add(x)
    y = Role()
    y.role_text = 'sys admin'
    engine.session.add(y)
    engine.session.commit()
    
    role_idx = engine.session.query(Role).filter(
        Role.role_text == 'sys admin').one().role_idx
    for fcn_idx in ['nde_tasks', 'nde_search_full']:
        z = RoleFunction()
        z.role_idx = role_idx
        z.fcn_idx = fcn_idx
        z.permit = 15
        engine.session.add(z)
    engine.session.commit()

#-----------------------------------------------------------------------

def basic_login(user, password, longname):
    """ Returns a test web application that is already logged in.

        If user details are not given, a set of defaults are created.
    """

    if not lokai.lk_ui.StaticPath:
        set_use_form_token(False)

    if not user:
        make_basic_roles()
        user = 'blue-bottle'
        password = 'bottle-brush'
        longname = 'Not A Firkin'
        make_a_user(user, password, longname)

    
    test_app = Client(make_app(), BaseResponse)

    res = test_app.get('/login')
    if res.status_code != 200:
        raise LoginFailure, ("Request login page - expect status 200"
                             " - find %d"%res.status_code)
    res = test_app.post('/login', data={'1___username': user,
                                   '1___password': password,
                                   '1___login'   : 'login'})
    #
    if res.status_code == 200:
            html_doc = BeautifulSoup(res.data)
            err_set = html_doc.findAll('span', {'class': 'lokai_error'})
            err_text = ''
            for e in err_set:
                if e.string:
                    err_text += e.string.strip()
            if err_text != '':
                raise LoginFailure, err_text
    else:
        if res.status_code != 302:
            raise LoginFailure, ("Request login page - expect status 302"
                                 " - find %d"%res.status_code)
    return test_app

#-----------------------------------------------------------------------

def pack(response):
    return '\n'.join([ln for ln in response.response])

def check_errors(html):
    any_error = html.findAll(attrs={'class': 'lokai_error'})
    messages = []
    for e in any_error:
        if e.string:
            messages.append(e.string)
    return messages

#-----------------------------------------------------------------------
