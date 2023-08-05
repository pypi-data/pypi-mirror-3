# Name:      lokai/lk_worker/ui/methods/list_page.py
# Purpose:   Responses to requests for project related objects
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

import copy

from werkzeug import url_encode

from lokai.tool_box.tb_database.orm_access import get_column_value

from lokai.tool_box.tb_forms.widget import (ButtonRow,
                                     DisplayOnlyWidget)

from lokai.lk_worker.nodes.search import search_children, search_ordered
from lokai.lk_worker.nodes.search_filtered import get_node_basic
from lokai.lk_worker.models import ndNode
from lokai.lk_worker.models.builtin_data_activity import ndActivity

from lokai.lk_worker.nodes.graph import is_cycle
from lokai.lk_worker.nodes.node_data_functions import NodeFamily
from lokai.lk_worker.ui.local import get_object_reference
from lokai.lk_worker.ui.link_widget import LinkWidget
from lokai.lk_worker.ui.methods.selection_list import SelectionList

#-----------------------------------------------------------------------

import pyutilib.component.core as component
from lokai.lk_worker.extensions.controller_interface import IWorkerController

controller_interface = component.ExtensionPoint(IWorkerController)

#-----------------------------------------------------------------------

__all__ = ['ListPage']

#-----------------------------------------------------------------------

