# Name:      lokai/lk_worker/ui/widget.py
# Purpose:   Provides restful widgets
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

import urllib
import types

from werkzeug import html

from docutils.core import publish_parts

from lokai.tool_box.tb_forms.widget import (Widget,
                                     CompositeWidget,
                                     ButtonRow,
                                     RowWidget,
                                     )
from lokai.tool_box.tb_forms.form_shapes import (field_set_widget,
                                          RENDER_WIDE_WIDGET,
                                          RENDER_NORMAL_WIDGET,
                                          hint_block,
                                          )

from lokai.lk_worker.ui.rest_support import convert_shebang

#-----------------------------------------------------------------------

def super_widget(title, content, hint, error_tup, required, style, rgb_tup):
    
    outer_set = [
        html.div(
            html.div(
                ''.join([content, hint_block(hint)]),
                **{'class': 'wide_container'}),
            **{'class': 'widget_row'}),
        html.div(**{'class': 'space_line'})
        ]
    return '\n  '.join(outer_set)

def render_widget_super(widget):
    '''
    Renders a 'super' widget:
    [ [      element       ] ]
    '''
    return super_widget(widget.get_title(),
                        widget.render_content(),
                        widget.get_hint(),
                        widget.get_error_tup(),
                        widget.required,
                        widget.get_style(),
                        widget.rgb_tup
                        )

RENDER_SUPER_WIDGET = render_widget_super

#-----------------------------------------------------------------------

class LkWidget(Widget):
    """Override some aspects of tb_forms widget to avoid clashes
    """

    WIDGET_SHAPE_TO_RENDERER = {'wide': RENDER_WIDE_WIDGET,
                                'normal': RENDER_NORMAL_WIDGET,
                                'super': RENDER_SUPER_WIDGET}

#-----------------------------------------------------------------------

# Local convenience function

def break_tuple(target, length):
    """ Pick all the elements from a tuple or list, defaulting
        rightmost values if given lenth greater that tuple length.

        A text string is treated as a single length tuple.

        Expect to be called as a, b, c = break_tuple(x, 3)
        """
    op = [None]*length
    if isinstance(target, types.StringTypes):
        op[0] = target
    else:
        for i in range(min(len(target), length)):
            op[i] = target[i]
    return op

#-----------------------------------------------------------------------

class RstWidget(LkWidget):
    """ The value is converted to HTML from ReST
    """

    def __init__(self, name, value=None, **kwargs):
        LkWidget.__init__(self, name, value=value, **kwargs)
        self._parsed = True
        self.destination_url = kwargs.get('destination', None)
        self.settings = {'halt_level':5}
        if kwargs.has_key('initial_header_level'):
            self.settings['initial_header_level'] = (
                kwargs['initial_header_level'])
        if kwargs.has_key('doctitle_xform'):
            self.settings['doctitle_xform'] = (
                kwargs['doctitle_xform'])
        self.text_width = kwargs.get('raw_text_width', 70)
        self.text_style = kwargs.get('raw_text_style', '>')
        
    def render_content(self):
        if self.value:
            p = publish_parts(
                convert_shebang(self.value,
                                text_width=self.text_width),
                writer_name='html',
                destination_path = self.destination_url,
                settings_overrides = self.settings)
            op = p['html_body']
        else:
            op = '&nbsp;'
        return op

#-----------------------------------------------------------------------

class HtmlWidget(LkWidget):
    """ Widget for entering a html string: corresponds to
   
        title : string. This is assumed to be valid HTML!

        the output text is held in the title variable 
    """

    def __init__(self, name, value=None, **kwargs):
        self.need_clear = kwargs.get('add_space_line', True)
        LkWidget.__init__(self, name, value, **kwargs)

    # overloaded to allow full width output
    def render(self):
        r = []
        class_name = '%s widget' % self.__class__.__name__
        self.attrs['class'] = class_name
        
        r.append(html.div(self.get_title(),
                          **{'class': class_name,
                             'style': "text-align:left"}))
        if self.need_clear:
            r.append(html.div(**{'class': 'space_line'}))
        return '\n'.join(r)
    
    def render_content(self):
        return None

#-----------------------------------------------------------------------

class SideBarWidget(HtmlWidget):
    """ Rename to allow different formatting
    """

    def __init__(self, name, value=None, **kwargs):
        HtmlWidget.__init__(self, name, value, **kwargs)
        self.need_clear = False

#-----------------------------------------------------------------------
