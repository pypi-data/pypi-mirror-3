# Name:      lokai/lk_worker/ui/local.py
# Purpose:   connect URL to login pages
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

from werkzeug import Response, Local, LocalManager, url_unquote
from werkzeug.routing import Map
 
import pyutilib.component.core as component

import lokai.tool_box.tb_common.configuration as config
import lokai.tool_box.tb_common.notification as notify
import lokai.tool_box.tb_common.dates as dates

import lokai.lk_ui.utils as utils
import lokai.lk_ui

from lokai.lk_login.permissions import FunctionPermissions
from lokai.lk_login.userpermission import UserPermission, GUEST_NAME
from lokai.lk_worker.nodes.node_data_functions import get_user_node_permissions
from lokai.lk_worker.nodes.data_interface import get_node_dataset
from lokai.lk_worker.nodes.search import find_from_string

#-----------------------------------------------------------------------

APPLICATION_NAME = 'lk_worker'

APPLICATION_PATH = None

APPLICATION_SCHEME = None

#-----------------------------------------------------------------------

local = Local()
local_manager = LocalManager([local])
publisher = local('publisher')

#-----------------------------------------------------------------------

url_map = Map()
url_adapter = None
handler_map = utils.HandlerMap()

def get_adapter():
    global url_adapter
    if not url_adapter:
        global APPLICATION_PATH
        APPLICATION_PATH = config.get_global_config(
            ).get(
            APPLICATION_NAME, {}
            ).get(
            'application_path')
        if APPLICATION_PATH and APPLICATION_PATH[0] != '/':
            APPLICATION_PATH = '/'+APPLICATION_PATH
        global APPLICATION_SCHEME
        APPLICATION_SCHEME = config.get_global_config(
            ).get(APPLICATION_NAME, {}).get(
            'application_scheme', 'http')
        url_adapter = url_map.bind(lokai.lk_ui.ServerName,
                                   APPLICATION_PATH,
                                   None,
                                   APPLICATION_SCHEME,
                                   )
    return url_adapter

expose = utils.make_expose(url_map, handler_map)
url_for = utils.make_url_for(get_adapter)

#-----------------------------------------------------------------------
# Identify a node from the URL data

def get_object_reference(request):
    """ Return the object reference that has been isolated from the url
    """
    return request.derived_locals.get('object_id')

def get_object_candidates(request):
    """ Find the object or set of objects that is/are the target of
        this request. This could come from the url, the query, or the
        form itself.

        When looking into the form we make the assumption that the
        form details are held inside a fieldset layer, hence the
        special field name.

        return [object_id]
    """
    possible_id = request.derived_locals.get('object_id')
    if possible_id:
        return [possible_id] #>>>>>>>>>>>>>>>>>>>>
    path = request.derived_locals.get('object_path')
    url_idx = request.routing_vars.get('object_id')
    if path:
        possible_id = path        
    elif url_idx:
        possible_id = url_idx
    if possible_id == "**new**":
        possible_id = [possible_id]
    elif possible_id:
        possible_id = url_unquote(possible_id)
        request.derived_locals['search_path'] = possible_id
        possible_id = find_from_string(possible_id, expand=True)
    notify.info("--- From url object id - %s" % possible_id)
    return possible_id

#-----------------------------------------------------------------------
# Expand a restriction set using an extra permission function
from lokai.lk_login.permissions import PERM_MODIFY, PERM_DELETE

# We are only interested in extending when actions can modify the
# modify the current node.
TARGET_MASK = PERM_MODIFY+PERM_DELETE

def expand_permission(given_restriction, using_function):
    """ Given a set of permissions to use as an access restriction,
        apply the perm.expand method to all the inner workings and
        return a new set of permissions.

        :given_restriction: a collection of permission definitions for
            use as an access restriction. See lk_login.permissions -
            test_permission_list for what is allowed.

        :using_function: The function to apply.

        Returns, either the original restrction or a new restriction
        list containing FunctionPermissions objects in place of each
        dictionary in the original.
    """
    if not using_function:
        return given_restriction
    if not isinstance(given_restriction, (list, tuple)):
        if isinstance(given_restriction, dict):
            use_restriction = [given_restriction]
        else:
            return given_restriction
    else:
        use_restriction = given_restriction

    op = []
    for restriction in use_restriction:
        if restriction:
            fp = FunctionPermissions()
            fp.update(restriction)
            op.append(fp.extend(using_function, TARGET_MASK))
    return op
        
#-----------------------------------------------------------------------
# Decorator to check permissions
from werkzeug.exceptions import Unauthorized, NotFound

