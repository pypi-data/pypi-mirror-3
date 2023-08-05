# Name:      lokai/lk_worker/ui/publisher.py
# Purpose:   Publish login pages
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

from werkzeug import SharedDataMiddleware

from lokai.tool_box.tb_database.orm_interface import engine
import lokai.lk_ui
from lokai.lk_ui.session import SessionRequest
from lokai.lk_ui.base_publisher import BasePublisher

import lokai.lk_worker.ui.main_controller as controllers
from lokai.lk_worker.ui.local import (
    url_for, handler_map, get_adapter, local, local_manager, IWorkerHandler)
from lokai.lk_login.userpermission import GUEST_NAME
from lokai.lk_worker.models.builtin_data_resources import user_top_trees
from lokai.lk_worker.nodes.graph import NodeFamily
from lokai.lk_worker.nodes.search import find_in_path
from lokai.lk_worker.models import ndNode

#-----------------------------------------------------------------------

from lokai.lk_worker.extensions.extension_manager import (
    get_all_extensions,
    LK_REGISTER_ALL,
    )

get_all_extensions(LK_REGISTER_ALL)

#-----------------------------------------------------------------------

class lkWorker(BasePublisher):

    """ Worker application -

        Display the search form

        Respond to node requests

    """
    pass

#-----------------------------------------------------------------------

""" The worker publisher is wrapped in a shared data middleware so that
    '/static' is recognised when this is run stand alone. The
    consolidating publisher also uses the same wrapping, so that,
    under deployment conditions, the '/static' url is handled at the
    higher level.
"""
def get_lk_worker_publisher():
    return SharedDataMiddleware(
        lkWorker(handler_map, get_adapter, local, local_manager,
                 route_handler_interface=IWorkerHandler),
        {'/static': lokai.lk_ui.StaticPath})

#-----------------------------------------------------------------------

class menu_finder(object):

    def __init__(self, user):
        """ Build a menu for this user based on possible menu groups
            in the database and in any case all avaialble top trees.
        """
        self.user = user
        self.found_set = {}
        self.groups = []
        self.build()

    def build(self):
        """ Put the menu together """
        # Find the group definitions
        candidate_groups = find_in_path(['', 'Menu Groups', '*'])
        if candidate_groups:
            node_set = engine.session.query(
                ndNode
                ).filter(
                ndNode.nde_idx.in_(candidate_groups)
                ).all()
        else:
            node_set = []
        for node_object in node_set:
            group_name = node_object.nde_description
            group_name = group_name if group_name is not None else ''
            group_position = node_object.nde_name
            if group_position.isdigit():
                group_position = int(group_position)
            else:
                group_position = 900
            self.groups.extend(
                self.menu_for_tree(
                    user_top_trees(GUEST_NAME, node_object.nde_idx),
                    group = group_name,
                    position = group_position))
            if self.user:
                self.groups.extend(
                    self.menu_for_tree(
                        user_top_trees(self.user, node_object.nde_idx),
                        group = group_name,
                        position = group_position))
        #--
        # Add any remaining from top_trees
        self.groups.extend(
                    self.menu_for_tree(
                               user_top_trees(GUEST_NAME)))
        if self.user:
            self.groups.extend(
                self.menu_for_tree(
                    user_top_trees(self.user)))
            
    def menu_for_node(self, nde_object):
        """ Build the menu entry for a single node """
        other_name = nde_object.nde_name
        other_link = nde_object.nde_client_reference or nde_object.nde_idx
        if not other_link in self.found_set:
            self.found_set[other_link] = True
            other_item = {
                'link': url_for('default', {'object_id': other_link}),
                'title': other_name,
                }
            return other_item

    def menu_for_tree(self, top_trees, group=None, position=900):
        """ Build a menu for a set of tree tops """
        op = []
        bucket = op
        if not group is None:
            op = [{'title': group,
                   'position': position,
                   'children': []}]
            bucket = op[0]['children']
        for top_idx in top_trees:
            family =  NodeFamily(parent=top_idx, order='nde_client_reference')
            top_node = family.parents[0]
            top_item = self.menu_for_node(top_node)
            if top_item:
                if group is None:
                    top_item['position'] = position
                children = []
                for other_node in family.siblings_left:
                    other_item = self.menu_for_node(other_node)
                    if other_item:
                        children.append(other_item)
                if children:
                    top_item['children'] = children
                bucket.append(top_item)
        return op
        
def menu_builder(request):
    """ Build a menu for logging in and out
    """
    mf = menu_finder(request.user)
    return mf.groups
    op = menu_for_user(GUEST_NAME, 100, group='')
    return op

#-----------------------------------------------------------------------

if __name__ == '__main__':
    from werkzeug import run_simple

    from lokai.tool_box.tb_common.configuration import handle_ini_declaration
    handle_ini_declaration(prefix='lk')
    
    from lokai.lk_worker.models import model
    model.init()

    from lokai.lk_ui.publisher import build_skin
    build_skin()
    
    def make_app():
        return get_lk_worker_publisher()

    run_simple('localhost', 5000, make_app(), use_relaoder=True, processes=2)

#-----------------------------------------------------------------------
