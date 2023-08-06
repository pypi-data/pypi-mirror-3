# Name:      lokai/lk_worker/models/builtin_data_resources.py
# Purpose:   Define plugins on the IWorkerData interface
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

from collections import namedtuple

import pyutilib.component.core as component

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import (
    insert_or_update,
    delete_row,
    MUST_NOT_EXIST,
    )
from lokai.tool_box.tb_database.orm_base_object import OrmBaseObject

from lokai.lk_login.userpermission import UserPermission, SCOPE_SITE
from lokai.lk_login.db_objects import RoleFunction, Role
from lokai.lk_worker.models import (
    ndNode,
    model
    )
from lokai.lk_worker.nodes.search import search_here, search_up, search_down

from lokai.lk_worker.extensions.data_interface import IWorkerData

#-----------------------------------------------------------------------

class ndRoleAllocation(OrmBaseObject):
    
    search_fields = ['nde_idx', 'rla_user', 'rla_mnemonic']
    option_list_map = {'node_roles' : 'rla_mnemonic'}

model.register(ndRoleAllocation, 'nd_role_allocation')

#-----------------------------------------------------------------------

class ndUserAssignment(OrmBaseObject):

    search_fields = ['nde_idx']

model.register(ndUserAssignment, 'nd_user_assignment')

#-----------------------------------------------------------------------

class ResourceList(object):
    """ Store a resource list as a dictionaray keyed on user name.

        Useful for comparing old and new lists for update.

        The object also contains an ordering, so that iteration is
        done in the same order as the items were inserted.
    """

    def __init__(self, resource_list=None):
        """
            :resource_list: [ ... (k,v) ... ]
            
        """
        self._content = {}
        self._ordering = []
        if resource_list:
            if isinstance(resource_list, (type([]), type(()))):
                for k,v in resource_list:
                    self[k] = v
            else:
                for k, v in resource_list.iteritems():
                    if isinstance(v, (type([]), type(()))):
                        for vk in v:
                            self[k] = vk
                    else:
                        self[k] = v

    def __setitem__(self, k, v):
        if k not in self._ordering:
            self._ordering.append(k)
            self._content[k] = [v]
        else:
            self._content[k].append(v)

    def __len__(self):
        return len(self._ordering)
    
    def contains(self, k, v):
        """ Return True if the key 'k' exists and that the list at 'k'
            contains 'v'
        """
        try:
            return v in self._content[k]
        except KeyError:
            return False

    def remove(self, k, v):
        """ Modify in-place: remove the value 'v' from the list at 'k'.

            Do nothing if not found.
        """
        try:
            self._content[k].remove(v)
            if not self._content[k]:
                del self._content[k]
        except (KeyError, ValueError,):
            pass

    def keys(self):
        return self._ordering

    def iteritems(self):
        for k in self._ordering:
            for v in self._content[k]:
                yield k,v

    def normalise(self):
        """ Return a new object that does not contain any items in
            self where the value is None or 'remove'
        """
        op = ResourceList()
        for k,v in self.iteritems():
            if v is not None and v != 'remove':
                op[k] = v
        return op

    CompareResponse = namedtuple('CompareResponse', 'both, self, other')
    def compare(self, other):
        """ Return three objects:

            # Contains all items common between the two.

            # Contains all items found in self and not in other.

            # Contains all items found in other and not in self.

        """
        # We cannot guarantee that the two objects are in the same
        # order. So we do this the obvious way.
        op_both = ResourceList()
        op_other = ResourceList()
        op_self = ResourceList()
        for k, v in self.iteritems():
            if other.contains(k, v):
                op_both[k] = v
            else:
                op_self[k] = v
        for k, v in other.iteritems():
            if not self.contains(k, v):
                op_other[k] = v
        return self.CompareResponse(op_both, op_self, op_other)

    def __str__(self):
        op = ['-----']
        for k, v in self.iteritems():
            op.append("%s: %s" % (k, v))
        return '\n'.join(op)

#-----------------------------------------------------------------------

def get_node_resource_list(nde_idx, **kwargs):
    """ Return a resource/role list for this node or upwards

        user = limit search to the given user

        order_by = return list ordered by given field

        full = True for search upwards in tree
    """
    # Implementation note: The search_up/down/here functions do not
    # work if there is no ndNode object in the query, so we have to
    # include it. However, the result is then stripped so that we get
    # just a list of ndResourceAllocation objects
    if isinstance(nde_idx, list):
        node_list = nde_idx
    elif nde_idx is None:
        node_list = None
    else:
        node_list = [nde_idx]
    user = kwargs.get('user')
    full = kwargs.get('full')
    from_top = kwargs.get('from_top')
    order_by = kwargs.get('order_by')
    qy = engine.session.query(
        ndRoleAllocation, ndNode).join(
        (ndNode, ndRoleAllocation.nde_idx == ndNode.nde_idx))
    if user:
        if isinstance(user, (type([]), type(()))):
            qy = qy.filter(ndRoleAllocation.rla_user.in_(user))
        else:
            qy = qy.filter(ndRoleAllocation.rla_user == user)
    if full:
        qy = search_up(qy, node_list)
    elif from_top:
        qy = search_down(qy, node_list)
    else:
        qy = search_here(qy, node_list)
    if order_by:
        qy = qy.order_by(order_by)
    full_set = qy.all()
    return [item[0] for item in full_set]

