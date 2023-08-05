#!/usr/bin/python
# Name:      lokai/lk_worker/sys_procs/lk_import_document.py
# Purpose:   Read a formatted multi-node document file.
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

"""
Read a reStructuredText file into one or more nodes
====================================================

The input file is an rst file that can be edited and run through rst
formatters, such as rst2pdf, in the normal way. This allows for
off-line editing and validation of texts that are intended for storage
in text nodes in the lk_worker database.

The input file contains control information, a control block, that
identifies the node to be updated. This control information is hidden
in a specifically structured comment block, so that it is invisible to
the rst processing.

A single file may contain text for more than one node.

Each node's worth of text consists of a control block, followed by the
text itself. The text is terminated by the end of the file or by the
next control block.

The control block looks like::

  ..
    nd_node:
      nde_name: some name text
      nde_type: text
      nde_client_reference: text
    parent: [list, of, parent, nodes]


The control block starts with a line containing 'nd_node:' and is
terminated by an empty line. The layout can be anything that conforms
to the YAML specification.

The allowed elements are:

  :nde_name: Required. Used to identify the node in the target hierarchy.

      If a node already exists with that name under the given parent
      path (see below) then that node is updated with the text from
      the input file. If the node does not exist, it is created.
      
  :nde_type: Optional. Defaults to 'text'.

      If the node exists and has a different type from the one given,
      then an error is raised.

  :nde_client_reference: A system wide unique reference. If the node
      exists, the existing client reference is overwritten with this
      value.

  :parent: Optional. The default is the root node given in the call to
      the program.

      The parent of a node can be specified as empty, a single name,
      or a path (string or list). The given path is appended to the
      root node given in the call to the program. The resulting path
      must result in a single parent node. The implication is that all
      expected elements must exist in order for the path to mean
      anything.

      - The path search works the same way as the UI, using
         search_filtered. Do not forget the '=' at the beginning of a
         string with a '/' delimted path.

      - The path search always starts from the top of the forest. That
         is the previous node in the input data is never assumed to be
         the parent of the node being processed.
      
"""

#-----------------------------------------------------------------------

import os
import re
import yaml

import logging
import lokai.tool_box.tb_common.configuration as config
import lokai.tool_box.tb_common.notification as notify
import lokai.tool_box.tb_common.dates as dates
from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_worker.extensions.extension_manager import (
    get_all_extensions,
    LK_REGISTER_TYPES_AND_MODELS)

from lokai.lk_worker.models import model
from lokai.lk_worker.nodes.graph import make_link
from lokai.lk_worker.nodes.data_interface import (get_node_dataset,
                                                  put_node_dataset)

from lokai.lk_worker.nodes.search import (find_from_string,
                                          find_in_path,
                                          find_nodes_by_client_references,
                                          )
from lokai.lk_worker.nodes.graph import top_trees

#-----------------------------------------------------------------------

doc_info_start = re.compile("\A *nd_node *:")

