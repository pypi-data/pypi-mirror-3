# Name:      lokai/tool_box/tb_database/orm_interface.py
# Purpose:   Manage global SQL Alchemy environment
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

import sqlalchemy
import sqlalchemy.orm as orm

from lokai.tool_box.tb_common.configuration import get_global_config
import lokai.tool_box.tb_common.notification as notify

#-----------------------------------------------------------------------

class DatabaseError(Exception):
    """Primary error class for the underlying database class"""
    pass

class DatabaseInitialisation(DatabaseError):
    pass

#-----------------------------------------------------------------------

# Make the global scoped session.

Session = sqlalchemy.orm.scoped_session(
    sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False))

#-----------------------------------------------------------------------

CreateEngineArgs = ('convert_unicode',
                   'connect_args',
                   'creator',
                   'echo',
                   'echo_pool',
                   'encoding',
                   'execution_options',
                   'label_length',
                   'listeners',
                   'logging_name',
                   'max_overflow',
                   'module',
                   'pool',
                   'poolclass',
                   'pool_logging_name',
                   'pool_size',
                   'pool_recycle',
                   'pool_timeout',
                   'strategy',
                   )

#-----------------------------------------------------------------------

class EngineHandler(object):

    """
    The EngineHandler object provides a single point of access for an
    SQL Alchemy scoped session.

    The session is available accross an entire application. This makes
    it possible to manage database transactions across all parts of an
    application.

    The handler is able to open multiple databases at once. Each
    database is connected to an engine.

    This version of the handler is linked to a common configuration
    file format. Each major section of the configuration file contains
    one or more [database] sections. Within each [database] section
    there is one (and only one) 'name' item, and one (and only one)
    'connect' item. The 'name' item is used to link the application to
    the connection.

    Use:
    >>># Import the engine handler
    >>>from lokai.tool_box.tb_database.orm_interface import engine
    >>># Do things with the session
    >>>query_object = engine.session.query(orm_object)

    The engine object is initialised by the ORMRegistry (above)

    Initialising the engine is controlled by the arguments to
    sqlalchemy.create_engine. The values for these arguments are
    extracted from the relevant entry in the configuration file. These
    entries, if specified, have the same name as the corresponding
    argument to sqlalchemy.create_engine.

    """
    
    def __init__(self):
        self.engines = {}
        self.session = Session

    def get_engine(self, section=None, name=None):
        """ Entry point for creating the engine.

            Assumes the config object is available somewhere.
        """
        if not self.engines.get(section, {}).get(name, None):
            if section and name:
                # Try to create the engine from config
                self.build_engine(section, name)
            else:
                raise DatabaseInitialisation, (
                       "Configuration section or database  name not provided")
        if self.engines.get(section, {}).get(name, None):
            return self.engines[section][name]
        return None

    def build_engine(self, section=None, db_name=None):
        """ Read the config file and assign engines """
        if not db_name:
            return None
        try:
            engine_dict = get_global_config()[section][db_name]
        except KeyError:
            raise DatabaseInitialisation, (
                "Unrecognised database name %s:%s"%(section, db_name))
        engine_url = engine_dict['url']
        engine_args = {}
        # Need to copy the relevant items across- sqlalchemy will
        # complain if it does not recognise an argument name, and we
        # might want to include other entries in the configuration.
        for arg_name in CreateEngineArgs:
            if arg_name in engine_dict:
                engine_args[arg_name] = engine_dict[arg_name]
        engine = sqlalchemy.create_engine(engine_url, **engine_args)
        if engine:
            # Engine started successfully
            if not self.engines.get(section, None):
                self.engines[section] = {}
            self.engines[section][db_name] = engine
        else:
            raise ValueError(
                "Engine not created for %s:%s" % (section,
                                                  db_name))
        return None

    def dispose(self):
        """ Close the session and dispose of each engine """
        self.session.close_all()
        for section in self.engines.itervalues():
            for engine in section.itervalues():
                engine.dispose()

#-----------------------------------------------------------------------

engine = EngineHandler()

#-----------------------------------------------------------------------

class OrmRegistry(object):
    """
    Database model.
    
    Registers ORM mappings classes <-> database tables.

    Delays the real mapping with SQLAlchemy until explicitly
    requested.

    Databases are named internally using a two tier convention derived
    from the idea that applications can be added to the universe in
    groups, and each group might have one or more database. This is
    reflected in the assumed configuration file format where one
    section may define a number of databases.
    
    Usage:
    >>> # create a registry for each database:
    >>> model = ORMRegistry('login', 'login_db')
    >>> # register each ORM object
    >>> model.register(classUser, 'user_table')
    ...
    >>> # initialise all of the models, by initialising any one of them: 
    >>> model.init()
    >>> # all of the newly created models will be auto-initialised
    >>> # this can also be achieved by ORMRegistry.init_models()
    """
    
    # list of registries [usually per database]
    _instances = []
    # should newly created registries initialise themselves?
    _auto_initialize = False
    
    def __init__(self, section, db_name):
        """ Creates a ORM class registry for the database specified in
            the config file under db_name in section
        """
        self.mappings = []
        self.mappers = [] # sqlalchemy.orm.Mapper objects
        self.metadata = None
        self.section = section
        self.db_name = db_name
        self._instances.append(self)
        if self._auto_initialize:
            self.init()

    @classmethod
    def init_models(cls):
        """ Initializes all models defined so far, and make future
            models auto initialize themselves
        """
        if not cls._auto_initialize:
            # it is important to set it first, as registries will call this
            # method again if it _auto_initialize is False
            cls._auto_initialize = True
            for registry in cls._instances:
                registry.init()

    def map_class_to_table(self, cls, tablename):
        table = sqlalchemy.Table(tablename, self.metadata)
        self.mappers.append(orm.mapper(cls, table))
        
    def register(self, cls, tablename):
        self.mappings.append((cls, tablename))
        if self.metadata:
            self.map_class_to_table(cls, tablename)
    
    def init(self):
        """ Initializes this model - and all other models defined, as
            well.
        """
        if not self.metadata:
            notify.debug('Initialise %s:%s'%(self.section, self.db_name))
            engine_obj = engine.get_engine(self.section,
                                           self.db_name)
            if not engine_obj:
                raise ValueError(
                    "Engine not found for %s:%s" % (self.section,
                                                    self.db_name))
            self.metadata = sqlalchemy.MetaData(bind=engine_obj, reflect=True)
            for (cls, tablename) in self.mappings:
                self.map_class_to_table(cls, tablename)
            self.__class__.init_models()

    def reload(self):
        """ Clear out any existing registrations and start
            over. Useful for testing.
        """
        for mapper in self.mappers:
            mapper.dispose()
        self.mappers = []
        if self.metadata:
            self.metadata.clear()
        self.metadata = None
        self.init()

#-----------------------------------------------------------------------
