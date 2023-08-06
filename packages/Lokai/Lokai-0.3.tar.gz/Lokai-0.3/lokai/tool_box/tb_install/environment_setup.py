# Name:      lokai/tool_box/tb_install/environment_setup.py
# Purpose:   Create working directories and config files
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
    environment_setup takes a yaml description of any directories and
    their (text based) content that need to be present in the running
    environment.

    The module is executable, and it provides a function
    (process_setup) that can be called from other places (such as test
    scripts).

    When run against an environment that already exists any target
    text files that are found are renamed with a date. The facility
    does _not_ attempt to merge the content. Perhaps it should.
"""
#-----------------------------------------------------------------------

import sys
import yaml
import os
import datetime

#-----------------------------------------------------------------------

class AbandonExecution(Exception):
    pass

#-----------------------------------------------------------------------

def process_setup(source, working_directory='.'):
    """ Read the yaml source file.

        Prepend working_directory onto paths. Use os.path.join, so it
        is possible to override relative path with absolute, but you
        have to be explicit.
    """
    pwd = os.path.expanduser(working_directory)
    for arg_set in yaml.safe_load_all(source):
        for name, body in arg_set.iteritems():
            process_node(os.path.join(pwd, name), body)

def process_node(path, body):
    """ Recurse through the structure, creating things as we go.
    """
    if body == None:
        create_directory(path)
    elif not isinstance(body, type({})):
        create_file(path, body)
    else:
        create_directory(path)
        for name, new_body in body.iteritems():
            process_node(os.path.join(path, name), new_body)

def create_directory(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            raise AbandonExecution, \
                  "Directory path points to existing file: %s"%path
    else:
        os.makedirs(path)

def create_file(path, body):
    time_stamp = datetime.datetime.now()
    if os.path.exists(path):
        if os.path.isdir(path):
            raise AbandonExecution, \
                  "File path points to existing file: %s"%path
        dir,name = os.path.split(path)
        new_name = "%s.%s"% (name, time_stamp.strftime("%Y%m%d%H%M%S"))
        new_path = os.path.join(dir, new_name)
        os.rename(path, new_path)
    target = open(path,'w')
    target.write(body)
    target.close()

#-----------------------------------------------------------------------

if __name__ == '__main__':
    import optparse
    usage = ("Set up config files and working directories based on "
             "current or given working directory. Use stdin by default")
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-f', '--file', dest = 'source_file',
                      help="Name of file to process")
    parser.add_option('-w', '--working-directory',
                      dest='working_directory',
                      default='.',
                      help="Override working directory")
    (options, args) = parser.parse_args()
    if options.source_file:
        source = open(options.source_file)
    else:
        source = sys.__stdin__
    process_setup(source, options.working_directory)

#-----------------------------------------------------------------------
