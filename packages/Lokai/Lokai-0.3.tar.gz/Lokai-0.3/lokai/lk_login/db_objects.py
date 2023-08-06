# Name:      lokai/lk_login/db_objects.py
# Purpose:   Objects for ORM link to database
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

use_hashlib = False
try:
    from hashlib import sha1
    use_hashlib = True
except:
    import sha

import random
import string

from lokai.tool_box.tb_database.orm_interface import OrmRegistry
from lokai.tool_box.tb_database.orm_base_object import OrmBaseObject

#-----------------------------------------------------------------------
# The database
__db_name__ = "login_db"
__ini_section__ = "login"

model = OrmRegistry(__ini_section__, __db_name__)

#-----------------------------------------------------------------------
# User

class User(OrmBaseObject):
    
    search_fields = ['user_uname']
    
    def _hashPassword(self, plaintext, salt=None):
        """Turn <plaintext> into a hashed password.
        This uses standard python libraries rather than the old and weaker
        """
        if salt is None:
            # No salt given, create a new one.
            salt = ''.join(random.choice(string.ascii_letters) for x in range(8))
        # "Salting" the password (i.e. adding random chars) means you can't just
        # look up the hash in a table.
        if use_hashlib:
            password = sha1(salt)
            password.update(plaintext)
        else:
            password = sha.new(salt)
            password.update(plaintext)
        op = '%s|%s' % (salt, password.hexdigest())
        return op

    def isPassword(self, vx):
        existingpassword = self['user_pword']
        if not existingpassword:
            return False
        if not ('|' in existingpassword):
            # setItem salt|hashes plaintext password
            self['user_pword'] = self._hashPassword(existingpassword)
            # changes are automatically saved at the next commit
            existingpassword = self['user_pword']
        if existingpassword and ('|' in existingpassword):
            # This is a hashed password and so we need to hash the given one
            # and compare it.
            salt = existingpassword.split('|', 1)[0]
            op = self._hashPassword(vx, salt)
            return (op == existingpassword)
        # Should not get here any more as unhashed passwords
        # are hashed and then stored to the database
        return False

model.register(User, 'login_user')

#-----------------------------------------------------------------------
# Organisation

class Organisation(OrmBaseObject):
    
    search_fields = ['org_idx']

model.register(Organisation, 'login_organisation')

#-----------------------------------------------------------------------
# User Role

class UserRole(OrmBaseObject):

    search_fields = ['user_uname', 'role_text']

model.register(UserRole, 'login_user_role')

#-----------------------------------------------------------------------
# Role

class Role(OrmBaseObject):

    search_fields = ['role_text']

model.register(Role, 'login_role')

#-----------------------------------------------------------------------
# Function

class Function(OrmBaseObject):

    search_fields = ['fcn_text']

model.register(Function, 'login_function')

#-----------------------------------------------------------------------
# Role/Function
class RoleFunction(OrmBaseObject):

    search_fields = ['role_text', 'fcn_text']

model.register(RoleFunction, 'login_role_function')

#-----------------------------------------------------------------------
