# Name:      lokai/lk_ui/base_publisher.py
# Purpose:   Publish pages
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

import urlparse
from sqlalchemy.exc import IntegrityError

import lokai.tool_box.tb_common.notification as notify

import pyutilib.component.core as component

from werkzeug import Request, ClosingIterator, Response
from werkzeug.exceptions import HTTPException, NotFound, Unauthorized

from lokai.tool_box.tb_common.exception_format import get_print_exc_plus
from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_ui.session import SessionRequest
from lokai.lk_ui import ServerName, set_server_name
from lokai.lk_login.db_objects import model

import lokai.lk_ui

from lokai.lk_ui.ui_default import wrap_page
from lokai.lk_ui.render_template import render_template

#-----------------------------------------------------------------------

def render_error(given_template, request):
    """ Render an error using the given template """
    this_host_parts = urlparse.urlsplit(request.host_url)
    this_host_base = this_host_parts[1].split(':')[0] # strip port
    if request and request.referrer:
        referrer_parts = urlparse.urlsplit(request.referrer)
        referrer_base = referrer_parts[1].split(':')[0] # strip port
    else:
        referrer_base = ''
    link_from_self = (referrer_base == this_host_base)
    if link_from_self:
        notify.error("Broken link, from %s to %s"%(request.referrer,
                                                   request.base_url))
    inner_page = render_template(given_template,
                                        request=request,
                                        user=request.user,
                                        link_from_self=link_from_self
                                        )
    if 'DOCTYPE' in inner_page[:50]:
        return inner_page
    else:
        context = wrap_page.make_context(request, inner_page)
        return render_template(lokai.lk_ui.PageTemplate, **context)

def get_print_request(environ, request):
    op = []
    if environ:
        op.append("CGI environment:")
        for k,v in environ.iteritems():
            op.append(">> %s: %s" % (k,v))
    if request:
        op.append("Request:")
        op.append(">> User: %s" % request.user)
    return '\n'.join(op)
        
#-----------------------------------------------------------------------

commit = engine.session.commit
rollback = engine.session.rollback

class BasePublisher(object):

    """ Worker application -

        Display the search form

        Respond to node requests

    """

    def __init__(self, given_views, get_adapter, local, local_manager,
                 route_handler_interface=None):
        """ Create a basic publisher object that can be called to
            produce a response.

            :given_views: A module or other object that has executable
                attributes correspnding to the endpoints of the url map.

            :get_adapter: An executable that returns a url adapter
                that is used for matching the current response. This
                is done this way because the adapter has to be created
                dynamically, but only once. It is called with no
                arguments. The map is bound into the adapter using
                configuration settings.

            :local: A pointer to the thread_local space.

            :local_manager: A pointer the the local space
                manager. This is called at the end of a response to
                clean up the thread_local environment.

        """
        self.views = given_views
        self.get_adapter = get_adapter
        self.local = local
        self.local_manager = local_manager
        self.handler_extensions = None
        if route_handler_interface:
            self.handler_extensions = component.ExtensionPoint(
                route_handler_interface)

    def publish(self, environ, start_response):
        if not ServerName:
            set_server_name(environ.get('SERVER_NAME'))
        model.init()
        self.local.publisher = self
        adapter = self.get_adapter()
        request = None
        try:
            endpoint, values = adapter.match(environ.get('PATH_INFO'),
                                             environ['REQUEST_METHOD'])
            environ['wsgiorg.routing_args'] = ((), values)
            request = SessionRequest(environ)
            handler = getattr(self.views, endpoint)
            need_to_try = True
            try_count = 0
            while need_to_try:
                need_to_try = False
                try_count += 1
                try:
                    response = handler(request)
                    request.store_session(response)
                    op = response(environ, start_response)
                    commit()
                except IntegrityError, e:
                    if ('duplicate key' in str(e).lower() and
                        try_count < 10):
                        rollback()
                        need_to_try = True
                    else:
                        raise
            return op
        except (Unauthorized, NotFound), e:
            try:
                if not request:
                    try:
                        request = SessionRequest(environ)
                    except:
                        pass
                response = Response(render_error('lk_error_404.html',
                                             request),
                                mimetype='text/html')
                response.status_code = 404
                op = response(environ, start_response)
                rollback()
                return op
            except:
                notify.critical(get_print_request(environ, request))
                notify.critical(get_print_exc_plus())
                response = Response(render_error('lk_error_final.html',
                                                 request),
                                    mimetype='text/html')
                response.status_code = 400
                op = response(environ, start_response)
                rollback()
                return op

        except HTTPException, e:
            notify.critical(get_print_request(environ, request))
            notify.critical(get_print_exc_plus())
            response = e
            op = response(environ, start_response)
            rollback()
            return op
        except:
            notify.critical(get_print_request(environ, request))
            notify.critical(get_print_exc_plus())
            try:
                response = Response(render_error('lk_error_any.html',
                                                 request),
                                    mimetype='text/html')
                response.status_code = 400
                op = response(environ, start_response)
            except:
                notify.critical("Responding to error in error trap")
                notify.critical(get_print_request(environ, request))
                notify.critical(get_print_exc_plus())
                response = Response(render_error('lk_error_final.html',
                                                 request),
                                    mimetype='text/html')
                response.status_code = 400
                op = response(environ, start_response)
            rollback()
            return op
        finally:
            self.local_manager.cleanup()
            notify.getLogger().flush()
        engine.session.close_all()

    def __call__(self, environ, start_response):
        op = self.publish(environ, start_response)
        return op

#-----------------------------------------------------------------------
