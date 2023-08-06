#!/usr/bin/python
# Name:      lokai/tool_box/tb_job_manager/tb_print_job_tree.py
# Purpose:   Print out the tree of connected jobs based on cofiguration.
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

from optparse import OptionParser, TitledHelpFormatter

from lokai.tool_box.tb_job_manager.utils import ParamFile

#-----------------------------------------------------------------------

class doTree(object):

    def __init__(self, file_list):
        self.file_list = file_list
        self.tree = {}
        self.found = {'source': {},
                      'processed': {},
                      'output': {}
                      }
        for file in self.file_list:
            try:
                self._gather(file)
            except KeyError:
                continue
        for job_name, content in self.tree.iteritems():
            self._try_parent(job_name, content)
        for job_name, content in self.tree.iteritems():
            if not 'parent_set' in content or not content['parent_set']:
                print "==>"
                self.print_tree(job_name, content)
            
    def _gather(self, file):
        job_name = os.path.basename(file)
        x_globals = {}
        content = {}
        execfile(file, x_globals, content)
        base = content['environment_path']
        #
        #
        self.tree[job_name] = content
        #
        #
        self._add_s_files('source', job_name, base,
                          content.get('source_path', '*empty*'))
        #
        self._add_o_files('processed', job_name, base,
                          content.get('processed_path'))
        #
        self._add_o_files('output', job_name, base,
                          content.get('output_path'))

    def _add_s_files(self, dest, job_name, path, given_name):
        if given_name is None:
            return
            #>>>>>>>>>>>>>>>>>>>>
        name_set = given_name
        if isinstance(name_set, types.StringTypes):
            name_set = [given_name]
        for name in name_set:
            env_name = name
            if name != '*empty*':
                env_name = os.path.join(path, name)
            if env_name in self.found[dest]:
                
                print "'%s' file %s used in %s and %s" % (
                    dest, env_name, self.found['s'][env_name], job_name)
            else:
                self.found[dest][env_name] = job_name

    def _add_o_files(self, dest, job_name, path, given_name):
        if given_name is None:
            return
            #>>>>>>>>>>>>>>>>>>>>
        name_set = given_name
        if isinstance(name_set, types.StringTypes):
            name_set = [given_name]
        for name in name_set:
            env_name = os.path.join(path, name)
            detail = self.found[dest].get(env_name, [])
            detail.append(job_name)
            self.found[dest][env_name] = detail

    def _link_parent(self, parent_set, dest, job_name, source):
        if parent_set:
            for parent in parent_set:
                if 'child_set' not in self.tree[parent]:
                    self.tree[parent]['child_set'] = {}
                self.tree[parent]['child_set'][job_name] = (dest, source)
                if 'parent_set' not in self.tree[job_name]:
                    self.tree[job_name]['parent_set'] = []
                self.tree[job_name]['parent_set'].append(parent)
        
    def _try_parent(self, job_name, content):
        base = content['environment_path']
        source_list = content.get('source_path', '*empty*')
        if isinstance(source_list, types.StringTypes):
            source_list =[source_list]
        for source in source_list:
            env_name = os.path.join(base, source)
            parent_set = []
            candidate = self.found['processed'].get(env_name)
            self._link_parent(candidate, 'processed', job_name, source)
            candidate = self.found['output'].get(env_name)
            self._link_parent(candidate, 'output', job_name, source)

    def print_tree(self, job_name, content, using= None, indent=''):
        
        op = [indent, job_name]
        if using:
            op.append(" (From: %s: %s)" % using)
        print ''.join(op)
        indent += '    '
        child_set = content.get('child_set', {})
        for child, link_block in child_set.iteritems():
            self.print_tree(child, self.tree[child], link_block, indent)

#-----------------------------------------------------------------------

DEFAULT_GENERAL_PARAM_FILE = 'job_environment.conf'
DEFAULT_PARAM_DIRECTORY = 'job_environment.d'

def main_():
    parser = OptionParser(formatter=TitledHelpFormatter())
    parser.description = ("Given a set of job parameter files print a tree "
                          "or trees of jobs that are connected by taking "
                          "input from one or other of the outputs from some "
                          "other job. The job parameter files are found in "
                          "a similar way to that used by the JobEnvironment "
                          "object, so that by default the command can be run "
                          "from the working directory of an application set. ")
    parser.epilog = ("The tree produced may not be the one actually used. It "
                     "is possible to add a parameter file to a job at run "
                     "time and this command cannot know about this.")

    parser.add_option('-g', '--general-configuration',
                      dest='general_param_file',
                      action='store',
                      help=("Path to the general job parameter file. "
                            "If given, this file should contain an "
                            "'app_param_path' entry that defines where "
                            "the job parameter files are kept. "
                            "[Default %s]"%DEFAULT_GENERAL_PARAM_FILE)
                      )
    parser.add_option('-p', '--param-directory',
                      dest='app_param_path',
                      help=("Path to a directory where application parameter "
                            "files can be found. If given, this parameter "
                            "overrides any settings in the general "
                            "configuration. [Default %s]"%DEFAULT_PARAM_DIRECTORY)
                      )
    (options, argset) = parser.parse_args()
    general_param_file = options.general_param_file
    if not general_param_file:
        if os.path.exists(DEFAULT_GENERAL_PARAM_FILE):
            general_param_file = DEFAULT_GENERAL_PARAM_FILE

    target_dir = options.app_param_path
    if not target_dir:
        target_dir = DEFAULT_PARAM_DIRECTORY
        if general_param_file:
            job_conf = ParamFile(general_param_file)

            if hasattr(job_conf, 'app_param_path'):
                target_dir = job_conf.app_param_path

    if os.path.isdir(target_dir):
        param_files = os.listdir(target_dir)
        param_files = [os.path.join(target_dir, x) for
                       x in param_files if (x[-1] != '~' and
                                            x[-4:] != '.txt' and
                                            x[0] != '.')]
        if param_files:
            doTree(param_files)
        else:
            print "No job parameter files in %s"%target_dir
    else:
        print "No job parameter directory %s"%target_dir

    return 0 # Success?

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
