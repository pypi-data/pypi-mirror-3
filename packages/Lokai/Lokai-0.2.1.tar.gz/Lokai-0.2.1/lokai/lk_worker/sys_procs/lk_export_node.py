#!/usr/bin/python
# Name:      lokai/lk_worker/sys_procs/lk_export_node.py
# Purpose:   Find a node and export it
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

# Find one or more nodes and print a serialisation to stdout

#-----------------------------------------------------------------------

import yaml
import base64

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_common.configuration import handle_ini_declaration
from lokai.tool_box.tb_common.dates import timetostr

from lokai.lk_worker.extensions.extension_manager import (
    get_all_extensions,
    LK_REGISTER_TYPES_AND_MODELS)

from lokai.lk_worker.models import model
from lokai.lk_worker.models.builtin_data_attachments import make_version
from lokai.lk_worker.nodes.data_interface import get_node_dataset
from lokai.lk_worker.nodes.search import find_from_string
from lokai.lk_worker.nodes.graph import child_trees

#-----------------------------------------------------------------------

class ExportSuite(object):
    """ Holds the output file!
    """

    def __init__(self, sink):
        if hasattr(sink, 'write'):
            self.fp = sink
        else:
            self.fp = open(sink, 'w')

    def export_node(self, candidate, parent):
        """ Export this node recursively - assume full permissions because
            this is a data management thing.
        """
        export_data = {'nd_node': {}}
        node_data = get_node_dataset(candidate)
        # get_node_dataset returns a single object or a list of objects in
        # ['nd_node'] which is the result of a query. If we ever change
        # that query to produce a different structre we are in trouble.
        response_set = node_data['original_result']
        if not isinstance(response_set, (list, tuple)):
            response_set = [response_set]
        for data_object in response_set:
            if data_object:
                object_name = data_object.__class__.__name__
                target_object = {}
                for ident in data_object.keys():
                    target_object[ident] = data_object[ident]
                export_data['nd_node'][object_name] = target_object
        if 'attachments' in node_data:
            nda_set = []
            # This is a AttachmentCollection
            for nda in node_data['attachments'].get_in_sequence():
                export_nda = {'base_location': nda.base_location,
                              'other_location': nda.other_location,
                              'description': nda.description,
                              'content_type': nda.content,
                              'uploaded_by': nda.user_name,
                              'file_name': nda.file_name,
                              'file_version': make_version(nda.version),
                              'upload_time': nda.timestamp
                              }
                file_source = nda.get_target_path()
                file_content = open(file_source).read()
                file_string = base64.b64encode(file_content)
                export_nda['file_content'] = file_string
                nda_set.append(export_nda)
            export_data['attachments'] = nda_set
        export_data['parent'] = parent
        # Export as a single list element to look like part of a longer
        # list
        yaml.dump([export_data], self.fp)
        child_set = child_trees(candidate)
        for child in child_set:
            self. export_node(child, candidate)

#-----------------------------------------------------------------------

def main_():
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    parser.description = ("Export one or more nodes using node name "
                          "(with wild cards) or a path. Use a parent "
                          "node to search down from")
    parser.usage = "%prog [options] node_criterion [node_criterion]"
    parser.add_option('-p', '--parent',
                      dest = 'parent_id',
                      help = 'Client reference, IDX path for the parent.'
                      ' Default None.',
                      )

    parser.add_option('-v', '--verbose',
                      dest = 'talk_talk',
                      help = "Request some feed back from the process",
                      action = 'count'
                      )
    parser.set_defaults(description="Created by make_node from the command line")

    handle_ini_declaration(prefix='lk')
 
    (options, args) = parser.parse_args() 

    if options.talk_talk:
        print "Seeking        : %s"%' '.join(args)
        print "Options: Parent: %s"%str(options.parent_id)


    # configure these models
    model.init()
    get_all_extensions(LK_REGISTER_TYPES_AND_MODELS)

    parent_set = None
    if options.parent_id is not None:
        parent_set = find_from_string(options.parent_id)
        if options.talk_talk:
            print "Parents:", parent_set
        if not parent_set:
            parser.error("Parent ID did not find a parent")

    candidates = []
    for argstring in args:
        candidates.extend(find_from_string(argstring, parent_set))

    if options.talk_talk and not candidates:
        print "No candidates found for the given arguments"
    
    for candidate in candidates:
        exp = ExportSuite(sys.stdout)
        exp.export_node(candidate, None)

    return 0 # Success?

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
