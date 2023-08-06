# Name:      lokai/lk_login/user_model.py
# Purpose:   UI independent things for user data
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

import re
import random
from sqlalchemy.sql import or_

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update, get_row
from lokai.lk_login.db_objects import User

#-----------------------------------------------------------------------

ALPHANUM = re.compile('[+=*%;#\[\]@\r\n]')

def validate_email(email, user_uname=None):
    """ return (error, message) """
    error_count = 0
    message = ''
    if email:
        eparts = email.split('@')
        if len(eparts) == 1:
            message = "Invalid email address - no '@' sign"
            error_count = 1
        elif len(eparts) > 2:
            message = "Invalid email address - too many '@' signs"
            error_count = 1
        else:
            if ';' in email:
                message = "Invalid email address - ';' not allowed"
                error_count = 1
        if error_count == 0:
            ux = engine.session.query(
                User
                ).filter(
                User.user_email == email)
            if user_uname:
                ux = ux.filter(User.user_uname != user_uname)
            ux = ux.first()
            if ux:
                message = "Email used by another"
                error_count = 1
    return error_count, message

def validate_lname(lname):
    """ return (error, message) """
    error_count = 0
    message = ''
    if lname:
        bad_set = ALPHANUM.findall(lname)
        if len(bad_set) == 1:
            message = ("Your display name contains '%s'"
                       " - an invalid character"%bad_set[0])
            error_count = 1
        elif len(bad_set) > 1:
            message = ("Your display name contains '%s'"
                       " - which are invalid characters"%' '.join(bad_set))
            error_count = 1
    return error_count, message

#-----------------------------------------------------------------------

USER_ID_LOW  = 1000000
USER_ID_HIGH = 9000000

MAX_UNAME_TRIAL = 9999

def make_user_uname():
    """ Generate a random number that can be used as a user name.

        The number is tested against existing user names, so is unique
        so long as only one registration is being tried at one time.

        If two registrations coincide, one will fail with a duplicate
        key error.

        If we have a lot of users we could need many goes through the
        test loop. In order to gurantee the process terminates we
        check against a (large) maximum number of tries.
    """
    trial = 0
    while 1:
        trial += 1
        assert trial < MAX_UNAME_TRIAL
        test_uname = str(random.randint(USER_ID_LOW, USER_ID_HIGH))
        test_list = engine.session.query(User).filter(
            User.user_uname == test_uname).first()
        if not test_list:
            return test_uname


#-----------------------------------------------------------------------

def user_view_store(record, new_user=False):
    """ Update an existing user with details from the given record """
    required_existing = 1 if new_user==False else 0
    insert_or_update(User, record, required_existing=required_existing)
    return True

def user_view_get(username):
    """ Fetch user details from the database using the username. This
        can be one of a number of alternative ways of identifying the
        user.
    """
    if username:
        user = engine.session.query(
            User
            ).filter(
            or_((User.user_uname==username),
                (User.user_email==username.lower())
            )).first()
        return user
    return None

#-----------------------------------------------------------------------
