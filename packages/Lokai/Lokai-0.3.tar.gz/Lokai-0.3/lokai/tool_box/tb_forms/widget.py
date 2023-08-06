# Name:      lokai/tool_box/tb_forms/widget.py
# Purpose:   Provide widget support for Quixote form mechanism
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

#
# Based on:
#
# """$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/quixote/form/widget.py $
# $Id: widget.py, v 1.31 2007/03/03 18:04:01 mike Exp $
#
# Provides the basic web widget classes: Widget itself, plus StringWidget,
# TextWidget, CheckboxWidget, etc.
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

import struct
from werkzeug import html, FileStorage
from lokai.tool_box.tb_forms.form_shapes import (
    RENDER_WIDE_WIDGET,
    RENDER_NORMAL_WIDGET,
    field_set_widget,
    multi_column_widget,
    row_widget,
)

from lokai.tool_box.tb_common.dates import ErrorInDateString, timetostr

#-----------------------------------------------------------------------

def subname(prefix, name):
    """Create a unique name for a sub-widget or sub-component."""
    # $ is NOT nice 
    # it's valid as part of a Javascript identifier - unfortunately it 
    # can nerf any javascript library that uses $ as a function name
    return "%s___%s" % (prefix, name)

def basename( fullname ):
    abc = fullname.split( '___' )
    return abc[-1]

def merge_attrs(base, overrides):
    """({string: any}, {string: any}) -> {string: any}
    """
    items = []
    if base:
        items.extend(base.items())
    if overrides:
        items.extend(overrides.items())
    attrs = {}
    for name, val in items:
        if name.endswith('_'):
            name = name[:-1]
        attrs[name] = val
    return attrs

