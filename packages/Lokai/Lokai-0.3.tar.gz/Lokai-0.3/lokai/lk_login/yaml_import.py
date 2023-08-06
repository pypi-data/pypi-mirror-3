# Name:      lokai/lk_login/yaml_import.py
# Purpose:   Initialise login data from a yaml file
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
from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_login.db_objects import (Organisation,
                                       Function,
                                       Role,
                                       RoleFunction,
                                       User,
                                       UserRole,
                                       )

#-----------------------------------------------------------------------

class YamlLogin(object):
    """ Class to work with YamlImport to handle basic login data.

        Designed to be used as a mixin
    """

    def __init__(self, **kwargs):
        self.map = {
            'orgs'  : {},
            'users' : {},
            'roles' : {}}
        self.register('organisation', self.process_organisation)
        self.register('function', self.process_function)
        self.register('role', self.process_role)
        self.register('user', self.process_user)

    #-------------------------------------------------------------------

    def process_organisation(self, data_set):
        for organisation in data_set.iteritems():
            self._base_process_organisation(organisation)

    def process_function(self, data_set):
        for function, detail in data_set.iteritems():
            self._base_process_function(function, detail)

    def process_role(self, data_set):
        for role, detail in data_set.iteritems():
            self._base_process_role(role, detail)

    def process_user(self, data_set):
        for user, detail in data_set.iteritems():
            self._base_process_user(str(user), detail)
                    
    #-------------------------------------------------------------------
    # Utilities for handling the objects. The map that is used here
    # allows objects to be found without reference to the database.

    def find_org(self, organisation):
        if self.map['orgs'].has_key(organisation):
            return self.map['orgs'][organisation]
        if self.ignore:
            return None
        org_query = engine.session.query(Organisation)
        org_query = org_query.filter_by(org_name=organisation)
        orgs = org_query.all()
        if len(orgs) == 1:
            self.map['orgs'][organisation] = orgs[0]['org_idx']
            return orgs[0]['org_idx']
        else:
            return None
        
    def find_user(self, uname):
        if self.map['users'].has_key(uname):
            return self.map['users'][uname]
        if self.ignore:
            return None 
        user_query = engine.session.query(User)
        user_query = user_query.filter_by(user_uname=uname)
        users = user_query.all()
        if len(users) == 1:
            self.map['users'][uname] = users[0]['user_uname']
            return users[0]['user_uname']
        else:
            return None

    def find_role(self, role):
        if self.map['roles'].has_key(role):
            return self.map['roles'][role]
        if self.ignore:
            return None 
        role_query = engine.session.query(Role)
        role_query = role_query.filter_by(role_text=role)
        roles = role_query.all()
        if len(roles) == 1:
            self.map['roles'][role] = roles[0]['role_text']
            return roles[0]['role_text']
        else:
            return None

    #-------------------------------------------------------------------

    def _base_process_organisation(self, organisation):
        """ Place an organisation
        """
        org_str = "Organisation - %s" % str(organisation)
        if self.ignore:
            notify.info("Ignored %s" % org_str)
            return
        if organisation:
            org_query = engine.session.query(Organisation)
            org_query = org_query.filter_by(org_name=organisation)
            res = org_query.all()
            if len(res) == 0:
                org = Organisation()
                org['org_name'] = organisation
                notify.info("Storing %s" % org_str)
                engine.session.add(org)
                engine.session.flush()
                engine.session.refresh(org)
                self.map['orgs'][organisation] = org['org_idx']
            elif len(res) == 1:
                self.map['orgs'][organisation] = res[0]['org_idx']
            else:
                notify.info("%s found for %s" % (str(len(res)),
                                                      org_str))
        else:
            notify.info("No data found for %s" % org_str)

    #-------------------------------------------------------------------

    def _base_process_function(self, fcn_text, fcn_description):
        """ Place a function
        """
        func_str = "Function - %s:%s" % (str(fcn_text), str(fcn_description))
        if self.ignore:
            notify.info("Ignored %s: %s" % (func_str, fcn_description))
            return
        if fcn_text:
            # Does it exist
            func_query = engine.session.query(Function)
            func_query = func_query.filter_by(fcn_text=fcn_text)
            res = func_query.all()
            if len(res) == 0:
                func = Function()
                func['fcn_text'] = fcn_text
                func['fcn_description'] = fcn_description
                engine.session.add(func)
                # We need the idx there for role_funcs
                engine.session.flush()
                notify.info("Storing %s" % func_str)
            elif len(res) == 1:
                notify.info("Found %s (updating description)" % func_str)
                func = res[0]
                func['fcn_description'] = fcn_description
                engine.session.add(func)
            else:
                notify.warn("Error: %s existing found for %s" % (
                                    str(len(res)),
                                    func_str))
        else:
            notify.info("Not enough data found for %s" % func_str)

    #-------------------------------------------------------------------

    def _base_process_role(self, role_text, detail):
        """ Place a role and associated role_functions
        """
        role_str = "Role - %s with %s" % (str(role_text),
                                          str(detail))
        if self.ignore:
            notify.info("Ignored %s" % role_str)
            return
        if role_text and isinstance(detail, dict):
            # Does the role exist?
            role_query = engine.session.query(Role)
            role_query = role_query.filter_by(role_text=role_text)
            res = role_query.all()
            if len(res) == 0:
                role = Role()
                role['role_text'] = role_text
                engine.session.add(role)
                engine.session.flush()
                engine.session.refresh(role)
                # notify.debug(engine.session.new)
                role_text = role['role_text']
                notify.info("Storing %s" % role_str)
                self.map['roles'][role_text] = role_text
            elif len(res) == 1:
                role_text = res[0]['role_text']
                notify.info("Using existing %s" % role_str)
                self.map['roles'][role_text] = role_text
            else:
                notify.warn("Error: %s existing found for %s" % (
                                        str(len(res)),
                                        role_str))
            # RoleFunctions
            for fcn_text, scope in detail.items():
                rf_str = "RoleFunction - %s:%s" % (str(fcn_text),
                                                   str(scope))
                rf_query = engine.session.query(RoleFunction)
                rf_query = rf_query.filter_by(role_text=role_text,
                                              fcn_text=fcn_text)
                res = rf_query.all()
                if len(res) == 0:
                    rf = RoleFunction()
                    rf['role_text'] = role_text
                    rf['fcn_text'] = fcn_text
                    rf['permit'] = scope
                    notify.info("Storing %s" % rf_str)
                    engine.session.add(rf)
                elif len(res) == 1:
                    notify.info("Found %s (updating the scope)" % rf_str)
                    # Update the scope
                    rf = res[0]
                    rf['permit'] = scope
                    if scope:
                        engine.session.add(rf)
                    else:
                        engine.session.delete(rf)
                        engine.session.flush()
                else:
                    notify.info("%s found for %s" % (
                                        str(len(res)),
                                        rf_str))

    #-------------------------------------------------------------------

    def _base_process_user(self, user, detail):
        """ Place a user and associated user_role
        """
        user_str = "User - %s with %s" % (str(user),
                                          str(detail))
        if not user:
            notify.info("No data found for %s" % user_str)
            return
        elif self.ignore:
            notify.info("Ignored %s" % user_str)
            return
        # Does user exist?
        user_query = engine.session.query(User).filter_by(user_uname=user)
        res = user_query.all()
        if len(res) == 0:
            usr = User()
            usr['user_uname'] = user
            usr['user_pword'] = detail.get('password', None)
            usr['user_lname'] = detail.get('long_name', None)
            usr['user_email'] = detail.get('email', None)
            organisation = detail.get('organisation', None)
            if organisation :
                usr['org_idx'] = self.find_org(organisation)
            engine.session.add(usr)
            engine.session.flush()
            engine.session.refresh(usr)
            notify.info("Storing %s" % user_str)
            self.map['users'][user] = usr['user_uname']
        elif len(res) == 1:
            notify.info("Found %s" % user_str)
            self.map['users'][user] = res[0]['user_uname']
        else:
            notify.info("%s found for %s" % (str(len(res)),
                                                  user_str))
            return
        # UserRoles
        notify.info("UserRoles")
        user_uname = self.find_user(user)
        if not user_uname:
            notify.info("User uname not found, cannot add roles")
            return
        for role, scope in detail.get('roles', []):
            role_text = self.find_role(role)
            if not role_text:
                notify.info("Role not found with %s" % str(role))
                return
            ur_str = "UserRole - %s:%s" % (str(role), str(scope))
            if self.ignore:
                notify.info("Ignored %s" % ur_str)
                return
            # Does it exist already
            ur_query = engine.session.query(UserRole)
            ur_query = ur_query.filter_by(user_uname=user_uname, 
                                          role_text=role_text,
                                          role_scope=scope)
            res = ur_query.all()
            if len(res) == 0:
                ur = UserRole()
                ur['user_uname'] = user_uname
                ur['role_text'] = role_text
                ur['role_scope'] = scope
                engine.session.add(ur)
                notify.info("Storing %s" % ur_str)
            elif len(res) == 1:
                notify.info("Found %s" % ur_str)
            else:
                notify.info("%s found for %s" % (str(len(res)),
                                                       ur_str))
    
    #-------------------------------------------------------------------