def get_actual_node_resource_list(nde_idx, **kwargs):
    res = get_node_resource_list(nde_idx, **kwargs)
    return ResourceList(
        [(x.rla_user, x.rla_mnemonic) for x in res]
        )

def get_full_node_resource_list(nde_idx, **kwargs):
    res = get_node_resource_list(nde_idx, full=True, **kwargs)
    return ResourceList(
        [(x.rla_user, x.rla_mnemonic) for x in res]
        )

def get_user_top_resource_list(username, tops=None):
    """ Return a list of role allocation objects (tree tops) that all
        have the given user as an allocated resource.
    """
    nde_idx = tops
    return get_node_resource_list(nde_idx, from_top=True, user=username)

def user_top_trees(username, tops=None):
    """ Return a list of node idx that all have the
        given user as an allocated resource.
    """
    op = get_user_top_resource_list(username, tops)
    return [role.nde_idx for role in op]

#-----------------------------------------------------------------------

def get_permissions_for(resource_list, delay_table_reads=None):
    """ Find permission objects for all these guys.

        Returs a UserPermission object

        :resource_list: ResourceList
        
        :delay_table_reads: if this evaluates as True then the
            UserRole is not read. The result contains permissions
            defined only by the resource list. You can call the
            get_user_permits method on the returned object if you want
            to add these global permissions at a later stage in your
            calculations.
    """
    # A user may have more than one role in this mixture, so we need
    # to accumulate the permissions.
    #
    # Certain roles may not have any entries with specific
    # permissions. These are functional roles rather than permissive
    # roles and are handled in different ways. The selection and
    # accumulation will simply do nothing.
    accumulator = {}
    for username, role in resource_list.iteritems():
        if not accumulator.has_key(username):
            accumulator[username] = UserPermission(
                user=username,
                delay_table_reads=delay_table_reads)
        rf_query = engine.session.query(RoleFunction).join(
            (Role, Role.role_text == RoleFunction.role_text)).filter(
            Role.role_text == role)
        for rf in rf_query.all():
            accumulator[username].merge_item(
                rf.fcn_text, (SCOPE_SITE, rf.permit))
    #
    return accumulator

#-----------------------------------------------------------------------
# Special code for user/resource

def node_add_resource(nde_idx, uname, role):
    """ Add a new resource to the node - return a history note
    """
    user_data = {'nde_idx' : nde_idx,
                 'rla_user' : uname,
                 'rla_mnemonic' : role}
    insert_or_update(ndRoleAllocation, user_data, required_existing=MUST_NOT_EXIST)
    return "Add new resource %s, role %s"% (uname, role)

def node_del_resource(nde_idx, uname, role):
    """ Remove a resource from the node - return a history note
    """
    user_data = {'nde_idx' : nde_idx,
                 'rla_user' : uname,
                 'rla_mnemonic': role,
                 }
    _op = delete_row(ndRoleAllocation, user_data)
    #
    # Add in the history
    return ("User %s, role %s has been removed from the resources"% (
                      (uname, role)))

#-----------------------------------------------------------------------

class PiResourceData(component.SingletonPlugin):
    """ Link to nde_activity """
    component.implements(IWorkerData, inherit=True)

    def __init__(self):
        self.name = 'resources'

    def nd_read_query_extend(self, query_in, **kwargs):
        query_result = query_in.add_entity(ndUserAssignment).outerjoin(
            (ndUserAssignment, ndNode.nde_idx==ndUserAssignment.nde_idx))
        return query_result

    def nd_read_data_extend(self, query_result, **kwargs):
        result_map = {}
        if query_result and isinstance(query_result, (list, tuple)):
            for data_object in query_result:
                if isinstance(data_object, ndUserAssignment):
                    result_map['nd_assignment'] = data_object
                    break
            nde_idx = query_result[0].nde_idx
            resource_list = get_actual_node_resource_list(
                nde_idx, order_by = ndRoleAllocation.rla_user)
            result_map['nd_resource'] = resource_list
        return result_map

    def nd_write_data_extend(self, new_data, old_data=None):
        hist_response = []
        nde_idx = new_data['nd_node']['nde_idx']
        if 'nd_assignment' in new_data:
            new_data['nd_assignment']['nde_idx'] = nde_idx
            insert_or_update(ndUserAssignment, new_data['nd_assignment'])
            engine.session.flush()
        if 'nd_resource' in new_data:
            old_obj_set = get_actual_node_resource_list(nde_idx)
            new_obj_set = new_data['nd_resource']
            try:
                new_obj_set = new_obj_set.normalise()
            except AttributeError:
                new_obj_set = ResourceList(new_obj_set)
            obj_diff = new_obj_set.compare(old_obj_set)
            for uname, role in obj_diff.self.iteritems():
                node_add_resource(nde_idx, uname, role)
            for uname, role in obj_diff.other.iteritems():
                node_del_resource(nde_idx, uname, role)
        return hist_response

    def nd_delete_data_extend(self, data_object):
        """ data object is the extended object used elsewhere.

            Do this the sledghammer way.
        """
        hist_response = []
        nde_idx = data_object['nd_node']['nde_idx']
        engine.session.query(ndUserAssignment).filter(
            ndUserAssignment.nde_idx == nde_idx).delete()
        engine.session.query(ndRoleAllocation).filter(
            ndRoleAllocation.nde_idx == nde_idx).delete()
        return hist_response

#-----------------------------------------------------------------------
