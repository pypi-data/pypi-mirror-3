# Name:      lokai/lk_worker/ui/pages.py
# Purpose:   Responses to requests for node related objects
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

""" The functions in this module are an interface to the actual
    controllers that will be used to generate a page.

    The functions generally identify the type of node being served and
    then call the appropriate controller.

    This stuff could equally well be in the controllers module, but
    this way a) should be easier to read, and b) makes it easier for
    other mappings to use these interfaces.
"""
#-----------------------------------------------------------------------
import logging

from werkzeug import Response, redirect, url_encode
import lokai.tool_box.tb_common.notification as notify
from lokai.tool_box.tb_database.orm_interface import engine
import lokai.tool_box.tb_common.dates as dates
from lokai.lk_ui.ui_default.wrap_page import wrap_page, wrap_application
from lokai.lk_worker.ui.local import url_for, get_object_reference

from lokai.lk_worker.models.builtin_data_activity import HistoryStore
from lokai.lk_worker.nodes.node_data_functions import (node_add_parent,
                                          node_delete_parent,
                                          )
from lokai.lk_worker.models.builtin_data_resources import node_new_resource
from lokai.lk_worker.nodes.data_interface import get_node_dataset

#-----------------------------------------------------------------------

import pyutilib.component.core as component
from lokai.lk_worker.extensions.controller_interface import IWorkerController

controller_extensions = component.ExtensionPoint(IWorkerController)

#-----------------------------------------------------------------------

def not_authorized(request):
    response = wrap_page(request, 'You are not authorised to view this page.')
    response.status_code=401
    return response

#-----------------------------------------------------------------------

def node_properties(request):
    """ Display the content of an existing node so it can be edited.
    """
    object_reference = get_object_reference(request)
    data_object = {}
    if object_reference != '**new**' and object_reference:
        data_object = get_node_dataset(object_reference, user=request.user)
        try:
            obj_type = data_object['nd_node'].nde_type
        except KeyError:
            obj_type = 'generic'
    else:
        obj_type = request.args.get('type', 'generic')
    target_controller = (controller_extensions.service(obj_type) or
                         controller_extensions.service('generic'))
    return target_controller.nd_controller_display_edit(
        request, object_reference, data_object)

def node_add(request):
    """ Display an empty node form so that a new node can be added.

        Do this by redirecting to the edit page but using the given
        object as the potential parent.

        Retain the 'type' argument from the URI and pass this on to
        the edit process. The type is defaulted to generic.
    """
    object_reference = get_object_reference(request)
    
    qry_parts = {'object_id': '**new**'}
    qry_parts.update(request.args)
    qry_parts['up'] = object_reference
    target = url_for('edit', qry_parts)
    return redirect(target)
    
def node_update(request):
    """ Respond to a POST return from an edit form.
    """
    object_reference = get_object_reference(request)
    data_object = {}
    if object_reference != '**new**' and object_reference:
        data_object = get_node_dataset(object_reference, user=request.user)
        try:
            obj_type = data_object['nd_node'].nde_type
        except KeyError:
            obj_type = 'generic'
    else:
        obj_type = request.args.get('type', 'generic')

    target_controller = (controller_extensions.service(obj_type) or
                         controller_extensions.service('generic'))
    return target_controller.nd_controller_respond_update(
        request, object_reference, data_object)

node_insert = node_update

def node_display(request):
    """ Display a non-editable version of the node data
    """
    object_reference = get_object_reference(request)
    data_object = get_node_dataset(object_reference, user=request.user)
    try:
        obj_type = data_object['nd_node'].nde_type
    except KeyError:
        obj_type = 'generic'

    target_controller = (controller_extensions.service(obj_type) or
                         controller_extensions.service('generic'))
    return target_controller.nd_controller_display_formatted(
        request, object_reference, data_object)

def node_list(request):
    object_reference = get_object_reference(request)
    data_object = get_node_dataset(object_reference, user=request.user)
    try:
        obj_type = data_object['nd_node'].nde_type
    except KeyError:
        obj_type = 'generic'

    target_controller = (controller_extensions.service(obj_type) or
                         controller_extensions.service('generic'))
    return target_controller.nd_controller_display_list(
        request, object_reference, data_object)

def node_list_post(request):
    object_reference = get_object_reference(request)
    data_object = get_node_dataset(object_reference, user=request.user)
    try:
        obj_type = data_object['nd_node'].nde_type
    except KeyError:
        obj_type = 'generic'

    target_controller = (controller_extensions.service(obj_type) or
                         controller_extensions.service('generic'))
    return target_controller.nd_controller_update_list(
        request, object_reference, data_object)
    
    
