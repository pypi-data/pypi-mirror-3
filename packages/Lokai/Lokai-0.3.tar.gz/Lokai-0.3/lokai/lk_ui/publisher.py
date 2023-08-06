#! /usr/bin/python
# Name:      lokai/lk_ui/publisher.py
# Purpose:   The front end wrapper
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
import logging

from werkzeug import DispatcherMiddleware, SharedDataMiddleware
from werkzeug import Local, LocalManager
from werkzeug.exceptions import HTTPException

from lokai.tool_box.tb_common.configuration import handle_ini_declaration
import lokai.tool_box.tb_common.configuration as config
from lokai.tool_box.tb_common.import_helpers import (get_module_attribute,
                                               get_module_path)
import lokai.tool_box.tb_common.notification as notify
from lokai.lk_job_manager.job_harness import setLoggers
import lokai.lk_ui

import lokai.lk_ui.ui_default.default_publisher as home_page

#-----------------------------------------------------------------------

local = Local()
local_manager = LocalManager([local])

#-----------------------------------------------------------------------

""" Initalise the application by looking through the configuration
    file.

    [all]

        Defines some optional email and log_file detail that is used
        to set up loggging.

        
    [skin]

        Defines the outer template to use for mounted applications
        that conform to the intended pattern and actually use this
        template.

        Points to various functions that are used to fill parts of the
        main template. This includes the main menu.

    [{app}]

        For some application - app - generate a mount point so that
        the dispatcher can find it.

"""

def build_logger(verbosity=1,
                 log_file=None,
                 process_id='ui_publisher'):
    """ Capture logging details from the config.

        We have changed the default criticality level to ERROR. That
        means that, if defined, the email_dev gets both CRITICAL and
        ERROR messages. This reflects a more conventional logger usage
        in the UI compared to the job manager.

        Correspondingly, we ignore the site email, because we don't
        want generic info messages comming at us for every normal
        access.  Partly, it detracts from responsiveness, and also it
        floods someone's inbox

    """
    cs = config.get_global_config()
    cs_all = cs.get('all', {})

    log_file_actual = (log_file if
                         log_file else
                         cs_all.get('ui_log_file', 'lokai_ui.log'))
    from_addr = cs_all.get('email_from')
    if not from_addr or '@' in from_addr:
        use_from = from_addr
    else:
        use_from = "%s@%s"%(from_addr, cs_all.get('smtp_from_host'))
    setLoggers(verbosity=verbosity,
               log_file=log_file_actual,
               process_id=process_id,
               email_from=use_from,
               critical_to=cs_all.get('email_dev'),
               critical_subject=("Lokai:  %s: critical" %
                                 (cs_all.get('site_name', 'web site'))),
               to_database=False,
               capacity=0, # Force no buffering
               criticality_level=logging.ERROR, 
               )

    # Add a duplicate set of loggers to catch werkzeug stuff.
    
    # Pity, really. I'd rather redirect werkzeug messages to our
    # choice of name, but I can't see how to do that in a reasonable
    # amount of my time.
    setLoggers(verbosity=verbosity,
               log_file=log_file_actual,
               process_id='werkzeug',
               email_from=cs_all.get('email_from'),
               critical_to=cs_all.get('email_dev'),
               critical_subject=("Lokai:  %s: critical" %
                                 (cs_all.get('site_name', 'web site'))),
               to_database=False,
               capacity = 0 # Force no buffering
               )

