# Name:      lokai/tool_box/tb_forms/form_shapes.py
# Purpose:   Templates for various aspects of forms
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

from string import Template
from werkzeug import html

#-----------------------------------------------------------------------

EXPAND_SCRIPT = (u'onclick="var subtext = this.in'
                 'nerHTML.substring(2);for(i=1;i<5;i++){if(typeof t'
                 'his.parentNode.childNodes[i]==\'object\'){if(this'
                 '.parentNode.childNodes[i].tagName==\'DIV\'){if(th'
                 'is.parentNode.childNodes[i].style.display==\'none'
                 '\'){this.parentNode.childNodes[i].style.display='
                 '\'block\';this.innerHTML = \' - \' + subtext;}els'
                 'e{this.parentNode.childNodes[i].style.display=\'n'
                 'one\';this.innerHTML = \' + \' + subtext;}i+=5;}}};"')

# Note the render_unobtrusive_fieldset_closer function too
# For 'closed' field sets this should be added to the end  of the page
def render_expandable_field_set(**kwargs):
    """ Render a fieldset with optional added javascript for opening
        and closing.
    
        kwargs can consist of:

        expand    : None, False, 'open', 'close[d]'   : default None
                    None or False = not expanding
                    'open' = expanding shown open initially
                    else: expanding shown closed initially
        pretext   : text before fieldset      : default ''
        firsttext : first text in div         : default ''
        showntext : text before hidable div   : default ''
    """
    title = kwargs.get('title', None)
    expand = kwargs.get('expand', None)
    pretext = kwargs.get('pretext', '')
    firsttext = kwargs.get('firsttext', '')
    showntext = kwargs.get('showntext', '')
    border = kwargs.get('border', True)
    ret = []
    ret.append( u'%s' % pretext )
    class_list = ["lk_fieldset"]
    if border:
        class_list.append("lk_fieldset_border")
    style_text = ''
    
    ret.append(u"""<fieldset class='%s'%s>""" % (' '.join(class_list), style_text))
    if title or expand not in [None, False]:
        style_text = ''
        style_list = []
        expand_div = ''
        expand_text = ''
        if expand not in [None, False]:
            style_list.append('cursor:pointer')
            expand_text = " %s" % EXPAND_SCRIPT
            if expand == 'open':
                cur_state = 'block'
                title = u' - %s' % title
            else:
                cur_state = 'none'
                title = u' + %s' % title
            expand_div = (u'<div style="display:block" '
                                 'name="expand_%s">' % cur_state)
        if style_list:
            style_text = " style='%s'" % ';'.join(style_list)
        ret.append(u"<legend class='%s'%s%s>%s</legend>%s%s" % (
            ' '.join(class_list),
            style_text,
            expand_text,
            u'%s' % title,
            u'%s' % showntext,
            u'%s' % expand_div))
    ret.append(u'%s' % firsttext)
    return u"\n".join(ret)

def render_unobtrusive_fieldset_closer():
    return u'''<script type="text/javascript">
/* <![CDATA[ */
$(document).ready(function(){
    // Iterate the name="expand_none" elements and close them
    $("[name=expand_none]").css('display', 'none');
});
/* ]]> */
</script>'''
    
render_field_set = render_expandable_field_set

#-----------------------------------------------------------------------

def message_block(error_tup):
    return html.span(html(error_tup[0]),
                    **{'class': 'lokai_error',
                       'id': "%s_%s_message"% (str(error_tup[2]), str(error_tup[1]))
                       })

def hint_block(hint):
    if hint:
        return html.div(html(hint),
                        **{'class': 'hint'})
    return ''

def required_block(required):
    if required:
        return html.em(html('*'),
                         **{'class': 'required'}
                         )
    return ''
        
#-----------------------------------------------------------------------

def normal_widget(title,
                  name,
                  content,
                  hint,
                  error_tup,
                  required,
                  style,
                  additional):

    inner_set=[]
    inner_set.append(html.label(''.join([required_block(required),
                                       html(title) if title else '&nbsp']),
                              **{'class': 'lk_left_container',
                                 'for': name}))
    inner_set.append(''.join([content,
                              hint_block(hint)]))
    if error_tup and error_tup[0]:
        inner_set.append(html.span(message_block(error_tup),
                                  **{'class': 'lk_right_container'}))
    elif additional:
        inner_set.append(html.span(additional,
                                  **{'class': 'lk_right_container'}))
    
    return html.li(
        '\n  '.join(inner_set),
        **{'class': 'widget_row'})

def render_widget_normal(widget):
    '''
    Renders a 'normal' widget: 
    [ [ title ][ element ][ error ] ]
    '''
    return normal_widget(widget.get_title(),
                         widget.get_name(),
                         widget.render_content(),
                         widget.get_hint(),
                         widget.get_error_tup(),
                         widget.required,
                         widget.get_style(),
                         widget.get_additional(),
                         )

