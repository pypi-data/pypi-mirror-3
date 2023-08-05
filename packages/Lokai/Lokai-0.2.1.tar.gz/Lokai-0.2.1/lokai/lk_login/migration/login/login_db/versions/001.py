# Name:      lokai/lk_login/migration/login/login_db/versions/001.py
# Purpose:   
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

from sqlalchemy import *
from migrate import *

meta = MetaData()

all_tables = []

# login_organisation
all_tables.append(Table('login_organisation', meta,
    Column('org_idx', Integer, primary_key=True),
    Column('org_name', String),
))

# login_user
all_tables.append(Table('login_user', meta,
    Column('user_uname', String, primary_key=True),
    Column('user_pword', String),
    Column('user_email', String),
    Column('user_lname', String),
    Column('user_start', Date),
    Column('user_end', Date),
    Column('org_idx', Integer,
           ForeignKey('login_organisation.org_idx')),
))

# login_role
all_tables.append(Table('login_role', meta,
    Column('role_text', String, primary_key=True),
))

# login_user_role
all_tables.append(Table('login_user_role', meta,
    Column('user_uname', String,
           ForeignKey('login_user.user_uname'),
           primary_key=True),
    Column('role_text', String,
           ForeignKey('login_role.role_text'),
           primary_key=True),
    Column('role_scope', String, primary_key=True),
))

# login_function
all_tables.append(Table('login_function', meta,
    Column('fcn_text', String, primary_key=True),
    Column('fcn_description', String),
))

# login_role_function
all_tables.append(Table('login_role_function', meta,
    Column('role_text', String,
           ForeignKey('login_role.role_text'),
           primary_key=True),
    Column('fcn_text', String,
           ForeignKey('login_function.fcn_text'),
           primary_key=True),
    Column('permit', Integer),
))

#-----------------------------------------------------------------------

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; use
    # the given engine named 'migrate_engine'
    meta.bind = migrate_engine

    for tbl in all_tables:
        tbl.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    # meta.reflect()
    # Just drop the known tables defined above, thus leaving
    # the `migrate_version` table for upgrading afterward
    meta.bind = migrate_engine
    meta.drop_all(tables=all_tables)

#-----------------------------------------------------------------------
