# -*- coding: utf-8 -*-
# Name:      lokai/tool_box/tb_common/rest_support.py
# Purpose:   Handle chunks of text as parts of a ReST document. 
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

import types
from docutils.core import publish_parts

from textwrap import fill

#-----------------------------------------------------------------------

default_text_width = 0

_headings = {'h1':'+',
             'h2':'-',
             'h3':'=',
             'h4':'~',
             'h5':'>',
             'h6':'<'
             }

def as_heading(heading, text, *kwargs):
    """ Make a heading element out of a single line of text.
    """
    return "%s\n%s\n\n"%(text, _headings[heading]*len(text))
    

#-----------------------------------------------------------------------

def as_raw_html(text, **kwargs):
    """ convert either text, or a list of lines into a raw html block.
    """
    if isinstance(text, types.StringTypes):
        lines = text.splitlines()
    else:
        lines = text
    op = ['.. raw:: html\n\n']
    op += ["  %s"%xx for xx in lines]
    return '\n'.join(op)

#-----------------------------------------------------------------------

def as_raw_text(text, **kwargs):
    """ convert either text, or a list of lines into a pre-formatted
        text block.
    """
    text_width = kwargs.get('text_width', default_text_width)
    text_style = kwargs.get('text_style', ' ')+' '
    if isinstance(text, types.StringTypes):
        lines = text.splitlines()
    else:
        lines = text
    op = ['::\n\n']
    if text_width > 0:
        op += [fill(xx,
                    text_width,
                    initial_indent = text_style,
                    subsequent_indent = text_style)
               for xx in lines]
    else:
        op += ["  %s"%xx for xx in lines] 
    return '\n'.join(op)

#-----------------------------------------------------------------------

def as_inline_link(text, link):
    """ put text and link together in the syntax for an in-line
        hypertext reference
    """
    return "`%s <%s>`_"%(text, link)

#-----------------------------------------------------------------------

def convert_shebang(text, **kwargs):
    """ If text is headed by #!xxx. interpret the xxx and return a
        ReST fragment.
    """
    if text and text.startswith('#!'):
        line_list = text.splitlines()
        line_1 = line_list[0]
        if line_1 == '#!rst':
            # Bit of a waste of time, this one, but we ought to
            # support it.
            return '\n'.join(line_list[1:])
        elif line_1 == '#!raw':
            # Make like an email system
            return as_raw_text(line_list[1:], **kwargs)
        elif line_1 == '#!html':
            # Force ReST raw output
            return as_raw_html(line_list[1:], **kwargs)
        else:
            # Just chuck it out anyway
            return text
    else:
        return text

#-----------------------------------------------------------------------

def as_published_html(text, **kwargs):
    """ Return html for direct output based on the content of text.

        Used for embedded texts, so basically assumes ReST.
    """
    destination_url = kwargs.get('destination', None)
    settings = {'halt_level': 5}
    if 'initial_header_level' in kwargs:
        settings['initial_header_level'] = (
            kwargs['initial_header_level'])
    if 'doctitle_xform' in kwargs:
        settings['doctitle_xform'] = (
            kwargs['doctitle_xform'])

    if text:
        p = publish_parts(
                convert_shebang(text,
                                **kwargs),
                writer_name='html',
                destination_path = destination_url,
                settings_overrides = settings)

        return p['html_body']
    return '<!-- empty text -->'

#-----------------------------------------------------------------------
# Provide an api for creating ReST tables

class RstTableCreate(Exception):
    pass

class RstTableEmpty(RstTableCreate):
    pass

class RstTableSpanClash(RstTableCreate):
    pass

