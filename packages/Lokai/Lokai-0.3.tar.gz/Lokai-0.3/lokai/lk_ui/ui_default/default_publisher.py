# Name:      lokai/lk_ui/ui_default/default_publisher.py
# Purpose:   A publisher application place holder
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

from werkzeug import Response, ClosingIterator, redirect
from werkzeug.exceptions import NotFound

import lokai.tool_box.tb_common.configuration as config

from lokai.lk_ui.session import SessionRequest
from lokai.lk_ui import ServerName, set_server_name
from lokai.lk_ui.base_publisher import render_error
from lokai.lk_login.db_objects import model

#-----------------------------------------------------------------------

DefaultDefaultPath = '/pages/HomePage/default'
global DefaultPath
DefaultPath = None

class DefaultPublisher(object):
    """ The default Publisher object is called when the
        DispatcherMiddleware cannot find a target. This might be
        because the url really does not match any targets. However,
        the DM object is limited to recognising non-empty paths, and
        the user might have entered a host name without a '/', or
        maybe a single trailing '/' (reasonable first entry to a
        site!). In this default responder we look for empty path info
        and then redirect to a path found in the config file as
        'default_path' in section [default].

        If there is no suitable path we default to /pages/Home
    """

    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        #model.model.init()
        if not environ['PATH_INFO'] or environ['PATH_INFO'] == '/':
            # Try the default page
            return redirect(DefaultPath, 301)(environ, start_response)
        elif 'favicon' in environ['PATH_INFO']:
            response = Response('no favicon',
                                mimetype='text/html')
            response.status_code = 404
            return ClosingIterator(response(environ, start_response))

        if not ServerName:
            set_server_name(environ.get('SERVER_NAME'))
        model.init()
        request = SessionRequest(environ)
        response = Response(render_error('lk_error_404.html',
                                         request),
                            mimetype='text/html')
        response.status_code = 404
        return ClosingIterator(response(environ, start_response))

#-----------------------------------------------------------------------

def menu_builder(request):
    return [{
        'title': '',
        'position': 1,
        'children': [{'link': DefaultPath,
            'title': 'Home',
            'position': 1,
            }]}]

#-----------------------------------------------------------------------

def get_default_publisher():
    global DefaultPath
    if not DefaultPath:
        DefaultPath = config.get_global_config(
            ).get(
            'default', {}
            ).get(
            'default_path', DefaultDefaultPath)
    return DefaultPublisher()

#-----------------------------------------------------------------------
