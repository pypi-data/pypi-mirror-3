# Name:      lokai/lk_login/permissions.py
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

#-----------------------------------------------------------------------
# Define some useful constants

PERM_READ   = 1
PERM_MODIFY = 2
PERM_ADD    = 4
PERM_DELETE = 8

SCOPE_SITE  = 'site'

GUEST_NAME  = 'anonymous' # Depends on defining this in the database.

#-----------------------------------------------------------------------

class ScopeSet(dict):
    """ Mimics a dictionary where the entries are:

        {scope: actions}

        :scope: either SCOPE_SITE or something else. Can be used to
            restict the scope of a permission to a particular data area.

        :actions: integer, being the sum of any required action permissions.
        
    """
    def __init__(self, vl=None):
        """ Initialise to empty, or to given value.

            :vl: either

                (scope: actions)

                or

                {scope: actions}
        """
        super(ScopeSet, self).__init__()
        if vl:
            if isinstance(vl, type(())):
                self[vl[0]] = vl[1]
            else:
                self.update(vl)

    def any_action (self):
        """ Return all possible actions for all scopes """
        op = 0
        for k, v in self.items():
            op = op | v
        return op

    def __add__ (self, vl):
        """ Merge in a new set of permissions from a tuple, dictionary
            or ScopeSet
        """
        if isinstance(vl, type(())):
            ip = {vl[0]: vl[1]}
        else:
            ip = vl
        op = self
        for scope, perm in ip.items():
            if scope in self:
                op[scope] = self[scope] | perm
            else:
                op[scope] = perm
        return op

#-----------------------------------------------------------------------

