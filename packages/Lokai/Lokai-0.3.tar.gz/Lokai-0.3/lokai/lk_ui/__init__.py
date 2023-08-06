# Name:      lokai/lk_ui/__init__.py
# Purpose:   Common stuff and globals.
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

# Switch form tokens on and off - mainly for testing

global UseFormToken
UseFormToken = True
def set_use_form_token(value):
    global UseFormToken
    UseFormToken = True
    if not value:
        UseFormToken = False

def get_use_form_token():
    global UseFormToken
    return UseFormToken

#-----------------------------------------------------------------------
# Current server name
#
# Stored here because we are not binding url Maps to the environement
# (because we have multiple maps mounted under different prefixes).
#
# Generally, we want to store this only once, on the first request.

global ServerName
ServerName = ''
def set_server_name(name_string):
    """ Set the value of the global server name """
    global ServerName
    ServerName = name_string

#-----------------------------------------------------------------------
# Common page template.
#
# The template referenced here can be used by a mounted application to
# wrap content. This template provides a common look to mounted
# applications. The template is expected to provide the initial html
# declaration.

global PageTemplate
PageTemplate = None
def set_page_template(name_string):
    """ Set the value of the common page given a name as a string """
    global PageTemplate
    PageTemplate = name_string

global TemplatePath
TemplatePath = None
def set_template_path(name_string):
    """ Set the path where templates are to be found """
    global TemplatePath
    TemplatePath = name_string

global TemplateCachePath
TemplateCachePath = None
def set_template_cache_path(name_string):
    """ Set the path where templates are to be found """
    global TemplateCachePath
    TemplateCachePath = name_string

global StaticPath
StaticPath = None
def set_static_path(name_string):
    """ Set the path where statics are to be found """
    global StaticPath
    StaticPath = name_string

def get_static_path():
    global StaticPath
    return StaticPath

#-----------------------------------------------------------------------
# Common ident builder
#
# A function that returns a dictionary normally containing identity
# information, such as site name, user name and anything else that
# tell the user where they are. The dictionary can be passed to the
# common page template which has presumably been defined to use the
# information.

global MakeIdent
MakeIdent = None
def set_make_ident(a_callable):
    """ Set the value for the ident builder given a callable """
    global MakeIdent
    MakeIdent = a_callable

#-----------------------------------------------------------------------
# Common menu builder
#
# A function that returns html text. This text is passed to the common
# page template which should have been designed to use this text as
# for a main menu.

global MakeMenu
MakeMenu = None
def set_make_menu(a_callable):
    """ Set the value for the menu builder given a callable """
    global MakeMenu
    MakeMenu = a_callable

#-----------------------------------------------------------------------

