# Name:      lokai/lk_register/register_pages.py
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

import lokai.tool_box.tb_common.notification as notify
from lokai.tool_box.tb_database.orm_interface import engine
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
from lokai.lk_login.password_pages import (do_password_message,
                                           SMTPRecipientsRefused)

from lokai.lk_register.newpass import make_password
from lokai.lk_register.register_action import user_register_action

#-----------------------------------------------------------------------

def user_view_form(form, container, request):
    if not request.user: # Not allowed to be logged in
        readonly = not form.can_login_edit
        container.add(
            HtmlWidget, 'user_msg',
            title=(
                "<p>Please enter an email and a long name.</p>"
                "<p>The email will become your log-in identity, "
                "and we will use your long name to display on "
                "the site pages.</p>"
                "<p>When you submit these details we will email you with a "
                "password and you can then log in.</p>"
                )
            )
        container.add(StringWidget, 'email',
                      title='Your email address',
                      readonly=readonly)
        container.add(StringWidget, 'email2',
            title='... and email again, please',
            required=True)
        container.add(StringWidget, 'long_name',
                      title='Your name for display',
                      required=True,
                      readonly=readonly)
        container.add(SubmitWidget, 'update',
                      title='',
                      value='Update',
                      readonly=readonly)
    else:
        container.add(HtmlWidget, 'no_user',
                      title=(
                          "<p>You are logged in already.</p>"
                          )
                      )

def user_view_validate(form, container, request):
    if not form.can_login_edit:
        return 1, {}
        #>>>>>>>>>>>>>>>>>>>>
    error_count = 0
    if form.has_errors():
        error_count += 1
    if form.request.user:
        return 1, {}
        #>>>>>>>>>>>>>>>>>>>>
    email = container.get_widget('email').value
    if email:
        email = email.lower()
    ec, em = validate_email(email)
    if ec:
        container.get_widget('email').set_error(em)
        error_count += ec
    if not email:
        container.get_widget('email').set_error(
            "An email address is required.")
        error_count += 1
    email2 = container.get_widget('email2').value
    if email2:
        email2=email2.lower()
    if email2 != email:
        container.get_widget('email').set_error(
            "Your two email addresses do not match.")
        self.error_count += 1
    lname = container.get_widget('long_name').value
    ec, em = validate_lname(lname)
    if ec:
        container.get_widget('long_name').set_error(em)
        error_count += ec

    record = {}
    if error_count == 0:
        user_uname = make_user_uname()
        user_pword = make_password(8)
        form.new_obj = {'user_uname': user_uname,
                        'user_lname': lname,
                        'user_email': email,
                        'user_pword': user_pword,
                        }

    return error_count

#-----------------------------------------------------------------------
class EditUser(Form):

    def __init__(self, request):
        Form.__init__(self, request, use_tokens=get_use_form_token(),
                      )
        self.can_login_edit = True
        self.add_composite('user_main',
                           title = 'User Profile',
                           fieldset   = {},
                           )
        container = self.get_widget('user_main')
        user_view_form(self, container, self.request)
        if request.user:
            container.add(SubmitWidget, 'update', 'Update')
        
    def process_input(self):
        container = self.get_widget('user_main')
        self.error_count = user_view_validate(self,
                                                      container, self.request)
        if self.error_count:
            return False
        user_view_store(self.new_obj, new_user=True)
        return user_register_action(self.new_obj)
        
#-----------------------------------------------------------------------

class UserRegisterContext(object):
    """ Set up a url_for context for the user self-manage pages so
        that they can be used from different publishers.
    """
    def __init__(self, url_for):
        self.url_for = url_for

    def user_register_get(self, request):
        detail_page = EditUser(request)
        return wrap_application(request, detail_page.render())

    def user_register_post(self, request):
        detail_page = EditUser(request)
        detail_page.has_errors() # to get the data from the input

        if detail_page.process_input() and detail_page.error_count == 0:
            #
            # Send an email
            login_link = request.host_url+self.url_for('login_form_display')
            try:
                do_password_message(detail_page.new_obj,
                                    request.host,
                                    login_link)
                # Now go report done
                target = 'password_done'
                return redirect(self.url_for(target))
            except SMTPRecipientsRefused, e:
                # Oops - possible invalid email address
                # Introspect the display object and go back to the user
                engine.session.rollback()
                notify.warn("SMTPRecipientsRefused: %s"%str(e))
                container = detail_page.get_widget('user_main')
                container.get_widget('email').set_error(
                    "There was a problem sending you a password. Is your "
                    "email addres valid?")
                # Drop out to return the form to the user
        return wrap_application(request, detail_page.render())

#-----------------------------------------------------------------------
