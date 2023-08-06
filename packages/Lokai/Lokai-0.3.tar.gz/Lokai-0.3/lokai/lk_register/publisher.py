# Name:      lokai/lk_register/publisher.py
# Purpose:   Publish login pages that allow users to register
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

from werkzeug import SharedDataMiddleware

import lokai.lk_ui
from lokai.lk_ui.base_publisher import BasePublisher

import lokai.lk_register.controllers as controllers
from lokai.lk_register.local import url_for, get_adapter, local, local_manager

#-----------------------------------------------------------------------

class lkLogin(BasePublisher):

    """ Login application -

        Display the login form

        Respond to the POST

    """
    pass

#-----------------------------------------------------------------------

""" The login publisher is wrapped in a shared data middleware so that
    '/static' is recognised when this is run stand alone. The
    consolidating publisher also uses the same wrapping, so that,
    under deployment conditions, the '/static' url is handled at the
    higher level.
"""
def get_lk_login_publisher():
    return SharedDataMiddleware(
        lkLogin(controllers, get_adapter, local, local_manager),
        {'/static': lokai.lk_ui.StaticPath})

#-----------------------------------------------------------------------

def menu_builder(request):
    """ Build a menu for logging in and out
    """
    if request.user:
        return [{
            'title': '',
            'children': [{'title': 'Logout',
                 'link': url_for('logout')},
                {'title': 'User Profile',
                 'link': url_for('edit_user')}]
            }]
    else:
        return [{
            'title': '',
            'children': [{'title': 'Login',
                 'link': url_for('login_form_display')},
                {'title': 'Register',
                 'link': url_for('add_user')}]}]

#-----------------------------------------------------------------------

if __name__ == '__main__':
    from werkzeug import run_simple

    from lokai.tool_box.tb_common.configuration import handle_ini_declaration
    handle_ini_declaration(prefix='lk')
    
    from lokai.lk_worker.models import model
    model.init()

    from lokai.lk_ui.publisher import build_skin
    build_skin()
    
    def make_app():
        return get_lk_login_publisher()

    run_simple('localhost', 5000, make_app(), use_relaoder=True, processes=2)

#-----------------------------------------------------------------------
