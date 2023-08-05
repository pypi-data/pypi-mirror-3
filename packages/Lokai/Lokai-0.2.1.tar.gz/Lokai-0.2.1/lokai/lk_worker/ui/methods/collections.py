# Name:      lokai/lk_worker/ui/methods/collections.py
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

import datetime
import copy

from werkzeug import url_decode, url_encode
import lokai.tool_box.tb_common.notification as notify
from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import get_column_value
import lokai.tool_box.tb_common.dates as dates
from lokai.tool_box.tb_forms.form import Form

from lokai.tool_box.tb_forms.widget import (StringWidget,
                                            SubmitWidget,
                                            DisplayOnlyWidget,
                                            ButtonRow,
                                            DateWidget,
                                            CompositeWidget,
                                            RawCompositeWidget,
                                            SingleSelectWidget,
                                            HiddenWidget,
                                            )
from lokai.lk_worker.ui.link_widget import LinkWidget
from lokai.lk_ui import get_use_form_token

from lokai.lk_login.db_objects import User
from lokai.lk_login.userpermission import UserPermission, GUEST_NAME

from lokai.lk_worker.models import ndNode
from lokai.lk_worker.models.builtin_data_activity import ndActivity

from lokai.lk_worker.models.builtin_data_resources import (
    get_full_node_resource_list,
    user_top_trees)
from lokai.lk_worker.nodes.node_data_functions import get_user_node_permissions

from lokai.lk_worker.nodes.search import search_ordered
from lokai.lk_worker.nodes.search_filtered import (search_filtered,
                                      get_node_basic)
from lokai.lk_worker.nodes.data_interface import get_node_dataset

from lokai.lk_worker.ui.methods.selection_list import SelectionList

from lokai.lk_worker.ui.local import url_for, get_object_reference

#-----------------------------------------------------------------------

import pyutilib.component.core as component
from lokai.lk_worker.extensions.view_interface import IWorkerView

view_extensions = component.ExtensionPoint(IWorkerView)

from lokai.lk_worker.extensions.controller_interface import IWorkerController

controller_extensions = component.ExtensionPoint(IWorkerController)

#-----------------------------------------------------------------------

