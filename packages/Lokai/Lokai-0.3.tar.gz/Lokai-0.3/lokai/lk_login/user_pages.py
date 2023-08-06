# Name:      lokai/lk_login/user_pages.py
# Purpose:   Controller and views for handling account details
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

import re
from werkzeug import redirect

from lokai.tool_box.tb_database.orm_access import get_row
from lokai.tool_box.tb_forms import (Form,
                               StringWidget,
                               SubmitWidget,
                               PasswordWidget,
                               DisplayOnlyWidget,
                               HiddenWidget,)
from lokai.lk_worker.ui.widget import HtmlWidget

from lokai.lk_ui import get_use_form_token
from lokai.lk_ui.ui_default.wrap_page import wrap_application
import lokai.lk_ui
from lokai.lk_login.db_objects import User
from lokai.lk_login.user_model import (validate_email,
                                       validate_lname,
                                       make_user_uname,
                                       user_view_store)

#-----------------------------------------------------------------------

def user_view_form(form, container, request, new_user=False):
    if request.user or new_user:
        readonly = not form.can_login_edit
        form.add_hidden('user_uname', request.user)
        container.add(StringWidget, 'email',
                      title='Your email address',
                      readonly=readonly)
        container.add(DisplayOnlyWidget, 'uname_display',
                      title='Your User ID',
                      readonly=readonly)
        container.add(StringWidget, 'long_name',
                      title='Your name for display',
                      required=True,
                      readonly=readonly)
        if form.can_login_edit:
            container.add(PasswordWidget, 'password1',
                          title='Password',
                          readonly=readonly)
            container.add(PasswordWidget, 'password2',
                          title='... and again',
                          readonly=readonly)
    else:
        container.add(HtmlWidget, 'no_user',
                title=(
                    "<p>You are not logged in.</p>"
                    "<p>Please use the menu to log in and then try again.</p>")
                )

def user_view_build(form, container, request, new_user=False):
    if not form.request.user or new_user:
        return
    ux_return = get_row(User, {'user_uname': form.request.user})
    if not ux_return:
        return
    ux = ux_return[0]
    form.get_widget('user_uname').set_value(ux.user_uname)
    container.get_widget('email').set_value(ux.user_email)
    container.get_widget('uname_display').set_value(ux.user_uname)
    container.get_widget('long_name').set_value(ux.user_lname)

def user_view_validate(form, container, request, new_user=False):
    if not form.can_login_edit:
        return 1, {}
        #>>>>>>>>>>>>>>>>>>>>
    error_count = 0
    if form.has_errors():
        error_count += 1
    if not new_user:
        user_uname = form.get_widget('user_uname').value
    else:
        user_uname = make_user_uname()
    if not form.request.user and not new_user:
        container.get_widget('email').set_error(
            "You are not logged in")
        return 1, {}
        #>>>>>>>>>>>>>>>>>>>>
    if not new_user and user_uname != form.request.user:
        container.get_widget('email').set_error(
            "Your login does not match the data.")
        return 1, {}
        #>>>>>>>>>>>>>>>>>>>>
    pwd1 = container.get_widget('password1').value
    pwd2 = container.get_widget('password2').value
    pwd1 = '' if pwd1 is None else pwd1.strip()
    pwd2 = '' if pwd2 is None else pwd2.strip()
    if pwd1 != pwd2:
        container.get_widget('password1').set_error(
            "Your two passwords do not match")
        error_count += 1
    if new_user and not pwd1:
        container.get_widget('password1').set_error(
            "You must enter a password")
        error_count += 1
    email = container.get_widget('email').value
    if email:
        email = email.lower()
    ec, em = validate_email(email, user_uname)
    if ec:
        container.get_widget('email').set_error(em)
        error_count += ec
    if not email:
        container.get_widget('email').set_error(
            "An email address is required.")
        error_count += 1
    lname = container.get_widget('long_name').value
    ec, em = validate_lname(lname)
    if ec:
        container.get_widget('long_name').set_error(em)
        error_count += ec

    record = {}
    if error_count == 0:
        record = {'user_uname': user_uname,
                  'user_lname': lname,
                  'user_email': email
                  }
        if pwd1:
            record['user_pword'] = pwd1.replace('|', '#')
    return error_count, record

#-----------------------------------------------------------------------
class EditUser(Form):

    def __init__(self, request, new_user=False):
        Form.__init__(self, request, use_tokens=get_use_form_token())
        self.new_user = new_user
        self.can_login_edit = True
        self.add_composite('user_main',
                           title = 'User Profile',
                           fieldset   = {},
                           )
        container = self.get_widget('user_main')
        user_view_form(self, container, self.request)
        if request.user:
            container.add(SubmitWidget, 'update', 'Update')
        
    def build_data(self):
        container = self.get_widget('user_main')
        user_view_build(self, container, self.request, new_user=self.new_user)
        
    def process_input(self):
        container = self.get_widget('user_main')
        self.error_count, record = user_view_validate(self,
                                                      container, self.request,
                                                      new_user=self.new_user)
        if self.error_count:
            return False
        return user_view_store(record, new_user=self.new_user)

#-----------------------------------------------------------------------

class UserManageContext(object):
    """ Set up a url_for context for the user self-manage pages so
        that they can be used from different publishers.
    """
    def __init__(self, url_for):
        self.url_for = url_for

    def user_edit(self, request, new_user=False):
        detail_page = EditUser(request, new_user)
        detail_page.build_data()
        return wrap_application(request, detail_page.render())

    def user_edit_post(self, request, new_user=False):
        detail_page = EditUser(request, new_user)
        detail_page.has_errors() # to get the data from the input

        if detail_page.process_input() and detail_page.error_count == 0:
            target = 'edit_user'
            return redirect(self.url_for(target))
        return wrap_application(request, detail_page.render())

#-----------------------------------------------------------------------
