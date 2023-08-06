# Name:      lokai/lk_login/pages.py
# Purpose:   Form processing for login
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

from sqlalchemy.sql import or_
from werkzeug import redirect, html

import lokai.tool_box.tb_common.notification as notify
import lokai.tool_box.tb_common.dates as dates

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_forms import (Form,
                               StringWidget,
                               PasswordWidget,
                               SubmitWidget,
                               )
from lokai.tool_box.tb_forms.widget import Widget

from lokai.lk_ui import get_use_form_token
from lokai.lk_ui.ui_default.wrap_page import wrap_application
from lokai.lk_login.db_objects import User, Organisation

#-----------------------------------------------------------------------

from werkzeug import html

class LoginLinkWidget(Widget):

    def __init__(self, name, value=None, **kwargs):
        self.url_for = kwargs.get('url_for')
        Widget.__init__(self, name, value=value, **kwargs)
        # It is possible we don't know the target when creating the
        # form.  Allow the user to set these attributes later, when
        # some data has been read.
        self.target = kwargs.get('target')
        given_url_parts = kwargs.get('url_parts', {})
        given_query = kwargs.get('query', {})
        self.url_parts = {}
        self.url_parts.update(given_url_parts)
        self.url_parts.update(given_query)
        self._parsed = True

    def get_parts(self):
        """ Return the elements of the widget for posting into a template """
        return {'path': self.url_for(self.target, self.url_parts),
                'value': self.value,
                'class': 'LinkWidget'
                }

    def make_href(self):
        if self.attrs.has_key('disabled'):
            return self.value
        else:
            path = self.url_for(self.target, self.url_parts)
            return html.a(self.value,
                          **{'class': 'LinkWidget',
                             'href': path})

    def render_content(self):
        return self.make_href()

#-----------------------------------------------------------------------

def getorganisationname(oid):
    org = engine.session.query(Organisation).filter_by(org_idx=oid).first()
    if org:
        return org['org_name']
    return None

def test_login(request, username, password):
    """ Check that the given <username>, <password> pair exists in the
        database.

        Return user name id all OK. None otherwise.
    """
    if username:
        user = engine.session.query(
            User
            ).filter(
            or_((User.user_uname==username),
                (User.user_email==username.lower())
                )).first()
    else:
        user = None
    if user:
        # We also expect a password field
        if user.isPassword(password.replace('|', '#')):
            request.user = user.user_uname # This is the important part.
            # print "Logged in as", ux['user_lname']
            return user
    return None

def set_user_session(request, ux):
    username = ux.get('user_lname', ux.get('user_uname', None))
    orgname = None
    try:
        orgname = getorganisationname(ux['org_idx'])
    except:
        pass
    request.client_session = request.client_session
    request.client_session['ident'] = {
        'user long name'    : username,
        'organisation name' : orgname}

#-----------------------------------------------------------------------

class LoginContext(object):
    """ Set up a url_for context for the login/logout pages so that
        they can be used from different publishers.
    """
    def __init__(self, url_for):
        self.url_for = url_for

    def getloginform(self, request, disabled=False):
        """ Define a user login form

            Return the form object
        """
        form = Form(request, use_tokens=get_use_form_token(),
                    action=self.url_for('login_activate'))
        possible_return = request.args.get('return', '')
        form.add_hidden('return_target', value=possible_return)
        form.add_composite('1',
                          title      = 'Log In',
                          fieldset   = {},
                          )
        one = form.get_widget('1')
        one.add(StringWidget, 'username', title='Username',
                required=True, disabled=disabled)
        one.add(PasswordWidget, 'password', title='Password',
                required=True, disabled=disabled)
        if disabled:
            one.add(LoginLinkWidget, 'logout',
                    value='Logout',
                    title='',
                    target='logout',
                    url_for=self.url_for)
        else:
            one.add(SubmitWidget, 'login', 'Login')
        one.add(LoginLinkWidget, 'new_password',
                value='Click here',
                title='Forgotten your password?',
                target='new_password',
                url_for=self.url_for)

        return form

    #-----------------------------------------------------------------------

    def draw_login_form(self, request):
        form = self.getloginform(request)
        loggedin = False
        if request.user:
            loggedin = True
        title = ''
        main_content = ''
        if loggedin:
            back_link = form.get_widget('return_target').value
            if not back_link:
                back_link = self.url_for('confirm')
            return redirect(back_link)
        else:
            return wrap_application(request, form.render())

    #-----------------------------------------------------------------------

    def draw_confirmed_form(self, request):
        form = self.getloginform(request, disabled=True)
        one = form.get_widget('1')
        user_wdg = one.get_widget('username')
        if request.user:
            message = 'Is logged in'
            user_wdg.set_value(request.user)
        else:
            message = 'No-one is logged-in'
        user_wdg.set_error(message)
        return wrap_application(request, form.render())

    #-------------------------------------------------------------------

    def process_login_form(self, request):
        form = self.getloginform(request)
        loggedin = False
        if request.user:
            loggedin = True
        elif form.is_submitted() and not form.has_errors():
            # Try to log in.
            one = form.get_widget('1')
            usr = test_login(request,
                             one.get_widget('username').value, 
                             one.get_widget('password').value)
            if not usr:
                one.get_widget('username').set_error('Invalid username/password')
                notify.info("Login failed for %s from %s at %s"%(
                    one.get_widget('username').value,
                    request.referrer,
                    dates.timetostr(dates.now())))
            else:
                loggedin = True
                set_user_session(request, usr)
                notify.info("User %s logged in from %s at %s"%(
                    usr.user_uname,
                    request.referrer,
                    dates.timetostr(dates.now())))
        if loggedin:
            back_link = form.get_widget('return_target').value
            if not back_link:
                back_link = '/'
            return redirect(back_link)
        return wrap_application(request, form.render())

    #-------------------------------------------------------------------

    def process_logout(self, request):
        if request.user:
            session = request.client_session
            session['user'] = None
            try:
                del session['ident']
            except KeyError:
                pass
            notify.info("User %s logged out from %s at %s"%(
                request.user,
                request.referrer,
                dates.timetostr(dates.now())))
        return redirect('/')

    #-------------------------------------------------------------------