def build_skin():
    """ Capture the template and related filler modules.
    """
    skin_parameters = config.get_global_config().get('skin', {})
    lokai.lk_ui.set_page_template(
        skin_parameters.get('page_template', 'main_page.html'))
    
    template_set = skin_parameters.get('templates', '')
    template_path_list = [
        os.path.join(get_module_path(x.strip()), 'templates') for
        x in template_set.split(',') if x.strip()]
    default_template = os.path.join(
        get_module_path('lokai.lk_ui.ui_default'), 'templates')
    if not default_template in template_path_list:
        template_path_list.append(default_template)
    lokai.lk_ui.set_template_path(template_path_list)

    lokai.lk_ui.set_template_cache_path(
        skin_parameters.get('template_cache', None))

    static_set = skin_parameters.get('static', template_set)
    static_path_list = [
        os.path.join(get_module_path(x.strip()), 'static') for
        x in static_set.split(',') if x.strip()]
    default_static = os.path.join(
        get_module_path('lokai.lk_ui.ui_default'), 'static')
    if not default_static in static_path_list:
        static_path_list.append(default_static)
    lokai.lk_ui.set_static_path(static_path_list[0])
    
    menu_builder = skin_parameters.get(
        'menu_builder',
        'lokai.lk_ui.ui_default.make_menu.make_menu')
    if menu_builder:
         lokai.lk_ui.set_make_menu(get_module_attribute(menu_builder))
         
    ident_builder = skin_parameters.get(
        'ident_builder',
        'lokai.lk_ui.ui_default.make_ident.make_ident')
    if ident_builder:
         lokai.lk_ui.set_make_ident(get_module_attribute(ident_builder))

def build_application_mounts():
    """ Capture the details for each application that is mounted.

        Return:

            a default application that will be called if the given url
            does not match any loaded mount points.

            a dictionary of {path: application}

        Both of which are suitable for passing to a
        DispatcherMiddleware object.

        The default app is identified from one of:

            A mount path of '/'

            An entry in ['default']

            Failing these, the lk_ui.ui_default application
    """
    default_app = None
    mount_set = {}
    for name, block in config.get_global_config().iteritems():
        if 'application_publisher' in block:
            app_call = get_module_attribute(block['application_publisher'],
                                       'publisher')
            # The app_call function will return a publisher. It has to
            # be done this way to defer definition until the config
            # file has been processed
            app = app_call() # Get the actual publisher
            if name == 'default':
                if default_app:
                    raise ValueError('Trying to set Default Application twice')
                default_app = app
            else:
                path = block.get('application_path', name)
                if path == '' or path == '/':
                    if default_app:
                        raise ValueError('Trying to set Default Application twice')
                    default_app = app
                else:
                    if path[0] != '/':
                        path = "/%s"%path
                    mount_set[path] = app

    if not default_app:
        default_app = home_page.get_default_publisher()
    return default_app, mount_set

#-----------------------------------------------------------------------

""" The primary publishing object for Lokai based applications.

    This WSGI object is a wrapper that allows access to mounted WSGI
    applications that do the real work.
"""

class Lokai(DispatcherMiddleware):

    def __init__(self):
        build_skin()
        notify.info("--- StaticPath = %s" % lokai.lk_ui.StaticPath)
        default_app, mount_points = build_application_mounts()
        notify.info("--- Mount points = %s" % str(mount_points))
        try:
            DispatcherMiddleware.__init__(self, default_app, mount_points)
        except KeyboardInterrupt:
            notify.warn("Terminated by keyboard interrupt")
        except:
            notify.exception('Terminated by untrapped error')

def get_lokai_consolidating_publisher():
    return SharedDataMiddleware(
        Lokai(), {'/static': lokai.lk_ui.StaticPath})
                                                     
#-----------------------------------------------------------------------

def make_app():

    build_logger(2)

    return get_lokai_consolidating_publisher()
    
#-----------------------------------------------------------------------

if __name__ == '__main__':
    import werkzeug
    import optparse

    parser = optparse.OptionParser()
    parser.add_option('--host',
                      dest='host',
                      help='The host name of this server [default: %default]')
    parser.add_option('--port',
                      dest='port',
                      type='int',
                      help='The port the server listens on [default: %default]')
    parser.add_option('--max-children',
                      dest='max_children',
                      type='int',
                      help='The maximum number of pre-forked processes to use '
                      '[default: %default]')
    parser.add_option('--use-reloader',
                      dest='use_reloader',
                      action='store_true',
                      help='Add this if you want the server to reload '
                      'when a source file changes [default: %default]')

    parser.set_defaults(
        host='localhost',
        port=8080,
        max_children=5,
        use_reloader=False,
        )
    (options, args) = parser.parse_args()

    handle_ini_declaration(prefix='lk')

    werkzeug.run_simple(options.host,
                        options.port,
                        make_app(),
                        use_reloader=options.use_reloader,
                        processes=options.max_children,
                        passthrough_errors=False,
                        threaded=False)

#-----------------------------------------------------------------------