class DocumentImport(object):

    def __init__(self, file_name, root_tree):
        """ Process a single document file into its constituent nodes

            :file_name: the input file to be processed. Either text of
                file name, or a file-like object.

            :root_tree: list of candidates returned by
                find_from_string, or None

        """
        notify.info("Processing: %s under %s"%(file_name, root_tree))
        self.file_name = file_name
        self.root_tree = root_tree
        if hasattr(self.file_name, 'readline'):
            self.file_pointer = self.file_name
        else:
            self.file_pointer = open(self.file_name, 'r')

    def initialise_document(self):
        self.dox = [] # Current text store
        self.yml = [] # Current control data (text) store
        self.obj = {} # Current actual node data
        self.document_number += 1
        self.start_line = self.line_number
        
    def process(self):
        self.line_number = 0
        self.document_number = -1
        self.initialise_document()
        track = [] # keep track of lines for when we backtrack
        state = 'd' # Currently scanning document text
        for ln in self.file_pointer:
            # Read the whole file sequentially, noting what part of
            # the structure we are in using 'status'
            self.line_number += 1
            if state == 'd':
                if ln.rstrip() == '..':
                    track.append(ln)
                    state = 'c' # start comment
                else:
                    self.dox.append(ln)
            elif state == 'c':
                # We have started a comment, so look for the defining
                # content
                yml_match = doc_info_start.match(ln)
                if yml_match:
                    # found the first line of a yaml block. Flush existing
                    # document and collect the new yaml lines.
                    self.flush_document()
                    self.yml.append(ln)
                    state = 'y' # YAML block
                else:
                    # Not a yaml block afterall, so backtrack into document.
                    state = 'd'
                    self.dox.extend(track)
                    self.dox.append(ln)
                track = []
            elif state == 'y':
                if ln.startswith(' '):
                    # Continue collecting yaml lines until terminated by a
                    # line that does not begin with a space.
                    self.yml.append(ln)
                else:
                    state = 'd'
                    self.dox.append(ln)
        self.flush_document()

    def flush_document(self):
        if not self.yml:
            self.initialise_document()
            return # >>>>>>>>>>>>>>>>>>>>
        self.obj = yaml.safe_load(u''.join(self.yml))
        node_obj = self.obj['nd_node']
        notify.debug("The node header %s"%str(self.obj))
        # Put the current document into the node
        node_obj['nde_description'] = u''.join(self.dox)

        # Force a default node type
        if 'nde_type' not in node_obj:
            node_obj['nde_type'] = 'text'

        # Find the local parent for this node
        parent_path = str(self.obj.get('parent', '')) # yaml interprets numbers as numbers
        notify.debug("Local parent for node %s"%str(parent_path))

        # We must have a node name
        if 'nde_name' not in node_obj:
            notify.error("No nde_name in document "
                         "number %d starting at line %d" %
                         (self.document_number,
                          self.start_line))
            self.initialise_document()
            return # >>>>>>>>>>>>>>>>>>>>
        node_name = str(node_obj['nde_name']) # yaml interprets numbers as numbers
        immediate_parent = self.root_tree
        notify.debug("About to search global root %s"%str(immediate_parent))
        search_candidates = immediate_parent
        node_path = ['', '*']
        if immediate_parent is None:
            search_candidates = top_trees()
            node_path = ['']
        if parent_path:
            notify.debug(
                "Looking for local parent under global: %s" % search_candidates)
            immediate_parent = find_from_string(parent_path, search_candidates)
            search_candidates = immediate_parent
            node_path = ['', '*']
        if parent_path and not immediate_parent:
            notify.error("No parent found using %s in document "
                         "number %d starting at line %d" %
                         (parent_path,
                          self.document_number,
                          self.start_line))
            self.initialise_document()
            return # >>>>>>>>>>>>>>>>>>>>
        if immediate_parent and len(immediate_parent) > 1:
            notify.error("Too many parents found using %s in document "
                         "number %d starting at line %d" %
                         (parent_path,
                          self.document_number,
                          self.start_line))
            self.initialise_document()
            return # >>>>>>>>>>>>>>>>>>>>
        notify.debug("Final search candidates %s"%str(search_candidates))
        node_path.append(node_name)
        notify.debug("And looking for %s"%str(node_path))
        node_list = find_from_string(node_name, search_candidates)
        notify.debug("Giving found node %s"%str(node_list))
        if len(node_list) > 1:
            notify.error("Duplicate nodes %s found for %s + %s in document "
                         "number %d starting at line %d" %
                         (str(node_list),
                          parent_path,
                          node_name,
                          self.document_number,
                          self.start_line))
            self.initialise_document()
            return # >>>>>>>>>>>>>>>>>>>>
        client_ref_list = find_nodes_by_client_references(
            node_obj.get('nde_client_reference'))
        this_date = dates.now()
        node_obj['nde_date_modify'] = this_date
        if node_list:
            # Exists
            old_obj = get_node_dataset(node_list[0])
            if client_ref_list:
                if (len(node_list) > 1 or
                    node_list[0] !=  old_obj['nd_node']['nde_idx']):
                    notify.error("Client reference %s already in use"
                                 "found for %s + %s in "
                                 "document number %d "
                                 "starting at line %d" %
                                 (str(node_list),
                                  node_name,
                                  node_obj['nde_client_reference'],
                                  self.document_number,
                                  self.start_line))
                    self.initialise_document()
                    return # >>>>>>>>>>>>>>>>>>>>

            if old_obj['nd_node']['nde_type'] != node_obj['nde_type']:
                notify.error("Trying to change node type "
                             "for %s + %s in document "
                             "number %d starting at line %d" %
                             (parent_path,
                              node_name,
                              self.document_number,
                              self.start_line))
                self.initialise_document()
                return # >>>>>>>>>>>>>>>>>>>>
            notify.info("Existing node for %s + %s in document "
                        "number %d starting at line %d" %
                        (parent_path,
                         node_name,
                         self.document_number,
                         self.start_line))
            node_obj['nde_idx'] = node_list[0]
            put_node_dataset(self.obj, old_obj)
        else:
            if client_ref_list:
                notify.error("Client reference %s already in use"
                             "found for %s + %s in "
                             "document number %d "
                             "starting at line %d" %
                             (str(node_list),
                              node_name,
                              node_obj['nde_client_reference'],
                              self.document_number,
                              self.start_line))
                self.initialise_document()
                return # >>>>>>>>>>>>>>>>>>>>

            notify.info("New node for %s + %s in document "
                             "number %d starting at line %d" %
                             (parent_path,
                              node_name,
                              self.document_number,
                              self.start_line))
            node_obj['nde_date_create'] = this_date
            nde_idx = put_node_dataset(self.obj)
            if immediate_parent:
                make_link(nde_idx, immediate_parent[0])
        engine.session.flush() # so it can be picked up later on
        self.initialise_document()

