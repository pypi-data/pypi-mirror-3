# Name     : tool_box/tb_database/migration_tools.py
# Copyright: 
# Purpose  : Manage database migration 
# Notes    : Taking passed database names and versions
#            manage the upgrade/downgrade of the respective database(s)
# 
#-----------------------------------------------------------------------

""" Database migration - capabilities

    Report on the version status of databases, including whether the
    physical database exists and whether the schema is under version
    control.

    Upgrade to a given version of a database, creating the physical
    database if needed.

    Downgrade to a given version of a database.

    Clean a database by downgrading to version zero before uprading to
    a given version.

    Clean a database by dropping the physical database before
    upgrading to a given version.

    Notes:

    - The drop database capability understands that multiple schemas
      may use the same physical database and will avoid dropping the
      database twice in a single run by comparing database
      url. However, the order of specification of databases is
      significant and it is still possible to upgrade a schema in a
      particular physical database and subsequently drop that same
      database in rlation to another schema.

    - Migration of some databases may depend on the existence of other
      databases. Many databases use sequences, for example, which have
      to be defined in the login database. It is important to ensure
      that databases are upgraded in the correct order.

    - The version control repository for each database must be
      findable.  This can be managed through the following steps:

          Use the module path given explicitly when instantiating the
          DBController. This module path must, when imported, lead to
          a directory that contains the path
          `section/database/manage.py`

          Look for a module path through the configuration file entry
          `migrate-module` under the appropriate section.  This works
          the same way as an explicit module.

          Look for a hint using the configuration file entry `module`
          under the appropriate section.  The directory where this
          module is found is used as a starting point. The tree is
          searched upwards to find a directory path `xxx/migration` on
          the assumption that this will produce a valid path
          `xxx/migration/section/database/manage.py`

     **FIX ME**

     Drop database does not work correctly - there is a database
     connection left open that prevents the drop from happening.
"""

#-----------------------------------------------------------------------

import sys
import os
from subprocess import Popen
import ConfigParser

import migrate.versioning.api

import sqlalchemy
import psycopg2.extensions as pg

from lokai.tool_box.tb_common.configuration import (
    get_global_config,
    get_global_config_file,
    )

#-----------------------------------------------------------------------

def _make_subprocess_command(element_set):
    """ Given a list of elements that make up a potential command
        line, build in some common parts
    """
    op = ['python'] # to start with
    op.append(element_set[0]) # add in the python module to execute
    op.extend(element_set[1:]) # and put the others on
    return op

#-----------------------------------------------------------------------

def find_possible_module(module_path):
    """ Given a module name, find a file path that appears that it
        might possbly contain migration scripts. Any path found is not
        evaluated explicitly to test for versions.

        Searches back up the tree from whatever file is picked up by
        the given module. Does not do any searches down any branch.

        Search limited to the extent of the dotted module path itself
        so we don't go back too far.
    """
    while module_path:
        try:
            module = __import__(module_path)
            if hasattr(module, '__file__'):
                module_dir = os.path.split(module.__file__)[0]
                migrate_dir = os.path.join(module_dir, 'migration')
                if os.path.isdir(migrate_dir):
                    return migrate_dir # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        except:
            pass
        if module_path and module_path.find('.') > -1:
            module_path = '.'.join(module_path.split('.')[:-1])
        else:
            module_path = None

#-----------------------------------------------------------------------
#
# Useful for finding the path to the __init__ file
def get_target_file(name):
    #
    # name : string. Dot separated import name.
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod.__file__

#-----------------------------------------------------------------------