def is_allowed(given_restriction):
    """ Check the given permission set against any currently available
        information.
        
        'owner' is the instance of the directory class that is being
        called.

        'given_restriction' is a Permission.test_permit_list format string, (alias
        permission)
        
        Makes assumptions about the underlying application: detail_idx
        is the currernt node; up is a possible parent node; down is a
        possible child node. Permissions are checked against the first
        of these that is given and is a real node.
    """
    def _check_responder(responder):
        return_name = responder.__name__
        def _allowed_responder(request):
            now_string = dates.timetostr(dates.now())
            user = request.user or GUEST_NAME
            candidate_set = get_object_candidates(request)
            if not candidate_set or candidate_set[0] == '**new**':
                # The node itself is not helping - we try the
                # potential parent node.
                if candidate_set:
                    request.derived_locals['object_id'] = candidate_set[0]
                else:
                    request.derived_locals['object_id'] = None
                possible_id = request.args.get('up')
                if not possible_id:
                    possible_id = request.args.get('down')
                candidate_set = find_from_string(possible_id, expand=True)
                if candidate_set:
                    candidate = candidate_set[0]
                    permissions = (
                        get_user_node_permissions(candidate_set[0], user))
                    node_perm_data = get_node_dataset(candidate,
                                                         'local_permission')
                    node_perm_setting = node_perm_data.get('local_permission')
                    use_restriction = expand_permission(given_restriction,
                                                        node_perm_setting)
                    can_do = permissions.test_permit_list(use_restriction)
                else:
                    # Got here with an empty initial set and no up or
                    # down. Can't continue, either because the
                    # original requested item could not be found or
                    # the user entered an empty identifier
                    notify.warning(
                        "--- Find failure for %s from %s on %s ---\n"
                        "    Trying %s\n" %
                        (user, request.referrer, now_string,
                         request.url))
                    raise NotFound

            else:
                # The give URL might return more then one hit. Find
                # all the hits and exclude the ones we are not allowed
                # to see.
                allowed_set = []
                for candidate in candidate_set:
                    node_perm_data = get_node_dataset(candidate,
                                                         'local_permission')
                    node_perm_setting = node_perm_data.get('local_permission')
                    use_restriction = expand_permission(given_restriction,
                                                        node_perm_setting)
                    permissions = (
                        get_user_node_permissions(candidate, user))
                    this_can_do = permissions.test_permit_list(use_restriction)
                    if this_can_do:
                        allowed_set.append(candidate)
                if len(allowed_set) == 0:
                    # Nothing left - we are not allowed in
                    can_do = False
                elif len(allowed_set) == 1:
                    # One left - this is it!
                    request.derived_locals['object_id'] = allowed_set[0]
                    can_do = True
                else:
                    # We have more than one possibility: redirect to
                    # the search page
                    original_search = request.derived_locals.get('search_path')
                    search_filter = {'name': original_search}
                    base_query = {
                        'filter': url_encode(search_filter)}
                    return redirect(url_for('search_top', base_query))
                    # >>>>>>>>>>>>>>>>>>>>
            if can_do:
                notify.info(
                    "--- Authorisation granted to %s from %s on %s ---\n"
                    "    Trying %s\n"
                    "    Needs permission %s\n"
                    "    Has permisions %s\n" %
                    (user, request.referrer, now_string,
                     request.url, given_restriction, permissions))
                request.derived_locals['permissions'] = permissions
                return responder(request)
            else:
                notify.warning(
                    "--- Authorisation failure for %s from %s on %s ---\n"
                    "    Trying %s\n"
                    "    Needs permission %s\n"
                    "    Has permisions %s\n" %
                    (user, request.referrer, now_string,
                     request.url, given_restriction, permissions))
                raise Unauthorized
        _allowed_responder.__name__ = return_name
        return _allowed_responder
    return _check_responder

#-----------------------------------------------------------------------

def check_guest_access(request, given_restriction):
    """ Method to call when the decorator is not appropriate. That is,
        when there is no actual node to look for. In this case we are
        looking for the permissions attached to the user specifically,
        rather than those arising from allocation to any node.
    """
    user = request.user or GUEST_NAME
    permissions = UserPermission(user=user)
    request.derived_locals['permissions'] = permissions
    can_do = permissions.test_permit_list(given_restriction)
    now_string = dates.timetostr(dates.now())
    if not can_do:
        notify.warning(
            "--- Authorisation failure for %s from %s on %s ---\n"
            "    Trying %s\n"
            "    Needs permission %s\n"
            "    Has permisions %s\n" %
            (user, request.referrer, now_string,
             request.url, given_restriction, permissions))
        raise Unauthorized
    notify.info(
        "--- Authorisation granted to %s from %s on %s ---\n"
        "    Trying %s\n"
        "    Needs permission %s\n"
        "    Has permisions %s\n" %
        (user, request.referrer, now_string,
         request.url, given_restriction, permissions))
    return can_do

#-----------------------------------------------------------------------

class IWorkerHandler(component.Interface):
    """ An interface used by the publisher to identify handlers for
        routing endpoints
    """
    def __init__(self):
        """ The name defined here is the target endpoint """
        self.name = unknown

    @is_allowed([{'nde_tasks': 'read'}])
    def __call__(response):
        """ Must have this method - the handler class is 'called' by
            the publisher. Note that we can still decorate it to look
            for permissions.
        """
        pass

#-----------------------------------------------------------------------
