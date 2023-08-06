#!/usr/bin/python
# Name:      lokai/tool_box/tb_database/tb_migrate.py
# Purpose:   Creates clean databases, or changes versions of databases
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

""" Main program providing a command line interface to migration tools.

    Usage: python db_migrate [options] db_list

    Options:

    -f --file Defines the path to a configuration file. If this is not
            given the default mechanisms are used.

    -c --check Initiates a report on all the databases (see db_list)
            showing physical database status, current version and
            maximum available version.

    -r --roll-back Initiates a one line report that can be used as
            arguments to this program to reproduce the current state.

    -n --no-calls Inhibits actual actions on all or any
            database. Commands that would be executed are printed out.

    -t --task A default task that will apply to all database in this
            run, but only if the databases are extracted from the
            configuration file. (see db_list).

    -v --version A default requested version that will apply to all
            database in this run, but only if the databases are
            extracted from the configuration file. (see db_list).

    db_list

        This is a list of database references of the form:

            section.database:task=nn

            section.database=nn

            section.database

        where:

            :section: is the section or group in the configuration file

            :database: is the name of the database

            :task: is one of 'base' (drop the database first) or
              'tables' (downgrade to zero first).

            :nn: is the requested version number. Set the value to
              'max' to request the maximum available version. If the
              request is greater than the current version then the
              database is upgraded. If it is less than the current
              version the database is downgraded. If the database has
              been cleared down using 'base' or 'tables' then the
              database is upgraded.

"""

#-----------------------------------------------------------------------

import sys
import os
import UserDict

from optparse import OptionParser, TitledHelpFormatter

import lokai.tool_box.tb_common.configuration as config

from lokai.tool_box.tb_database.migration_tools import DBCollection

#-----------------------------------------------------------------------

def make_and_create(options, db_set):

    manager = DBCollection(task = options.task,
                          request = options.version,
                          do_actions = not options.no_calls
                          )
    manager.build_from_list(db_set)
    etxt = manager.get_errors()
    if not etxt:
        if options.report_roll_back:
            op = []
            for dbc in manager.data:
                append_str = (
                    "%s.%s=%d"%(dbc.section,
                                dbc.database,
                                dbc.current_version)
                    )
                op.append(append_str)
            print ' '.join(op),
            sys.exit(0)
        elif options.report_current:
            manager.report_status()
            sys.exit(0)
        else:
            manager.process_tasks()
            sys.exit(0)
    else:
        print etxt
        sys.exit(0)
    
def eval_db_options(db_list, configuration):
    db_descriptor_set = []
    is_ok = True
    for db_ref in db_list:
        request = None
        task = None
        if db_ref.find('=') > -1:
            db_ref, request = db_ref.split('=')
        if db_ref.find(':') > -1:
            db_ref, task = db_ref.split(':')
        if db_ref.find('.') > -1:
            section, db_name = db_ref.split('.')
        else:
            print >> sys.stderr, (
                 "Invalid database reference %s - "
                 "there must be a section and a name "
                 "separated by '.' (dot)"%db_ref)
            is_ok = False
        if is_ok:
            db_descriptor_set.append(
                make_db_descriptor(
                    configuration,
                    section, db_name, task, request
                    )
                )

    if is_ok:
        return db_descriptor_set
    else:
        return None

def get_db_config_set(configuration, options):
    db_descriptor_set = []
    
    for section, section_value in configuration.iteritems():
        for db_name, name_value in section_value.iteritems():
            if (isinstance(name_value, (dict,UserDict.UserDict)) and
                'url' in name_value):
                db_descriptor_set.append(
                    make_db_descriptor(
                        configuration,
                        section, db_name, options.task, options.version
                        )
                    )
    return db_descriptor_set

def make_db_descriptor(configuration, section, db_name, task, request):
    db_desc = {}
    db_desc['section'] = section
    db_desc['database'] = db_name
    db_desc['task'] = task
    db_desc['request'] = request
    return db_desc
                             
#-----------------------------------------------------------------------

def main_():
    parser = OptionParser(formatter=TitledHelpFormatter())
    parser.description = ("Migrate databases from one version to another, "
                          "up or down. For new starts, or for testing, databases "
                          "can be dropped and created or downgraded to zero "
                          "before any upgrade.")

    parser.epilog = ('Each database definition takes the form "section.db_name", '
                     '"section.db_name=nn", or "section.db_name:task=nn". '
                     'The nn is the target version. The task is one of "base" '
                     '(drop/create the database) or "tables" '
                     '(downgrade to version zero first).')
    
    parser.add_option('-f', '--file', dest = 'config_file',
                      default = None,
                      action = 'store',
                      help = 'Provide a path to a configuration file')

    parser.add_option('-n', '--no-calls', dest = 'no_calls',
                      default = False,
                      action = 'store_true',
                      help = 'Do nothing with any database '
                             '- report on commands that would be done')
    
    parser.add_option('-c', '--current', dest = 'report_current',
                      default = False,
                      action = 'store_true',
                      help = ('Do nothing with any database '
                              '- report on the status of all databases'))
    
    parser.add_option('-r', '--roll-back', dest = 'report_roll_back',
                      default = False,
                      action = 'store_true',
                      help = ('Do nothing with any database '
                              '- produce a roll-back argument set'))
    
    parser.add_option('-t', '--task', dest = 'task',
                      default = False,
                      action = 'store',
                      help = 'Default task for use when no databases are given')
    
    parser.add_option('-v', '--version', dest = 'version',
                      default = False,
                      action = 'store',
                      help = ("Defaut version for use when no databases "
                              "are given. Normally 'max'" ))
    
    parser.add_option('-d', '--database', dest = 'database_set',
                      default = None,
                      action = 'append',
                      help = 'Optional - Explicitly select a database as '
                      '"section.database" '
                      '- use option as many times as needed. '
                      'Positional arguments doe the same thing. If no databases '
                      'are provided then all databases in the current '
                      'configuration file are used.')
    
    (options, argset) = parser.parse_args()    

    if options.config_file:
        filename = os.path.abspath(options.config_file)
        if not os.path.isfile(filename):
            print >> sys.stderr, "Given config file not found - %s"%filename
            sys.exit(1)
        config.set_ini_file(filename)
    config.handle_ini_declaration(prefix='lk')

    configuration = config.get_global_config()

    db_list = []
    if options.database_set:
        db_list = options.database_set
    if argset:
        db_list.extend(argset)

    if options.task and not options.task in ['base', 'tables']:
        print >> sys.stderr, "Task must be one of 'base' or 'tables'"
        sys.exit(1)
    
    db_set = eval_db_options(db_list, configuration)

    if db_set == None:
        sys.exit(1)
        
    if len(db_set) == 0:
        db_set = get_db_config_set(configuration, options)

    if not db_set:
        print >> sys.stderr, "No databases found to create"
        sys.exit(1)
    make_and_create(options, db_set)

    return 0 # Success?

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
