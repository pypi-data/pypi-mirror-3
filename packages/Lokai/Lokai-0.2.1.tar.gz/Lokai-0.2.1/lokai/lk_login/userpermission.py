# Name:      lokai/lk_login/userpermission.py
# Purpose:   Build and handle a set of permissions.
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

import copy

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.lk_login.db_objects import (User,
                                       UserRole,
                                       RoleFunction,
                                       )

from lokai.lk_login.permissions import (FunctionPermissions,
                                        GUEST_NAME,
                                        SCOPE_SITE,
                                        )

#-----------------------------------------------------------------------

class UserPermission(FunctionPermissions):
    """ Identify all the permissions for the given user and keep them
        handy for testing.
    """

    def __init__(self, ** kwargs):

        super(UserPermission, self).__init__()

        self.user = kwargs.get('user', None)
        if self.user and not kwargs.get('delay_table_reads', None):
            self.get_user_permits()

    def get_user_permits(self):
        """ Look in UserRole and RoleFunction to build a set of
            permissions for this user.
        """
        # Get ALL RoleFunctions for the user
        rf_query = engine.session.query(RoleFunction, UserRole).join(
            (UserRole, RoleFunction.role_text==UserRole.role_text),
            (User, UserRole.user_uname==User.user_uname)
            )
        if self.user and self.user != GUEST_NAME:
            rf_query = rf_query.filter(User.user_uname.in_([self.user, GUEST_NAME]))
        else:
            rf_query = rf_query.filter(User.user_uname == GUEST_NAME)
        for role_func, userrole in rf_query.all():
            self.merge_item(role_func['fcn_text'],
                            (userrole['role_scope'], role_func['permit']))
             
#-----------------------------------------------------------------------
