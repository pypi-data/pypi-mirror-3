# Name:      lokai/lk_ui/utils.py
# Purpose:   Stuff that can be used by applications for WSGI support.
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

from werkzeug.routing import Map, Rule

#-----------------------------------------------------------------------

class HandlerMap(object):
    """ An empty class that can have functions added as attributes.

        Adding a function reference as an attribute makes an unbound
        reference, so it acts the same way as a module for our
        purposes.
    """
    pass

def make_expose(url_map, handler_map=None):
    """ Return a decorator that can be used on views to link the view
        to a given URL.

        :url_map: instance of werkzeug Map

        :handler_map: instance of any class. To avoid clashes the
            class should be initially empty. HandlerMap is provided as
            a standardised choice

        The mapping between url and view (in the form of a named
        endpont) is stored in the given URL map.

        The mapping between the named endpoint and the target function
        being decorated is held as an attribute of the handler_map
        class instance.
    """
    def expose(rule, **kw):
        """ Decorator:

            @expose('some_url')
            def view(...)
                ...


            @expose('some_url', methods=['POST'])
            def view_to_update(...)
                ...

            See documenation on URL mapping
        """
        def decorate(f):
            kw['endpoint'] = f.__name__
            url_map.add(Rule(rule, **kw))
            if handler_map:
                setattr(handler_map, f.__name__, f)
            return f
        return decorate
    return expose

def make_url_for(get_adapter):
    """ Return a function locked to the local thread data that can be
        used to create a URL given the endpoint and any variable data.

        See documentation on URL mapping: build method of MapAdapter.

        The adapter that is used to create the url depends on the
        application environment and is built dynamically from
        configuration data. The :get_adapter: argument allows this
        binding to be deferred.

        :get_adapter: An executable that returns a url adapter
                that is used for matching the current response. 
    """
    def url_for(endpoint, values=None, _external=False):
        adapter = get_adapter()
        if values:
            return adapter.build(endpoint, values,
                                 force_external=_external)
        else:
            return adapter.build(endpoint, {},
                                 force_external=_external)
    return url_for

#-----------------------------------------------------------------------