class DBController(object):
    """ Provides access to mechanisms that can be used to build other
        tools and processes for creating, cleaning and migrating a
        database.

        Initialise with...

        section = section or group wthin the configuration file

        database = name of database within that section

        module = dotted module name that points to the top of the
                 migrate tree for this database. If not given, use
                 "databasename.migrate" from config file or search from
                 "module" in config file.
    """

    def __init__(self, **kwargs):
        self.error = []
        self.section = kwargs.get('section')
        self.database = kwargs.get('database')
        self.module = kwargs.get('module')
        self.tablespace = kwargs.get('tablespace')
        self.requested_version = kwargs.get('request')
        if self.requested_version and self.requested_version != 'max':
            try:
                self.requested_version = int(self.requested_version)
            except ValueError:
                self.error.append(
                    "Database %s.%s: Invalid requested version %s"%(
                        self.section,
                        self.database,
                        self.requested_version))
                self.requested_version = None
        self.url = None
        self.task = kwargs.get('task')
        self.migrate_command = None
        self.dbstats = None
        self.current_version = None
        self.available_version = None

        configuration = get_global_config()

        try:
            name_part = configuration[self.section][self.database]
            try:
                self.url = name_part['url']
            except KeyError:
                self.url = None
                self.error.append(
                    "Database %s.%s does not have a url"%(self.section,
                                                          self.database))
        except KeyError:
            self.url = None
            self.error.append(
                "Database %s.%s does not have a section"%(self.section,
                                                      self.database))
        if not self.error:
            if not self.module:
                self.module = configuration[self.section].get("migrate-module")
            if self.module:
                migration_directory = os.path.dirname(get_target_file(self.module))
            else:
                possible_module =  configuration[self.section].get('module')
                migration_directory = find_possible_module(possible_module)
                if not migration_directory:
                    self.error.append(
                        "No 'module' defined for section %s"%self.section)
                    migration_directory = None
            if migration_directory:
                manager = os.path.join(migration_directory,
                                       self.section,
                                       self.database)
                if os.path.exists(manager) and os.path.isdir(manager):
                    target_file = os.path.join(manager, 'manage.py')
                    if os.path.isfile(target_file):
                        self.migrate_command = os.path.abspath(target_file)
                    else:
                        self.error.append(
                            "Directory %s does not contain manager program"%manager)
                else:
                    self.error.append("Directory %s does not exist"%manager)
            else:
                self.error.append(
                    "Could not find a migration command for %s.%s"%
                    (self.section,
                     self.database))

        if not self.error:
            self.get_db_stats()

            if (self.requested_version and
                self.requested_version != 'max' and
                self.requested_version > self.available_version):
                self.error.append(
                    "Request for version %s "
                    "exceeds available version %s"%(self.requested_version,
                                                   self.available_version)
                    )

    #-------------------------------------------------------------------
    
    def db_drop(self):
        """ Drop the specified database """
        # Issues the command "drop database" - needs to be connected
        # to template01
        assert self.url[:8] == 'postgres', (
            "URL %s is not a postgres url"%self.url)
        (baseurl, db) = self.url.rsplit('/', 1)
        postgresurl = baseurl + '/postgres'
        e = sqlalchemy.create_engine(postgresurl, echo=False, echo_pool=False)
        c = e.connect()
        c.detach()
        c.connection.set_isolation_level(pg.ISOLATION_LEVEL_AUTOCOMMIT)
        c.execute("drop database %s;" % db) 

    def db_create(self):
        """ Create the specified database """
        # Issues the command "create database" - needs to be connected
        # to template01
        assert self.url[:8] == 'postgres', (
            "URL %s is not a postgres url"%self.url)
        (baseurl, db) = self.url.rsplit('/', 1)
        postgresurl = baseurl + '/postgres'
        e = sqlalchemy.create_engine(postgresurl, echo=False, echo_pool=False)
        c = e.connect()
        c.detach()
        c.connection.set_isolation_level(pg.ISOLATION_LEVEL_AUTOCOMMIT)
        if not self.tablespace:
            c.execute("create database %s with "
                "encoding = 'UTF8';" % db)
        else:
            c.execute("create database %s with "
                "encoding = 'UTF8' tablespace = %s ;" % (db, self.tablespace))

    #-------------------------------------------------------------------

    def test_db_exists(self):
        """ Use the url to open the migrate_version table. Error responses
            are used to return:

            0 = db exists and the version table exists.

            1 = db exists but version table does not.

            2 = db does not exist.

        """
        try:
            engine = sqlalchemy.create_engine(self.url,
                                              echo=False,
                                              echo_pool=False)
            connection = engine.connect()
            connection.detach()
            try:
                res = connection.execute("select * from migrate_version "
                                   "where repository_id='%s';"%self.database)
                row_set = res.fetchall()
                if len(row_set):
                    self.dbstats = 0
                else:
                    self.dbstats = 1
            except sqlalchemy.exc.ProgrammingError:
                text = str(sys.exc_info()[1])
                if "not exist" in text:
                    self.dbstats = 1
                else:
                    raise
        except sqlalchemy.exc.OperationalError:
            text = str(sys.exc_info()[1])
            if "not exist" in text:
                self.dbstats = 2
            else:
                raise
        return self.dbstats

    def get_db_stats(self):
        """ Execute the given migrate command with appropriate arguments
            to find out what version the database is at and what the
            maximum available version is.

            Returns dictionary:
              db_stat: 0,1,2 returned from test_db_exists
              current: the current version
              available: the maximum available version
        """
        assert self.migrate_command and os.path.isfile(self.migrate_command), (
            "Invalid migration command file %s" % str(self.migrate_command))
        repository_path = os.path.dirname(self.migrate_command)
        self.test_db_exists()
        if self.dbstats == 0:
            res = migrate.versioning.api.db_version(self.url, repository_path)
            self.current_version = res
        else:
            self.current_version = 0
        res = migrate.versioning.api.version(repository_path)
        self.available_version = res
        sqlalchemy.pool.clear_managers()
        
    #-------------------------------------------------------------------

    def get_full_migration_sequence(self):
        """ Return command elements that can be executed to provide the
            appropriate upgrade or downgrade command.

            A list of zero to 2 commands can be returned. Each command is
            itself represented by a list of elements. The commands
            returned are;

                drop the database
                create the database
                place database under version control
                downgrade to zero
                upgrade or downgrade
        """
        op = []
        current_version = self.current_version
        url = self.url
        db_exists = self.dbstats
        task = self.task
        if task == 'base':
            if db_exists != 2:
                #Database exists, so drop it
                op.append(['internal',
                           'drop',
                           url
                           ])
            db_exists = 2 # after the drop
        if db_exists == 2:
            # need to create
            op.append(['internal',
                       'create',
                       url
                       ])
            op.append(_make_subprocess_command([self.migrate_command,
                                                'version_control'
                                                ]))
            current_version = 0
            db_exists = 1 # need to create the version table !
        elif task == 'tables':
            if db_exists == 1:
                op.append(_make_subprocess_command([self.migrate_command,
                                                    'version_control'
                                                    ]))
                db_exists = 0 # After all this
            op.append(_make_subprocess_command([self.migrate_command,
                                                "downgrade",
                                                "--version=%s" % '0'
                                                ]))
            current_version = 0
        if db_exists == 1:
            op.append(_make_subprocess_command([self.migrate_command,
                                                'version_control'
                                                ]))
            db_exists = 0 # finally
        # -- database cleaning now done - think about the version change    
        requested_version = self.requested_version
        if requested_version == 'max':
            requested_version = self.available_version
        if requested_version > self.available_version:
            raise ValueError(
                "Requested version %s is above "
                "max version %s for database %s:%s" % (
                    str(requested_version),
                    str(self.db_stats['available']),
                    str(self.section),
                    str(self.database)))
        if current_version < requested_version:
            proc = _make_subprocess_command([self.migrate_command, "upgrade"])
            if requested_version != self.available_version:
                proc.append("--version=%s" % str(requested_version))
            op.append(proc)
        elif current_version > requested_version:
            proc = _make_subprocess_command([self.migrate_command, "downgrade"])
            proc.append("--version=%s" % str(requested_version))
            op.append(proc)
        return op

    #-------------------------------------------------------------------
    
    def run_processes(self, do_actions, process_list, url_remove, url_create):
        """ Given a list of things to do - go do them.

            url_remove and url_create are lists that keep a history of
            remove and create actions and allow communication between
            the item and the collection. This recognises that database
            items are mutually dependent if they share the same
            physical database.
        """
        for process in process_list:
            if do_actions:
                if process[0] != 'internal':
                    Popen(process).wait()
                else:
                    if process[1] == 'drop':
                        if not process[2] in url_remove:
                            self.db_drop()
                            url_remove.append(process[2])
                    elif process[1] == 'create':
                        if not process[2] in url_create:
                            self.db_create()
                            url_create.append(process[2])
            else:
                print process
        #--done

