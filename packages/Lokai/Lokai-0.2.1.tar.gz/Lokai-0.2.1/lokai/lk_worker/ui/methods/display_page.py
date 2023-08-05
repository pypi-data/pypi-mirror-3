# Name:      lokai/lk_worker/ui/methods/display_page.py
# Purpose:   Handle formatted, read-only, display of node details.
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

from lokai.lk_worker.ui.rest_extra import render_page
from lokai.lk_worker.ui.methods.base_form import NodeBaseForm

from lokai.lk_worker.nodes.node_data_functions import PermittedNodeFamily
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
                              perm = 'nde_tasks',
                              use_tokens=False,
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
                           fieldset   = {'border':1},
                          )
        self.detail = self.get_widget('detail')
        self.add_form_elements()

    def build_objects(self):
        """ Set up drop down lists such as depend on node type.
        """
        if self.obj_ref and self.obj_ref != '**new**':
            self.parents = PermittedNodeFamily(node=self.obj_ref,
                                    user = self.request.user,
                                    perm = [{'nde_tasks': 'read'}]).parents

            self.obj_type = self.obj['nd_node'].nde_type
            #
            # Insert something here to pick up other data types
            #


    def add_form_elements(self):
        self.detail.add(SideBarWidget, 'activity',
                        title = '',
                        output = 'super'
                        )
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
            title_text =  "New Entry"
            form_title = title_text
        else:
            title_text = ("<strong>%s</strong> (%s)"%
                          (node.nde_name,
                           type_lname))
            form_title = ("%s (%s)"%
                          (node.nde_name,
                           type_lname))
        self.detail.set_title(title_text)
        self.set_title(form_title)
        self.detail.get_widget('activity').set_title(self._formatted_side_bar())
        node_body = self.detail.get_widget('display_body')
        
        node_body.set_title(self._formatted_main())

    def process_input(self, deep_get=None, perm=None):
        pass

    def _formatted_main(self):
        node = self.obj['nd_node']
        response_list = []
        if self.view_interface.service('node'):
            description_text = node.nde_description or '(No description given)'
            response_list.append(render_page(description_text, self.request))
        
        # Bring in the extensions
        for extn in self.view_interface:
            response_list.extend(extn.nd_display_main(self))
        return '<br>'.join(response_list)
    
    def _formatted_side_bar(self):
        response_list = []
        node = self.obj['nd_node']
        if self.view_interface.service('node'):
            response_list.append("Node Number %s"% node.nde_idx)
            if hasattr(node, 'nde_client_reference'):
                response_list.append("External Reference %s"%
                                     node.nde_client_reference)
            response_list.append("Last updated %s"% node.nde_date_modify)
            response_list.append("Created %s"%node.nde_date_create)

        # Bring in the extensions
        for extn in self.view_interface:
            response_list.extend(extn.nd_display_side(self))
                    
        
        return '<br>'.join(response_list)        

#-----------------------------------------------------------------------
