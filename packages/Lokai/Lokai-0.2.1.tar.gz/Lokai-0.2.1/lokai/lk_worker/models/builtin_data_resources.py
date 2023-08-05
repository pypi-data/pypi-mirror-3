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

from sqlalchemy import and_

import pyutilib.component.core as component

from lokai.tool_box.tb_common.dates import strtotime
from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import (
    get_row,
    insert_or_update,
    delete_row
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
    
    search_fields = ['nde_idx', 'rla_user']
    option_list_map = {'node_roles' : 'rla_mnemonic'}

model.register(ndRoleAllocation, 'nd_role_allocation')

#-----------------------------------------------------------------------

class ndUserAssignment(OrmBaseObject):

    search_fields = ['nde_idx']

model.register(ndUserAssignment, 'nd_user_assignment')

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
    
def get_full_node_resource_list(nde_idx, **kwargs):
    return get_node_resource_list(nde_idx, full=True, **kwargs)
    
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

        By default the UserPermission object picks up the full set of
        roles defind for that user in UserRole. The permissions
        returned here are merged into that default set. This behaviour
        can be overridden by passing delay_table_reads=True.

    """
    # A user may have more than one role in this mixture, so we need
    # to accumulate the permissions.
    #
    # Certain roles may not have any entries with specific
    # permissions. These are functional roles rather than permissive
    # roles and are handled in different ways. The selection and
    # accumulation will simply do nothing.
    accumulator = {}
    for resource in resource_list:
        username = resource.rla_user
        if not accumulator.has_key(username):
            accumulator[username] = UserPermission(
                user=username,
                delay_table_reads=delay_table_reads)
        rf_query = engine.session.query(RoleFunction).join(
            (Role, Role.role_text == RoleFunction.role_text)).filter(
            Role.role_text == resource.rla_mnemonic)
        for rf in rf_query.all():
            accumulator[username].merge_item(
                rf.fcn_text, (SCOPE_SITE, rf.permit))
    #
    return accumulator

#-----------------------------------------------------------------------
# Special code for user/resource

def node_new_resource(uname, nde_idx):
    """ Add a new resource to the node - return a history note
    """
    user_data = {'nde_idx' : nde_idx,
                 'rla_user' : uname,
                 'rla_mnemonic' : 'undefined'}
    op = get_row(ndRoleAllocation, user_data)
    if len(op) == 0:
        insert_or_update(ndRoleAllocation, user_data)
        txt = "Add new resource %s"% uname
    else:
        txt = "Attempt to add existing resource %s"% uname
    #
    # Add in the history
    return txt

def node_mod_resource(uname, nde_idx, new_role, old_role):
    """ Modify a resource on the node - return a history note
    """
    user_data = {'nde_idx' : nde_idx,
                 'rla_user' : uname,
                 'rla_mnemonic' : new_role}
    _op = insert_or_update(ndRoleAllocation, user_data)
    #
    # Add in the history
    return ("Role for user %s changed from %s to %s"% (
                      uname, old_role, new_role))


def node_del_resource(uname, nde_idx):
    """ Remove a resource from the node - return a history note
    """
    user_data = {'nde_idx' : nde_idx,
                 'rla_user' : uname}
    _op = delete_row(ndRoleAllocation, user_data)
    #
    # Add in the history
    return ("User %s has been removed from the resources"% (
                      uname))

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
            temp_rla_set = get_node_resource_list(
                nde_idx, order_by = ndRoleAllocation.rla_user)
            result_map['nd_resource'] = temp_rla_set
        return result_map

    def nd_write_data_extend(self, new_data, old_data=None):
        hist_response = []
        nde_idx = new_data['nd_node']['nde_idx']
        if 'nd_assignment' in new_data:
            new_data['nd_assignment']['nde_idx'] = nde_idx
            insert_or_update(ndUserAssignment, new_data['nd_assignment'])
            engine.session.flush()
        if 'nd_resource' in new_data:
            old_obj_set = engine.session.query(ndRoleAllocation).filter(
            ndRoleAllocation.nde_idx == nde_idx).all()
            old_set = dict([(obj.rla_user, obj) for
                            obj in old_obj_set])
            for new_obj in new_data['nd_resource']:
                new_obj['nde_idx'] = nde_idx
                new_user = new_obj['rla_user']
                new_mnemonic = new_obj['rla_mnemonic']
                if new_user in old_set:
                    old_obj = old_set[new_user]
                    if new_mnemonic == 'remove':
                        engine.session.delete(old_obj)
                    elif new_mnemonic != old_obj['rla_mnemonic']:
                        old_obj['rla_mnemonic'] = new_mnemonic
                        engine.session.add(old_obj)
                    del old_set[new_user]
                else:
                    insert_or_update(ndRoleAllocation, new_obj)
            engine.session.query(ndRoleAllocation).filter(
                and_((ndRoleAllocation.nde_idx == nde_idx),
                     (ndRoleAllocation.rla_user in old_set.keys())
                     )).delete(synchronize_session='fetch')
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
