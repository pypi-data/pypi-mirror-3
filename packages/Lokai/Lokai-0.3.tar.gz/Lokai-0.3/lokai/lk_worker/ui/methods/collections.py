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
import json

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

from lokai.lk_worker.ui.methods.list_page import ListPage as ndListPage

from lokai.lk_worker.ui.local import url_for, get_object_reference

from lokai.lk_worker.ui.pages import make_default_selection

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
        self.current_target = request.derived_locals['current_target']
        self.node_perm = request.derived_locals['permissions']
        self.search_full = self.node_perm.test_permit_list(
            [{'nde_search_full': 'read'}])
        self.request = request
        self.new_child = request.values.get('down')
        self.obj_ref = object_reference
        self.obj = data_object
        filter_data = request.args.get('filter')
        self.selection_filter = {}
        if filter_data:
            self.selection_filter = json.loads(filter_data)
        if not filter_data:
            self.selection_filter_data = (
                make_default_selection(request, object_reference))
        self.new_filter = None
        if self.search_full:
            self._get_useful_data()

        # Defer building the form so that any class inheriting this
        # one can add to the init actions after calling this __init__
        self.build_form_needed = True

    def _identify_form_action(self):
        # Use one.get_widget().value here. The form one[xx] has the
        # side effect of parsing the input and, as there is none, the
        # value goes to None
        one = self.get_widget('search')
        if 'nd_node' in one and one.get_widget('nd_node').value:
            self.action = url_for(self.current_target,
                                  {'object_id':
                                   one.get_widget('nd_node').value})
            
        else:
            self.action = url_for(self.current_target)

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
        for uname, role in available_resources.iteritems():
            user = engine.session.query(
                User).filter(
                User.user_uname == uname).one()
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
        one.add(HiddenWidget, 'nd_node')
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
        self._identify_form_action()
        self.build_form_needed = False

    def process_input(self):
        if self.build_form_needed:
            self.build_form()
        error_count = 0
        if self.has_errors(): # force form to parse itself
            error_count = 1
        one = self.get_widget('search')
        #
        # Check a few things ...
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
        #-- done
        return True

    def _place_filter_value(self, widget, w_name, f_name):
        try_value = self.selection_filter.get(f_name)
        if try_value:
            widget.get_widget(w_name).set_value(try_value)

    def restore_filter_value(self):
        """ Put the filter back into the form
        """
        one = self.get_widget('search')
        if self.obj_ref:
            if 'nd_node' in one:
                one.get_widget('nd_node').set_value(self.obj_ref)
        if self.selection_filter:
            self._place_filter_value(one, 'name', 'name')
            self._place_filter_value(one, 'nd_tags', 'nd_tags')
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
            return self.new_filter != self.selection_filter

    def render(self):
        if self.build_form_needed:
            self.build_form()
        return Form.render(self)

#-----------------------------------------------------------------------

class ListPage(ndListPage):

    keys = {
        # Describe the form
        'perm'      : 'nde_tasks',
        'title'     : 'Selected Nodes',
        'formname'  : 'nb_list',
        'chunksize' : 15,
        }

    """ headings: Don't have to appear here. See method
        _get_disply_columns. This is a hook to allow you to get the
        columns in any way you like.

        List of tuples, one tuple per visible column.

        Tuple format is

            (field_name, title, data_object)

        where

            field_name is the name of the field in the data_object.

            title is the display title for the column.

            data_object is a database object that contains the
            field_name and which can be used for sorting.
    """
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

        super(ListPage, self).__init__(request, object_reference, data_object)

        self.search_full = self.node_perm.test_permit_list(
            [{'nde_search_full': 'read'}])

    def run_query(self):

        user_perm = UserPermission(user=self.request.user)
        self.u_set = []
        candidates = None # That is to say - all
        if not user_perm.test_permit_list([{'nde_tasks': 'read'}]):
            # If the user is not _generally_ privileged we have to limit
            # the search to relevant nodes.
            if 'nd_node' in self.selection_filter:
                # Best to check privilege explicitly as it might be
                # outside the top trees.
                nde_test = self.selection_filter['nd_node']
                local_perm = get_user_node_permissions(
                    nde_test, self.request.user or GUEST_NAME)
                if not local_perm.test_permit_list([{'nde_tasks': 'read'}]):
                    del self.selection_filter['nd_node']
            if 'nd_node' not in self.selection_filter:
                # Without a node to filter on, we limit by top_trees
                candidates =  user_top_trees(self.request.user or GUEST_NAME)
        if self.selection_filter:
            query = search_filtered(self.selection_filter, candidates)
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

#-----------------------------------------------------------------------
