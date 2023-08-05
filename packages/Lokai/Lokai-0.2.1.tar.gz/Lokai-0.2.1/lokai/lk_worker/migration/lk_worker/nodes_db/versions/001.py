# Name:      lokai/lk_worker/migration/lk_worker/nodes_db/versions/001.py
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
# Node
#
# A Node is the base unit for the project/task management system.
#
# Nodes form a hierarcy, with a single root node as the top.
#
# Within the hierarchy Nodes are given notional types which are
# used to support a user interface and to manage the associated
# functionality.
#
# Node heirarchy is indicated by an owner link. That is, we can
# start at a Node and work up. Going down the hierarchy is a matter
# of selecting all Nodes which have the owner field set to the
# value for the 'current' Node.
#
# The Node Identifier can be used to distinguish the type of the
# node by combining a type mnemonic with a numeric sequence.
# Ideally, the numeric sequence is of fixed length, with zero padding,
# so that alphabetic ordering becomes the same as numeric ordering.
#

# nd_node
table = Table(
    'nd_node', meta,
    Column('nde_idx', String, primary_key=True),
    Column('nde_name', String),    # Node human name
    Column('nde_client_reference', String),
    Column('nde_type', String),
    Column('nde_description', String),
    Column('nde_date_create', DateTime), # Node creation date
    Column('nde_date_modify', DateTime), # Node last modified date
    )

all_tables.append(table)

all_sequence.append(Sequence('nd_node_nde_idx_seq', metadata=meta))

Index('nd_node_nde_client_reference',
                table.c.nde_client_reference)

#-----------------------------------------------------------------------
# The node heirarchy is created by constructing edges in the graph.
#
# A node can be linked in to more than one tree; it has more than one
# parent
#
# The parent to choose when moving up the tree may be defined by
# context. If such a context is not available, then the choice is made
# using the boolean 'nde_choice'

# nd_edge
table = Table(
    'nd_edge', meta,
    Column('nde_parent', String, primary_key=True),
    Column('nde_child',  String, primary_key=True),
    Column('nde_choice', Boolean),
    Column('nde_sequence', Integer)
    )

all_tables.append(table)

#-----------------------------------------------------------------------
# For efficiency, we map SQL sets to the hierarchy using a parent
# manifest. This is simply an unordered list of all the nodes that are
# ancestors of the given node.

# nd_parent
table = Table(
    'nd_parent', meta,
    Column('nde_idx', String, primary_key=True),                       
    Column('nde_parent', String, primary_key=True),
    )

all_tables.append(table)

#-----------------------------------------------------------------------
# A basic project or task node type:

# nd_activity
table = Table(
    'nd_activity', meta,
    Column('nde_idx', String, primary_key=True),
    Column('act_date_start', Date),   # Start date of the activity
    Column('act_date_finish', Date),  # Finish date of the activity
    Column('act_date_work', Integer),   # Estimated work hours
    Column('act_date_remind', Date),  # Bring-forward date
    Column('act_status', String),     # Status of the activity
    Column('act_priority', String),   # Simple priority
    Column('act_type', String),       # sub-type for seaching
    Column('act_user', String),        # Currently assigned user
    Column('act_sub_type', String),    # sub-sub-type
    )

all_tables.append(table)

#-----------------------------------------------------------------------
# Node actions
#
# Any Node, particularly if it is a task, has a history of actions
# performed. This might include notes entered by the person responsible
# for action, and automatic items resulting from a staus change.

# nd_history
table = Table(
    'nd_history', meta,
    Column('nde_idx', String,
           primary_key=True),
    Column('hst_user', String,         # User initiating this item
           primary_key=True),
    Column('hst_text', String),        # The descriptive text
    Column('hst_time_entry', DateTime, # Date and time of entry
           primary_key=True),
    Column('hst_type', String,         # Indicate manual, auto or other
           primary_key=True),
    )

all_tables.append(table)

#-----------------------------------------------------------------------
# Roles for a node
#
# The Role is a way of linking people or groups to Nodes. All links
# should be to the contacts database. That is, all details of name and
# address are held elsewhere.
#
# This table is stretched to include all people related information,
# from those working on the node through to the client. A standard
# set of role names is required to allow functions to identify role types.

# nd_role_allocation
table = Table(
    'nd_role_allocation', meta,
    Column('nde_idx', String,
           primary_key=True),
    Column('rla_mnemonic', String), # The role this user has on this  node
    Column('rla_user', String,      # The user that has the role
           primary_key=True), 
    )

all_tables.append(table)

#-----------------------------------------------------------------------
# User Assignment
#
# Allocates functional roles for a user against a node. Answers the
# question - who is in charge, or who is currently working on this.
#
# Maps only a single user for now. This may change later (which is why
# it is a separate table.
#
# This does not carry permissions - see Role Allocation
#
#-----------------------------------------------------------------------

# nd_user_assignment
table = Table(
    'nd_user_assignment', meta,
    Column('nde_idx', String(), primary_key=True),
    Column('usa_user', String())
    )

all_tables.append(table)

#-----------------------------------------------------------------------
# attachements to nodes get stored in the file system. This table
# holds helpful meta data.
#
# base_location - the top level directory where the file is stored.
#
# other_location - information that can be used to find the directory
#         below the base_location. For example, this could be the node
#         nde_idx.
#
# file_name - the original file name (sans path).
#
# file_version - a version number for the file that allows a file of
#         the same name to be uploaded to the same directory.
#
#     The above 4 items provide a unique path to the file.
#
# description - Some text provided by the user.
#
# uploaded_by - The usernsme of the person uploading.
#
# content_type - the mime/type provided by the upload request.


table = Table(
    'nd_attachment', meta,
    Column('base_location', String, primary_key=True),
    Column('other_location', String, primary_key=True),
    Column('file_name', String, primary_key=True),
    Column('file_version', String, primary_key=True),
    Column('description', String),
    Column('uploaded_by', String),
    Column('content_type', String),
    Column('upload_time', DateTime())
    )

all_tables.append(table)

#-----------------------------------------------------------------------
# Tags, used for searching, are stored one tag at a time in a table.

table = Table(
    'nd_node_tag', meta,
    Column('nde_idx', String, primary_key=True),
    Column('nde_tag_text', String, primary_key=True),
    )

all_tables.append(table)

#-----------------------------------------------------------------------
# Subscribers to a node receive emails when the node content changes
# (depending on what goes into the history)

table = Table(
    'nd_node_subscriber', meta,
    Column('nde_idx', String, primary_key=True),
    Column('nde_subscriber_list', String, primary_key=True),
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