class ListPage(SelectionList):

    keys = {
        # Describe the form
        'perm'      : 'nde_tasks',
        'title'     : '',
        'formname'  : 'nb_list',
        'chunksize' : 10,
        }

    headings_limited = [
        ('nde_client_reference', 'Node Reference', ndNode),
        ('nde_name', 'Name', ndNode),
        ]
    headings_full = [
        ('nde_client_reference', 'Node Reference', ndNode),
        ('nde_name', 'Name', ndNode),
        ('act_date_remind', 'Bring Forward', ndActivity),
        ('act_status', 'Status', ndActivity),
        ('act_priority', 'Priority', ndActivity),
        ('nde_date_modify', 'Last changed', ndNode)
        ]
    
    def __init__(self, request, object_reference, data_object, **kwargs):
        self.node_perm = perm = request.derived_locals['permissions']
        self.request = request
        self.obj_ref = object_reference
        self.new_child = request.args.get('down')
        self.filter = request.args.get('filter', {})

        self.search_full = self.node_perm.test_permit_list(
            [{'nde_search_full': 'read'}])
        if self.search_full:
            self.headings = copy.copy(self.headings_full)
        else:
            self.headings = copy.copy(self.headings_limited)

        SelectionList.__init__(self, request)

    def _add_to_query(self, query):
        """ Add another table to the basic node query. Do this by
            overloading.
        """
        return query
    
    def run_query(self):
        # Don't need permission - we must be at a node that does it for us
        query = get_node_basic()
        query = self._add_to_query(query)
        query = search_children(query, self.obj_ref)
        query = search_ordered(
            query,
            self.flow,
            self.sort_column,
            self.headings[self.heading_map[self.sort_column]][2])
        self.u_set_len = query.count()
        start = self.start_row
        end = start + self.chunksize
        self.u_set = query.all()[start:end]

    def build_navigation(self):
        #
        # This form has three buttons - left, up and right

        base_query = {}
        if self.filter:
            base_query = {'filter': url_encode(self.filter)}
        if self.new_child:
            base_query['down'] = self.new_child
            
        self.btf_enabled = [True, True, True]
        left_row = self.start_row - self.chunksize
        if left_row < 0:
            left_row = 0
            self.btf_enabled[0] = False
            self.btf_enabled[1] = False
        right_row = self.start_row + self.chunksize
        if right_row >= self.u_set_len:
            right_row = 0
            self.btf_enabled[2] = False
        order = self.current_col
        flow = self.flow
        left_query = {'row' : left_row,
                      'order' : order,
                      'flow' : flow}
        left_query.update(base_query)
        up_query = {'row' : 0,
                    'order' : order,
                    'flow' : flow}
        up_query.update(base_query)
        right_query = {'row' : right_row,
                       'order' : order,
                       'flow' : flow}
        right_query.update(base_query)
        if self.obj_ref:
            target = 'list'
            url_parts = {'object_id': self.obj_ref}
        else:
            target = 'search_top'
            url_parts = None
        self.btf_pages = [('Previous',
                           target, url_parts, left_query),
                          ('First',
                           target, url_parts, up_query),
                          ('Next',
                           target, url_parts, right_query),
                          ]
        #
        # Now for the headings
        self.columns = []
        for some_heading in self.headings:
            if (isinstance(some_heading, (list, tuple)) and
                len(some_heading) > 1):
                flow = 'ASC'
                title = some_heading[1]
                if self.current_col == some_heading[0]:
                    if self.flow == 'ASC':
                        title = "%s (+)"% title
                        flow = 'DSC'
                    else:
                        title = "%s (-)"% title
                        flow = 'ASC'
                query = {'row' : self.start_row,
                         'order' : some_heading[0],
                         'flow' : flow}
                query.update(base_query)
                if self.obj_ref:
                    target = 'list'
                    url_parts = {'object_id': self.obj_ref}
                else:
                    target = 'search_top'
                    url_parts = None
                self.columns.append((some_heading[0],
                                     title,
                                     target,
                                     url_parts,
                                     query))

    def build_row_display(self, u_row, widget):
        # Add display widgets to a given row widget

        # We know that the first column contains a node number, so the
        # value for that is also the value for the link.

        # 1st column has a link

        row_type = get_column_value(u_row, 'nde_type')
        row_controller = controller_interface.service(row_type)
        try:
            act_view = row_controller.view_interface.service('activity')
        except AttributeError:
            raise AttributeError("No view interface for %s" % row_type) 
        if act_view:
            selection_sets = act_view.nd_view_selection_lists()
            act_type_options = selection_sets.get('severity')
            priority_options = selection_sets.get('priority')
            status_options = selection_sets.get('status')
        else:
            act_type_options = None
            priority_options = None
            status_options = None
        base_query = {}
        if self.new_child:
            base_query['down'] = self.new_child

        value = get_column_value(u_row, self.headings[0][0])
        if value is None:
            value = get_column_value(u_row, 'nde_idx')
        query = {}
        query.update(base_query)
        target = 'default'
        if self.new_child:
            target = 'list'
        url_parts = {'object_id': value}
        widget.add(LinkWidget, '0',
                   value = value,
                   target = target,
                   query = query,
                   url_parts = url_parts)
        for j in range(1, len(self.headings)):
            field_name = self.headings[j][0]
            value = get_column_value(u_row, field_name)
            widget.add(DisplayOnlyWidget, str(j))
            if field_name == 'act_priority':
                if priority_options:
                    value = priority_options.get_value(value)
                else:
                    value = ''
            if field_name == 'act_status':
                if status_options:
                    value = status_options.get_value(value)
                else:
                    value = ''
            if field_name == 'act_type':
                if act_type_options:
                    value = act_type_options.get_value(value)
                else:
                    value = ''
            widget.get_widget(str(j)).set_value(value)

    def build_post_form(self):
        # Add in the submit row so that it goes at the end
        if self.new_child:
            self.table_widget.add(ButtonRow, 'actions')
            button_row = self.table_widget.get_widget('actions')
            if is_cycle(self.new_child, self.obj_ref):
                button_row.add(DisplayOnlyWidget, 'is_cycle',
                               value = 'This entry cannot be used as a parent')
                button_row.add(LinkWidget, 'link', 'Return to original node',
                               target = 'default',
                               url_parts = {'object_id': self.new_child},
                               query={})
            else:
                button_row.add(DisplayOnlyWidget, 'nothing')
                button_row.add(LinkWidget, 'link', 'Use as parent node',
                               target = 'link',
                               url_parts = {'object_id': self.new_child},
                               query={'up' : self.obj_ref})

#-----------------------------------------------------------------------
