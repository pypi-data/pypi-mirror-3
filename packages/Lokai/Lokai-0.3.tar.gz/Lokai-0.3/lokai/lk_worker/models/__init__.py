# Name:      lokai/lk_worker/models/__init__.py
# Purpose:   Define things for nodes
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

""" Define data models and components for built in data items """

from lokai.tool_box.tb_database.orm_interface import OrmRegistry
from lokai.tool_box.tb_database.orm_base_object import (OrmBaseObject,
                                                  OrmSequencedObject)

__db_name__ = "nodes_db"
__ini_section__ = "lk_worker"

model = OrmRegistry(__ini_section__, __db_name__)

#-----------------------------------------------------------------------

class ndNode(OrmSequencedObject):
    
    seq_width       = 10
    seq_prefix      = None
    seq_column      = 'nde_idx'
    
    search_fields = ['nde_idx']

model.register(ndNode, "nd_node")

#-----------------------------------------------------------------------

class ndEdge(OrmBaseObject):
    
    search_fields = ['nde_child', 'nde_parent']

model.register(ndEdge, "nd_edge")

#-----------------------------------------------------------------------

class ndParent(OrmBaseObject):

    search_fields = ['nde_idx', 'nde_parent']

model.register(ndParent, "nd_parent")

#-----------------------------------------------------------------------
