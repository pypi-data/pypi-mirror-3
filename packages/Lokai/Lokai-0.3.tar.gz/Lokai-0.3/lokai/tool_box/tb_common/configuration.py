# Name:      lokai/tool_box/tb_common/configuration.py
# Purpose:   Reads a configuration file
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
   Set up an internal, global, representation of the configuration
   file. This is mostly about finding the name of the file to load,
   and subsequently loading it.

   We use ConfigParser internally, parsed and structured to look like
   a dictionary.

   We are assuming that there is one and only one configuration file
   for the running program instance. This seems reasonable, as the
   configuration defines the instance.

   The actual identification of the file is done somewhere 'out there'
   in the application. See handle_ini_declaration, below.

   In general, the application needs only:

       handle_ini_declaration(filename)

             Identify and open the required file

             If filename is not given the function searches for *.ini
             in the current working directory. If one and only one is
             found, open it, if there is more than one, look for a
             single file starting with a given prefix (case
             insensitive), else raise an error.

             Because ConfigObj allows this, you can also pass in a
             list of text lines or a StringIO object. This function
             does not check what is passed in, it simply forwards it
             (via the global __config_file__) to ConfigObj.

       get_global_config()

             Pick up the ConfigObj

   If defaults are needed, set a ConfigObj validation file.
"""
#-----------------------------------------------------------------------

import sys
import UserDict
import os.path
import ConfigParser

#-----------------------------------------------------------------------

__all__ = ('handle_ini_declaration',
           'get_ini_declaration',
           'set_ini_file',
           'set_global_config_file', 
           'set_global_config_default', 
           'get_global_config',
           )

#-----------------------------------------------------------------------

class ConfigurationSection(UserDict.IterableUserDict):
    """ An object that contains zero, one or more option values, and
        zero, one or more sub-sections.

        A subsection is identified when the name of an option contains
        a dot. The text before the dot is the subsection name, and the
        text after the dot is the new option name.

        A subsection is an instance of ConfigurationSection
    """

    def __setitem__(self, key, value):
        try:
            section, option = key.split('.', 1)
            target = self.data.setdefault(section, ConfigurationSection())
            target[option] = value
        except ValueError:
            self.data[key] = value
        

class ConfigurationManager(ConfigurationSection):
    """ An object that looks like a dictionary and contains the
        content of the configuration file.

        Use get_global_config() to find a global instance of this.
    """

    def __init__(self):
        ConfigurationSection.__init__(self)
        config_file = get_global_config_file()
        self.extend(config_file)

    def extend(self, file_thing):
        """ Extend (or update) the current configuration using the
            given file-like object. Existing values are overwritten.
        """
        new_parser = ConfigParser.SafeConfigParser()
        if hasattr(file_thing, 'readline'):
            new_parser.readfp(file_thing)
        else:
            new_parser.read(file_thing)

        for section in new_parser.sections():
            # Fun can be had with dots in main section names!
            for opt, value in new_parser.items(section):
                self["%s.%s" % (section,opt)] = value

#-----------------------------------------------------------------------

def get_ini_declaration(prefix):
    """
    Return the ini_file file name.
    
    If already set, return the previously set value.
    
    Else, check the working directory and return the one and only file
    that matches .INI or .ini (or .InI, or.Ini ...)
    """
    ini_file = get_global_config_file()
    if ini_file == None:
        candidate_set = os.listdir('.')
        # Reduce list to ini files only
        candidate_set = [candidate for
                         candidate in candidate_set
                         if os.path.splitext(candidate)[1].lower() == '.ini']
        assert len(candidate_set) > 0, ("No ini files found in"
                                        " working directory %s" % os.getcwd())
        if len(candidate_set) > 1:
            # Too many - be specific to the given prefix
            lp = len(prefix)
            candidate_set = [candidate for
                         candidate in candidate_set
                         if os.path.splitext(candidate)[0].lower()[:lp] == prefix]
        assert len(candidate_set) > 0, ("No suitable ini files"
                                        " using '%s' found in"
                                        " working directory %s" % (
                                            prefix, os.getcwd()))
        assert len(candidate_set) == 1, ("Too many ini files"
                                         " using '%s' found in"
                                         " working directory %s" % (
                                             prefix, os.getcwd()))
        ini_file = candidate_set[0]
    return ini_file

def set_ini_file(file_name):
    set_global_config_file(file_name)
    
def handle_ini_declaration(file_name=None, prefix=''):
    if not file_name:
        file_name = get_ini_declaration(prefix)
    set_ini_file(file_name)

#-----------------------------------------------------------------------
#
# Create some globals
global __config_file__
__config_file__ = None

def set_global_config_file(value):
    global __config_file__
    # allow setting only once, but allow for 'setting' to the same value
    assert __config_file__ is None or __config_file__ == value, (
        "Configuration file can only be set once")
    __config_file__ = value

def get_global_config_file():
    return __config_file__

global __global_config__
__global_config__ = None

def set_global_config(value):
    global __global_config__
    __global_config__ = value

def get_global_config():
    if __global_config__ is None:
        set_global_config(ConfigurationManager())
    return __global_config__

def clear_global_config():
    """ Used in testing"""
    global __config_file__
    __config_file__ = None
    global __default_options__
    __default_options__ = None
    global __global_config__
    __global_config__ = None
   
#-----------------------------------------------------------------------
