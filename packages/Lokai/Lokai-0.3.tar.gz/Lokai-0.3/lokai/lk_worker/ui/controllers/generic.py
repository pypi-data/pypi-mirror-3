# Name:      lokai/lk_worker/ui/controllers/generic.py
# Purpose:   Responses to requests for type = 'generic'
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

#-----------------------------------------------------------------------

import json
from collections import namedtuple

from werkzeug import redirect, Response
from werkzeug.exceptions import NotFound

import lokai.tool_box.tb_common.notification as notify
from lokai.lk_ui.ui_default.wrap_page import wrap_application
from lokai.lk_ui.file_responder import getFileResponse

import pyutilib.component.core as component
from lokai.lk_worker.extensions.controller_interface import IWorkerController
from lokai.lk_worker.extensions.view_interface import IWorkerView

#-----------------------------------------------------------------------

from lokai.lk_worker.ui.local import url_for

from lokai.lk_worker.ui.methods.list_navigator import ListNavigator
from lokai.lk_worker.ui.methods.detail_page import DetailPage
from lokai.lk_worker.ui.methods.header_page import HeaderPage
from lokai.lk_worker.ui.methods.list_page import ListPage
from lokai.lk_worker.ui.methods.collections import (
    FilterPage,
    ListPage as FilteredListPage,
    )
from lokai.lk_worker.ui.methods.display_page import DisplayPage
from lokai.lk_worker.nodes.search import search_children
from lokai.lk_worker.nodes.search_filtered import get_node_basic

from lokai.lk_worker.models.builtin_data_attachments import (
    NodeAttachment,
    AttachmentNotFound
    )

#-----------------------------------------------------------------------

def navigation_wrap(template, request, navigation_detail, page_data):
    """ Put the page into a template with navigation wrappers """
    return wrap_application(
        request,
        page_data,
        template,
        tree_navigator = navigation_detail['tree_navigator'],
        tab_headers = navigation_detail['tabs'],
        )

STANDARD_TEMPLATE = 'lk_worker_app_generic.html'

NavigationOrder = namedtuple('NavigationOrder', 'order,sort_object,flow')

#-----------------------------------------------------------------------

