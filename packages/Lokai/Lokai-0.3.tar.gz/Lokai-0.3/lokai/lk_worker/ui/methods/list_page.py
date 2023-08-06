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
import json

import lokai.tool_box.tb_common.dates as dates
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

from lokai.lk_worker.extensions.view_interface import IWorkerView

view_extensions = component.ExtensionPoint(IWorkerView)

from lokai.lk_worker.extensions.controller_interface import IWorkerController

controller_extensions = component.ExtensionPoint(IWorkerController)

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
        super(ListPage, self).__init__(
            request, object_reference, data_object)

        self._get_field_map()
        self.search_full = self.node_perm.test_permit_list(
            [{'nde_search_full': 'read'}])


    def _get_display_columns(self):
        """ set self.headings with an appropriate set of columns
            acording to whatever logic might apply. Typically this might
            depend on user permisions.
        """
        self.search_full = self.node_perm.test_permit_list(
            [{'nde_search_full': 'read'}])
        if self.search_full:
            self.headings = copy.copy(self.headings_full)
            for extn in view_extensions:
                if 'severity' in extn.nd_view_selection_lists():
                    self.headings[4:4] = [('act_type', 'Severity', ndActivity)]
                    break
        else:
            self.headings = copy.copy(self.headings_limited)

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
        if self.selection_filter:
            base_query = {'filter': json.dumps(self.selection_filter)}
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
            url_parts = {'object_id': self.obj_ref}
        else:
            url_parts = None
        target = self.current_target
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
                    url_parts = {'object_id': self.obj_ref}
                else:
                    url_parts = None
                target = None
                if len(some_heading) > 2:
                    target = self.current_target
                self.columns.append((some_heading[0],
                                     title,
                                     target,
                                     url_parts,
                                     query))

    def _basic_field(self, u_row, field_name, widget, column):
        value = get_column_value(u_row, field_name)
        widget.add(DisplayOnlyWidget, str(column), value=value)

    def _date_field(self, u_row, field_name, widget, column):
        value = get_column_value(u_row, field_name)
        value = dates.timetostr(value, '%Y-%m-%d')
        widget.add(DisplayOnlyWidget, str(column), value=value)

    def _date_time_field(self, u_row, field_name, widget, column):
        value = get_column_value(u_row, field_name)
        value = dates.timetostr(value, '%Y-%m-%d %H:%M')
        widget.add(DisplayOnlyWidget, str(column), value=value)
        
    def _node_reference(self, u_row, field_name, widget, column):
        value = get_column_value(u_row, field_name)
        base_query = {}
        if self.new_child:
            base_query['down'] = self.new_child
        if not value:
            value = get_column_value(u_row, 'nde_idx')
        query = {}
        url_parts = {'object_id': value}
        query.update(base_query)
        widget.add(LinkWidget, '0',
                   value = value,
                   target = 'default',
                   url_parts = url_parts,
                   query = query)

    def _act_status(self, u_row, field_name, widget, column):
        status_options = self.row_selection_sets.get('status')
        value = get_column_value(u_row, field_name)
        try:
            value = status_options.get_value(value)
        except AttributeError:
            pass
        widget.add(DisplayOnlyWidget, str(column), value=value)

    def _act_priority(self, u_row, field_name, widget, column):
        status_options = self.row_selection_sets.get('priority')
        value = get_column_value(u_row, field_name)
        try:
            value = status_options.get_value(value)
        except AttributeError:
            pass
        widget.add(DisplayOnlyWidget, str(column), value=value)

    def _act_type(self, u_row, field_name, widget, column):
        status_options = self.row_selection_sets.get('severity')
        value = get_column_value(u_row, field_name)
        try:
            value = status_options.get_value(value)
        except AttributeError:
            pass
        widget.add(DisplayOnlyWidget, str(column), value=value)

    def _get_field_map(self):
        self.field_map = {
            'nde_client_reference': self._node_reference,
            'nde_name': self._basic_field,
            'act_date_remind': self._date_field,
            'act_status': self._act_status,
            'act_priority': self._act_priority,
            'act_type': self._act_type,
            'nde_date_modify': self._date_time_field,
            }
    
    def _prepare_for_list_display(self, u_row):
        """ Set up any data, such as selection sets, that might be
            usefull somewhere in the current row.
        """
        row_type = get_column_value(u_row, 'nde_type')
        target_extension = (controller_extensions.service(row_type) or
                            controller_extensions.service('generic'))
        self.row_selection_sets = target_extension.nd_view_selection_lists()

    def build_row_display(self, u_row, widget):
        """ Add display widgets to a given row widget """
        self._prepare_for_list_display(u_row)
        for j in range(0, len(self.headings)):
            field_name = self.headings[j][0]
            self.field_map.get(
                field_name, self._basic_field)(
                u_row, field_name, widget, j)

    def build_post_form(self):
        """ Add any usefull links at the base of the form.

            This default structure supports the search for potential
            parents.
        """
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
