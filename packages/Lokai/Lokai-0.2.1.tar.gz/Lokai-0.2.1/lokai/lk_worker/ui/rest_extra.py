# Name:      lokai/lk_worker/ui/rest_extra.py
# Purpose:   Add some useful directives and roles.
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
from docutils import nodes
from docutils.parsers import rst
from lokai.tool_box.tb_common.rest_support import as_published_html

from lokai.lk_worker.ui.local import url_for

#-----------------------------------------------------------------------

from docutils.parsers.rst.directives.images import Image, Figure
from docutils import nodes
from docutils.parsers.rst import directives, states
from docutils.nodes import fully_normalize_name, whitespace_normalize_name
from docutils.parsers.rst.roles import set_classes

#-----------------------------------------------------------------------

# Match 'a b c <x y z>' or 'a b c x y z'
URI_FIND = re.compile("(?P<txt>.*)<(?P<uri>.*)>|(?P<uri2>.*)")

def find_uri(given_string):
    """ Split given string into URI and text parts.

        Return tuple (URI, text) where text might be empty.
    """
    match_obj = URI_FIND.match(given_string)
    if not match_obj:
        return (None, None)
    res = match_obj.groupdict()
    if res['uri2'] is not None:
        return (res['uri2'].strip(), None)
    return (res['uri'].strip(), res['txt'].strip())
    
#-----------------------------------------------------------------------

class PageImage(Image):

    def run(self):
        if 'align' in self.options:
            if isinstance(self.state, states.SubstitutionDef):
                # Check for align_v_values.
                if self.options['align'] not in self.align_v_values:
                    raise self.error(
                        'Error in "%s" directive: "%s" is not a valid value '
                        'for the "align" option within a substitution '
                        'definition.  Valid values for "align" are: "%s".'
                        % (self.name, self.options['align'],
                           '", "'.join(self.align_v_values)))
            elif self.options['align'] not in self.align_h_values:
                raise self.error(
                    'Error in "%s" directive: "%s" is not a valid value for '
                    'the "align" option.  Valid values for "align" are: "%s".'
                    % (self.name, self.options['align'],
                       '", "'.join(self.align_h_values)))
        messages = []
        link, display = find_uri(' '.join(self.arguments))
        reference = self.make_uri(link)
        self.options['uri'] = reference
        reference_node = None
        if 'target' in self.options:
            block = states.escape2null(
                self.options['target']).splitlines()
            block = [line for line in block]
            target_type, data = self.state.parse_target(
                block, self.block_text, self.lineno)
            if target_type == 'refuri':
                reference_node = nodes.reference(refuri=data)
            elif target_type == 'refname':
                reference_node = nodes.reference(
                    refname=fully_normalize_name(data),
                    name=whitespace_normalize_name(data))
                reference_node.indirect_reference_name = data
                self.state.document.note_refname(reference_node)
            else:                           # malformed target
                messages.append(data)       # data is a system message
            del self.options['target']
        set_classes(self.options)
        image_node = nodes.image(self.block_text, **self.options)
        if reference_node:
            reference_node += image_node
            return messages + [reference_node]
        else:
            return messages + [image_node]

class PageFigure(Figure):

    def run(self):
        figwidth = self.options.pop('figwidth', None)
        figclasses = self.options.pop('figclass', None)
        align = self.options.pop('align', None)
        (image_node,) = PageImage.run(self)
        if isinstance(image_node, nodes.system_message):
            return [image_node]
        figure_node = nodes.figure('', image_node)
        if figwidth == 'image':
            if PIL and self.state.document.settings.file_insertion_enabled:
                # PIL doesn't like Unicode paths:
                try:
                    i = PIL.open(str(image_node['uri']))
                except (IOError, UnicodeError):
                    pass
                else:
                    self.state.document.settings.record_dependencies.add(
                        image_node['uri'])
                    figure_node['width'] = i.size[0]
        elif figwidth is not None:
            figure_node['width'] = figwidth
        if figclasses:
            figure_node['classes'] += figclasses
        if align:
            figure_node['align'] = align
        if self.content:
            node = nodes.Element()          # anonymous container for parsing
            self.state.nested_parse(self.content, self.content_offset, node)
            first_node = node[0]
            if isinstance(first_node, nodes.paragraph):
                caption = nodes.caption(first_node.rawsource, '',
                                        *first_node.children)
                figure_node += caption
            elif not (isinstance(first_node, nodes.comment)
                      and len(first_node) == 0):
                error = self.state_machine.reporter.error(
                      'Figure caption must be a paragraph or empty comment.',
                      nodes.literal_block(self.block_text, self.block_text),
                      line=self.lineno)
                return [figure_node, error]
            if len(node) > 1:
                figure_node += nodes.legend('', *node[1:])
        return [figure_node]

