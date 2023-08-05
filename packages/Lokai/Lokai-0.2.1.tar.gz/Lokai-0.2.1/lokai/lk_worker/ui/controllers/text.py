# Name:      lokai/lk_worker/ui/controllers/text.py
# Purpose:   Responses to requests for type = 'text'
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

from werkzeug import redirect, Response
from werkzeug.exceptions import NotFound

import lokai.tool_box.tb_common.notification as notify
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
from lokai.lk_worker.ui.methods.display_page_text import DisplayPage

from lokai.lk_worker.models.builtin_data_attachments import (
    NodeAttachment,
    AttachmentNotFound
    )
from lokai.lk_worker.ui.controllers.generic import (PiGenericController,
                                                    NavigationOrder,
                                                    navigation_wrap)

#-----------------------------------------------------------------------

TEXT_TEMPLATE = 'lk_worker_app_text.html'

#-----------------------------------------------------------------------

class PiTextController(PiGenericController):
    component.implements(IWorkerController, inherit=True)

    navigation_template = TEXT_TEMPLATE
    function_tabs = [
        ('display', 'Display'),
        ('edit', 'Detail', [{'nde_tasks': 'edit'}]),
        ('list', 'List', [{'nde_tasks': 'edit'}]),
        ('search', 'Search'),
        ]

    def __init__(self):
        self.name = 'text'
        self.display_name = 'Text Only'
        self.view_interface = component.ExtensionPoint(IWorkerView)
        self.display_page = DisplayPage

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
        request.derived_locals['current_target'] = 'display'
        return self.nd_controller_display_formatted(request,
                                                    object_reference,
                                                    data_object)

    def nd_controller_download_file(self, request,
                                 object_reference, data_object):
        """ Return an attachment based on the component from the url
        """
        try:
            nda = NodeAttachment(
                'node',
                request.routing_vars['object_id'],
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
