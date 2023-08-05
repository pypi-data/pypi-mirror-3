# Name:      lokai/lk_worker/ui/controllers/resource_group.py
# Purpose:   Responses to requests for type = 'resource_group'
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

""" A Resource Group is a way of allocating users to groups so that
    members of the group can have access to sub-trees that belong to
    that group. Allocating a resource to the group automatically
    confers access to the connected sub-groups.

    In this case the group is modelled as a node and users are allocated
    to the node. Sub-trees that are accessible by this group are
    linked as children to this node.

    A user must be allocated a role on the group, and this role is
    then applied to the connected sub-trees.

    This mechanism models, and replaces, the equivalent mechanism
    where a group is modelled as a named resource that is allocated to
    each sub-tree. Users are aliased to that resource by being
    members of that group.

    There are two advantages to using a node to represent groups
    rather than mapping to a psuedo-resource. It allows users to be
    given different roles in the group, and it allows groups to be
    defined in different parts of the hierarchy, thus allowing the
    same group name to be used in different scopes.

    There is, in principle, no reason why any node could not be used
    as a group. However, there is a potential security issue in that
    any user allocated to the group node also has access to the details
    of that group node. Creating a specific resource_group type allows
    access to the details to be controlled.

    The controller is necessary anyway as a response to the node
    type.

    It allows us to limit the content of the function tabs by
    appropriate permissions. We have set this to ``nde_resource``
    rather than inventing a new permission type, so that
    ``lkw_manager``s can see the edit-related views (and add/remove members).

    The type is derived from the 'text' type, so the user sees a
    formatted version of the description and an appended list of all
    the sub-trees that are accessible.

    ``nd_controller_display_edit`` and ``nd_controller_display_add``
    are redefined here so that the required local permission can be
    passed in to the detail page. This traps attempts at direct entry
    using a manually entered URL.

"""
#-----------------------------------------------------------------------

import lokai.tool_box.tb_common.notification as notify

from lokai.lk_worker.ui.methods.list_navigator import ListNavigator
from lokai.lk_worker.ui.methods.detail_page import DetailPage

#-----------------------------------------------------------------------

from lokai.lk_worker.ui.controllers.text import PiTextController, navigation_wrap

#-----------------------------------------------------------------------

class PiResourceGroupController(PiTextController):

    function_tabs = [
        ('display', 'Display'),
        ('edit', 'Detail', [{'nde_resource': 'edit'}]),
        ('list', 'List', [{'nde_resource': 'edit'}]),
        ('search', 'Search'),
        ]
    
    def __init__(self):
        PiTextController.__init__(self)
        self.name = 'resource_group'
        self.display_name = 'Resource Group'

    
    def nd_controller_display_edit(self, request,
                                   object_reference, data_object):
        """ Present a screen of editable fields (permissions allowing)
            that is used to modify an existing object.
        """
        detail_page = DetailPage(request, object_reference, data_object,
                                 view_interface=self.view_interface,
                                 perm='nde_resource',
                                 )
        detail_page.build_data()
        navigation = ListNavigator(request, object_reference, data_object,
                                   self.navigation_order)
        navigation_detail = navigation.get_parts()
        page_html = detail_page.render()
        return navigation_wrap(self.navigation_template,
                               request, navigation_detail, page_html)

    def nd_controller_display_add(self, request,
                                  object_reference, data_object):
        """ Present a screen of editable fields (permissions allowing)
            that is used to create a new object.

            object reference points to the parent.
        """
        detail_page = DetailPage(request, object_reference, data_object,
                                 view_interface=self.view_interface,
                                 perm='nde_resource',
                                 )
        detail_page.build_data()
        navigation = ListNavigator(request, object_reference, data_object,
                                   self.navigation_order)
        navigation_detail = navigation.get_parts()
        page_html = detail_page.render()
        return navigation_wrap(self.navigation_template,
                               request, navigation_detail, page_html)

#-----------------------------------------------------------------------
