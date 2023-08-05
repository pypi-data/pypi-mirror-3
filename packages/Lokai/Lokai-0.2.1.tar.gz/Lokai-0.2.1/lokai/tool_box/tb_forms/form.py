# Name:      lokai/tool_box/tb_forms/form.py
# Purpose:   Provide basic form manipulation.
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

# based on:
# """$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/quixote/form/form.py $
# $Id: form.py, v 1.14 2007/01/31 09:46:59 mark Exp $
#
# Provides the Form class and related classes.  Forms are a convenient
# way of building HTML forms that are composed of Widget objects.
#
#-----------------------------------------------------------------------

# This software is derived from the Quixote package and modified: to
# work with werkzeug; to use a different rendering process; and
# generally to perform in the Lokai tool box environment.

# The following is a copy of the license used in Quixote 2.7

#-----------------------------------------------------------------------
# This version of Quixote is derived from Quixote 2.4, released by CNRI.
# See doc/LICENSE_24.txt for the licensing terms of that release. Changes
# made since that release are summarized in the CHANGES.txt file along
# with a list of authors. Those changes are made available under the
# following terms (commonly known as the MIT/X license).

# Copyright (c) the Quixote developers

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#-----------------------------------------------------------------------


from werkzeug import html

from lokai.tool_box.tb_common.random import randbytes

from lokai.tool_box.tb_forms.widget import (
    HiddenWidget, StringWidget, TextWidget,
    CheckboxWidget, SingleSelectWidget, RadiobuttonsWidget,
    MultipleSelectWidget, ResetWidget, SubmitWidget, FloatWidget,
    IntWidget, PasswordWidget, DateWidget, CalendarWidget, FileWidget,
    PlainTextWidget, DateTimeWidget,
    CompositeWidget)

#-----------------------------------------------------------------------
#Form token methods.

MAX_FORM_TOKENS = 16

def create_form_token(request):
    """() -> string

    Create a new form token and add it to a queue of outstanding form
    tokens for this session.  A maximum of MAX_FORM_TOKENS are saved.
    The new token is returned.
    """
    # The strange pattern of getting a reference to _form_tokens and
    # then putting that reference back is there to ensure that the
    # session sees the list as having been modified!
    token = randbytes(8)
    form_tokens = request._form_tokens
    form_tokens.append(token)
    extra = len(request._form_tokens) - request.MAX_FORM_TOKENS
    if extra > 0:
        del form_tokens[:extra]
    request._form_tokens = form_tokens
    return token

def has_form_token(request, token):
    """(token : string) -> boolean

    Return true if 'token' is in the queue of outstanding tokens.
    """
    if request._form_tokens:
        return token in request._form_tokens
    return False

def remove_form_token(request, token):
    """(token : string)

    Remove 'token' from the queue of outstanding tokens.
    """
    request._form_tokens.remove(token)

#-----------------------------------------------------------------------

class FormTokenWidget(HiddenWidget):
    """ This widget is automatically created if 'use_tokens is set for
        a form instance.

        The idea is that a token is inserted into the form as a hidden
        field and the same token value is stored in the session. When
        the form is submitted the hidden field is compare with the
        session version. If they do not match the form is considered
        to be invalid.

        More then one form can be active at one time, up to a maximum
        of MAX_FORM_TOKENS.

        It is up to the application to respond to this in a sensible
        way. Arbitrarily clearing all errors is not a good approach
        when using this mechanism.

        The mechanism also requires an environment that supports a
        session. The request must have a _form_tokens attribute that
        is a list of tokens. If that environment is not present then
        the form token mechanism is not activated.
    """

    def _parse(self, request):
        token = request.form.get(self.name)
        if not has_form_token(request, token):
            self.error = 'invalid' # this error does not get displayed
        else:
            remove_form_token(request, token)

    def render_error(self, error):
        return ''

    def render(self):
        self.value = create_form_token(self.form_obj.request)
        return HiddenWidget.render(self)

#-----------------------------------------------------------------------

