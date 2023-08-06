# Name:      lokai/lk_worker/ui/views/subscribers.py
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

from sqlalchemy.orm.exc import NoResultFound

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_forms.widget import(
    CompositeWidget,
    StringWidget,
    )
from lokai.lk_login.db_objects import User

import pyutilib.component.core as component
from lokai.lk_worker.extensions import PluginIdCompare
from lokai.lk_worker.extensions.view_interface import IWorkerView

#-----------------------------------------------------------------------

class PiSubscribersView(PluginIdCompare, component.SingletonPlugin):

    def __init__(self):
        self.name = 'subscribers'
        self.selection_maps = {} # Selection maps, if required.

    def nd_view_selection_lists(self):
        return self.selection_maps

    def nd_view_form_extend(self, form):
        if not (form.node_perm and
                form.node_perm.test_permit_list([{'nde_tasks': 'read'},
                                                 {'nde_tasks': 'edit'}])):
            return
        form.detail.add(CompositeWidget, 'notification_subscribers',
                        title = "Add or modify subscribers",
                        fieldset = {'expand': 'closed'}
                        )
        container = form.detail.get_widget('notification_subscribers')
        container.add(StringWidget, 'nd_node_subscriber',
                      title = 'Notification recipients')

    def nd_view_form_populate(self, form):
        if not (form.node_perm and
                form.node_perm.test_permit_list([{'nde_tasks': 'read'},
                                                 {'nde_tasks': 'edit'}])):
            return
        if not( form.obj and 'nd_node_subscriber' in form.obj):
            return
        container = form.detail.get_widget('notification_subscribers')
        container.get_widget(
            'nd_node_subscriber'
            ).set_value(
            form.obj.get('nd_node_subscriber', {}).get('nde_subscriber_list'))

    def nd_view_form_default(self, form):
        pass

    def nd_view_form_process(self, form):
        error_count = 0
        container = form.detail.get_widget('notification_subscribers')
        s_widget = container.get_widget('nd_node_subscriber')
        subs_text = container['nd_node_subscriber']
        if not subs_text:
            return error_count

        subs_list = subs_text.split(',')
        new_subs_list = []
        error_list = []
        for sub_name in subs_list:
            sub_name = sub_name.strip()
            if not sub_name:
                continue
            if '@' in sub_name:
                new_subs_list.append(sub_name)
            else:
                try:
                    possible_obj = engine.session.query(
                        User
                        ).filter(
                        User.user_uname == sub_name).one()
                    possible_email = possible_obj['user_email']
                    if not possible_email:
                        error_list.append("No email found for %s"%sub_name)
                        error_count += 1
                    else:
                        new_subs_list.append(possible_email)
                except NoResultFound:
                    error_list.append("No user found for name %s"%sub_name)
                    error_count += 1
        new_subs_text = ', '.join(new_subs_list)
        if not error_count:
            form.new_obj['nd_node_subscriber'] = {'nde_subscriber_list':
                                              new_subs_text}
        else:
            e_text = ' - '.join(error_list)
            s_widget.set_error(e_text)
            container.fieldset['expand'] = 'open'
        return error_count

    def nd_view_form_store(self, form):
        if not (form.node_perm and
                form.node_perm.test_permit_list([{'nde_tasks': 'edit'}])):
            return []

        if not( form.obj and 'nd_node_subscriber' in form.obj):
            return []

        return []

    def nd_display_main(self, form):
        return []

    def nd_display_side(self, form):
        return []

#-----------------------------------------------------------------------
