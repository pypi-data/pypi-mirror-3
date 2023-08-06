#!/usr/bin/python
# Name:      lokai/tool_box/tb_common/tb_ccss_cat.py
# Purpose:   Concatenate a set of CleverCSS fiels and produce CSS out.
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

import os
import types
from cStringIO import StringIO
from optparse import OptionParser, TitledHelpFormatter
import ordereddict
import clevercss

from lokai.tool_box.tb_common.import_helpers import get_module_path

#-----------------------------------------------------------------------

class Engine(clevercss.Engine):

    def merged_rules(self, context=None):
        """ Merge the rules so that there is only one instance for each
            selector.

            Merging is done by converting a rule set into an ordered
            dictionary and using that to update any previous entry for
            the same selector. The result should preserve the ordering
            of items in a rule set except where the update adds a new
            entry.
        """
        op = ordereddict.OrderedDict()
        for selectors, defs in self.evaluate(context):
            # Join multiple selectors together in a comma separated list
            select_string = u',\n'.join(selectors)
            # Convert the declarations into a dictionary
            def_dict = ordereddict.OrderedDict(defs)
            # Update an existing entry, or add a new entry
            try:
                op[select_string].update(def_dict)
            except KeyError:
                op[select_string] = def_dict
                
        for s, r in op.iteritems():
            yield s, r

    def to_css(self, context=None):
        """ Generate the resulting css string """
        blocks = []
        for select_string, def_dict in self.merged_rules(context):
            block = []
            block.append(select_string + ' {')
            for key, value in def_dict.iteritems():
                block.append(u'  %s: %s;' % (key, value))
            block.append('}')
            blocks.append(u'\n'.join(block))
        return u'\n\n'.join(blocks)

#-----------------------------------------------------------------------

def get_file_path(given_path):
    elements = []
    head, tail = os.path.split(given_path)
    elements.append(tail)
    while head:
        head, tail = os.path.split(head)
        elements.append(tail)
    elements.reverse()
    module = elements[0]
    print elements
    try:
        module_path = get_module_path(module)
    except ImportError:
        module_path = module
    if len(elements) > 1:
        op_path = os.path.join(module_path, *elements[1:])
    else:
        op_path = module_path
    return op_path

class StringBucket(object):

    def __init__(self):
        self.bucket = StringIO()

    def append(self, given_path):
        fp_is_open = False
        if isinstance(given_path, types.StringTypes):
            fp = open(get_file_path(given_path))
            fp_is_open = True
        else:
            fp = given_path # Assume it is an open file
        try:
            block = fp.read()
            while block:
                self.bucket.write(block)
                block = fp.read()
        finally:
            if fp_is_open:
                fp.close()

    def getvalue(self):
        return self.bucket.getvalue()

#-----------------------------------------------------------------------
EXAMPLE_FILE_NAME = 'lokai.lk_ui.ui_default.static/lokai_css.txt'

if __name__ == '__main__':
     parser = OptionParser(formatter=TitledHelpFormatter())
     parser.description = (
         "Convert one or more CleverCSS input files into a single CSS "
         "output. Where necessary, blocks of rules for each set of "
         "selectors are merged so that there is one rule-set for each "
         "selector set. The file paths given on the comand line may "
         "start as a python module reference. In such a case the module "
         "reference is replaced by the path to the module.")

     options, argset = parser.parse_args()

     sb = StringBucket()
     for ff in argset:
         sb.append(ff)
     ee = Engine(sb.getvalue())
     print ee.to_css()

#-----------------------------------------------------------------------