class Form(object):
    """
    Provides a high-level mechanism for collecting and processing user
    input that is based on HTML forms.

    Instance attributes:
      widgets : [Widget]
        widgets that are not subclasses of SubmitWidget or HiddenWidget
      submit_widgets : [SubmitWidget]
        subclasses of SubmitWidget, normally rendered at the end of the
        form
      hidden_widgets : [HiddenWidget]
        subclasses of HiddenWidget, normally rendered at the beginning
        of the form
      _names : { name:string : Widget }
        names used in the form and the widgets associated with them
    """

    TOKEN_NAME = "_form_id" # name of hidden token widget

    TOKEN_NOTICE = html.div(
        html('The form you have submitted is invalid.  Most '
             'likely it has been successfully submitted once '
             'already.  Please review the the form data '
             'and submit the form again.'),
        **{'class': "errornotice"})

    def __init__(self,
                 request_object=None,
                 method="post",
                 action=None,
                 enctype=None,
                 use_tokens=True,
                 **attrs):
        self.request = request_object
        if method not in ("post", "get"):
            raise ValueError("Form method must be 'post' or 'get', "
                             "not %r" % method)
        self.method = method
        self.action = action or self._get_default_action()
        if 'class' not in attrs:
            attrs['class'] = 'lokai'
        self.attrs = attrs
        self.widgets = []
        self.hidden_widgets = []
        self._names = {}

        if enctype is not None and enctype not in (
            "application/x-www-form-urlencoded", "multipart/form-data"):
            raise ValueError, ("Form enctype must be "
                               "'application/x-www-form-urlencoded' or "
                               "'multipart/form-data', not %r" % enctype)
        self.enctype = enctype

        if (use_tokens  and
            self.method == "post" and
            self.request and
            hasattr(self.request, '_form_tokens')):
            # unique token for each form, this prevents many cross-site
            # attacks and prevents a form from being submitted twice
            self.add(FormTokenWidget, self.TOKEN_NAME, value=None)

        if self.attrs.has_key('fieldset'):
            self.fieldset = {'legend':'',
                             }
            for f_setting in self.fieldset.keys():
                if self.attrs['fieldset'].has_key(f_setting):
                    self.fieldset[f_setting] = self.attrs['fieldset'][f_setting]
            del self.attrs['fieldset']
        self.dynamic = False
        if self.attrs.has_key('dynamic'):
            self.dynamic = self.attrs['dynamic']

    def _get_default_action(self):
        query = self.request.query_string
        if query:
            return '?'+query
        else:
            return ""

    # -- Form data access methods --------------------------------------

    def __getitem__(self, name):
        """(name:string) -> any
        Return a widget's value.  Raises KeyError if widget named 'name'
        does not exist.
        """
        try:
            return self._names[name].parse(self.request)
        except KeyError:
            raise KeyError, 'no widget named %r' % name

    def __contains__(self, name):
        return name in self._names
    
    def has_key(self, name):
        """Return true if the widget named 'name' is in the form."""
        return name in self

    def get(self, name, default=None):
        """(name:string, default=None) -> any
        Return a widget's value.  Returns 'default' if widget named 'name'
        does not exist.
        """
        widget = self._names.get(name)
        if widget is not None:
            return widget.parse(self.request)
        else:
            return default

    def get_widget(self, name):
        """(name:string) -> Widget | None
        Return the widget named 'name'.  Returns None if the widget does
        not exist.
        """
        return self._names.get(name)


    def get_all_widgets(self):
        """() -> [Widget]
        Return all the widgets that have been added to the form.  Note that
        this while this list includes submit widgets and hidden widgets, it
        does not include sub-widgets (e.g. widgets that are part of
        CompositeWidgets)
        """
        return self._names.values()

    def get_messages(self):
        """() -> {widget name: message text, ...}
        Returns a dictionary of non-empty error text for all widgets known
        to the form.
        """
        error_set = {}
        for k, obj in self._names.items():
            error = obj.error
            if error:
                error_set[k] = error
        return error_set

    # -- Form processing and error checking ----------------------------

    def is_submitted(self):
        """() -> bool

        Return true if a form was submitted.  If the form method is 'POST'
        and the page was not requested using 'POST', then the form is not
        considered to be submitted.  If the form method is 'GET' then the
        form is considered submitted if there is any form data in the
        request.
        """
        if self.method == 'post':
            if self.request.method == 'POST':
                return True
            else:
                return False
        else:
            return bool(request.args)

    def has_errors(self):
        """() -> bool

        Ensure that all components of the form have parsed themselves. Return
        true if any of them have errors.
        """
        has_errors = False
        if self.is_submitted():
            for widget in self.get_all_widgets():
                if widget.has_error(self.request):
                    has_errors =  True
        return has_errors

    def clear_errors(self):
        """Ensure that all components of the form have parsed themselves.
        Clear any errors that might have occured during parsing.
        """
        for widget in self.get_all_widgets():
            widget.clear_error(self.request)

    def set_error(self, name, error):
        """(name : string, error : string)
        Set the error attribute of the widget named 'name'.
        """
        widget = self._names.get(name)
        if not widget:
            raise KeyError, "unknown name %r" % name
        widget.set_error(error)

    def set_messages(self, set_of_errors):
        """set_of_errors: {name:string, name:string, ...}
        Set the error text for all widgets named in the input.
        """
        for name, error in set_of_errors.items():
            widget = self._names.get(name)
            if widget:
                widget.set_error(error)

    # -- Form population methods ---------------------------------------

    def add(self, widget_class, name, *args, **kwargs):
        """ Define a new widget and append it to the current set """
        if name in self._names:
            raise ValueError, "form already has '%s' widget" % name
        if 'id' in self.attrs:
            kwargs['form_id'] = self.attrs['id']
        kwargs['form_obj'] = self
        widget = widget_class(name, *args, **kwargs)
        self.add_w(widget)

    def add_w(self, widget):
        """ Add a pre-defined widget """
        self._names[widget.name] = widget
        if isinstance(widget, HiddenWidget):
            self.hidden_widgets.append(widget) # will render at beginning
        else:
            self.widgets.append(widget)

    # convenience methods

    def add_submit(self, name, value=None, **kwargs):
        self.add(SubmitWidget, name, value, **kwargs)

    def add_reset(self, name, value=None, **kwargs):
        self.add(ResetWidget, name, value, **kwargs)

    def add_hidden(self, name, value=None, **kwargs):
        self.add(HiddenWidget, name, value, **kwargs)

    def add_string(self, name, value=None, **kwargs):
        self.add(StringWidget, name, value, **kwargs)

    def add_text(self, name, value=None, **kwargs):
        self.add(TextWidget, name, value, **kwargs)

    def add_password(self, name, value=None, **kwargs):
        self.add(PasswordWidget, name, value, **kwargs)

    def add_checkbox(self, name, value=None, **kwargs):
        self.add(CheckboxWidget, name, value, **kwargs)

    def add_single_select(self, name, value=None, **kwargs):
        self.add(SingleSelectWidget, name, value, **kwargs)

    def add_multiple_select(self, name, value=None, **kwargs):
        self.add(MultipleSelectWidget, name, value, **kwargs)

    def add_radiobuttons(self, name, value=None, **kwargs):
        self.add(RadiobuttonsWidget, name, value, **kwargs)

    def add_float(self, name, value=None, **kwargs):
        self.add(FloatWidget, name, value, **kwargs)

    def add_int(self, name, value=None, **kwargs):
        self.add(IntWidget, name, value, **kwargs)

    def add_calendar(self, name, value=None, **kwargs):
        self.add(CalendarWidget, name, value, **kwargs)

    def add_plain_text(self, name, value=None, **kwargs):
        self.add(PlainTextWidget, name, value, **kwargs)

    def add_file(self, name, value=None, **kwargs):
        self.enctype = 'multipart/form-data'
        self.add(FileWidget, name, value, **kwargs)

    def add_date(self, name, value=None, **kwargs):
        self.add(DateWidget, name, value, **kwargs)

    def add_date_time(self, name, value=None, **kwargs):
        self.add(DateTimeWidget, name, value, **kwargs)

    def add_composite(self, name, value=None, **kwargs):
        self.add(CompositeWidget, name, value, **kwargs)

    # -- Layout (rendering) methods ------------------------------------

    def render(self):
        """() -> HTML text
        Render a form as HTML.
        """
        return self.render_html()

    def render_html(self):
        return html.form(self._render_body(),
                         method=self.method,
                         enctype=self.enctype,
                         action=self.action,
                         **self.attrs)
 
    def _render_widgets(self):
        rendering_object = []
        for widget in self.widgets:
            rendering_object.append(widget.render())
        return ''.join(rendering_object)

    def _render_hidden_widgets(self):
        rendering_object = []
        for widget in self.hidden_widgets:
            rendering_object.append(widget.render())
        return html.div(''.join(rendering_object),
                        **{'class': 'HiddenWidgetContainer'})

    def _render_error_notice(self):
        ## just return none as we don't use this
        token_widget = self.get_widget(self.TOKEN_NAME)
        if token_widget is not None and token_widget.has_error():
            # form tokens are enabled but the token data in the request
            # does not match anything in the session.  It could be an
            # a cross-site attack but most likely the back button has
            # be used
            return self.TOKEN_NOTICE
        else:
            return ''

    def _render_body(self):
        rendering_object = []
        rendering_object.append(self._render_hidden_widgets())
        if self.has_errors():
            rendering_object.append(self._render_error_notice())
        rendering_object.append(self._render_widgets())
        return ''.join(rendering_object)

#-----------------------------------------------------------------------
# Utility functions for composite widgets

def deep_get_widget(target, name_list):
    """ Recursive get_widget to delve into composite widgets"""
    if len(name_list) > 0:
        is_widget = target.get_widget(name_list[0])
        if is_widget:
            return deep_get_widget(is_widget, name_list[1:])
        return is_widget
    return target

def deep_get_value(target, name_list, default=None):
    """ Find the value of a widget burried inside a composite"""
    widget = deep_get_widget(target, name_list)
    if widget:
        return widget.value
    return default

def deep_set_value(target, name_list, value=None):
    """ Set the value of a widget burried inside a composite"""
    widget = deep_get_widget(target, name_list)
    if widget:
        widget.set_value(value)

def deep_set_error(target, name_list, error=None):
    """ Set error value of a widget burried inside a composite"""
    widget = deep_get_widget(target, name_list)
    if widget:
        widget.set_error(error)
    

#-----------------------------------------------------------------------
