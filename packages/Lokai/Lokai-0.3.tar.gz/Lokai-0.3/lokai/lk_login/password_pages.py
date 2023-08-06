# Name:      lokai/lk_login/password_pages.py
# Purpose:   Controller and views for handling password request
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

import smtplib
from smtplib import SMTPRecipientsRefused # expose this for our users

from email.mime.text import MIMEText
import os
from werkzeug import redirect

from lokai.tool_box.tb_database.orm_interface import engine
import lokai.tool_box.tb_common.configuration as config
import lokai.tool_box.tb_common.notification as notify
import lokai.tool_box.tb_common.smtp as smtp

from lokai.tool_box.tb_forms import (Form,
                               StringWidget,
                               SubmitWidget,
                               DisplayOnlyWidget)

from lokai.lk_ui import get_use_form_token
from lokai.lk_ui.ui_default.wrap_page import wrap_application
from lokai.lk_login.db_objects import User
import lokai.lk_ui
from lokai.lk_login.newpass import make_password

#-----------------------------------------------------------------------

MAIL_BODY = (
    "You requested a password when logging in to %s.\n"
    "\n"
    "Your new password is %s\n"
    "\n"
    "You may set a new password after you log in at %s.\n")
    
#-----------------------------------------------------------------------

def do_password_message(user_object, host_name, login_link):
    """ Send new password on to the user.
    """
    email_address = user_object['user_email']
    target_word = user_object['user_pword']
    from_name = 'noreply'

    msg_txt = MAIL_BODY%(host_name, target_word, login_link)
    msg = MIMEText(msg_txt)
    msg['Subject'] = "New password for %s"%host_name
    msg['To'] = email_address
    notify.info("User %s at %s has changed password"%
                (user_object['user_uname'],
                 email_address
                 ))
    smtp_server = smtp.SmtpConnection(config_section='all')
    msg['From'] = smtp_server.make_from(from_name)
    smtp_server.sendmail(from_name, [email_address], msg.as_string())
    smtp_server.quit()

#-----------------------------------------------------------------------

class PasswordPage(Form):

    def __init__(self, request, url_for):
        self.url_for = url_for
        Form.__init__(self, request, use_tokens=get_use_form_token())
        self.add_composite('1',
                           title      = 'Password Request',
                           fieldset   = {},
                           )
        one = self.get_widget('1')
        one.add(StringWidget, 'email1',
                title='Please enter an email address',
                required=True)
        one.add(StringWidget, 'email2',
                title='... and again',
                required=True)
        one.add(SubmitWidget, 'request', 'Request Password')

    def process_input(self):
        if self.has_errors():
            return False
        one = self.get_widget('1')
        email1 = one.get_widget('email1').value
        email2 = one.get_widget('email2').value
        if email1:
            email1 = email1.lower()
            email1 = email1.strip()
        if email2:
            email2 = email2.lower()
            email2 = email2.strip()
        if email1 != email2:
            one.get_widget('email1').set_error(
                "Your two email address do not match")
            return False
        equery = engine.session.query(User).filter(
            User.user_email == email1)
        eset = equery.all()
        if len(eset) == 0:
            one.get_widget('email1').set_error(
                "Your email does not match a user entry")
            return False
        if len(eset) > 1:
            one.get_widget('email1').set_error(
                "Your email matches more than one user entry")
            return False
        user_obj = eset[0]
        user_obj['user_pword'] = make_password(8)
        engine.session.add(user_obj)
        engine.session.flush
        
        # Getting links to other parts of the site like this is
        # worrysome. If someone invents an alternative login suite
        # then this url_for might return the wrong answer.
        login_link = self.request.host_url+self.url_for('login_form_display')
        do_password_message(user_obj,
                            self.request.host,
                            login_link)
        return True
           
class DonePage(Form):
    
    def __init__(self, request, url_for):
        self.url_for = url_for
        Form.__init__(self, request, use_tokens=get_use_form_token())
        self.add_composite('1',
                           title      = 'Password Request',
                           fieldset   = {},
                           )
        one = self.get_widget('1')
        one.add(DisplayOnlyWidget, 'email1',
                value = "Thank you - "
                "a new password has been sent to your email address")
        
#-----------------------------------------------------------------------

class PasswordContext(object):
    """ Set up a url_for context for the get password pages so that
        they can be used from different publishers.
    """
    def __init__(self, url_for):
        self.url_for = url_for

    def user_password(self, request):
        detail_page = PasswordPage(request, self.url_for)
        return wrap_application(request, detail_page.render())

    def user_password_done(self, request):
        detail_page = DonePage(request, self.url_for)
        return wrap_application(request, detail_page.render())

    def user_password_post(self, request):
        detail_page = PasswordPage(request, self.url_for)
        detail_page.has_errors() # to get the data from the input

        if detail_page.process_input():
            target = 'password_done'
            url_parts = {}
            qry_parts = {}
            try:
                qry_parts['up'] = request.args['up']
            except KeyError:
                pass

            return redirect(self.url_for(target))
        return wrap_application(request, detail_page.render())

#-----------------------------------------------------------------------
