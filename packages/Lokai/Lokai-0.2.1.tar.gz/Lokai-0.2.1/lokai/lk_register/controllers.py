# Name:      lokai/lk_register/controllers.py
# Purpose:   connect URL to login pages
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

import lokai.lk_ui.utils as utils
import lokai.lk_ui

from lokai.lk_login.pages import LoginContext
from lokai.lk_login.password_pages import  PasswordContext
from lokai.lk_login.user_pages import UserManageContext

from lokai.lk_register.local import expose, url_for
from lokai.lk_register.register_pages import UserRegisterContext

#-----------------------------------------------------------------------

login_context = LoginContext(url_for)
password_context = PasswordContext(url_for)
user_manage_context = UserManageContext(url_for)
user_register_context = UserRegisterContext(url_for)

@expose('/', methods=['GET'])
def login_form_display(request):
     return login_context.draw_login_form(request)

@expose('/', methods=['POST'])
def login_activate(request):
    return login_context.process_login_form(request)

@expose('/logout')
def logout(request):
    return login_context.process_logout(request)

@expose('/confirm')
def confirm(request):
    return login_context.draw_confirmed_form(request)

@expose('/new_password', methods=['GET'])
def new_password(request):
     return password_context.user_password(request)

@expose('/new_password', methods=['POST'])
def password_post_form(request):
     return password_context.user_password_post(request)

@expose('/password_done', methods=['GET'])
def password_done(request):
     return password_context.user_password_done(request)

@expose('/manage',  methods=['GET'])
def edit_user(request):
     return user_manage_context.user_edit(request)

@expose('/manage',  methods=['POST'])
def post_user(request):
     return user_manage_context.user_edit_post(request)

@expose('/register',  methods=['GET'])
def add_user(request):
    return user_register_context.user_register_get(request)

@expose('/register',  methods=['POST'])
def add_user_post(request):
    return user_register_context.user_register_post(request)

#-----------------------------------------------------------------------
