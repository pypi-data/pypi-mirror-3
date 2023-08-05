# Name:      lokai/lk_worker/ui/methods/display_page_text.py
# Purpose:   Handle display of node details
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

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_common.rest_support import as_heading

from lokai.lk_worker.ui.local import url_for
from lokai.lk_worker.ui.rest_extra import render_page
from lokai.lk_worker.ui.methods.base_form import NodeBaseForm


from lokai.lk_worker.models.builtin_data_activity import ndHistory
from lokai.lk_worker.nodes.node_data_functions import PermittedNodeFamily
from lokai.lk_worker.ui.local import get_object_reference
from lokai.lk_worker.ui.widget import HtmlWidget, SideBarWidget

#-----------------------------------------------------------------------

import pyutilib.component.core as component
from lokai.lk_worker.extensions.view_interface import IWorkerView
from lokai.lk_worker.extensions.controller_interface import IWorkerController

#-----------------------------------------------------------------------

__all__ = ['DisplayPage']

#-----------------------------------------------------------------------

class DisplayPage(NodeBaseForm):

    def __init__(self, request, object_reference, data_object, **kwargs):
        self.view_interface = (kwargs.get('view_interface') or
                                component.ExtensionPoint(IWorkerView))
        self.controller_interface =  (kwargs.get('controller_interface') or
                                component.ExtensionPoint(IWorkerController))
        self.node_perm = perm = request.derived_locals['permissions']
        self.request = request
        try:
            self.obj_type = data_object['nd_node'].nde_type
        except KeyError:
            self.obj_type = 'generic'
        NodeBaseForm.__init__(self,
                              request,
                              object_reference,
                              data_object,
                              enctype = "multipart/form-data",
                              title = 'Node Detail',
                              perm = 'nde_tasks'
                              )

    #-------------------------------------------------------------------
    
    def _identify_form_action(self):
        """ Decide on the url that is going to respond to user input.
        """
        # Exept that this is not really a form, and we are not
        # expecting anything. Return None to get a default.
        return None
    
    def build_form(self):
        self.add_composite('detail',
                           title      = self.title,
                           fieldset   = {},
                          )
        self.detail = self.get_widget('detail')
        self.add_form_elements()

    def build_objects(self):
        """ Set up drop down lists such as depend on node type.
        """
        if self.obj_ref and self.obj_ref != '**new**':
            self.parents = PermittedNodeFamily(
                node = self.obj_ref,
                user = self.request.user,
                perm = [{'nde_tasks': 'read'}]).parents
            self.children = PermittedNodeFamily(
                parent = self.obj_ref,
                perm = [{'nde_tasks': 'read'}]).siblings_left

    def add_form_elements(self):
        self.detail.add(HtmlWidget, 'display_body',
                        title = '',
                        output = 'super',
                        add_space_line = False,
                        )

    def populate_fields(self):
        self.has_errors()
        node = self.obj['nd_node']
        service = self.controller_interface.service(self.obj_type)
        type_lname = (service.nd_controller_display_name() if
                      service else self.obj_type)
        if self.obj_ref == '**new**':
            _t = "Name of new node"
            title_text =  "New Entry"
            form_title = title_text
        else:
            _t = self.obj_ref
            title_text = ("<strong>%s</strong>"%
                          node.nde_name
                          )
            form_title = ("%s"%
                          (node.nde_name))
        self.detail.set_title(title_text)
        self.set_title(form_title)
        node_body = self.detail.get_widget('display_body')
        
        node_body.set_title(self._formatted_main())

    def _get_main(self):
        """ Find the text that forms the main body of the display.

            Overridable to allow others to inherit this display
            paradigm.
        """
        node = self.obj['nd_node']
        return node.nde_description or '(No description given)'
    
    def _formatted_main(self):
        response_list = []
        body_list = []
        body_list.append(self._get_main())
        if self.children:
            body_list.append('----') # Transition
            subsection_list = []
            target = 'default'
            for subsection_obj in self.children:
                url_parts = {'object_id': subsection_obj.nde_idx}
                subsection_url = url_for(target, url_parts)
                subsection_name = subsection_obj.nde_name
                subsection_list.append(
                    '+ `%s <%s>`_'% (subsection_name, subsection_url))
            body_list.append('\n\n'.join(subsection_list))
           
        response_list.append(render_page('\n\n'.join(body_list), self.request))
        return '<br>'.join(response_list)

#-----------------------------------------------------------------------
