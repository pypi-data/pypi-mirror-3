# Name:      lokai/lk_register/register_action.py
# Purpose:   Do something when a user has registered
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

import lokai.tool_box.tb_common.configuration as config
from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_worker.nodes.search import find_from_string

from lokai.lk_worker.models.builtin_data_resources import ndRoleAllocation

#-----------------------------------------------------------------------

class UserRegistration(Exception):
    pass

#-----------------------------------------------------------------------

def user_register_action(data_object):
    """ Register a user to a group by allocating the user to a default
        node with a default role.

        :data_object: a dictionary defining the user, as captured by
            the registration forms.

        :default_node: is found from the configuration file at
            [login]
            user_default_group = {path to a node}
            user_default_role = {role name}
            
            :{path to a node}: is a partial path (see
                ``find_from_string`` that must identify a single,
                existing, node.

            :{role name}: optional setting. Names a specific
                pre-defined role. Default ``lkw_task``.

        Do nothing if there is no default node in the configuration.

    """
    cfg = config.get_global_config()
    group_path = cfg.get('login', {}).get('user_default_group')
    if group_path is None:
        return True
    group_set = find_from_string(group_path)
    if len(group_set) == 0:
        raise UserRegistration, (
            "No default group found for %s"%str(group_path))
    if len(group_set) > 1:
        raise UserRegistration, (
            "To many possible default groups found for %s"%str(group_path))
    group_idx = group_set[0]
    group_role =  cfg.get('login', {}).get('user_default_role', 'lkw_task')
    # Allocate a role to the default group
    user_role = ndRoleAllocation()
    user_role.rla_mnemonic = group_role
    user_role.rla_user = data_object['user_uname']
    user_role.nde_idx = group_idx
    engine.session.add(user_role)
    return True

#-----------------------------------------------------------------------