#-----------------------------------------------------------------------

class DBCollection(object):
    """ A collection of DBController objects. The collection provides
        common constructs for reporting on and manipulating the
        associated databases.
    """

    def __init__(self, **kwargs):
        self.data = [] # ordered set of DBControllers
        self.default_task = kwargs.get('task')
        self.default_version = kwargs.get('request')
        self.do_actions = kwargs.get('do_actions', True)

    def build_from_list(self, db_list):
        """ Construct the collection from a given list of
            databases. Each database is represented by a database
            descriptor dictionary that has a task and version
            associated. This constructor is deliberately separated
            from any command line interface that may be built.
        """
        for db_entry in db_list:
            dbc_obj = DBController(section = db_entry['section'],
                                   database = db_entry['database'],
                                   task = db_entry.get('task'),
                                   request = db_entry.get('request')
                                   )
            self.data.append(dbc_obj)
        #-- done

    def get_errors(self):
        op = []
        for dbc in self.data:
            if dbc.error:
                error_text = "\n".join(dbc.error)
                op.append("==== %s.%s:%s=%s at %s ===="%(dbc.section,
                                                   dbc.database,
                                                   str(dbc.task),
                                                   str(dbc.requested_version),
                                                   str(dbc.url))
                          )
                op.append(error_text)
        return '\n'.join(op)

    def process_tasks(self):
        """ Do the tasks for the items in the list.
        """
        url_remove = [] # remember deletions and creations
        url_create = []
        for dbc in self.data:
            p = dbc.get_full_migration_sequence()
            dbc.run_processes(self.do_actions, p, url_remove, url_create)
        #-- done

    def report_status(self):
        """ Print out the current state of all databases.
        """
        for dbc in self.data:
            status_text = ''
            if dbc.dbstats == 2:
                status_text = "<database does not exist> "
            elif dbc.dbstats == 1:
                status_text = "<database not under version control> "
            print "%s.%s at %s %s%s <= %s" % (dbc.section,
                                            dbc.database,
                                            str(dbc.url),
                                            status_text,
                                            str(dbc.current_version),
                                            str(dbc.available_version))

#-----------------------------------------------------------------------