#-----------------------------------------------------------------------

def main_():
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    parser.description = ("Read a ReStructuredText file (with control blocks) "
                          "and store the text in targetted nodes. Use a parent "
                          "node to search down from when identifying the "
                          "targetted nodes")
    parser.usage = "%prog [options] input_file [input_file]"
    parser.add_option('-p', '--parent',
                      dest = 'parent_id',
                      help = 'Client reference, IDX, path for the parent.'
                      ' Default None.',
                      )

    parser.add_option('-n', '--no-action', dest='ignore', action='store_true',
                      help='Do nothing with the database' )

    parser.add_option('-v', '--verbose',
                      dest = 'verbose',
                      help = "Request some feed back from the process",
                      action = 'count'
                      )
    parser.set_defaults(description="Created by make_node from the command line")

    config.handle_ini_declaration(prefix='lk')
 
    (options, args) = parser.parse_args() 

    log_level = {1:logging.WARNING,
                 2:logging.INFO,
                 3:logging.DEBUG
                 }
    notify.setLogName(
        os.path.splitext(
        os.path.basename(sys.argv[0]))[0])
    level = min(options.verbose, 3)
    logging.basicConfig(level=log_level.get(level,
                                             logging.ERROR))
    this_logger = notify.getLogger()
    this_logger.setLevel(level)
    target_handler = logging.StreamHandler()
    debug_logger = logging.getLogger(notify.getDebugName())
    debug_logger.addHandler(logging.StreamHandler())
    this_logger.addHandler(logging.StreamHandler())

    notify.info("Reading        : %s\n"
                "Options: Parent: %s" %
                (' '.join(args),
                 str(options.parent_id)))

    # configure these models
    model.init()
    get_all_extensions(LK_REGISTER_TYPES_AND_MODELS)

    parent_set = None
    if options.parent_id is not None:
        parent_set = find_from_string(options.parent_id)
        if not parent_set:
            parser.error("Parent ID did not find a parent")

    for argstring in args:
        if not os.path.exists(argstring):
            parser.error("File %s not found" % argstring)

    try:
        for argstring in args:
            di = DocumentImport(argstring, parent_set)
            di.process()
            if not options.ignore:
                engine.session.commit()        
    finally:
        engine.session.rollback()

    return 0 # Success?

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