class FunctionPermissions(dict):
    """ Store a set of permissions in a standardised form and allow
        searches and merges.
    """
    def __init__(self):
        super(FunctionPermissions, self).__init__()
        self.action_code = {
            'read'  :   PERM_READ,
            'view'  :   PERM_READ,
            'mod'   :   PERM_MODIFY,
            'edit'  :   PERM_MODIFY,
            'add'   :   PERM_ADD,
            'del'   :   PERM_DELETE,
            'delete':   PERM_DELETE
                         }

    def __setitem__(self, kv, ss_item):
        """ Store a scope set item  - convert to ScopeSet if required """
        if isinstance(ss_item, (type(1), type(''))):
            ss_item = (SCOPE_SITE, ss_item)
                      
        super(FunctionPermissions, self).__setitem__(kv, ScopeSet(ss_item))

    def update(self, other):
        """ Our own version of update that uses merge_item for
            consistency
        """
        for key, ss_item in other.iteritems():
            scope = SCOPE_SITE # by default
            if isinstance(ss_item, type('')):
                actions = ss_item
            else:
                try:
                    scope = ss_item[0]
                    actions = ss_item[1]
                except TypeError:
                    actions = ss_item
                except IndexError:
                    actions = ss_item[0]
            try:
                actions = self.action_code[actions]
            except KeyError:
                actions = actions
            
            self.merge_item(key, (scope, actions))

    def __str__(self):
        bd = []
        for k, v in self.items():
            bd.append("%s: %s"%(k, str(v)))
        op = "{%s}" % ', '.join(bd)
        return op

    def merge_item (self, function, tpl_actions):
        """ Merge the scope/action pair into the permission set.

            If the function is already present, the actions are added
            in to each relevant scope.
        """
        # tpl_perm = (scope, permit)
        if function in self:
            self[function] += tpl_actions
        else:
            self[function] = ScopeSet(tpl_actions)
            
    def test_permit(self, kv, action_restriction, scope=SCOPE_SITE):
        """ Return True if this instance supports the given action
            scope (read/modify/add/delete).

            :action_restriction: is either:

                a string: one of 'read', 'view',
                'mod', 'edit', 'add' 'del', 'delete'

                or

                a tuple where the first entry is one of the above.

            A True value is returned if any of the permissions in this
            instance contain the given action flag.
            
        """
        if (isinstance(action_restriction, type('')) and
            action_restriction in self.action_code.keys()):
            action_restriction = self.action_code[action_restriction]
        if isinstance(kv, (list, tuple)) and len(kv) == 1:
            kv = kv[0]
        # Return true if the action_restriction bit is set in the permit field
        try:
            return action_restriction & self[kv][scope] > 0
        except KeyError:
            return False

    def test_permit_list(self, given_restriction):
        """ Return True if this instance supports the given
            restriction.
        
            given_restriction: The security level needed to show an item
            
                Allowed [None], [{}], None (all return True)
         
                [ {func:(scope, req), func2:(scope2, req2)},
                  {func3:(scope3, req3)} ]

                Implies either
                    (func-scope-req AND func2-scope2-req2)

                    or
                    
                    func3-scope3-req3

                Available requirements are:
                   'read' aka 'view'
                   'mod'  aka 'edit'
                   'add'
                   'del'  aka 'delete'
        """
        if not isinstance(given_restriction, (list, tuple)):
            if isinstance(given_restriction, dict):
                given_restriction = [given_restriction]
            elif not given_restriction:
                return True
            else:
                # Permissions list not supplied as a list
                return False

        for perm_dict in given_restriction:
            # each perm_dict is now an AND dictionary
            if not perm_dict:
                # An empty entry in the outer list is only valid if it
                # is the only entry in the list.
                if len(given_restriction) == 1:
                    return True
                return False # Not being able to test should not pass
            elif not isinstance(perm_dict, dict):
                return False # Not being able to test should not pass
            else:
                # Empty dict?
                if len(given_restriction) == 1 and len(perm_dict.keys()) == 0:
                    return True
            # Now to test the given dictionary. The first failure here
            # is a failure of the 'and' condition.
            ok = True #
            for func, pd_func in perm_dict.iteritems():
                if isinstance(pd_func, dict):
                    inner_trial = True
                    for func_scope, func_action in pd_func.iteritems():
                        if not self.test_permit(func, func_action, func_scope):
                            inner_trial = False
                            break
                    if not inner_trial:
                        ok = False
                        break
                else:
                    func_scope = SCOPE_SITE # Unless we discover otherwise
                    func_action = PERM_READ # Unless we discover otherwise
                    if (isinstance(pd_func, type('')) and
                        pd_func in self.action_code.keys()):
                        # Passed ONLY the requirement
                        func_action = pd_func
                    elif isinstance(pd_func, (type(1))):
                        # Numeric passed in as requirement
                        func_action = pd_func
                    elif (isinstance(pd_func, (type(()), type([]))) and
                          len(pd_func) == 2 and
                          (pd_func[1] in self.action_code.keys() or
                           isinstance(pd_func[1], type(1)))):
                        # Usable format is ok
                        func_scope, func_action = pd_func
                    if not self.test_permit(func, func_action, func_scope):
                        ok = False
                        # No point in continuing
                        break
            if ok:
                # passed something in the 'or' list
                return True
        return False

    def append(self, other):
        """ Merge the premissions in the 'other' permission object
            into this object.
        """
        for fcn_text, detail in other.iteritems():
            for scope, permit in detail.iteritems():
                self.merge_item(fcn_text, (scope, permit))

    def __add__(self, other):
        """ Add the two permission objects to produce a third.
        """
        op = copy.deepcopy(self)
        op.append(other)
        return op

    def extend(self, given_function, action_mask):
        """ Extend the permission set by adding the given function but
            only for scopes that match the given action mask in any
            other function in the set.

            :given_function: a function name. An entry for this
                function will be created (if not found), or updated
                (if found) if there is another function that matches
                the given action mask for any scope.

            :action_mask: integer. A set of actions that must be
                matched for the above condition.

            The new or updated entry will have only the actions that
            matched those given in action_mask for any and every scope
            that contains such a match to the action mask.
        """
        op = FunctionPermissions() # Avoid changing self in place
        for func, pd_func in self.iteritems():
            for scope, action in pd_func.iteritems():
                new_action = action & action_mask
                if new_action:
                    op.merge_item(given_function, (scope, new_action))
        op.append(self)
        return op

#-----------------------------------------------------------------------