class RstTable(object):
    """ Create a table object that will render as text using the rst
        grid layout markup. You can then pass this rendered version to
        an rst reader/writer combo to get HTML, PDF or whatever.

        Use:

        :obj.cell: to add cells to the table

        :obj.span: to merge cells in rectangles

        :obj.render: to get the rst text output
        
    """

    def __init__(self):
        self.rows = {}
        self.col_width = {}
        self.row_height = {}
        self.col_min = None
        self.col_max = None
        self.span_set = []
        self.heading_row = None

    def _capture_max_min(self, col):
        self.col_max = max(col, self.col_max)
        self.col_min = ((self.col_min is not None and min(col, self.col_min)) or
                        col)
        
    def span(self, col1, row1, col2, row2):
        """ Create a rectangle of merged cells.

            :col1:

            :row1: are the top left cell of the rectangle


            :col2:

            :row2: are the bottom right of the rectangle

            See 'cell' below for inserting content.

            Creating a span over cells that have content results in
            merging the conent.
        
        """
        mc1, mr1, mc2, mr2 = self.match_span(col1, row1)
        if mc1:
            raise RstTableSpanClash, "%s, %s falls inside %s, %s" % (
                col1, row1, mc1, mr1)
        mc1, mr1, mc2, mr2 = self.match_span(col2, row2)
        if mc1:
            raise RstTableSpanClash , "%s, %s falls inside %s, %s" % (
                col2, row2, mc1, mr1)       
        self.span_set.append((col1, row1, col2, row2))
        self._capture_max_min(col1)
        self._capture_max_min(col2)
        
    def cell(self, col, row, content):
        """ Place a cell in the table

            :col:

            :row: are the positon of the cell, 'one' based.              

              There is no need to predefine the table size. The
              eventual table size is deduced from the maximum row or
              column numbers.

              Cell 1,1 is at the top left and the table expands left
              and down.

              Implied cells that have no content are rendered as empty
              cells, as might be expected.

              To insert content into a merged rectangle (see 'span'
              above), simply refer to the col/row for the top left
              corner.

            :content: is a text string.

              White space is not trimmed off.
              
              If the content is a single line (no line breaks within
              it, the cell will be rendered in rst to fit all the
              content on a single line.

              If the content contains line breaks the cell will be
              rendered in rst as a multi line cell with corresponding
              line breaks. If you need an empty line between text
              parts to get rst to render the page properly, then
              include two line breaks in the appropriate places.
              
        """
        if row not in self.rows:
            self.rows[row] = {}
        if content is not None:
            content_lines = content.split('\n')
        else:
            content_lines = ''
        self.rows[row].update({col: content_lines})
        for line in content_lines:
            self.col_width[col] = max(len(line),
                                      self.col_width.get(col, 0))
        self._capture_max_min(col)
        self.row_height[row] = max(len(content_lines),
                                   self.row_height.get(row, 0))

        
    def render(self):
        if self.col_max == None:
            raise RstTableEmpty
        
        table_out = []
        for row in sorted(self.rows.keys()):
            table_out.append(self.render_row(row))
        head_out = []
        for col in range(self.col_min, self.col_max+1):
            head_out.append(self.render_separator(col, row, 'left', 'top'))
        table_out.append(u'%s+'% ''.join(head_out))
        return u'\n'.join(table_out)
    
    def render_row(self, row):
        row_set = []
        head_out = []
        for col in range(self.col_min, self.col_max+1):
            col_pos, row_pos = self.check_span(col, row)
            head_out.append(
                self.render_separator(col, row, col_pos, row_pos))
        row_set.append(u"%s+"%''.join(head_out))
        for row_line in range(self.row_height[row]):
            row_out = []
            for col in range(self.col_min, self.col_max+1):
                col_pos, row_pos = self.check_span(col, row)
                row_out.append(
                    self.render_full_cell(col, row, row_line, col_pos, row_pos))
            row_set.append(u'%s|'%''.join(row_out))
        return u'\n'.join(row_set)
    
    def render_full_cell(self, col, row, row_line, col_pos, row_pos):
        left_char = (col_pos == 'left' and u'|') or u' '
        content_set = self.rows[row].get(col, [u''])
        if row_line < len(content_set):
            content = content_set[row_line]
        else:
            content = u''
            
        return u'%s%s%s'% (left_char,
                          content,
                          u' '*(self.col_width.get(col, 1) - len(content)))

    def render_separator(self, col, row, col_pos, row_pos):
        if row_pos =='top':
            row_sep = u'-'
            if self.heading_row and row == self.heading_row+1:
                row_sep = u'='
            fill_string = row_sep*self.col_width.get(col, 1)
            left_char = u'+'
        else:
            fill_string = u' '*self.col_width.get(col, 1)
            if col_pos == 'left':
                left_char = u'+'
            else:
                left_char = u' '
        return u'%s%s'% (left_char, fill_string)

    def match_span(self, col, row):
        for col1, row1, col2, row2 in self.span_set:
            if (row >= row1 and row <= row2 and
                col >= col1 and col <= col2):
                # found a span
                return col1, row1,  col2, row2
        return None, None, None, None
    
    def check_span(self, col, row):
        """ return col position, row position in respect of a defined
            span
        """
        col1, row1, col2, row2 = self.match_span( col, row)
        if col1:
            col_pos = ((col == col1 and 'left') or
                       (col == col2 and 'right') or
                       'mid')
            row_pos = ((row == row1 and 'top') or
                       (row == row2 and 'bottom') or
                       'mid')
            return col_pos, row_pos
        return 'left', 'top'

#-----------------------------------------------------------------------
