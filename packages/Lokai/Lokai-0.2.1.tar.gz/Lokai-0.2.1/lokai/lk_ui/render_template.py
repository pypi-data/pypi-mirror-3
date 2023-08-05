# Name:      lokai/lk_ui/render_template.py
# Purpose:   Interface to the template engine
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

from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache

import lokai.lk_ui

#-----------------------------------------------------------------------

global TemplateEnvironment
TemplateEnvironment = None
def set_template_environment():
    """ Set up a template environment from the global parameters """
    global TemplateEnvironment
    TemplateEnvironment = Environment(
        loader=FileSystemLoader(lokai.lk_ui.TemplatePath),
        bytecode_cache=FileSystemBytecodeCache(lokai.lk_ui.TemplateCachePath))

#-----------------------------------------------------------------------

def render_template(template, **context):
    """ Look for and render the given template using the given context variables.

        template: name of the template

        context: dictionary of variables for inserting into the template.
    """
    if TemplateEnvironment is None:
        set_template_environment()
    return TemplateEnvironment.get_template(template).render(**context)

#-----------------------------------------------------------------------
