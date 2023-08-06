# Name:      lokai/lk_worker/tests/scripts/test_graph_functions.py
# Purpose:   Testing aspects of node graph manipulation
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

import sys
import unittest
import logging

from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_worker.models import (ndNode,
                                    ndEdge,
                                    ndParent,
                                    )

from lokai.lk_worker.nodes.graph import (make_link,
                                         make_unlink,
                                         top_trees,
                                         child_trees,
                                         )
from lokai.lk_worker import ndGraphCycle

from lokai.lk_worker.tests.helpers import (
    module_initialise,
    module_close,
    delete_table_content,
    insert_node_data,
    )

#-----------------------------------------------------------------------

setup_module = module_initialise
teardown_module = module_close

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        delete_table_content([ndNode,
                              ndEdge,
                              ndParent])

    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 - confirm that inserting data works
        """
        node_set = []
        now = '2000-10-16'
        name = 'root node'
        message = 'Inserted first'
        node_set.append(insert_node_data(name, now))
        node_set.append(insert_node_data('first child', now))
        x = engine.session.query(ndNode).count()
        expect = 2
        self.assert_(x==expect, 
                     "Simple node fetch after first inserts. "
                     "Expecting %d rows, got %d"%(expect, x))
        value_op = make_link(node_set[1], node_set[0], query_test=True)
        
        engine.session.commit()
        expect = '0000000003'
        for v1, v2 in value_op:
            self.assert_(v1 == expect,
                         "First link operation - expect node %s,"
                         " found %s"%(expect,v1))
        parent_op = engine.session.query(ndParent).all()
        self.assert_(len(parent_op) == 1,
                     "First link operation - total parent set length expected 1,"
                     " found %d"%len(parent_op))
        self.assert_(parent_op[0].nde_idx == expect,
                     "First link operation - expect parent set for %s"
                     " found %s"% (expect, parent_op[0].nde_idx))
        expect = '0000000002'
        self.assert_(parent_op[0].nde_parent == expect,
                     "First link operation - expect parent %s"
                     " found %s"% (expect, parent_op[0].nde_parent))
        this_edge = engine.session.query(
            ndEdge
            ).filter(
            ndEdge.nde_child == node_set[1]).one()
        self.assertEqual(this_edge.nde_sequence, 0)

    def test_t002(self):
        """ test_t002 - More complex link operations
        """
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        
        node_set.append(insert_node_data(idx_1, now))
        node_set.append(insert_node_data(idx_2, now))
        node_set.append(insert_node_data(idx_3, now))
        node_set.append(insert_node_data(idx_4, now))
        #
        # Link 2 and 3 under 1
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        
        engine.session.commit()
        #
        # Check that second link worked
        edge_set = engine.session.query(
            ndEdge
            ).filter(
            ndEdge.nde_child == idx_3).all()
        self.assertEqual(len(edge_set), 1,
                         "Second insert should produce 1 edge,"
                         " found %d"%len(edge_set))
        self.assertEqual(edge_set[0].nde_parent, idx_1,
                         "Second insert, parent expected %s,"
                         " found %s"%(idx_1, edge_set[0].nde_parent))
        parent_set =  engine.session.query(ndParent).filter(
            ndParent.nde_idx == idx_3).all()
        self.assertEqual(len(parent_set), 1,
                         "Second insert should produce 1 parent,"
                         " found %d"%len(parent_set))
        expect = idx_1
        self.assertEqual(parent_set[0].nde_parent, expect,
                         "Second insert, manifest parent expected %s,"
                         " found %s"%(expect, parent_set[0].nde_parent))
        #
        # Link 4 under 3
        make_link(node_set[3], node_set[2])
         
        engine.session.commit()
        parent_set =  engine.session.query(ndParent).filter(
            ndParent.nde_idx == idx_4).all()
        self.assertEqual(len(parent_set), 2,
                         "Third insert should produce 2 parents,"
                         " found %d"%len(parent_set))
        self.assert_(parent_set[0].nde_parent in [idx_1, idx_3],
                     "Third insert[0], manifest parent expected '...1' or '...3',"
                     " found %s"%parent_set[0].nde_parent)
        
        self.assert_(parent_set[1].nde_parent in [idx_1, idx_3],
                     "Third insert[1], manifest parent expected '...1' or '...3',"
                     " found %s"%parent_set[1].nde_parent)
        
        #
        # Link 4 under 2
        make_link(node_set[3], node_set[1])
         
        engine.session.commit()
        parent_set =  engine.session.query(ndParent).filter(
            ndParent.nde_idx == idx_4).all()
        self.assertEqual(len(parent_set), 3,
                         "Fourth insert should produce 3 parents,"
                         " found %d"%len(parent_set))
        self.assert_(parent_set[0].nde_parent in [idx_1,
                                                  idx_3,
                                                  idx_2],
                     "Third insert[0], manifest parent"
                     " expected '...1', '...2' or '...3',"
                     " found %s"%parent_set[0].nde_parent)
        
        self.assert_(parent_set[1].nde_parent in [idx_1,
                                                  idx_2,
                                                  idx_3],
                     "Third insert[1], manifest parent"
                     " expected '...1', '...2' or '...3',"
                     " found %s"%parent_set[1].nde_parent)

    def test_t003(self):
        """ test_t003 - test for cycles
        """
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        node_set.append(insert_node_data(idx_1, now))
        node_set.append(insert_node_data(idx_2, now))
        node_set.append(insert_node_data(idx_3, now))
        node_set.append(insert_node_data(idx_4, now))
        #
        # Link 2 and 3 under 1, and 4 under 3
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        make_link(node_set[3], node_set[2])
        
        engine.session.commit()
        #
        # Link 1 under 4 should produce a cycle
        # Check that a cyclic link is refused.
        self.assertRaises(ndGraphCycle,
                           make_link,
                           node_set[0],
                           node_set[3])

    def test_t004(self):
        """ test_t004 - unlink a node
        """
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        node_set.append(insert_node_data(idx_1, now))
        node_set.append(insert_node_data(idx_2, now))
        node_set.append(insert_node_data(idx_3, now))
        node_set.append(insert_node_data(idx_4, now))
        #
        # Link 2 and 3 under 1, and 4 under 3
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        make_link(node_set[3], node_set[2])
        
        engine.session.commit()
        #
        # Unlink 3, leaving two root trees
        make_unlink(node_set[2], node_set[0])

        engine.session.commit()
        parent_set = engine.session.query(ndParent).filter(
            ndParent.nde_idx == node_set[2]).all()
        self.assert_(len(parent_set) == 0,
                     "Unlink from single parent - expect zero parents"
                     " - found %d"%len(parent_set))
        
        parent_set = engine.session.query(ndParent).filter(
            ndParent.nde_idx == node_set[3]).all()

        self.assert_(len(parent_set) == 1,
                     "Unlink under single parent - expect 1 parent"
                     " - found %d"%len(parent_set))
        self.assert_(parent_set[0].nde_parent == node_set[2],
                     "Unlink under single parent - expect %s"
                     " - found %s"%(node_set[2],
                                    parent_set[0].nde_parent))

    def test_t005(self):
        """ test_t005 - Look for root nodes
        """
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        node_set.append(insert_node_data(idx_1, now))
        node_set.append(insert_node_data(idx_2, now))
        node_set.append(insert_node_data(idx_3, now))
        node_set.append(insert_node_data(idx_4, now))
        #
        # Link 2 and 3 under 1, and leave 4 open
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        
        engine.session.commit()

        root_set = top_trees()
        self.assert_(len(root_set) == 2,
                     "Root set, expect length 2"
                     " - found %d"%len(root_set))
        self.assert_(root_set[0] in [node_set[0], node_set[3]],
                     "Root set[0] expect 1 or 4"
                     " - found %s"%root_set[0])
        self.assert_(root_set[1] in [node_set[0], node_set[3]],
                     "Root set[0] expect 1 or 4"
                     " - found %s"%root_set[1])

    def test_t006(self):
        """ test_t006 - Look for child nodes
        """
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        node_set.append(insert_node_data(idx_1, now))
        node_set.append(insert_node_data(idx_2, now))
        node_set.append(insert_node_data(idx_3, now))
        node_set.append(insert_node_data(idx_4, now))
        #
        # Link 2 and 3 under 1, and 4 under 3
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        make_link(node_set[3], node_set[2])
        
        engine.session.commit()

        root_set = top_trees()
        self.assert_(len(root_set) == 1,
                     "Root set, expect length 1"
                     " - found %d"%len(root_set))
        self.assert_(root_set[0] in [node_set[0]],
                     "Root set[0] expect 1"
                     " - found %s"%root_set[0])
        child_set = child_trees(root_set)
        self.assert_(len(child_set) == 2,
                     "Number of children - expect 2"
                     " - find %d"%len(child_set))
        self.assert_(child_set[0] in [node_set[1], node_set[2]],
                     "Root set[0] expect 1 or 4"
                     " - find %s"%child_set[0])
        self.assert_(child_set[1] in [node_set[1], node_set[2]],
                     "Root set[0] expect 1 or 4"
                     " - find %s"%child_set[1])
        
    def test_t007(self):
        """ test_t007 - Look for child nodes with single string instead of list
        """
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        node_set.append(insert_node_data(idx_1, now))
        node_set.append(insert_node_data(idx_2, now))
        node_set.append(insert_node_data(idx_3, now))
        node_set.append(insert_node_data(idx_4, now))
        #
        # Link 2 and 3 under 1, and 4 under 3
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        make_link(node_set[3], node_set[2])
        
        engine.session.commit()

        child_set = child_trees(node_set[0])
        self.assert_(len(child_set) == 2,
                     "Number of children - expect 2"
                     " - find %d"%len(child_set))
        self.assert_(child_set[0] in [node_set[1], node_set[2]],
                     "Root set[0] expect 1 or 4"
                     " - find %s"%child_set[0])
        self.assert_(child_set[1] in [node_set[1], node_set[2]],
                     "Root set[0] expect 1 or 4"
                     " - find %s"%child_set[1])

    def test_t008(self):
        """ test_t008 : update nde_sequence value
        """
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        idx_5 = '0000000006'
        node_set.append(insert_node_data(idx_1, now))
        node_set.append(insert_node_data(idx_2, now))
        node_set.append(insert_node_data(idx_3, now))
        node_set.append(insert_node_data(idx_4, now))
        node_set.append(insert_node_data(idx_5, now))
        #
        # Link 2 and 3 under 1 in the same commit
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        
        engine.session.commit()
        edge_1 = engine.session.query(
            ndEdge
            ).filter(
            ndEdge.nde_child == node_set[1]).one()
        edge_2 = engine.session.query(
            ndEdge
            ).filter(
            ndEdge.nde_child == node_set[2]).one()
        # The two edges should have different nde_squence values
        self.assertEqual(edge_1.nde_sequence, 0)
        self.assertEqual(edge_2.nde_sequence, 1)
        #
        # Add a new node to this parent gets the next sequence value
        make_link(node_set[3], node_set[0])
        
        engine.session.commit()
        edge_3 = engine.session.query(
            ndEdge
            ).filter(
            ndEdge.nde_child == node_set[3]).one()
        self.assertEqual(edge_3.nde_sequence, 2)

        # Update a sequence value and try again
        edge_2.nde_sequence = 20
        engine.session.add(edge_2)
        engine.session.commit()
        
        make_link(node_set[4], node_set[0])
        engine.session.commit()
        edge_4 = engine.session.query(
            ndEdge
            ).filter(
            ndEdge.nde_child == node_set[4]).one()
        self.assertEqual(edge_4.nde_sequence, 21)

#-----------------------------------------------------------------------

if __name__ == "__main__":

    import lokai.tool_box.tb_common.helpers as tbh
    options, test_set = tbh.options_for_publish()
    tbh.logging_for_publish(options)
    setup_module() 
    try:
        tbh.publish(options, test_set, TestObject)
    finally:
        try:
            teardown_module()
        except NameError:
            pass    

#-----------------------------------------------------------------------