class FilterPage(Form):

    def __init__(self, request, object_reference, data_object, **kwargs):
        Form.__init__(self, request_object=request,
                      use_tokens=get_use_form_token(),
                      **kwargs)
        self.node_perm = request.derived_locals['permissions']
        self.search_full = self.node_perm.test_permit_list(
            [{'nde_search_full': 'read'}])
        self.search_on_node = self.node_perm.test_permit_list(
            [{'nde_tasks': 'read'}])
        self.request = request
        self.new_child = request.values.get('down')
        self.obj_ref = object_reference
        self.obj = data_object
        filter_data = request.args.get('filter')
        self.filter = {}
        if filter_data:
            self.filter = url_decode(filter_data)
        self.new_filter = None
        if self.search_full:
            self._get_useful_data()
        self.build_form()

    def _get_useful_data(self):
        """ Specific background data to support full search
        """
        self.status_selection = [('00', 'All', '00'),
                                 ('10', 'Open', '10'),
                                 ('20', 'Open & Active', '20'),
                                 ('30', 'Active', '30'),
                                 ('40', 'Closed', '40'),
                                 ]
        self.resource_selection = [('**ignore**',
                                    'Omit search for assigned user',
                                    '**ignore**')]
        available_resources = get_full_node_resource_list(self.obj_ref)
        for some_resource in available_resources:
            user = engine.session.query(
                User).filter(
                User.user_uname == some_resource.rla_user).one()
            display_name = user.user_lname
            if not display_name:
                display_name = user.user_uname
            self.resource_selection.append(
                (user.user_uname,
                 display_name,
                 user.user_uname))
        if len(self.resource_selection) == 1:
            user_lname = request.client_session.get(
                'ident', {}).get('user long name')
            self.resource_selection.append(
                (self.request.user,
                 str(user_lname),
                 self.request.user))

    def build_form(self):
        if self.new_child:
            self.add(HiddenWidget, 'down', value=self.new_child)
        self.add(CompositeWidget, 'search',
                           title      = 'Filter',
                           fieldset   = {},
                          )
        one = self.get_widget('search')
        if self.search_on_node:
            one.add(StringWidget, 'nd_node',
                    title = 'Search from here downwards',
                    hint = ('Enter a complete node id number to '
                            'start the search from'),
                    readonly = not self.search_full)
            #
            one.add(StringWidget, 'client_ref',
                    title = 'External Reference',
                    hint = 'Enter a part of an external reference')
        #
        one.add(StringWidget, 'name',
                title = 'Node Name',
                hint = 'Enter a part of a name')
        #
        one.add(StringWidget, 'nd_tags',
                title = 'Search Tags',
                hint = 'One or more space separated tags')
        #
        if self.search_full:
            one.add(SingleSelectWidget, 'assignee',
                    value = self.request.user,
                    title = 'Select assigned user',
                    options = self.resource_selection)
            #
            one.add(SingleSelectWidget, 'status',
                    value = '20',
                    title = "Status range",
                    options = self.status_selection)
            #
            one.add(CompositeWidget, 'activity',
                    title      = 'Activities',
                    fieldset   = {'expand': 'open'}
                              )
            act = one.get_widget('activity')
            act.add(RawCompositeWidget, 'bf_range', #Brought forward range
                    title = 'Bring Forward Date (From - To)',
                    output='normal'
                    )
            bf_range = act.get_widget('bf_range')
            bf_range.add(DateWidget, 'bf_range_from',
                         hint='Show items with reminder dates >= this date')
            bf_range.add(DateWidget, 'bf_range_to',
                         hint='Show items with reminder dates <= this date')
        #
        one.add(SubmitWidget, 'filter_button',
                value = 'Show selection')
        self.restore_filter_value()
        # Use one.get_widget().value here. The form one[xx] has the
        # side effect of parsing the input and, as there is none, the
        # value goes to None
        if 'nd_node' in one and one.get_widget('nd_node').value:
            self.action = url_for('search',
                                  {'object_id':
                                   one.get_widget('nd_node').value})
            
        else:
            self.action = url_for('search_top')                  

    def process_input(self):
        error_count = 0
        if self.has_errors(): # force form to parse itself
            error_count = 1
        one = self.get_widget('search')
        #
        # Check a few things ...

        if self.search_on_node:
            input_errors = {}
            # Any node entered in the node box must be permitted.
            local_nde_idx = one['nd_node']
            if local_nde_idx:
                any_match = get_node_basic(local_nde_idx).all()
                if len(any_match) != 1:
                    input_errors['nd_node'] = (
                        "%s not found"% local_nde_idx)
            error_count += len(input_errors)
            for k in input_errors:
                one.get_widget(k).set_error(input_errors[k])

        if self.search_full:
            input_errors = {}
            # Reminder dates must be valid and ordered.
            act = one.get_widget('activity')
            bf_range = act.get_widget('bf_range')
            bf_from = bf_range['bf_range_from']
            btf_from_date = None
            btf_to_date = None
            if bf_from:
                try:
                    btf_from_date = dates.strtotime(bf_from)
                except dates.ErrorInDateString:
                    input_errors['bf_range'] = "%s is not a valid date"% bf_from
                except ValueError:
                    input_errors['bf_range'] = ("%s has too many days for"
                                                " the month"% bf_from)
                    
            bf_to = bf_range['bf_range_to']
            if bf_to:
                try:
                    btf_to_date = dates.strtotime(bf_to)
                except dates.ErrorInDateString:
                    input_errors['bf_range'] = "%s is not a valid date"% bf_to
                except ValueError:
                    input_errors['bf_range'] = ("%s has too many days for"
                                                " the month"% bf_to)
                
            if ((btf_from_date and btf_to_date) and
                (btf_from_date > btf_to_date) ):
                input_errors['bf_range'] = (
                    "From date should be less than to date")

            error_count += len(input_errors)
            for k in input_errors:
                act.get_widget(k).set_error(input_errors[k])
        if error_count:
            return False
        #
        # Place new filter in the object
        self.get_filter_value()
        #
        # Set up any extra display stuff
        if self.obj and 'nd_node' in one:
            one.get_widget('nd_node').set_error(self.obj['nd_node'].nde_name[:50])
        #-- done
        return True

    def _place_filter_value(self, widget, w_name, f_name):
        try_value = self.filter.get(f_name)
        if try_value:
            widget.get_widget(w_name).set_value(try_value)

    def restore_filter_value(self):
        """ Put the filter back into the form
        """
        one = self.get_widget('search')
        if self.obj_ref:
            if 'nd_node' in one:
                one.get_widget('nd_node').set_value(self.obj_ref)
        if self.filter:
            self._place_filter_value(one, 'name', 'name')
            self._place_filter_value(one, 'nd_tags', 'nd_tags')
            if self.search_on_node:
                self._place_filter_value(one, 'nd_node', 'nd_node')
                self._place_filter_value(one, 'client_ref', 'client_ref')
            if self.search_full:
                act = one.get_widget('activity')
                bf_range = act.get_widget('bf_range')
                self._place_filter_value(one, 'status', 'status')
                self._place_filter_value(one, 'assignee', 'assignee')
                self._place_filter_value(bf_range,
                                         'bf_range_from',
                                         'bf_range_from')
                self._place_filter_value(bf_range,
                                         'bf_range_to',
                                         'bf_range_to')
            
    def _find_filter_value(self, widget, w_name, f_name):
        if widget[w_name]:
            self.new_filter[f_name] = widget[w_name]
            
    def get_filter_value(self):
        self.new_filter = {}
        one = self.get_widget('search')
        self._find_filter_value(one, 'name', 'name')
        self._find_filter_value(one, 'nd_tags', 'nd_tags')
        if self.search_on_node:
            self._find_filter_value(one, 'nd_node', 'nd_node')
            self._find_filter_value(one, 'client_ref', 'client_ref')
        if self.search_full:
            act = one.get_widget('activity')
            bf_range = act.get_widget('bf_range')
            self._find_filter_value(one, 'status', 'status')
            self._find_filter_value(one, 'assignee', 'assignee')
            self._find_filter_value(bf_range,
                                    'bf_range_from',
                                    'bf_range_from')
            self._find_filter_value(bf_range,
                                    'bf_range_to',
                                    'bf_range_to')

    def is_new_filter(self):
        if self.new_filter == None:
            return False
        else:
            return self.new_filter != self.filter
        
