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
# nd_permission
#
# A single named function to be used for local permission restrictions
# on a node. See ticket at node 0000000039.
table = Table(
    'nd_permission', meta,
    Column('nde_idx', String, primary_key=True),
    Column('nde_permission', String, primary_key=True),
    
)

all_tables.append(table)

#-----------------------------------------------------------------------

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    for tbl in all_tables:
        tbl.create(checkfirst=True)
    for seq in all_sequence:
        seq.create()
 
def downgrade(migrate_engine):
    meta.bind = migrate_engine
    all_tables.reverse()
    for tbl in all_tables:
        tbl.drop(checkfirst=True)

#-----------------------------------------------------------------------
