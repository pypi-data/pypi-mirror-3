# Name:      lokai/lk_worker/ui/views/tags.py
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

from lokai.tool_box.tb_forms.widget import(
    StringWidget,
    )
from lokai.lk_worker.models.builtin_data_tags import PiTagData

import pyutilib.component.core as component
from lokai.lk_worker.extensions import PluginIdCompare
from lokai.lk_worker.extensions.view_interface import IWorkerView

#-----------------------------------------------------------------------

class PiTagsView(PluginIdCompare, component.SingletonPlugin):

    def __init__(self):
        self.name = 'tags'
        self.selection_maps = {} # Selection maps, if required.

    def nd_view_selection_lists(self):
        return self.selection_maps

    def nd_view_form_extend(self, form):
        if not (form.node_perm and
                form.node_perm.test_permit_list([{'nde_tasks': 'read'},
                                                 {'nde_tasks': 'edit'}])):
            return

        form.detail.add(StringWidget, 'nd_tags',
                        title = 'Search Tags')

    def nd_view_form_populate(self, form):
        if not (form.node_perm and
                form.node_perm.test_permit_list([{'nde_tasks': 'read'},
                                                 {'nde_tasks': 'edit'}])):
            return
        if form.obj and 'nd_tags' in form.obj:
            form.detail.get_widget('nd_tags').set_value(form.obj.get('nd_tags', ''))

    def nd_view_form_default(self, form):
        pass

    def nd_view_form_process(self, form):
        return 0

    def nd_view_form_store(self, form):
        if not (form.node_perm and
                form.node_perm.test_permit_list([{'nde_tasks': 'edit'}])):
            return

        form.new_obj['nd_tags'] = form.detail['nd_tags'] or ''
        return []

    def nd_display_main(self, form):
        return []

    def nd_display_side(self, form):
        response_list = []
        response_list.append("Tags: %s"% str(form.obj.get('nd_tags', '')))
        return response_list

#-----------------------------------------------------------------------
