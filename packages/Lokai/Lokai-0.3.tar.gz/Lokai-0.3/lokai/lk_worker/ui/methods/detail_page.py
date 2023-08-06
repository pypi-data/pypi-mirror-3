# Name:      lokai/lk_worker/ui/methods/detail_page.py
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

import logging

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update
from lokai.tool_box.tb_common.dates import now
from lokai.lk_worker.ui.rest_extra import render_page

from lokai.tool_box.tb_forms.widget import (
    CompositeWidget,
    SubmitWidget,
    )
from lokai.lk_ui import get_use_form_token

from lokai.lk_common.selection_map import SelectionMap
from lokai.lk_worker.ui.methods.base_form import NodeBaseForm
from lokai.lk_worker.ui.local import url_for

from lokai.lk_worker.models import ndNode, ndEdge
from lokai.lk_worker.nodes.data_interface import put_node_dataset
from lokai.lk_worker.nodes.graph import make_link
from lokai.lk_worker.models.builtin_data_activity import HistoryStore
from lokai.lk_worker.nodes.node_data_functions import PermittedNodeFamily
from lokai.lk_worker.ui.link_widget import LinkWidget
from lokai.lk_worker.ui.widget import HtmlWidget

#-----------------------------------------------------------------------

import pyutilib.component.core as component
from lokai.lk_worker.extensions.view_interface import IWorkerView
from lokai.lk_worker.extensions.controller_interface import IWorkerController

#-----------------------------------------------------------------------

__all__ = ['DetailPage']

#-----------------------------------------------------------------------