#-----------------------------------------------------------------------

class ListPage(SelectionList):

    keys = {
        # Describe the form
        'perm'      : 'nde_tasks',
        'title'     : 'Selected Nodes',
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
    
    def __init__(self, request, **kwargs):
        self.node_perm = perm = request.derived_locals['permissions']
        self.obj_ref = get_object_reference(request)
        self.new_child = request.args.get('down')
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

        filter_data = request.args.get('filter')
        self.filter = {}
        if filter_data:
            self.filter = url_decode(filter_data)
        SelectionList.__init__(self, request)

    def run_query(self):

        user_perm = UserPermission(user=self.request.user)
        self.u_set = []
        candidates = None # That is to say - all
        if not user_perm.test_permit_list([{'nde_tasks': 'read'}]):
            # If the user is not _generally_ privileged we have to limit
            # the search to relevant nodes.
            if 'nd_node' in self.filter:
                # Best to check privilege explicitly as it might be
                # outside the top trees.
                nde_test = self.filter['nd_node']
                local_perm = get_user_node_permissions(
                    nde_test, self.request.user or GUEST_NAME)
                if not local_perm.test_permit_list([{'nde_tasks': 'read'}]):
                    del self.filter['nd_node']
            if 'nd_node' not in self.filter:
                # Without a node to filter on, we limit by top_trees
                candidates =  user_top_trees(self.request.user or GUEST_NAME)
        if self.filter:
            query = search_filtered(self.filter, candidates)
            query = search_ordered(
                query,
                self.flow,
                self.sort_column,
                self.headings[self.heading_map[self.sort_column]][2])
            self.u_set_len = query.count()

            start = self.start_row
            end = start + self.chunksize
            self.u_set = query.all()[start:end]
        else:
            self.u_set_len = 0
            self.u_set = []

    def build_navigation(self):
        #
        # This form has three buttons - left, up and right

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
            target = 'search'
            url_parts = {'object_id': self.obj_ref}
        else:
            target = 'search_top'
            url_parts = {}
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
                    target = 'search'
                    url_parts = {'object_id': self.obj_ref}
                else:
                    target = 'search_top'
                    url_parts = {}
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
        target_extension = (controller_extensions.service(row_type) or
                            controller_extensions.service('generic'))
        selection_sets = target_extension.nd_view_selection_lists()
        priority_options = selection_sets.get('priority')
        status_options = selection_sets.get('status')
        act_type_options = selection_sets.get('severity')
        
        base_query = {}
        if self.new_child:
            base_query['down'] = self.new_child
        value = get_column_value(u_row, self.headings[0][0])
        if value is None:
            value = get_column_value(u_row, 'nde_idx')
        query = {}
        url_parts = {'object_id': value}
        query.update(base_query)
        widget.add(LinkWidget, '0',
                   value = value,
                   target = 'default',
                   url_parts = url_parts,
                   query = query)
        for j in range(1, len(self.headings)):
            field_name = self.headings[j][0]
            value = get_column_value(u_row, field_name)
            widget.add(DisplayOnlyWidget, str(j))
            if field_name == 'act_priority':
                try:
                    value = priority_options.get_value(value)
                except AttributeError:
                    pass
            if field_name == 'act_status':
                try:
                    value = status_options.get_value(value)
                except AttributeError:
                    pass
            if field_name == 'act_type':
                try:
                    value = act_type_options.get_value(value)
                except AttributeError:
                    pass
            widget.get_widget(str(j)).set_value(value)

    def build_post_form(self):
        # Add in the submit row so that it goes at the end
        self.table_widget.add(ButtonRow, 'actions')
        button_row = self.table_widget.get_widget('actions')
        button_row.add(DisplayOnlyWidget, 'csv')
        button_row.add(DisplayOnlyWidget, 'nothing')
        if (self.node_perm.test_permit(self.keys['perm'], 'add') and
            not self.new_child):
            if self.obj_ref:
                target = 'add'
                url_parts =  {'object_id': self.obj_ref}
            else:
                target = 'add_top'
                url_parts = {}
            button_row.add(LinkWidget, 'add', 'Add new node',
                           target = target,
                           url_parts = url_parts,
                           query={})

#-----------------------------------------------------------------------

