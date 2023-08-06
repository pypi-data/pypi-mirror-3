# Name:      lokai/lk_worker/ui/views/resources.py
# Purpose:   Provide user interviews specific to a node type
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
from lokai.tool_box.tb_database.orm_access import insert_or_update
from lokai.tool_box.tb_forms.widget import(
    CompositeWidget,
    SingleSelectWidget,
    )

from lokai.lk_common.selection_map import SelectionMap
from lokai.lk_login.db_objects import User, Role
from lokai.lk_login.user_model import user_view_get

from lokai.lk_worker.models.builtin_data_resources import ndUserAssignment
from lokai.lk_worker.models.builtin_data_resources import (
    ResourceList,
    get_full_node_resource_list,
    )
import pyutilib.component.core as component
from lokai.lk_worker.extensions import PluginIdCompare
from lokai.lk_worker.extensions.view_interface import IWorkerView

#-----------------------------------------------------------------------

class PiResourcesView(PluginIdCompare, component.SingletonPlugin):

    def __init__(self):
        self.name = 'resources'
        self.selection_maps = {} # Selection maps, if required.

    def nd_view_selection_lists(self):
        return self.selection_maps

    def nd_view_form_extend(self, form):
        if not (form.node_perm and
                form.node_perm.test_permit_list([{'nde_resource': 'read'},
                                                 {'nde_resource': 'edit'}])):
            return
        read_only = True
        if (form.node_perm and
            form.node_perm.test_permit_list([{'nde_resource': 'edit'}])):
            read_only = False
        assign_title =  "Assign a user or add users to the hierarchy"
        assignee_object = form.obj and form.obj.get('nd_assignment')
        if assignee_object:
            assign_title =  "Assign this task or add users to the hierarchy"
        form.detail.add(CompositeWidget, 'user_detail',
                        title = assign_title,
                        fieldset = {'expand' : 'closed'}
                        )
        container = form.detail.get_widget('user_detail')
        obj_type = form.obj.get('nd_node', {}).get('nde_type', 'generic')

        if form.obj:
            obj_ref = form.obj['nd_node'].nde_idx
            available_resources = get_full_node_resource_list(obj_ref)
            select_available = [('', "Select user to assign", ''), ]
            resource_list = available_resources.keys()
            if resource_list:
                user_query = engine.session.query(
                    User).filter(
                    User.user_uname.in_(resource_list))
                for user in user_query:
                    uname = user.user_uname
                    lname = user.user_lname or uname
                    select_available.append((uname, lname, uname))

            container.add(SingleSelectWidget, 'active_resource',
                          title = "Assigned user",
                          options = select_available,
                          disabled = read_only)
            if 'nd_resource' in form.obj:
                role_options = SelectionMap(data_object=Role,
                                            key_field='role_text',
                                            display_field='role_text',
                                            )
                row = 1
                for uname, role in form.obj['nd_resource'].iteritems():
                    usr_obj_set = engine.session.query(User).filter(
                        User.user_uname == uname).all()
                    display_name = uname
                    if usr_obj_set:
                        display_name = usr_obj_set[0].user_lname
                    row_name = "row%03d"% row
                    if role_options:
                        container.add(
                            SingleSelectWidget, row_name,
                            value = 'undefined',
                            title = display_name,
                            options = role_options.get_options(
                                appends=[('remove', 'Remove', 'remove')]),
                            disabled = read_only)
                    row += 1
            if not read_only:
                user_options = SelectionMap(data_object=User,
                                            key_field='user_uname',
                                            display_field='user_lname')
                container.add(SingleSelectWidget, 'newresource',
                              value = "Add new resource",
                              title = "Add new resource",
                              options = user_options.get_options(),
                              disabled = read_only)
        #-- done

    def nd_view_form_populate(self, form):
        if not (form.node_perm and
                form.node_perm.test_permit_list([{'nde_resource': 'read'},
                                                 {'nde_resource': 'edit'}])):
            return

        container = form.detail.get_widget('user_detail')
        if form.obj:
            assignee_object = form.obj.get('nd_assignment')
            if assignee_object:
                active_resource = assignee_object.usa_user
                container.get_widget('active_resource').set_value(active_resource)
                container.fieldset['expand'] = 'open'
        if 'nd_resource' in form.obj:
            row = 0
            for uname, role in form.obj['nd_resource'].iteritems():
                row += 1
                row_name = "row%03d"% row
                container.get_widget(row_name).set_value(role)
            if row:
                container.fieldset['expand'] = 'open'

    def nd_view_form_default(self, form):
        pass

    def nd_view_form_process(self, form):
        if not (form.node_perm and
                form.node_perm.test_permit_list([{'nde_resource': 'read'},
                                                 {'nde_resource': 'edit'}])):
            return 0

        error_count = 0
        container = form.detail.get_widget('user_detail')
        form.new_resource_object = None
        if 'newresource' in container:
            new_user = container['newresource']
            if new_user:
                user_object = user_view_get(new_user)
                if not user_object:
                    container.get_widget('newresource').set_error(
                        "Cannot find this user")
                    error_count += 1
                    container.fieldset['expand'] = 'open'
                else:
                    form.new_resource_object = user_object
        return error_count

    def nd_view_form_store(self, form):
        if not (form.node_perm and
                form.node_perm.test_permit_list([{'nde_resource': 'edit'}])):
            return  []

        update_object = form.new_obj
        hist_response = []
        if form.obj and 'nd_resource' in form.obj:
            container = form.detail.get_widget('user_detail')
            if container['active_resource']:
                usr_assigned = container['active_resource']
                update_object['nd_assignment'] = {
                    'nde_idx': form.obj_ref,
                    'usa_user': usr_assigned
                    }
                hist_response.append("Node assigned to %s"%usr_assigned)
            user_list = ResourceList()
            row = 1
            for uname, role in form.obj['nd_resource'].iteritems():
                row_name = "row%03d"% row
                old_val = role
                new_val = container[row_name]
                user_list[uname] = new_val
                if new_val != old_val:
                    if new_val and new_val != 'remove':
                        hist_response.append(
                            "User role for %s changed from %s to %s" % (
                                uname,
                                old_val,
                                new_val))
                        
                    elif new_val == 'remove':
                        hist_response.append(
                            "User role deleted for %s"%uname)
                row += 1
            if form.new_resource_object:
                new_user = form.new_resource_object['user_uname']
                user_list[new_user] = 'undefined'
                hist_response.append(
                    "Add new user role for %s"%new_user)
            update_object['nd_resource'] = user_list
        return hist_response

    def nd_display_main(self, form):
        return []

    def nd_display_side(self, form):
        response_list = []
        if (form.node_perm and
        form.node_perm.test_permit_list([{'nde_resource': 'read'},
                                         {'nde_resource': 'edit'}])):
            assignee_text = 'No-one assigned here'
            assignee_object = form.obj.get('nd_assignment')
            assignee_uname = assignee_object and assignee_object.usa_user
            if assignee_uname:
                user_set = engine.session.query(User).filter(
                    User.user_uname == assignee_uname).all()
                if len(user_set) == 1:
                    assignee_text = "Assigned to: %s" % (
                        user_set[0].user_lname or assignee_uname)
                elif len(user_set) == 0:
                    assignee_text = (
                        "Assigned to: "
                        "%s (not recognised)" % assignee_uname)
                else:
                    assignee_text = (
                        "Assigned to: "
                        "%s (multiple possibilities)" % assignee_uname)
            response_list.append(assignee_text)
            resource_set = form.obj and form.obj.get('nd_resource')
            if resource_set and len(resource_set):
                li_set = []
                li_set.append("Allocated users:<ul class='SideBarList'>")
                for uname, role in resource_set.iteritems():
                    li_set.append("<li>%s: %s</li>"%(
                        uname,
                        role))
                li_set.append("</ul>")
                response_list.append('\n'.join(li_set))
            else:
                response_list.append("No directly attached users")
        return response_list

#-----------------------------------------------------------------------