def wide_widget(title,
                name,
                content,
                hint,
                error_tup,
                required,
                style,
                additional):
    """
    """
    inner_set=['']
    inner_set.append(html.label(''.join([required_block(required),
                                       html(title) if title else '&nbsp']),
                              **{'class': 'lk_left_container',
                                 'for': name}))
    inner_set.append(''.join([content,
                              hint_block(hint)]))
    
    return html.li(
        '\n  '.join(inner_set),
        **{'class': 'widget_row'})

def render_widget_wide(widget):
    '''
    Renders a 'wide' widget:
    [ [ title ][      element       ] ]
    '''
    return wide_widget(widget.get_title(),
                         widget.get_name(),
                         widget.render_content(),
                         widget.get_hint(),
                         widget.get_error_tup(),
                         widget.required,
                         widget.get_style(),
                         widget.get_additional(),
                         )

# constants for widget's 'output' keyword attribute:

# normal:   [ [ title ][ element ][ error ] ]
RENDER_NORMAL_WIDGET = render_widget_normal

# wide:     [ [ title ][      element       ] ]
RENDER_WIDE_WIDGET = render_widget_wide

#-----------------------------------------------------------------------

def multi_column_widget(content_set,
                        style_set,
                        ):
    """ Draw multiple columns , trying to match the pattern of a
        normal form.  Used mostly for drawing sets of buttons on a
        form.

        content_set : content for each column

        style_set : optional style settings for corresponding column.

        Classes applied match up with the normal widget.
    """
    template = Template(
        "<div class='widget_row'>\n"
        "$row_text\n"
        "  <div class='space_line'></div>\n</div>\n"
        )
    column_template = Template(
        "<div class='$class'$style_text>$content</div>"
        )
    row_text = []
    _class = 'left_container'
    try:
        style_text = " style='%s'" % style_set[0]
    except IndexError:
        style_text = ''
    c = content_set[0]
    row_text.append(column_template.safe_substitute({'content': c,
                                                     'class': _class,
                                                     'style_text': style_text,
                                                     }))
    _class = "mid_container"
    for i in range(1, len(content_set)-1):
        try:
            style_text = " style='%s'" % style_set[i]
        except IndexError:
            style_text = ''
        c = content_set[i]
        row_text.append(column_template.safe_substitute({'content': c,
                                                         'class': _class,
                                                         'style_text': style_text,
                                                         }))
    i = len(content_set)-1
    _class = "right_container"
    try:
        style_text = " style='%s'" % style_set[i]
    except IndexError:
        style_text = ''
    c = content_set[i]
    row_text.append(column_template.safe_substitute({'content': c,
                                                     'class': _class,
                                                     'style_text': style_text,
                                                     }))
    return template.safe_substitute({'row_text': ''.join(row_text)})
       
#-----------------------------------------------------------------------

def row_widget(content_set,
               hint_set, 
               error_tup, 
               style_set,
               class_set=None):
    """ Build a row such that there is one div for each element in
        content set.

        content_set : list of displayable material

        hint_set : list of optional hint texts - there _must_ be one
            hint (possibly None) for each content item.

        error_tup : present for signature compatability - ignored.

        style_set : list of styles that can be applied to the
            corresponding content. Need be not as long as
            content. Remaining content is _not_ given a style.

        class_set : list of class names that can be applied to the
            correspoding content. Need be not as long as content. The
            last class found is applied to all remaining content.
    """
    template = Template(
        "<div class='widget_row'>\n"
        "$row_text\n"
        "  <div class='space_line'></div>\n</div>\n"
        )
    column = Template(
        "<div class='$class'$style_text>$content$hint_text</div>"
        )
    row_text = []
    for i in range(len(content_set)):
        c = content_set[i]
        try:
            h = hint_set[i]
        except IndexError:
            h = None
        _class = 'mid_container'
        if (class_set and
            isinstance(class_set, list) and
            len(class_set) > i and
            class_set[i]):
            _class = class_set[i]
        try:
            s = style_set[i]
            style_text = " style='%s'" % s
        except IndexError:
            style_text = ''
        row_text.append(column.safe_substitute({'content': c,
                                                'hint_text': hint_block(h),
                                                'class': _class,
                                                'style_text': style_text,
                                                }))
    return template.safe_substitute({'row_text': ''.join(row_text)})

#-----------------------------------------------------------------------

def field_set_widget(pretext, 
                     legend, 
                     firsttext,
                     content,
                     border=True,
                     expand=None):
    
    fieldset = {'border' : border,
                'expand' : expand
                }
    if pretext:
        fieldset['pretext'] = pretext
    if legend:
        fieldset['title'] = legend
    if firsttext:
        fieldset['firsttext'] = firsttext
    
    ret = []
    refs = render_expandable_field_set(**fieldset)
    if hasattr(refs, 's'):
        refs = refs.s
    ret.append(refs)
    if hasattr(content, 's'):
        content = content.s
    ret.append(content)
    if expand not in [None, False]:
        ret.append(u'</div>')
    ret.append(u'</fieldset><div class="space_line"></div>')
    return u'\n'.join(ret)

#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
