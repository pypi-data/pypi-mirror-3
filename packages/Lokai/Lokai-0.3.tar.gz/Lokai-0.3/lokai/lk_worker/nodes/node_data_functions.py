# Name:      lokai/lk_worker/nodes/node_data_functions.py
# Purpose:   Get and set utilities for nodes
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

from sqlalchemy.orm import exc as orm_exc

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.lk_worker import ndNodeMissing, ndIdentifierNotFound

from lokai.lk_login.userpermission import UserPermission, GUEST_NAME

from lokai.lk_worker import ndIdentifierNotFound

from lokai.lk_worker.nodes.graph import (make_link,
                            make_unlink,
                            child_trees)

from lokai.lk_worker.nodes.data_interface import (get_node_dataset,
                                                  delete_node_dataset)

from lokai.lk_worker.nodes.search import search_up, search_here, search_down

from lokai.lk_worker.models import (ndNode,
                                    ndEdge,
                                    )
from lokai.lk_worker.models.builtin_data_resources import (
    ndUserAssignment,
    get_full_node_resource_list,
    get_permissions_for
    )
from lokai.lk_worker.nodes.graph import NodeFamily

#-----------------------------------------------------------------------

def node_add_parent(child_ref, parent_ref):
    """ Add a new parent to the given child - return a history note
    """
    make_link(child_ref, parent_ref)
    #
    # Add in the history
    return ("Add link to parent %s"% parent_ref)

#-----------------------------------------------------------------------
      
def node_delete_parent(child_ref, parent_ref):
    """ Remove a parent from the given child - return a history note
    """
    make_unlink(child_ref, parent_ref)
    #
    # Add in the history
    return ("Remove link to parent %s"% parent_ref)

#-----------------------------------------------------------------------

def get_user_node_permissions(nde_idx, user):
    """ Quite specific return of a single UserPermission object
        relating this user to this node. The permissions are derived
        from all parent nodes.

        The anonymouse user is included here as well, so that any user
        always acts the same as the anonymous user.
    """
    local_user = user or GUEST_NAME
    local_user_set = [GUEST_NAME]
    if user:
        local_user_set.append(user)
    resource_list = get_full_node_resource_list(nde_idx, user=local_user_set)
    response = UserPermission(user=local_user)
    if resource_list:
        many_permission_set = get_permissions_for(resource_list)
        for uname in resource_list.keys():
            response.append(many_permission_set[uname])
    return response

#-----------------------------------------------------------------------

def get_assigned_resource_list(nde_idx, order_by=None):
    """ Return a list of users assigned to this node or its parents
    """
    if isinstance(nde_idx, list):
        node_list = nde_idx
    else:
        node_list = [nde_idx]
    qy = engine.session.query(
        ndUserAssignment).join(
        (ndNode, ndUserAssignment.nde_idx == ndNode.nde_idx))
    qy = search_up(qy, node_list)
    if order_by:
        qy = qy.order_by(order_by)
    return qy.all()

#-----------------------------------------------------------------------

class PermittedNodeFamily(NodeFamily):
    """ A version of NodeFamily that takes account of user
        permissions.
    """

    def __init__(self,  node=None, parent=None, **kwargs):
        """ The kwargs hold the key to modifying the content of the
            family:

            user = the name of the user
                   >>> we have a bit of a problem if there is no user <<<

            perm = a Permission.test_permit_list format string, (alias
                   permission)
        """
        self.user = kwargs.get('user')
        self.perm = kwargs.get('perm')
        # Do all the work in building a node family in the first place.
        NodeFamily.__init__(self, node, parent, **kwargs)

        # If the given node is None we have to have some degree of
        # permission on the parent. In that case, everything is fine
        # and we have nothing else to do.

        if node == None or node == '**new**':
            return
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        # We have to assume that we got here because the current user
        # has at least 'read' permission on the current node. 

        # The only case we have to worry about is when node is not
        # None and the permission comes from a role allocation against
        # that node and not from the parent.

        # First, we eliminate the parent...
        self.parents = self._reduced_list(self.parents)

        # If we still have at least one parent then we are ok to go
        if len(self.parents):
            return
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Forced into having to look at the siblings one at a time :-(
        self.siblings_left = self._reduced_list(self.siblings_left)
        self.siblings_right = self._reduced_list(self.siblings_right)
        #-- done

    def _reduced_list(self, candidates):
        """ Remove entries from this list if we have no permissions.

            Candidates is a list of node objects.
        """
        op = []
        for nde_obj in candidates:
            if (get_user_node_permissions(
                nde_obj.nde_idx, self.user).test_permit_list(self.perm)):
                op.append(nde_obj)
        return op

#-----------------------------------------------------------------------

def expunge_tree(object_reference):
    """ Delete this node and all lower nodes, not forgetting the graph
        links.

        This can have unexpected side effects if part of this tree is
        linked to another tree that is not being deleted. We do not
        test for this here.
    """
    child_set = child_trees(object_reference)
    if len(child_set) > 0:
        for child in child_set:
            expunge_tree(child)
    # Find the parents
    parent_set = (engine.session.query(ndEdge).filter
                  (ndEdge.nde_child == object_reference)).all()
    for parent in parent_set:
        make_unlink(object_reference, parent.nde_parent)
    delete_node_dataset(get_node_dataset(object_reference))

#-----------------------------------------------------------------------

def extract_identifier(data_object):
    """ Extract nde_client_reference or nde_idx

        Use for generating links
    """
    if isinstance(data_object, ndNode):
        return data_object.nde_client_reference or data_object.nde_idx
        #>>>>>>>>>>>>>>>>>>>>
    if isinstance(data_object, type([])):
        for new_object in data_object:
            if isinstance(new_object, ndNode):
                 return new_object.nde_client_reference or new_object.nde_idx
                 #>>>>>>>>>>>>>>>>>>>>
    if isinstance(data_object, type({})):
        if 'nd_node' in data_object:
            idx = data_object['nd_node'].nde_idx
            crf = data_object['nd_node'].nde_client_reference
            return crf or idx
            #>>>>>>>>>>>>>>>>>>>>
    if isinstance(data_object, (type(''), type(u''))):
        return data_object
        #>>>>>>>>>>>>>>>>>>>>
    raise ndIdentifierNotFound

#-----------------------------------------------------------------------