#-----------------------------------------------------------------------

URI_SPLIT = re.compile("(?P<obj1>.*)/file/(?P<file>.*)|(?P<obj2>.*)")

def find_file(given_string):
    """ Assume the given string is a URI, split the string if possible
        into an object reference and a target file reference.

        Return tuple (object, file) where file is None if there is no
        file.
    """
    match_obj = URI_SPLIT.match(given_string)
    if not match_obj:
        return (None, None)
    res = match_obj.groupdict()
    if res['obj2'] is not None:
        return (res['obj2'], None)
    else:
        return (res['obj1'], res['file'])

def render_page(text, request, **kwargs):
    """ Render the text using reStructuredText with some extra roles """
    
    def make_page_url(link):
        """ Build one of two possible url responses """
        object_id, file_name = find_file(link)
        if object_id == '#':
            object_id = request.routing_vars.get('object_id')
        if not object_id:
            return None
        if not file_name:
            url = url_for('default', {'object_id': object_id})
        else:
            url = url_for('get_file', {'object_id': object_id,
                                       'file_path': file_name})
        return url

    def directive_page(name, arguments, options, content, lineno,
                     content_offset, block_text, state, state_machine):
        """ Support for a directive that inserts a link into a new
            paragraph on the page.

            Usage::

                .. page:: target

            or::

                .. page:: text <target>

            where

            :target: is either a node identifier by itself, or a node
                identifier with a filename appended. (MyPage or
                MyPage/file/attachment_file).

                The special target '#' refers to the current page.

            :text: is an optional piece of text that will appear in the
                output document as the link.

            The link is made to the relevant page in the lk_worker
            hierarchy.

        """
        link, display = find_uri(' '.join(arguments))
        url = make_page_url(link)
        display = display if display else link
        #
        #
        if url:
            reference = nodes.reference(block_text, display)
            reference['refuri'] = url
            pgf = nodes.paragraph()
            pgf += reference
            return [pgf]
        else:
            warning = state_machine.reporter.warning(
                    '%s is not a valid page reference' % (arguments[0]),
                    nodes.literal_block(block_text, block_text),
                    line=lineno)
            return [warning]

    directive_page.arguments = (1,1,1)
    rst.directives.register_directive('page', directive_page)

    class LocalPageImage(PageImage):
        """ Allow the .. image:: directive to take a reference to
            something in a node.

            The allowed URIs are the same as for the .. page::
            directive.
        """
        def make_uri(self, link):
            return make_page_url(link)

    class LocalPageFigure(LocalPageImage):
        """ Allow the .. figure:: directive to take a reference to
            something in a node.

            The allowed URIs are the same as for the .. page::
            directive.
        """
        pass

    rst.directives.register_directive('page_img', LocalPageImage)
    rst.directives.register_directive('page_fig', LocalPageFigure)

    def role_page(name, rawtext, text, lineno, inliner, options={},
                          content=[]):
        """ Define a role for a page link. A link is inserted inline in
            the output text.

            This looks like::

                :page:`target`

            where target is as for the directive, above.

        """
        link, display = find_uri(text)
        url = make_page_url(link)
        display = display if display else link
        #
        #
        if url:
            reference = nodes.reference(rawtext, display)
            reference['refuri'] = url
            return [reference], []
        else:
            warning = nodes.warning(None, nodes.literal_block(text,
                'WARNING: %s is not a valid page reference' % rawtext))
            return warning, []
        
    rst.roles.register_local_role('page', role_page)

    return as_published_html(text, **kwargs)

#-----------------------------------------------------------------------