class WidgetValueError(Exception):
    """May be raised if a widget has problems parsing its value."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class WidgetProcessError(Exception):
    pass

class Widget(object):
    """Abstract base class for web widgets.

    Instance attributes:
      name : string
      value : any
      update : update
      error : string
      title : string
      hint : string
      required : bool
      attrs : {string: any}
      _parsed : bool

    Feel free to access these directly; to set them, use the 'set_*()'
    modifier methods.
    """

    REQUIRED_ERROR = 'required'
    
    WIDGET_SHAPE_TO_RENDERER = {'wide': RENDER_WIDE_WIDGET,
                                'normal': RENDER_NORMAL_WIDGET}

    def __init__(self, name, value=None, title="", hint="", required=False,
                 render_br=True, attrs=None, **kwattrs):
        assert self.__class__ is not Widget, "abstract class"
        self.name = name
        self.value = value
        self.update = False
        self.error = None
        self.title = title
        self.hint = hint
        self.required = required
        self.render_br = render_br
        self.attrs = merge_attrs(attrs, kwattrs)
        self.form_id = ''
        if self.attrs.has_key('form_id'):
            self.form_id = self.attrs['form_id']
            del self.attrs['form_id']
        self.form_obj = None
        if self.attrs.has_key('form_obj'):
            self.form_obj = self.attrs['form_obj']
            del self.attrs['form_obj']
        if self.attrs.has_key('readonly'):
            ## potentially set the readonly attribute
            ## only on certain element types
            readonly = self.attrs['readonly']
            if str(readonly).lower() in ['false', 'none', '']:
                del self.attrs['readonly']
            else:
                if self.__class__.__name__ in [ 'StringWidget',
                                                'PasswordWidget',
                                                'TextWidget',
                                                'CoupleWidget',
                                                'DateWidget',
                                                'DateTimeWidget',
                                                'NumberWidget',
                                                'SingleSelectWidget',
                                                'FloatWidget',
                                                'IntWidget',
                                                'CheckboxWidget',
                                                'MultiCheckWidget']:
                    self.attrs['readonly'] = "readonly"
                else:
                    del self.attrs['readonly']
        if self.attrs.has_key('disabled'):
            ## potentially set the disabled attribute
            disabled = self.attrs['disabled']
            if str(disabled).lower() in ['false', 'none', '']:
                del self.attrs['disabled']
            else:
                self.attrs['disabled'] = "disabled"
        # widget render method
        self.output_method = RENDER_NORMAL_WIDGET
        if self.attrs.has_key('output'):
            self.output_method = self.attrs['output']
            del self.attrs['output']
            # backward compatibility:
            #    if the parameter is given as a string like 'wide'
            if not callable(self.output_method):
                self.output_method = self.WIDGET_SHAPE_TO_RENDERER.get(
                                      self.output_method, RENDER_NORMAL_WIDGET)
        self._parsed = False
            
        # attrs['class'] is passed down to render_content and html.tag
        # which then adds it to the tag output - we default it where not sent
        if not self.attrs.get('class', None):
            self.attrs['class'] = '%s widget' % self.__class__.__name__

    def __repr__(self):
        return "<%s at %x: %s>" % (self.__class__.__name__,
                                   id(self),
                                   self.name)

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.name)

    def get_name(self):
        return self.name

    def set_value(self, value):
        self.value = value

    def set_update(self, update):
        self.update = update

    def get_update(self, request=None):
        return self.update

    def set_parsed(self):
        # to prevent parsing a new field when it is being added in
        # response to a submit. This prevents the value being set to
        # null just before the render simply because the field does
        # not appear in the response.
        self._parsed = True
        
    def set_additional(self, content):
        """ Set text to be drawn in the message are of the widget.

            The text is assumed to be valid HTML and is not escaped.

            The content is held separately from the error message
            text, so widget rendering can display either or both.  It
            is not guaranteed, but we expect the display to use the
            error text in preference to this content.
        """
        self.additional = content

    def get_additional(self):
        if hasattr(self, 'additional'):
            return self.additional
        return None

    def set_message(self, content):
        """ Set text to be drawn in the message are of the widget.

            The text is not assumed to be valid HTML and is therefor
            escaped. The escaped value is stored in self.additional
            and is therfore processed as additional text when the
            widget is rendered.
        """
        self.additional = html(content)

    def get_message(self):
        """ Get the message text - actually this returns the content
            of self.additional and HTML escaping might have happened.
        """
        self.get_additional()
        
    def set_error(self, error):
        self.error = error

    def get_error(self, request=None):
        self.parse(request)
        return self.error

    def get_error_tup(self, request=None):
        error_str = ''
        error = self.get_error(request)
        if error is not None and error != 'required':
            error_str = error
        return (error_str, self.get_name(), self.form_id)

    def has_error(self, request=None):
        return bool(self.get_error(request))

    def clear_error(self, request=None):
        self.parse(request)
        self.error = None

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def set_hint(self, hint):
        self.hint = hint

    def get_hint(self):
        return self.hint

    def get_style(self):
        return self.attrs.get('widget_style', None)

    def get_class(self):
        return self.attrs.get('css_class', None)

    def is_required(self):
        return self.required

    def parse(self, request=None):
        if not self._parsed:
            self._parsed = True
            if request is None:
                if self.form_obj:
                    request = self.form_obj.request
                else:
                    raise WidgetProcessError(
                        "Cannot find a request to process in %s:%s" %
                        (self.__class__.__name__, self.name))
            if request.form or request.method == 'POST':
                try:
                    self._parse(request)
                except WidgetValueError, exc:
                    self.set_error(exc)
                if (self.required and self.value is None and
                    not self.has_error(request)):
                    self.set_error(self.REQUIRED_ERROR)
        return self.value

    def _parse(self, request):
        # subclasses may override but this is not part of the public API
        value = request.form.get(self.name)
        if isinstance(value, basestring) and value.strip():
            self.value = value
        else:
            self.value = None

    def validate(self):
        '''
        Validates the widgets current content
        '''
        # force re-parsing of the widget, since parse is the method that does
        # the validation.
        # For this operation a fake http-request is used, that
        # has the widget's value in its form attribute for the widget
        # to take (and support methods used by parse)
        v = self.value
        fake_request = ValidationHTTPRequest(self)
        self._parsed = False
        self.parse(fake_request)
        assert self._parsed
        if v != self.value:
            # reset value
            self.value = v
        
    def render_title(self, title):
        op = []
        if title:
            if self.required:
                op.append(html.span(html('*'),
                         **{'class': 'required'}
                         ))
            if title == '':
                title = '&nbsp;'
            op.append(html(title))
            return ''.join(op)
        else:
            return html("""&nbsp;""")

    def render_hint(self, hint):
        if hint:
            return html.div(html(hint),
                            **{'class': "hint"})
        else:
            return ''

    def render_error(self, error):
        error_str = ''
        if error not in [None, '']:
            return html.div(html(error_str,
                                 **{'class': "error",
                                    'id': "%s_error" % self.get_name()}))

    def render(self):
        return self.output_method(self)

    def render_content(self):
        raise NotImplementedError

# class Widget

# -- Fundamental widget types ------------------------------------------
# These correspond to the standard types of input tag in HTML:
#   text     StringWidget
#   password PasswordWidget
#   radio    RadiobuttonsWidget
#   checkbox CheckboxWidget
#
# and also to the other basic form elements:
#   <textarea>  TextWidget
#   <select>    SingleSelectWidget
#   <select multiple>
#               MultipleSelectWidget

class StringWidget(Widget):
    """ Widget for entering a single string: corresponds to
        '<input type="text">' in HTML.

        Instance attributes:
        value : string
    """

    # This lets PasswordWidget be a trivial subclass
    HTML_TYPE = "text"
    
    def render_content(self):
        return html.input(type=self.HTML_TYPE,
                          name=self.name,
                          id=self.name,
                          value=self.value,
                          **self.attrs)

class FileWidget(StringWidget):
    """ Subclass of StringWidget for uploading files.

        Instance attributes: none
    """

    HTML_TYPE = "file"
    
    def _parse(self, request):
        parsed_value = request.files.get(self.name)
        if isinstance(parsed_value, FileStorage):
            self.value = parsed_value
        else:
            self.value = None


class PasswordWidget(StringWidget):
    """ Trivial subclass of StringWidget for entering passwords
        (different widget type because HTML does it that way).

        Instance attributes: none
    """

    HTML_TYPE = "password"

class TextWidget(Widget):
    """ Widget for entering a long, multi-line string; corresponds to
        the HTML"<textarea>" tag.

        Instance attributes:
        value : string
    """

    def _parse(self, request):
        Widget._parse(self, request)
        if self.value and self.value.find("\r\n") >= 0:
            self.value = self.value.replace("\r\n", "\n")

    def render_content(self):
        return html.textarea(self.value or "",
                             name=self.name,
                             id=self.name,
                             **self.attrs)

class CheckboxWidget(Widget):
    """Widget for a single checkbox: corresponds to "<input
    type=checkbox>".  Do not put multiple CheckboxWidgets with the same
    name in the same form.

    Instance attributes:
      value : boolean
    """

    def _parse(self, request):
        self.value = request.form.has_key(self.name)
        
    def set_checked(self, checked):
        self.checked = checked
        if self.checked in [None, False, 0]:
            self.checked = None
        else:
            self.checked = "checked"

    def render_content(self):
        # We may set .checked manually
        if not hasattr(self, 'checked'):
            self.checked = self.value and "checked" or None
        self.set_checked(self.checked)
        ret = ''
        if self.attrs.get('readonly', None):
            # Read Only version
            if self.checked:
                ret += html.input(type="hidden",
                                  name=self.name,
                                  value="yes")
                ret += str(self.checked)
        else:
            ret = html.input(type="checkbox",
                             name=self.name,
                             id=self.name,
                             value="yes",
                             checked=self.checked,
                             **self.attrs)
        return ret

class SelectWidget(Widget):
    """Widget for single or multiple selection; corresponds to
    <select name=...>
      <option value="Foo">Foo</option>
      ...
    </select>

    Instance attributes:
      options : [ (value:any, description:any, key:string) ]
      value : any
        The value is None or an element of dict(options.values()).
    """

    SELECTION_ERROR = "invalid value selected"
    
    def __init__(self, name, value=None, options=None, sort=False,
                 verify_selection=True, **kwargs):
        assert self.__class__ is not SelectWidget, "abstract class"
        Widget.__init__(self, name, value, **kwargs)
        self.options = []
        if not options:
            raise ValueError, "a non-empty list of 'options' is required"
        else:
            self.set_options(options, sort)
        self.verify_selection = verify_selection
        
    def get_allowed_values(self):
        return [item[0] for item in self.options]
    
    def get_descriptions(self):
        return [item[1] for item in self.options]
    
    def set_value(self, value):
        self.value = None
        for opt_refs in self.options:
            if value == opt_refs[0]:
                self.value = value
                break
    
    def set_options(self, options, sort=False):
        """(options: [objects:any], sort=False)
         or
           (options: [(object:any, description:any)], sort=False)
         or
           (options: [(object:any, description:any, key:any)], sort=False)

            Set the options list.  The list of options can be a list
            of objects, in which case the descriptions default to
            map(html, objects) applying html() to each description and
            key.
        
            If keys are provided they must be distinct.  If the sort
            keyword argument is true, sort the options by
            case-insensitive lexicographic order of descriptions,
            except that options with value None appear before others.
        """
        if options:
            first = options[0]
            values = []
            descriptions = []
            keys = []
            if isinstance(first, tuple):
                if len(first) == 2:
                    for value, description in options:
                        values.append(value)
                        descriptions.append(description)
                        keys.append(value)
                elif len(first) == 3:
                    for value, description, key in options:
                        values.append(value)
                        descriptions.append(description)
                        keys.append(key)
                else:
                    raise ValueError, 'invalid options %r' % options
            else:
                values = descriptions = options
    
            options = zip(values, descriptions, keys)
    
            if sort:
                def make_sort_key(option):
                    value, description, key = option
                    if value is None:
                        return ('', option)
                    else:
                        return (description.lower(), option)
                doptions = map(make_sort_key, options)
                doptions.sort()
                options = [item[1] for item in doptions]
        self.options = options
        
    def _parse_single_selection(self, parsed_key, default=None):
        for opt_refs in self.options:
            if opt_refs[2] == parsed_key:
                return opt_refs[0]
        else:
            if self.verify_selection:
                self.error = self.SELECTION_ERROR
                return default
            elif self.options:
                return self.options[0][0]
            else:
                return default
            
    def set_allowed_values(self, allowed_values, descriptions=None,
                           sort=False):
        """(allowed_values:[any], descriptions:[any], sort:boolean=False)
    
        Set the options for this widget.  The allowed_values and descriptions
        parameters must be sequences of the same length.  The sort option
        causes the options to be sorted using case-insensitive lexicographic
        order of descriptions, except that options with value None appear
        before others.
        """
        if descriptions is None:
            self.set_options(allowed_values, sort)
        else:
            assert len(descriptions) == len(allowed_values)
            self.set_options(zip(allowed_values, descriptions), sort)

    def is_selected(self, value):
        return value == self.value

    def render_content(self):
        options = []
        for object, description, key in self.options:
            if self.is_selected(object):
                selected = 'selected'
            else:
                selected = None
            if description is None:
                description = ""
            options.append(html.option(html(description),
                                       value=key,
                                       selected=selected))
        return html.select('\n'.join(options),
                           name=self.name,
                           id=self.name,
                           **self.attrs)


class SingleSelectWidget(SelectWidget):
    """Widget for single selection.
    """
    
    SELECT_TYPE = "single_select"
    MULTIPLE_SELECTION_ERROR = "cannot select multiple values"
    
    def _parse(self, request):
        parsed_key = request.form.get(self.name)
        if parsed_key:
            if isinstance(parsed_key, list):
                self.error = self.MULTIPLE_SELECTION_ERROR
            else:
                self.value = self._parse_single_selection(parsed_key)
        else:
            self.value = None

    def render_content(self):
        if self.attrs.get('readonly') == 'readonly':
            # Output as a hidden and a readonly
            ret = html.input(type='hidden',
                             name=self.name,
                             value=self.value)
            for opt_refs in self.options:
                if self.is_selected(opt_refs[0]):
                    ret += html.input(type='text',
                                      name=self.name+'_display',
                                      value=opt_refs[1],
                                      **self.attrs)
                    break
            return ret
        return SelectWidget.render_content(self)


class RadiobuttonsWidget(SingleSelectWidget):
    """Widget for a *set* of related radiobuttons -- all have the
    same name, but different values (and only one of those values
    is returned by the whole group).

    Instance attributes:
      delim : string = None
        string to emit between each radiobutton in the group.  If
        None, a single newline is emitted.
    """

    SELECT_TYPE = "radiobuttons"

    def __init__(self, name, value=None, options=None, delim=None, **kwargs):
        SingleSelectWidget.__init__(self, name, value, options=options,
                                    **kwargs)
        if delim is None:
            self.delim = "\n"
        else:
            self.delim = delim

    def render_content(self):
        tags = []
        for object, description, key in self.options:
            if self.is_selected(object):
                checked = 'checked'
            else:
                checked = None
            r = html.input(type="radio",
                           name=self.name,
                           id=self.name,
                           value=key,
                           checked=checked,
                           **self.attrs)
            tags.append(r + html(description))
        return html(self.delim).join(tags)


class MultipleSelectWidget(SelectWidget):
    """Widget for multiple selection.

    Instance attributes:
      value : [any]
        for multipe selects, the value is None or a list of
        elements from dict(self.options).values()
    """

    SELECT_TYPE = "multiple_select"
    
    def __init__(self, name, value=None, options=None, **kwargs):
        SelectWidget.__init__(self, name, value, options=options,
                              multiple='multiple', **kwargs)

    def set_value(self, value):
        allowed_values = self.get_allowed_values()
        if value in allowed_values:
            self.value = [ value ]
        elif isinstance(value, (list, tuple)):
            self.value = [ element
                           for element in value
                           if element in allowed_values ] or None
        else:
            self.value = None
        
    def is_selected(self, value):
        if self.value is None:
            return value is None
        else:
            return value in self.value
        
    def _parse(self, request):
        parsed_keys = request.form.get(self.name)
        if parsed_keys:
            if isinstance(parsed_keys, list):
                self.value =  [opt_refs[0]
                               for opt_refs in self.options
                               if opt_refs[2] in parsed_keys] or None
            else:
                _marker = []
                value = self._parse_single_selection(parsed_keys, _marker)
                if value is _marker:
                    self.value = None
                else:
                    self.value = [value]
        else:
            self.value = None

class ButtonWidget(Widget):
    """
    Instance attributes:
      label : string
      value : boolean
    """

    HTML_TYPE = "button"
    
    def __init__(self, name, value=None, **kwargs):
        Widget.__init__(self, name, value=None, **kwargs)
        self.set_label(value)

    def set_label(self, label):
        self.label = label

    def get_label(self):
        return self.label

    def render_content(self):
        # slightly different behavior here, we always render the
        # tag using the 'value' passed in as a parameter.  'self.value'
        # is a boolean that is true if the button's name appears
        # in the request.
        value = html(self.label) if self.label else None
        return html.input(
            type=self.HTML_TYPE,
            name=self.name,
            id=self.name,
            value=value, **self.attrs)

    def _parse(self, request):
        self.value = request.form.has_key(self.name)


class SubmitWidget(ButtonWidget):
    
    HTML_TYPE = "submit"
    
class ResetWidget(ButtonWidget):
    
    HTML_TYPE = "reset"

    
class HiddenWidget(Widget):
    """
    Instance attributes:
      value : string
    """
    
    def set_error(self, error):
        if error is not None:
            raise TypeError, 'error not allowed on hidden widgets'
        
    def render_content(self):
        return html.input(type="hidden",
                          name=self.name,
                          value=html(self.value),
                          **self.attrs)
    
    def render(self):
        return self.render_content()
    

# -- Derived widget types ----------------------------------------------
# (these don't correspond to fundamental widget types in HTML,
# so they're separated)

class DisplayOnlyWidget(Widget):
    """ The value is displayed as HTML string and not as an input
        widget of any sort.

        The given value must be trusted html.
    """

    def __init__(self, name, value=None, **kwargs):
        Widget.__init__(self, name, value=value, **kwargs)
        self._parsed = True

    def render_content(self):
        if self.value:
            r = self.value
        else:
            r = '&nbsp;'
        return r

class PlainTextWidget(Widget):
    """Widget for entering a html string: corresponds to
    '<div class="PlainTextWidget widget">...title value...</div>' in HTML.

    Instance attributes:
      title : string

    the output text is held in the title variable 
    """

    def __init__(self, name, value=None, **kwargs):
        Widget.__init__(self, name, value=None, **kwargs)

    # overloaded to allow full width output
    def render(self):
        op = []
        op.append(html.div(self.render_title(str(self.get_title())),
                           **{'style': "background-color:white; text-align:left"}
                           )
                  )
        op.append(html.div(**{'class': "space_line"}))
        return '\n'.join(op)

    def render_title(self, title):
        return html("%s" % str(title))
    
    def render_content(self):
        return None

class DateWidget(StringWidget):
    """
    Instance attributes: none
    """
    def __init__(self, *args, **kwargs):
        StringWidget.__init__(self, *args, **kwargs)
        if not self.attrs.has_key('date_type'):
            self.attrs['date_type'] = 'date'
    
    def render_content(self):
        js_value = self.value
        if js_value is not None:
            try:
                if self.attrs.get('date_type', 'date') == 'datetime':
                    js_value = timetostr(self.value, i='%Y-%m-%d %H:%M:%S')
                else:
                    js_value = timetostr(self.value, i='%Y-%m-%d')
            except (ErrorInDateString, ValueError):
                pass
        ret = html.input(type=self.HTML_TYPE,
                         name=self.name,
                         id=self.name,
                         value=js_value,
                         **self.attrs)
        return ret

class DateTimeWidget(DateWidget):
    def __init__(self, *args, **kwargs):
        kwargs['date_type'] = 'datetime'
        DateWidget.__init__(self, *args, **kwargs)

class CalendarWidget(StringWidget):
    """
    More a Div Widget than anything as the render and form elements are dynamic js
    Instance attributes: none
    """

    # overloaded to allow full page span
    def render(self):
        return self.render_content()
    
    def render_content(self):
        self.value = 'new Array()'
        ret = html.div(
            html.script("*<![CDATA[*/"
                        "showCalendarPicker( '%s', %s);"
                        "/*]]>*/" % (self.name, self.value),
                        type='text/javascript'),
            **{'class': "std_container",
               'id': self.name})
        return ret
    

class NumberWidget(StringWidget):
    """
    Instance attributes: none
    """

    # Parameterize the number type (either float or int) through
    # these class attributes:
    TYPE_OBJECT = None                  # eg. int, float
    TYPE_ERROR = None                   # human-readable error message
    
    def __init__(self, name, value=None, **kwargs):
        assert self.__class__ is not NumberWidget, "abstract class"
        assert value is None or type(value) is self.TYPE_OBJECT, (
            "form value '%s' not a %s: got %r" % (name,
                                                  self.TYPE_OBJECT,
                                                  value))
        StringWidget.__init__(self, name, value, **kwargs)

    def _parse(self, request):
        StringWidget._parse(self, request)
        if self.value is not None:
            try:
                self.value = self.TYPE_OBJECT(self.value)
            except ValueError:
                self.error = self.TYPE_ERROR


class FloatWidget(NumberWidget):
    """
    Instance attributes:
      value : float
    """

    TYPE_OBJECT = float
    TYPE_ERROR = "must be a number"
    

class IntWidget(NumberWidget):
    """
    Instance attributes:
      value : int
    """

    TYPE_OBJECT = int
    TYPE_ERROR = "must be an integer"

    
class OptionSelectWidget(SingleSelectWidget):
    """ Widget for single selection with automatic submission. Parse
        will always return a value from the given options, even if the form is
        not submitted. This allows its value to be used to decide what
        other widgets need to be created in a form.

        Instance attributes:
            value : any
    """

    SELECT_TYPE = "option_select"
    

    def __init__(self, name, value=None, options=None, **kwargs):
        SingleSelectWidget.__init__(self, name, value, options=options,
                                    onchange='submit()', **kwargs)

    def parse(self, request):
        if not self._parsed:
            self._parse(request)
            self._parsed = True
        return self.value

    def _parse(self, request):
        parsed_key = request.form.get(self.name)
        if parsed_key:
            if isinstance(parsed_key, list):
                self.error = self.MULTIPLE_SELECTION_ERROR
            else:
                self.value = self._parse_single_selection(parsed_key)
        elif self.value is None:
            self.value = self.options[0][0]

    def render_content(self):
        return (SingleSelectWidget.render_content(self) +
                html.noscript(html.input(type="submit", name="", value="apply")))

class CompositeWidget(Widget):
    """
    Instance attributes:
      widgets : [Widget]
      _names : {name:string : Widget}
    """

    def __init__(self, name, value=None, **kwargs):
        self.fieldset = {}
        if kwargs.has_key('fieldset'):
            self.fieldset = {'legend': '',
                             'expand': False}
            for f in self.fieldset.keys():
                if f in kwargs['fieldset']:
                    self.fieldset[f] = kwargs['fieldset'][f]
            del kwargs['fieldset']
        Widget.__init__(self, name, value, **kwargs)
        self.widgets = []
        self._names = {}

    def _parse(self, request):
        for widget in self.widgets:
            widget.parse(request)

    def __getitem__(self, name):
        return self._names[name].parse()

    def __contains__(self, name):
        return name in self._names

    def get(self, name):
        widget = self._names.get(name)
        if widget:
            return widget.parse()
        return None

    def get_widget(self, name):
        return self._names.get(name)
    
    def get_widgets(self):
        return self.widgets
    
    def clear_error(self, request=None):
        Widget.clear_error(self, request)
        for widget in self.widgets:
            widget.clear_error(request)
            
    def set_widget_error(self, name, error):
        self._names[name].set_error(error)
        
    def has_error(self, request=None):
        has_error = False
        if Widget.has_error(self, request):
            has_error = True
        for widget in self.widgets:
            if widget.has_error(request):
                has_error = True
        return has_error
    
    def validate(self):
        '''
        Validates the sub-widgets current content
        '''
        # re-validate sub-widgets
        for widget in self.widgets:
            widget.validate()

    def add(self, widget_class, name, *args, **kwargs):
        """ Define a new widget and append it to the current set """
        if self._names.has_key(name):
            raise ValueError, 'the name %r is already used' % name
        if self.attrs.get('disabled') and 'disabled' not in kwargs:
            kwargs['disabled'] = True
        kwargs['form_id'] = self.form_id
        kwargs['form_obj'] = self.form_obj
        widget = widget_class(subname(self.name, name), *args, **kwargs)
        self.add_w(widget)

    def add_w(self, widget):
        """ Add a pre-defined widget """
        self._names[basename(widget.name)] = widget
        self.widgets.append(widget)

    def insert(self, position, widget_class, name, *args, **kwargs):
        """ Define a new widget and insert it into the current set """
        if self._names.has_key(name):
            raise ValueError, 'the name %r is already used' % name
        if self.attrs.get('disabled') and 'disabled' not in kwargs:
            kwargs['disabled'] = True
        kwargs['form_id'] = self.form_id
        kwargs['form_obj'] = self.form_obj
        widget = widget_class(subname(self.name, name), *args, **kwargs)
        self.insert_w(position, widget)

    def insert_w(self, position, widget, name):
        """ Insert a pre-defined widget """
        self._names[basename(widget.name)] = widget
        self.widgets.insert(position, widget)

    def remove(self, name=None, position=None):
        this_posn = None
        this_name = None
        if name:
            this_name = name
            this_widget = self._names[name]
            for i in range( len( self.widgets ) ):
                if self.widgets[i] == this_widget:
                    this_posn = i
                    break
        elif position != None:
            if position < 0:
                this_posn = len( self.widgets ) + position
            else:
                this_posn = position
            this_name = basename( self.widgets[this_posn].name )
        if this_posn != None and this_name:
            del self.widgets[this_posn]
            del self._names[this_name]
        else:
            print "Failed to remove widget at given name %s, given position %s" % (
                str(name), str(position) )

    def render(self):
        if len(self.fieldset) > 0:
            op = field_set_widget(
                pretext    = '',
                legend     = self.get_title(),
                firsttext  = '',
                content    = self.render_content(),
                expand     = self.fieldset['expand'])
        else:
            op =  Widget.render(self)
        return op

    def render_content(self):
        r = []
        for widget in self.get_widgets():
            r.append(widget.render())
        return html.ol(''.join(r))
        
## Same as CompositeWidget except it only outputs the title
## and content of the subwidgets
class RawCompositeWidget(CompositeWidget):
        
    def render_content(self):
        op = []
        for widget in self.get_widgets():
            title_txt = widget.get_title(  )
            if title_txt:
                op.append(html.span(widget.render_title(title_txt),
                                   **{'class': 'small_container'}))
            op.append(widget.render_content())
        return ''.join(op)


class DummyWidget(Widget):
    """ Dummy Widget for use in ButtonRow as a spacer """

    def __init__(self, name, value=None, **kwargs):
        Widget.__init__(self, name, value=value, **kwargs)
        self._parsed = True

    def render_content(self):
        return ' &nbsp; '
    
class ButtonRow(CompositeWidget):
    """ Holds an ordered set of widgets and displays them on a single line.
    
        There is no title or error. This works best with 3 widgets,
        each one displays in its own column.
        
        If you have less than 3 widgets to display, call add_empty on
        this widget.
    """

    def __init__(self, name, value=None, **kwargs):
        CompositeWidget.__init__(self, name, value, **kwargs)


    def add_empty(self, name):
        if self._names.has_key(name):
            raise ValueError, 'the name %r is already used' % name
        widget = DummyWidget(subname(self.name, name))
        self.add_w(widget)

    def insert(self, position, widget_class, name, *args, **kwargs):
        if self._names.has_key(name):
            raise ValueError, 'the name %r is already used' % name
        if self.attrs.get('disabled') and 'disabled' not in kwargs:
            kwargs['disabled'] = True
        kwargs['form_id'] = self.form_id
        kwargs['form_obj'] = self.form_obj
        widget = widget_class(subname(self.name, name), *args, **kwargs)
        self.insert_w(position, widget)

    def render(self):
        content_set = []
        for widget in self.widgets:
            if widget:
                content_set.append(widget.render_content())
            else:
                content_set.append('')
        style_set = ['text-align: left;'] * len(content_set)
        op = multi_column_widget(content_set, style_set)
        return op

class TableWidget(CompositeWidget):

    def __init__(self, name, value=None, fieldset={}, tableset={}, **kwargs):
        '''        
        fieldset {} : contains fieldset parameters if this
        widget is to be drawn as a fieldset.
        
        tableset {} : contains tableset parameters to define and
        manage the tableset itself.
        
        tableset parameters:
        
           btf_enabled () : for each entry in the tuple:
        
                                True -> the relevant back, top or
                                forward button is enabled
        
                                False -> the relevant back, top or
                                forward button is shown, but
                                disabled
        
           heading_set [] : a list of (name, text) pairs to use as
                            headings for the columns. If not given,
                            there are no column headings. If is is
                            given, the headings are created out of
                            submit buttons.
        
                            If given, there must be a heading for
                            every column
        
        The body of the widget must be a composite widget with the
        name 'body' that contains all rows of the table. The body
        widget might reasonably be a CompositeWidget without the
        fieldset boundary and legend.
        
        The caller must add RowWidgets to the body widget as
        required.
        
        The caller should also add at least one submit button. All
        submit buttons, other than BTF, will be displayed after all
        RowWidgets.
        '''
        CompositeWidget.__init__(self, name, value,
                                 fieldset=fieldset, tableset=tableset,
                                 **kwargs)

        # Start by building a BTF line
        btf_enabled = tableset.get('btf_enabled', (True, True, True))
        self.add(ButtonRow, 'btf')
        btf_widget = self.get_widget('btf')
        btf_widget.add(SubmitWidget, 'btf_back', 'Back',
                       disabled=(not btf_enabled[0]))
        btf_widget.add(SubmitWidget, 'btf_top', 'Top',
                       disabled=(not btf_enabled[1]))
        btf_widget.add(SubmitWidget, 'btf_forward', 'Forward',
                       disabled=(not btf_enabled[2]))

        # Optionally, build a header line
        heading_set = tableset.get('heading_set', None)
        if heading_set:
            self.add(RowWidget, 'headings')
            head_widget = self.get_widget('headings')
            for h in heading_set:
                # Lovely syntax: Basically disabled if no sort_object.field
                # defined as third element of the tuple/list
                head_widget.add(SubmitWidget, h[0], h[1], disabled=(len(h)<3))

    def render(self):
        if len(self.fieldset) > 0:
            op = field_set_widget(
                pretext    = '',
                legend      = self.get_title(),
                firsttext  = '',
                content    = self.render_content(),
                expand     = self.fieldset.get('expand', None))
        else:
            op =  Widget.render( self )
        return op

    def render_content(self):
        op = []
        btf_widget = self.get_widget('btf')
        op.append(btf_widget.render())
        head_widget = self.get_widget('headings')
        if head_widget:
            op.append(head_widget.render())
        body_widget = self.get_widget('body')
        op.append(body_widget.render())
        for name in self._names:
            if name not in ['btf', 'headings', 'body']:
                widget = self.get_widget(name)
                op.append(widget.render())
        return html('\n').join(op)

class RowWidget(CompositeWidget):

    def __init__(self, name, value=None, **kwargs):
        CompositeWidget.__init__(self, name, value, **kwargs)

    def render(self):
        widget_set = self.get_widgets()
        if len(widget_set) > 0:
            width = 100/len(widget_set)
        else:
            width = 100
        content_set = []
        style_set = []
        hint_set = []
        class_set = []
        for widget in widget_set:
            content_set.append(widget.render_content())
            hint_set.append(widget.get_hint())
            style = 'width:%d%%;' % width
            ws = widget.get_style()
            if ws:
                style += ws
            style_set.append(style)
            if widget.attrs['class'].find('widget') < 0:
                # not a default class widget
                class_set.append(widget.attrs['class'])
            else:
                class_set.append(None)
        op = row_widget(content_set, 
                        hint_set, 
                        self.get_error_tup(), 
                        style_set,
                        class_set)
        return op

#-----------------------------------------------------------------------
    
## multiple checkboxes widget 
class MultiCheckWidget(Widget):
    """Widget for handling multiple columns of widgets
    """

    def __init__(self, name, value=None, options=None, heading=None, **kwargs):
        Widget.__init__(self, name, value=None, **kwargs)
        self.options = []
        if not options:
            raise ValueError, "a non-empty list of 'options' is required"
        else:
            self.options = options
        self.heading = heading

    # overloaded to allow full width output
    def render(self):
        self.attrs['class'] = '%s widget' % self.__class__.__name__
        return html.div(self.render_content(),
                        **{'class': '%s widget' % self.__class__.__name__,
                           'style': "text-align:left"})

    def render_title(self, title):
        return html("""&nbsp;""")
    
    def render_content(self):
        ## iterate the self.options and output a checkbox for read/edit/add/delete
        table = []
        op.append("""<table border="0" cellpadding="2" cellspacing="1">""")
        if self.heading:
            hp = html.tr(''.join([html.th(html(t)) for t in self.heading]))
            table.append(hp)
        cols = len(self.heading) - 1
        wd = int(float(30)/float(cols))
        for opt_refs in self.options:
            row = []
            row.append(html.td(html(opt_refs[1]), width='30%%'))
            vx = 1
            for _i in range(cols):
                checked = self.get_checked( opt_refs[0], vx ) and "checked" or None
                name = "%s[%s][%s]" % (self.name, opt_refs[0], str(vx))
                ret = ''
                if self.attrs.get('readonly', None):
                    # Read Only version
                    if checked:
                        ret += html.input(type="hidden",
                                          name=name,
                                          value="yes")
                        ret += "Yes"
                    else:
                        ret += "No"
                else:
                    ret = html.input(type="checkbox",
                                     name=name,
                                     value="yes",
                                     checked=checked,
                                     **self.attrs)
                row.append(html.td(ret,
                                   width='%s%%'%wd))
                vx = vx*2
            #
            table.append(html.tr(row))

        return html.table('\n'.join(table),
                          border="0", cellpadding="2", cellspacing="1") 

    def get_checked( self, sname, bit ):
        if type(self.value) == type({}):
            if self.value.has_key( sname ):
                if self.value[sname][1] & bit:
                    return True
        return False

    def set_value( self, values ):
        self.value = values

#-----------------------------------------------------------------------
