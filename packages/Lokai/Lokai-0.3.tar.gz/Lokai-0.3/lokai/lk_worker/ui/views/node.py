# Name:      lokai/lk_worker/ui/views/node.py
# Purpose:   Provide user interviews for generic node data
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

from lokai.tool_box.tb_common.dates import now
from lokai.tool_box.tb_forms.widget import (
    RowWidget,
    StringWidget,
    IntWidget,
    TextWidget,
    CompositeWidget,
    SingleSelectWidget,
    )

from lokai.lk_common.selection_map import SelectionMap
from lokai.lk_worker.ui.link_widget import LinkWidget

#-----------------------------------------------------------------------

import pyutilib.component.core as component
from lokai.lk_worker.extensions import PluginIdCompare
from lokai.lk_worker.extensions.view_interface import IWorkerView
from lokai.lk_worker.extensions.controller_interface import IWorkerController

from lokai.lk_worker.extensions.data_interface import IWorkerData
data_extensions = component.ExtensionPoint(IWorkerData)

#-----------------------------------------------------------------------

controller_interface = component.ExtensionPoint(IWorkerController)

#-----------------------------------------------------------------------

class PiNodeView(PluginIdCompare, component.SingletonPlugin):

    def __init__(self):
        self.name = 'node'
        self.selection_maps = {} # Selection maps, if required.

    def nd_view_selection_lists(self):
        return self.selection_maps

    def nd_view_form_extend(self, form):
        type_set = []
        for extn in controller_interface:
            if not extn.nd_controller_hidden():
                type_set.append(( extn.name, extn.nd_controller_display_name(),))
        type_option_object = SelectionMap(found_data=type_set)
        
        form.detail.add(CompositeWidget, 'node_edit',
                        title = 'Edit basic details',
                        fieldset = {'expand': 'open'}
                        )
        node_edit = form.detail.get_widget('node_edit')
        node_edit.add(StringWidget, 'nde_name',
                        title = 'Name',
                        )
        node_edit.add(StringWidget, 'client_ref',
                        title = 'External Reference',
                        )
        node_edit.add(SingleSelectWidget, 'node_type',
                        title = 'Data Type',
                        options = type_option_object.get_options(prepends=[]))
        node_edit.add(TextWidget, 'node_description',
                        title = 'Description',
                        output = 'wide')
        node_edit.add(IntWidget, 'node_order',
                      title = 'Display sequence number'
                      )
        node_edit.add(CompositeWidget, 'parents',
                        title = 'Parents',
                        output = 'wide',
                      fieldset={'expand': 'closed'}
                        )

    def nd_view_form_populate(self, form):
        node_edit = form.detail.get_widget('node_edit')
        node = form.obj['nd_node']
        node_edit.get_widget('nde_name').set_value(node.nde_name)
        if hasattr(node, 'nde_client_reference'):
            node_edit.get_widget(
                'client_ref').set_value(node.nde_client_reference)
        target_extension = (controller_interface.service(form.obj_type) or
                            controller_interface.service('generic'))
        type_lname = target_extension.nd_controller_display_name()
        field_label = form.obj_ref
        title_text = ("<strong>%s</strong> (%s)"%
                      (node.nde_name, type_lname))
        form_title = ("%s (%s)"%
                      (node.nde_name, type_lname)) 
        form.detail.set_title(title_text)
        form.set_title(form_title)
        node_edit.get_widget('nde_name').set_title(field_label)
        nde_type = node.nde_type
        node_edit.get_widget('node_type').set_value(nde_type)
        node_edit.get_widget('node_description').set_value(node.nde_description)
        nde_sequence = form.obj.get('nd_edge',{}).get('nde_sequence', '')
        node_edit.get_widget('node_order').set_value(nde_sequence)

        parent_box = node_edit.get_widget('parents')

        # Find the first parent in the list that is not the current
        # parent.
        next_up = None
        for parent_instance in form.parents:
            if parent_instance.nde_idx != form.this_up:
                next_up = parent_instance.nde_idx
                break

        for parent_instance in form.parents:
            if True:
                row_name = "row%s"% parent_instance
                parent_box.add(RowWidget, row_name)
                query = {}
                url_parts = {'object_id': parent_instance.nde_idx}
                name = "x%s"% parent_instance
                parent_box.add(LinkWidget, name,
                            value = "%s : %s"% (parent_instance.nde_idx,
                                                parent_instance.nde_name),
                            target = 'default',
                            url_parts = url_parts,
                            query = query
                            )
                this_box = parent_box.get_widget(name)
                query = {'up' : parent_instance.nde_idx,
                         }
                # Add in a link to this or a new parent to maintain
                # the 'up' value across the redirect.
                poss_up = (form.this_up
                           if parent_instance.nde_idx != form.this_up
                           else next_up)
                if poss_up:
                    query['next_up'] = poss_up
                url_parts = {'object_id': form.obj_ref}
                link_source = LinkWidget("del%s" %parent_instance,
                            value = "delete",
                            target = 'unlink',
                            url_parts = url_parts,
                            query = query
                            )
                this_box.set_additional(link_source.make_href())
        
        row_name = "row**new**"
        parent_box.add(LinkWidget, "**new**",
                    value = 'Search and add new parent',
                    target = 'search_top',
                    query = {'down' : form.obj_ref}
                    )

    def nd_view_form_default(self, form):
        # Do this for blank form 
        node_edit = form.detail.get_widget('node_edit')
        field_label = "Name of new node"
        title_text =  "New Entry"
        form_title = title_text
        form.detail.set_title(title_text)
        nde_type = form.obj_type
        node_edit.get_widget('node_type').set_value(nde_type)

        parent_box = node_edit.get_widget('parents')
        row_name = "row**new**"
        parent_box.add(LinkWidget, "**new**",
                    value = 'Search and add new parent',
                    target = 'search_top',
                    query = {'down' : form.obj_ref}
                    )

    def nd_view_form_process(self, form):
        input_errors = {}
        # Test the form information
        #
        node_edit = form.detail.get_widget('node_edit')
        nde_name = node_edit.get_widget('nde_name').value
        if nde_name is None:
            nde_name = ''
        nde_name = nde_name.strip()
        if not nde_name:
            text = "%s must be given" % (
                node_edit.get_widget('nde_name').title)
            input_errors['nde_name'] = text
            node_edit.get_widget('nde_name').set_error(text)
        return len(input_errors)

    def nd_view_form_store(self, form):
        hist_response = []
        node_edit = form.detail.get_widget('node_edit')
        node_detail = {'nde_date_modify' : form.this_date}
        if form.is_new:
            node_detail['nde_date_create'] = form.this_date
        else:
            node_detail['nde_idx'] = form.obj_ref
        nde_name = node_edit.get_widget('nde_name').value
        node_detail['nde_name'] = nde_name
        node_detail['nde_type'] = node_edit['node_type']
        node_detail['nde_description'] = node_edit['node_description']
        node_detail['nde_client_reference'] = node_edit['client_ref']
        form.new_obj['nd_node'] = node_detail
        nde_sequence = node_edit['node_order']
        form.new_obj['nd_edge'] = {'nde_sequence':nde_sequence}
        new_data =  form.new_obj.get('nd_node')
        old_data = form.obj.get('nd_node')
        if new_data and old_data:
            new_text = new_data.get('nde_description')
            old_text = old_data.get('nde_description')
            if old_text != new_text:
                hist_response.append(
                    "Node description updated")
        return hist_response

    def nd_display_main(self, form):
        return []

    def nd_display_side(self, form):
        return []

#-----------------------------------------------------------------------
