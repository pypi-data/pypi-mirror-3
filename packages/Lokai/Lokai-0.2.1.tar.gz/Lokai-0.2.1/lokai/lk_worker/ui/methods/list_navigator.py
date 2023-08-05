# Name:      lokai/lk_worker/ui/methods/list_navigator.py
# Purpose:   Display a list navigator panel for nodes.
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

import lokai.tool_box.tb_common.notification as notify
from lokai.tool_box.tb_forms.widget import (
    RowWidget,
    DummyWidget,
    CompositeWidget,
    )
from lokai.tool_box.tb_forms.form import Form

from lokai.lk_worker.models import ndNode

from lokai.lk_worker.nodes.node_data_functions import (PermittedNodeFamily,
                                          extract_identifier)
from lokai.lk_worker.ui.local import expand_permission
from lokai.lk_worker.ui.link_widget import (
    LinkWidget,
    LinkUpWidget,
    LinkLeftWidget,
    LinkRightWidget
    )

#-----------------------------------------------------------------------

import pyutilib.component.core as component
from lokai.lk_worker.extensions.controller_interface import IWorkerController

controller_extensions = component.ExtensionPoint(IWorkerController)

#-----------------------------------------------------------------------

__all__ = ['ListNavigator']

#-----------------------------------------------------------------------

class ListNavigator(Form):
    """ Build up/left/right navigation entries for display in the
        application template. Used to give user navigation through a
        tree.
    """

    def __init__(self, request, object_reference, data_object,
                 navigation_order=None, **kwargs):
        """
            :request: Request object.

            :object_reference: String. ID for the node.

            :data_object: Response from get_node_dataset
            
            :navigation_order: Named Tuple:

                :order: String. Database object object attribute name. See
                    NodeFamily.

                :sort_object: Database object. See NodeFamily.

                :flow: String. 'ASC' or 'DSC'. See NodeFamily.
            
        """
        Form.__init__(self, request, use_tokens=False)
        self.node_perm = perm = request.derived_locals['permissions']
        self.request = request
        self.current_target = self.request.derived_locals['current_target']
        self.obj_ref = object_reference
        self.obj = data_object
        self.obj_type = ((self.obj and
                         'nd_node' in self.obj and
                         self.obj['nd_node'].nde_type) or 'generic')

        self.up = request.args.get('up', None)
        self.new_child = request.args.get('down')
        self.navigation_order = navigation_order
        self.build_detail()

    def build_detail(self):
        """ Create the detail that needs to be displayed:

            - Three links to left/up/right

            - A list of links for function/display buttons
        """
        #
        # Navigation links
        family = PermittedNodeFamily(self.obj_ref,
                                     self.up,
                                     user= self.request.user,
                                     perm = [{'nde_tasks': 'read'}],
                                     order=self.navigation_order.order,
                                     sort_object=self.navigation_order.sort_object,
                                     flow=self.navigation_order.flow)
        base_query = {}
        base_target = 'default'
        if self.new_child:
            base_query['down'] = self.new_child
            base_target = 'list'
            
        self.tree_widgets = []
        
        target = ''
        left_name = '&nbsp;'
        disabled = True
        if len(family.siblings_left):
            enabled = False
            target = extract_identifier(family.siblings_left[-1])
            left_name = family.siblings_left[-1].nde_name
        this_query = {'object_id': target}
        try:
            this_query['up'] = extract_identifier(family.parents[0])
        except IndexError:
            pass

        this_query.update(base_query)
        left_widget = LinkLeftWidget('btf_001',
                                     left_name,
                                     target = base_target,
                                     url_parts = this_query,
                                     disabled = disabled
                                     )
        self.tree_widgets.append(left_widget)
        
        target = ''
        up_name = '&nbsp;'
        disabled = True
        if len(family.parents) and family.parents[0]:
            disabled = False
            target = extract_identifier(family.parents[0])
            up_name = family.parents[0].nde_name
        this_query = {'object_id': target}
        this_query.update(base_query)
        up_widget = LinkUpWidget('btf_002',
                                 up_name,
                                 target = base_target,
                                 url_parts = this_query,
                                 disabled = disabled
                                 )
        self.tree_widgets.append(up_widget)
          
        target = ''
        right_name = '&nbsp;'
        disabled = True
        if len(family.siblings_right):
            disabled = False
            target = extract_identifier(family.siblings_right[0])
            right_name = family.siblings_right[0].nde_name
        this_query = {'object_id': target}
        try:
            this_query['up'] = extract_identifier(family.parents[0])
        except IndexError:
            pass
        this_query.update(base_query)
        right_widget = LinkRightWidget('btf_003',
                                       right_name,
                                       target = base_target,
                                       url_parts = this_query,
                                       disabled = disabled
                                       )
        self.tree_widgets.append(right_widget)

        
        #
        # Function Buttons
        self.work_widgets = []
        
        service = (controller_extensions.service(self.obj_type) or
                   controller_extensions.service('generic'))
        path_set = service.nd_controller_tabs(self.request, self.obj_ref)
        query = {}
        if self.up:
            query['up'] = self.up
        query.update(base_query)
        query['object_id'] = self.obj_ref
        box_count = 0
        for p in path_set:
            url_parts = {}
            url_parts.update(query) # copy this across to avoid accidental update
            if self.current_target == p[0]:
                continue
            if len(p) > 2 and p[2] and self.node_perm:
                node_perm_setting = self.obj.get('local_permission')
                use_restriction = expand_permission(p[2],
                                                    node_perm_setting)
                if not self.node_perm.test_permit_list(use_restriction):
                    continue
            try:
                extra_query = p[3]
                url_parts.update(extra_query) # Can override object_id
            except IndexError:
                pass
            box_count += 1
            if not self.new_child:
                self.work_widgets.append(
                    LinkWidget('x%d'%box_count,
                               p[1],
                               target = p[0],
                               url_parts = url_parts,
                               query = {},
                               disabled = (self.obj_ref == None or
                                           self.obj_ref == '**new**' or
                                           self.obj_ref == 'None')))
            else:
                self.work_widgets.append(
                    LinkWidget('x%d'%box_count,
                               p[1],
                               target = p[0],
                               url_parts = url_parts,
                               query = {},
                               disabled = (self.obj_ref == None or
                                           self.obj_ref == '**new**' or
                                           self.obj_ref == 'None' or
                                           p[0][-1] != 'list')))

    def build_form(self):
        """ Create rows of links

            Top row contains 3 buttons:

            left goes leftwards in sibling set
            right goes rightwards in sibling set
            middle goes to parent

            Second row contains function/display buttons
        """
        self.add(CompositeWidget, 'links', fieldset={})
        link_box = self.get_widget('links')

        link_box.add(RowWidget, 'btf')
        btf_widget = link_box.get_widget('btf')
        for link in self.tree_widgets:
            btf_widget.add_w(link)
        for i in range(len(self.tree_widgets), 5):
            btf_widget.add(DummyWidget, "empty%02d"%(i+1))
        
        #
        # Function Buttons
        link_box.add(RowWidget, 'show')
        show_box = link_box.get_widget('show')
        for link in self.work_widgets:
            show_box.add_w(link)
            
        for i in range(len(self.work_widgets), 5):
            show_box.add(DummyWidget, 'zz%02d'%(i+1))

    def get_parts(self):
        """ Return the elements of the panel for posting into a template """
        return {'tree_navigator': [x.get_parts() for x in self.tree_widgets],
                'tabs': [x.get_parts() for x in self.work_widgets]}
        
#-----------------------------------------------------------------------
