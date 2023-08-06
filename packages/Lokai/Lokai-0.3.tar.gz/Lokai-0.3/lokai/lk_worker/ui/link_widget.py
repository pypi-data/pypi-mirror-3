# Name:      lokai/lk_worker/ui/link_widget.py
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

from lokai.tool_box.tb_forms.widget import Widget
from lokai.tool_box.tb_forms.form_shapes import field_set_widget
from lokai.lk_worker.ui.widget import CompositeWidget, ButtonRow, RowWidget
from lokai.lk_worker.ui.local import url_for

#-----------------------------------------------------------------------
    
class LinkWidget(Widget):
    """Creates a link that can be used to go places - use instead of buttons.
    
       kwargs['target'] : named target to be used by url_for

       kwargs['url_parts'] : dictionary of data values to be
           substituted for named placeholders in the target.

           Unrecognised items in ul_parts are appended as a query. 
       """

    HTML_TYPE = "link"
    
    def __init__(self, name, value=None, **kwargs):
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
        return {'path': url_for(self.target, self.url_parts),
                'value': self.value,
                'class': 'LinkWidget'
                }

    def make_href(self):
        if self.attrs.has_key('disabled'):
            return self.value
        else:
            path = url_for(self.target, self.url_parts)
            return html.a(self.value,
                          **{'class': 'LinkWidget',
                             'href': path})

    def render_content(self):
        return self.make_href()

class LinkUpWidget(LinkWidget):

    def render_content(self):
        op = []
        href_value = self.make_href()
        if href_value and href_value != '&nbsp;':
            op.append(html.span('Up:',
                                **{'class': "%sPrefix" % self.__class__.__name__}))
        op.append(href_value)
        return html.div(''.join(op),
                        **{'class': 'LinkWidgetContainer'}) 
        
class LinkLeftWidget(LinkWidget):

    def render_content(self):
        op = []
        href_value = self.make_href()
        if href_value and href_value != '&nbsp;':
            op.append(html.span('Left:',
                                **{'class': "%sPrefix" % self.__class__.__name__}))
        op.append(href_value)
        return html.div(''.join(op),
                        **{'class': 'LinkWidgetContainer'}) 
        
class LinkRightWidget(LinkWidget):

    def render_content(self):
        op = []
        href_value = self.make_href()
        if href_value and href_value != '&nbsp;':
            op.append(html.span('Right:',
                                **{'class': "%sPrefix" % self.__class__.__name__}))
        op.append(href_value)
        return html.div(''.join(op),
                        **{'class': 'LinkWidgetContainer'}) 
        
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

# Selection displays requires a slightly different table widget from
# the one given in tool_box. An alternative version that uses links
# instead of buttons is given here.

#-----------------------------------------------------------------------

class TableWidget(CompositeWidget):

    def __init__(self, name, value=None, fieldset={}, tableset={}, **kwargs):
        '''        
        fieldset {} : contains fieldset parameters if this
        widget is to be drawn as a fieldset.
        
        tableset {} : contains tableset parameters to define and
        manage the tableset itself.
        
        tableset parameters:
        
           btf_pages () : for each page link, a tuple containing a
                          name, a target and an optional query.
           
           btf_enabled () : for each entry in the tuple:
        
                                True -> the relevant link from
                                btf_pages is enabled
        
                                False -> the relevant link from
                                btf_pages is shown, but disabled

           heading_set [] : a list of (name, text, target, query) tuples
                            to use as headings for the columns. If not
                            given, there are no column headings. If it
                            is given, the headings are created out of
                            links. If target is not given, query must
                            also be not given, and the link is
                            disabled.
        
                            If given, there must be a heading for
                            every column
        
        The body of the widget must be a composite widget with the
        name 'body' that contains all rows of the table.  The body
        widget might reasonably be a CompositeWidget without the
        fieldset boundary and legend.
        
        The caller must add RowWidgets to the body widget as required.
        
        '''
        CompositeWidget.__init__(self, name, value,
                                 fieldset=fieldset,
                                 tableset=tableset,
                                 **kwargs)

        # Start by building a BTF line
        btf_enabled = tableset.get('btf_enabled', (True, True, True))
        btf_pages = tableset.get('btf_pages', [])
        self.add(ButtonRow, 'btf')
        btf_widget=self.get_widget('btf')
        for i in range(len(btf_pages)):
            v, t, u, q = break_tuple(btf_pages[i], 4)
            btf_widget.add(LinkWidget, 'btf_%03d'%i, v,
                           target = t,
                           url_parts = u,
                           query = q,
                           disabled=(not btf_enabled[i]))
        # Optionally, build a header line
        heading_set = tableset.get('heading_set', None)
        if heading_set:
            self.add(RowWidget, 'headings')
            head_widget = self.get_widget('headings')
            for h in heading_set:
                n, v, t, u, q = break_tuple(h, 5)
                head_widget.add(LinkWidget, n, v,
                                target = t,
                                url_parts = u,
                                query = q,
                                disabled = t is None)

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
        btf_widget=self.get_widget('btf')
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
        return '\n'.join(op)

#-----------------------------------------------------------------------