def node_default_view(request):
    object_reference = get_object_reference(request)
    data_object = get_node_dataset(object_reference, user=request.user)
    try:
        obj_type = data_object['nd_node'].nde_type
    except KeyError:
        obj_type = 'generic'

    target_controller = (controller_extensions.service(obj_type) or
                         controller_extensions.service('generic'))
    return target_controller.nd_controller_display_default(
        request, object_reference, data_object)

def node_link(request):
    child_ref = get_object_reference(request)
    parent_ref = request.args.get('up')
    hist = HistoryStore(child_ref, request.user)
    hist.append(node_add_parent(child_ref, parent_ref))
    hist.store()
    
    engine.session.flush()
    return node_default_view(request)

def node_unlink(request):
    child_ref = get_object_reference(request)
    parent_ref = request.args.get('up')
    hist = HistoryStore(child_ref, request.user)
    hist.append(node_delete_parent(child_ref, parent_ref))
    hist.store()
    
    engine.session.flush()
    query = {'object_id': child_ref}
    if request.args.get('next_up'):
        query['up'] = request.args['next_up']
    target = url_for('edit', query)
    return redirect(target)

def node_add_resource(request):
    child_ref = get_object_reference(request)
    new_user = request.args.get('user_idx')
    hist = HistoryStore(child_ref, request.user)
    hist.append(node_new_resource(new_user, child_ref))
    hist.store()
    
    target = url_for('edit', {'object_id': child_ref})
    return redirect(target)
    
def node_download_file(request):
    object_reference = get_object_reference(request)
    data_object = get_node_dataset(object_reference, user=request.user)
    try:
        obj_type = data_object['nd_node'].nde_type
    except KeyError:
        obj_type = 'generic'

    target_controller = (controller_extensions.service(obj_type) or
                         controller_extensions.service('generic'))

    return target_controller.nd_controller_download_file(
        request, object_reference, data_object)

#-----------------------------------------------------------------------

def make_default_selection(request):
    filter_data = {}
    perm = request.derived_locals['permissions']
    if perm.test_permit_list([{'nde_search_full': 'read'}]):
        time_now = dates.end_of_day(dates.now())
        #
        # Force start of day
        time_now = datetime.date(time_now.year, time_now.month, time_now.day)
        filter_data = {'assignee': request.user,
              'status': '20', # Open and Active
              'bf_range_to': time_now
              }
    return filter_data

from lokai.lk_worker.ui.methods.collections import FilterPage, ListPage

def node_collection(request):
    #
    # Check for initial search
    if 'filter' in request.args and 'default' in request.args['filter']:
        filter_data = make_default_selection(request)
        base_query = {'row': 0,
                      'filter': url_encode(filter_data)}
        if request.args.get('down'):
            base_query['down'] = request.args['down']
        obj_ref = get_object_reference(request)
        if obj_ref:
            base_query['object_id'] = obj_ref
            target = url_for('search', base_query)
        else:
            target = url_for('search_top', base_query)
        return redirect(target)
    #
    # Display a form
    filter_page = FilterPage(request, get_object_reference(request), {})
    op = filter_page.render()
    #
    # does build values, run query, build form then data
    list_page = ListPage(request)
    list_page.build_data()
    op += list_page.render()
    return wrap_application(request, op)

def node_set_filter(request):
    #
    # Look for a submited form and act accordingly.
    #
    object_reference = get_object_reference(request)
    data_object = (object_reference and
                   get_node_dataset(object_reference, user=request.user) or
                   {})
    filter_page = FilterPage(request, object_reference, data_object)
    # set filter
    if filter_page.process_input():
        #
        # Reset the start row because the filter has changed
        base_query = {'row': 0,
                      'filter': url_encode(filter_page.new_filter)}
        new_child = request.values.get('down')
        if new_child:
            base_query['down'] = new_child
        obj_ref = get_object_reference(request)
        if obj_ref:
            base_query['object_id'] = obj_ref
            target = url_for('search', base_query)
        else:
            target = url_for('search_top', base_query)
        return redirect(target)

    # We had some errors, so redisplay
    op = filter_page.render()
    # does build values, run query, build form then data
    list_page = ListPage(request)
    list_page.build_data()
    op += list_page.render()
    return wrap_application(request, op)

#-----------------------------------------------------------------------
