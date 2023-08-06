# Name:      lokai/lk_worker/migration/lk_worker/nodes_db/versions/002.py
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
all_sequence = []

#-----------------------------------------------------------------------
# Roles for a node
#
# The Role is a way of linking people or groups to Nodes. All links
# should be to the contacts database. That is, all details of name and
# address are held elsewhere.

# Originally allowed only one entry per user on a given node. Now
# allows multiple entries.
#

# nd_role_allocation
table = Table(
    'nd_role_allocation', meta,
    Column('nde_idx', String,),
    Column('rla_mnemonic', String), # The role this user has on this  node
    Column('rla_user', String)      # The user that has the role
    )

#-----------------------------------------------------------------------

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    pk_old = PrimaryKeyConstraint(table.c.nde_idx,
                                  table.c.rla_user)
    pk_old.autoname()
    pk_old.drop()
    pk_new = PrimaryKeyConstraint(table.c.nde_idx,
                                  table.c.rla_user,
                                  table.c.rla_mnemonic)
    pk_new.autoname()
    pk_new.create()
    
def downgrade(migrate_engine):
    meta.bind = migrate_engine

#-----------------------------------------------------------------------
