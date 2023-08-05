# Name:      lokai/tool_box/tb_install/yaml_import.py
# Purpose:   Basic extendable class that supports reading a yaml file
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

#-----------------------------------------------------------------------
import sys
import os
import yaml

import logging

import lokai.tool_box.tb_common.notification as notify
import lokai.tool_box.tb_common.dates as dates
from lokai.tool_box.tb_database.orm_interface import engine

#-----------------------------------------------------------------------

class YamlImport(object):
    """ Management of file read process and distribution of processing
        according to the main nodes of the file structure.

        The file to be imported is structured as one or more yaml
        documents - each document is a dictionary - each entry in the
        dictionary is some data to be processed. The keys to the
        dictionary are used to identify the code to be used to handle
        the data contained in that node.

        The input data:

        - The input uses yaml text formatting.

          See http://yaml.org/spec/1.1/#id857168

        - The input may be divided into more than one document (using
          '---').

          The data is commited to the database at the end of each yaml
          document.

        This management class is designed as a mixin to work with data
        specific classes. The data specific class must call
        self.register(...) for each data processor corresponding to
        top-level data names in the input yaml file.
    """

    def __init__(self, **kwargs):
        """ kwargs:

            file = file name or pointer to open file

            ignore = True to work through the file and not commit to the
                   database


            Assume that logging has already been set up
        """
        
        self.file = kwargs.get('file')
        if not self.file:
            notify.info("Using STDIN")
            self.file = sys.stdin
        else:
            notify.info("Using %s"%str(self.file))
        self.ignore = kwargs.get('ignore', False)
        self.time_now = dates.now()
        self.process_map = {}
        self.process_name = None

        if hasattr(self.file, 'readline'):
            self.file_pointer = self.file
        else:
            self.file_pointer = file(self.file)

    def process_all(self):
        """ Run through the file, processing documents and nodes as
            they are found.

            The process is separate from __init__ becasue the mixin
            needs to be built before processing starts.
        """
        for arg_set in yaml.safe_load_all(self.file_pointer):
            if not arg_set: continue
            for self.process_name, process_data in arg_set.iteritems():
                self.process_map.get(
                    self.process_name, self.process_default)(process_data)

            if not self.ignore:
                # commit the updates
                notify.info("Committing changes through session")
                engine.session.commit()

    def process_default(self, process_data):
        notify.error(
            "Process node %s is not supported"% self.process_name)

    def register(self, process_name, process_method):
        """ Register a new process method.

            A process method must be a class method from an
            inheriting class, and must take the data to be
            processed as argument.
        """
        self.process_map[process_name] = process_method

#-----------------------------------------------------------------------