class PiGenericController(component.SingletonPlugin):
    component.implements(IWorkerController, inherit=True)

    navigation_template = STANDARD_TEMPLATE
    navigation_order = NavigationOrder('nde_sequence', None, None)

    def __init__(self):
        self.name = 'generic'
        self.display_name = 'Generic'
        self.view_interface = component.ExtensionPoint(IWorkerView)
        self.display_page = DisplayPage

    def nd_controller_display_edit(self, request,
                                   object_reference, data_object):
        """ Present a screen of editable fields (permissions allowing)
            that is used to modify an existing object.
        """
        detail_page = DetailPage(request, object_reference, data_object,
                                 view_interface=self.view_interface)
        detail_page.build_data()
        navigation = ListNavigator(request, object_reference, data_object,
                                   self.navigation_order)
        navigation_detail = navigation.get_parts()
        page_html = detail_page.render()
        return navigation_wrap(self.navigation_template,
                               request, navigation_detail, page_html)

    def nd_controller_display_add(self, request,
                                  object_reference, data_object):
        """ Present a screen of editable fields (permissions allowing)
            that is used to create a new object.

            object reference points to the parent.
        """
        detail_page = DetailPage(request, object_reference, data_object,
                                 view_interface=self.view_interface)
        detail_page.build_data()
        navigation = ListNavigator(request, object_reference, data_object,
                                   self.navigation_order)
        navigation_detail = navigation.get_parts()
        page_html = detail_page.render()
        return navigation_wrap(self.navigation_template,
                               request, navigation_detail, page_html)

    def nd_controller_respond_update(self, request,
                                     object_reference, data_object):
        """ Given a form POST response, update the database and redirect
            to the edit page.

            This version responds to user input errors by redisplaying the
            edit page modified with error messages.
        """
        detail_page = DetailPage(request, object_reference, data_object,
                                 view_interface=self.view_interface)
        detail_page.has_errors() # to get the data from the input

        if detail_page.process_input() and detail_page.error_count == 0:
            qry_parts = {'object_id': detail_page.obj_ref}
            try:
                qry_parts['up'] = request.args['up']
            except KeyError:
                pass
            target = url_for('edit', qry_parts)
            return redirect(target)
        navigation = ListNavigator(request, object_reference, data_object,
                                   self.navigation_order)
        navigation_detail = navigation.get_parts()
        page_html = detail_page.render()
        return navigation_wrap(self.navigation_template,
                               request, navigation_detail, page_html)

    def nd_controller_respond_insert(self, request,
                                     object_reference, data_object):
        """ Given a form POST response, insert a new item into the
            database and redirect to the edit page.

            This version responds to user input errors by redisplaying the
            edit page modified with error messages.

            rq: a dictionary taken from the request query.

            rq['up'] contains the parent node that the new node will be
            linked to. This is processed inside the process_input code.

        """
        detail_page = DetailPage(request, object_reference, data_object,
                                 view_interface=self.view_interface)
        detail_page.has_errors() # to get the data from the input

        if detail_page.process_input() and detail_page.error_count == 0:
            qry_parts = {'object_id': detail_page.obj_ref}
            # We don't have to carry the object type forward as the
            # object has been stored.
            try:
                qry_parts['up'] = request.args['up']
            except KeyError:
                pass
            target = url_for('edit', qry_parts)
            return redirect(target)
        navigation = ListNavigator(request, object_reference, data_object,
                                   self.navigation_order)
        navigation_detail = navigation.get_parts()
        page_html = detail_page.render()
        return navigation_wrap(self.navigation_template,
                               request, navigation_detail, page_html)

    def nd_controller_display_formatted(self, request,
                                        object_reference, data_object):
        """ Display a page of static text based on the given object.

        """
        detail_page = self.display_page(request, object_reference, data_object,
                                 view_interface=self.view_interface)
        detail_page.build_data()
        navigation = ListNavigator(request, object_reference, data_object,
                                   self.navigation_order)
        navigation_detail = navigation.get_parts()
        page_html = detail_page.render()
        return navigation_wrap(self.navigation_template,
                               request, navigation_detail, page_html)

    def nd_controller_display_default(self, request,
                                      object_reference, data_object):
        """ Call one of the other display functions depending on what
            might be considered the default for this type.
        """
        query = get_node_basic()
        query = search_children(query, object_reference)
        u_set_len = query.count()
        if u_set_len:
            request.derived_locals['current_target'] = 'list'
            return self.nd_controller_display_list(request,
                                                   object_reference,
                                                   data_object)
        else:
            request.derived_locals['current_target'] = 'display'
            return self.nd_controller_display_formatted(request,
                                                        object_reference,
                                                        data_object)

    def nd_controller_display_list(self, request,
                                   object_reference, data_object):
        """ Display a list of children for the given node.
        """
        detail_page = HeaderPage(request, object_reference, data_object)
        detail_page.build_data()
        op = [detail_page.render()]
        list_page = ListPage(request, object_reference, data_object)
        list_page.build_data()
        op.append(list_page.render())
        navigation = ListNavigator(request, object_reference, data_object,
                                   self.navigation_order)
        navigation_detail = navigation.get_parts()
        page_html = '\n'.join(op)
        return navigation_wrap(self.navigation_template,
                               request, navigation_detail, page_html)

    def nd_controller_display_search(self, request,
                                     object_reference, data_object):
        """ Display a list of results for the given search.
        """
        #
        # Check for initial search
        if 'filter' in request.args and 'default' in request.args['filter']:
            filter_data = make_default_selection(request, object_reference)
            base_query = {'row': 0,
                          'filter': json.dumps(filter_data)}
            if request.args.get('down'):
                base_query['down'] = request.args['down']
            if object_reference:
                base_query['object_id'] = object_reference
                target = url_for('search', base_query)
            else:
                target = url_for('search_top', base_query)
            return redirect(target)
        #
        # Display a form
        filter_page = FilterPage(request, object_reference, {})
        page_html = filter_page.render()
        #
        # does build values, run query, build form then data
        list_page = FilteredListPage(request, object_reference, data_object)
        list_page.build_data()
        page_html += list_page.render()
        navigation = ListNavigator(request, object_reference, data_object,
                                   self.navigation_order)
        navigation_detail = navigation.get_parts()
        return navigation_wrap(self.navigation_template,
                               request, navigation_detail, page_html)

    def nd_controller_update_search(self, request,
                                    object_reference, data_object):
        filter_page = FilterPage(request, object_reference, data_object)
        # set filter
        if filter_page.process_input():
            #
            # Reset the start row because the filter has changed
            base_query = {'row': 0,
                          'filter': json.dumps(filter_page.new_filter)}
            new_child = request.values.get('down')
            if new_child:
                base_query['down'] = new_child
            if object_reference:
                base_query['object_id'] = object_reference
                target = url_for('search', base_query)
            else:
                target = url_for('search_top', base_query)
            return redirect(target)

        # We had some errors, so redisplay
        page_html = filter_page.render()
        # does build values, run query, build form then data
        list_page = FilteredListPage(request, object_reference, data_object)
        list_page.build_data()
        page_html += list_page.render()
        navigation = ListNavigator(request, object_reference, data_object,
                                   self.navigation_order)
        navigation_detail = navigation.get_parts()
        return navigation_wrap(self.navigation_template,
                               request, navigation_detail, page_html)

    def nd_controller_download_file(self, request,
                                    object_reference, data_object):
        """ Return an attachment based on the component from the url
        """
        try:
            nda = NodeAttachment(
                'node',
                object_reference,
                request.routing_vars['file_path'],
                unpack = True
                )
            return getFileResponse(nda.get_target_path())
        except (AttachmentNotFound, ValueError):
            file_ref = '/'.join([object_reference,
                                 request.routing_vars['file_path']])
            notify.error("--- File Not Found - %s" % file_ref)
            raise NotFound

#-----------------------------------------------------------------------