class DetailPage(NodeBaseForm):

    def __init__(self, request, object_reference, data_object, **kwargs):
        title = kwargs.get('title') or 'Node Detail'
        perm = kwargs.get('perm') or 'nde_tasks'
        self.view_interface = (kwargs.get('view_interface') or
                                component.ExtensionPoint(IWorkerView))
        self.controller_interface =  (kwargs.get('controller_interface') or
                                component.ExtensionPoint(IWorkerController))
        self.up = request.args.get('up', None)
        self.error_count = 0
        try:
            self.obj_type = data_object['nd_node'].nde_type
        except KeyError:
            self.obj_type = request.args.get('type', 'generic')
        # Look to see if the 'preview' submit button was pressed
        self.do_preview = request.form.get('detail___preview')
        # Build a drop-down option list of available types.
        type_set = []
        for extn in self.controller_interface:
            type_set.append(( extn.name, extn.nd_controller_display_name(),))
        self.type_option_object = SelectionMap(found_data=type_set)
        NodeBaseForm.__init__(self,
                              request,
                              object_reference,
                              data_object,
                              enctype = "multipart/form-data",
                              title = title,
                              perm = perm,
                              use_tokens = get_use_form_token(),
                              )

    def _identify_form_action(self):
        """ Decide on the url that is going to respond to user input.
        """
        if not self.obj_ref or self.obj_ref == '**new**':
            base_action = 'add'
            target_object = {'object_id': '**new**',
                             'up': str(self.up),
                             'type': self.obj_type}
        else:
            base_action = 'edit'
            target_object = {'object_id': self.obj_ref}
        return url_for(base_action, target_object)
        
    def build_form(self):
        """ Add any widgets to the form
        """
        self.add_composite('detail',
                           title      = self.title,
                           fieldset   = {},
                          )
        self.detail = self.get_widget('detail')
        self.add_form_elements()
        if self.obj:
            self.add_update_buttons()
        else:
            self.add_register_buttons()
        
    #-------------------------------------------------------------------
    # Main structure

    def add_register_buttons(self):
        """ Only want one button in this version.
        """
        if self.can_add:
            self.detail.add(SubmitWidget, 'register', 'Register')
    
    def add_update_buttons(self):
        """ Want two buttons in this version.
        """
        if self.can_edit:
            self.detail.add(SubmitWidget, 'preview', 'Preview')
            self.detail.add(SubmitWidget, 'update', 'Update')

    def build_objects(self):
        """ Set up drop down lists such as depend on node type.
        """
        self.parents = []
        self.this_up = None
        if self.obj_ref and self.obj_ref != '**new**':
            self.parents = PermittedNodeFamily(
                node=self.obj_ref,
                parent=self.up,
                user = self.request.user,
                perm = [{'nde_tasks': 'read'}]).parents

            self.obj_type = self.obj['nd_node'].nde_type
            if self.parents:
                self.this_up = self.parents[0].nde_idx
                edge = engine.session.query(
                    ndEdge
                    ).filter(
                    ndEdge.nde_parent == self.this_up).first()
                if edge:
                    self.obj['nd_edge'] = edge
        else:
            self.this_up = self.up

    def add_form_elements(self):
        if self.do_preview:
            self.detail.add(HtmlWidget, 'display_body',
                        title = '',
                        output = 'super',
                        add_space_line = False,
                        )
        for extn in self.view_interface():
            extn.nd_view_form_extend(self)

    def populate_fields(self):
        # intended to parse the empty form before we populate it 
        self.has_errors()
        #
        for extn in self.view_interface:
            extn.nd_view_form_populate(self)
                                             
    def populate_defaults(self):
        # intended to parse the empty form before we populate it 
        self.has_errors()
        #
        for extn in self.view_interface:
            extn.nd_view_form_default(self)

    def _process_validate(self):
        """ Partition process_input into two. Partly to foil McCabe,
            also to allow separate call for preview.
        """
        self.error_count = 0
        if self.has_errors():
            self.error_count = 1
        for extn in self.view_interface:
            self.error_count += extn.nd_view_form_process(self)
        if self.error_count:
            node_edit = self.detail.get_widget('node_edit')
            self.detail.set_title(
                self.detail.get_title()[:100] + " (Data not stored) ")
            node_edit.fieldset['expand'] = 'open'
            return False
        return True

    def _process_store(self):
        """ Handle the POST return
        """
        self.is_new = True
        if self.obj:
            self.is_new = False
        node_edit = self.detail.get_widget('node_edit')

        nde_name = node_edit.get_widget('nde_name').value
        if nde_name is None:
            nde_name = ''
        history_store = HistoryStore(None, self.request.user, nde_name=nde_name)
        self.this_date = now()
        #
        # Handle node extensions
        for extn in self.view_interface:
            history_store.append(extn.nd_view_form_store(self))
        self.obj_ref = put_node_dataset(self.new_obj, self.obj)
        #
        # Now the parent
        if self.up and self.is_new:
            make_link(self.obj_ref, self.up)
        #
        # And edge related stuff
        if self.this_up and 'nd_edge' in self.new_obj:
            self.new_obj['nd_edge']['nde_parent'] = self.this_up
            self.new_obj['nd_edge']['nde_child'] = self.obj_ref
            insert_or_update(ndEdge, self.new_obj['nd_edge'],  required_existing=1)
        history_store.time = self.this_date
        history_store.nde_idx = self.obj_ref
        history_store.store()
        engine.session.flush()
        self.detail.set_title(
            self.detail.get_title()[:100] + " (Data updated) ")
        return True

    def _formatted_main(self):
        return render_page(
            self.detail.get_widget('node_edit')['node_description'],
            self.request)

    def process_input(self):
        """ Respond to input somehow. Treat preview the same as error
            in that we do not update the database.

            We are mixing in controller functionality here. Not really
            the best place for it, but it allows us to manipulate the
            view. The alternative would be to introspect the view
            somehow, or build a completeley new one.
        """
        not_error = self._process_validate()
        if self.do_preview:
            node_body = self.detail.get_widget('display_body')
            node_body.set_title(self._formatted_main())
            return False # to force the controller to do something
        else:
            return not_error and self._process_store()

#-----------------------------------------------------------------------
