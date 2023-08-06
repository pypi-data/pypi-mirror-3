# Name:      lokai/lk_worker/tests/scripts/test_search_functions.py
# Purpose:   Testing aspects of node graph searching
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

from lokai.lk_worker.models import (
    ndNode,
    ndEdge,
    ndParent,
    )

from lokai.lk_worker.nodes.graph import (
    make_link,
    top_trees,
    child_trees,
    )

from lokai.lk_worker.nodes.search import (
    search_down,
    search_here,
    search_children,
    find_in_path,
    search_up,
    search_nearest_up
    )
from lokai.lk_worker.nodes.search_filtered import search_filtered

from lokai.lk_worker.tests.helpers import (
    module_initialise,
    delete_table_content,
    insert_node_data,
    module_close
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

    def test_t101(self):
        """ test_t101 - test search down withouth depth first limit
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

        test_query = engine.session.query(ndNode).filter(
            ndNode.nde_name.like('%03'))
        search = search_down(test_query, depth_first = False)
        self.assert_(search == test_query,
                     "search down should make no changes. Expect %s"
                     " - found %s"%(str(test_query),
                                    str(search)))
        #
        # Search all trees in the forest
        search = search_down(test_query, top_trees(), depth_first = False)
        result = search.all()
        self.assert_(len(result) == 1,
                     "search down for '02' - expect 1 record"
                     " - found %d"%len(result))
        self.assert_(result[0].nde_idx == idx_2,
                     "search down for %%03"
                     " - found %s"%result[0].nde_idx)
        #
        # Search a tree that does not contain the answer
        search = search_down(test_query, [idx_3], depth_first = False)
        result = search.all()
        self.assert_(len(result) == 0,
                     "search down other tree for '02' - expect zero records"
                     " - found %d"%len(result))
        #
        # Confirm that we can select from something in tops
        search = search_down(test_query, [idx_2], depth_first = False)
        result = search.all()
        self.assert_(len(result) == 1,
                     "search down chopped tree for '02' - expect 1 record"
                     " - found %d"%len(result))
        self.assert_(result[0].nde_idx == idx_2,
                     "search down chopped tree for %%03"
                     " - found %s"%result[0].nde_idx)
        
    def test_t102(self):
        """ test_t102 - test search down with depth first limit
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
        # This query should find everything
        test_query = engine.session.query(ndNode).filter(
            ndNode.nde_name.like('%00%'))
        search = search_down(test_query, depth_first = False)
        result = search.all()
        self.assert_(len(result) == 4,
                     "search down for '00' - expect 4 records"
                     " - found %d"%len(result))
        #
        # Search all trees in the forest
        search = search_down(test_query, top_trees(), depth_first = False)
        result = search.all()
        self.assert_(len(result) == 4,
                     "search down for '00' - expect 4 records"
                     " - found %d"%len(result))
        #
        # Search all trees in the forest with depth first
        search = search_down(test_query, top_trees())
        result = search.all()
        self.assert_(len(result) == 1,
                     "search down depth limited for '00' - expect 1 records"
                     " - found %d"%len(result))

        self.assert_(result[0].nde_idx == idx_1,
                     "search down depth limited for 00 - expect 000000001"
                     " - found %s"%result[0].nde_idx)

    def test_t103(self):
        """ test_t103 - test search down with depth first limit
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
        # This query should find the bottom-most node
        test_query = engine.session.query(ndNode).filter(
            ndNode.nde_name.like('%05'))
        #
        # Search all trees in the forest
        search = search_down(test_query, top_trees())
        result = search.all()
        self.assert_(len(result) == 1,
                     "search down for '04' - expect 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0].nde_idx == node_set[3],
                     "search down for 04 - expect %s"
                     " - found %s"%(node_set[3],
                                    result[0].nde_idx))

        

    def test_t104(self):
        """ test_t104 - test search down with empty start list
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
        
        # This query should find the bottom-most node if there is a
        # starting point
        test_query = engine.session.query(ndNode).filter(
            ndNode.nde_name.like('%05'))
        search = search_down(test_query, []) # Empty candidate list
        result = search.all()
        self.assert_(len(result) == 0,
                     "search down for '04' - expect 0 records"
                     " - found %d"%len(result))
        
    def test_t105(self):
        """ test_t105 - test search down match at the top of the tree
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
        # Search should also match the top
        test_query = engine.session.query(ndNode).filter(
            ndNode.nde_name.like('%02'))
        search = search_down(test_query, [node_set[0]])
        result = search.all()
        self.assert_(len(result) == 1,
                     "search down for '01' - expect 1 records"
                     " - found %d"%len(result))
        self.assertEqual(result[0].nde_idx, idx_1)

    def test_t106(self):
        """ test_t106 - test search down to select two from parallel branches
        """
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        node_set.append(insert_node_data(idx_1, now,
                                         nde_client_reference='abc'))
        node_set.append(insert_node_data(idx_2, now,
                                         nde_client_reference='abcde'))
        node_set.append(insert_node_data(idx_3, now,
                                         nde_client_reference='abcde'))
        node_set.append(insert_node_data(idx_4, now,
                                         nde_client_reference='abcdefg'))
        #
        # Link 2 and 3 under 1, and 4 under 3
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        make_link(node_set[3], node_set[2])
        
        engine.session.commit()
        
        #
        # Search should also match the top
        test_query = engine.session.query(ndNode).filter(
            ndNode.nde_client_reference == 'abcde')
        search = search_down(test_query, [node_set[0]])
        result = search.all()
        self.assert_(len(result) == 2,
                     "search down for 'abcde' - expect 2 records"
                     " - found %d"%len(result))
        check_it = [node.nde_idx for node in result]
        self.assert_(idx_2 in check_it and idx_3 in check_it)

    def test_t107(self):
        """ test_t107 - test search down to select one from one branches
        """
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        node_set.append(insert_node_data(idx_1, now,
                                         nde_client_reference='abc'))
        node_set.append(insert_node_data(idx_2, now,
                                         nde_client_reference='abcde'))
        node_set.append(insert_node_data(idx_3, now,
                                         nde_client_reference='abcdex'))
        node_set.append(insert_node_data(idx_4, now,
                                         nde_client_reference='abcdex'))
        #
        # Link 2 and 3 under 1, and 4 under 3
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        make_link(node_set[3], node_set[2])
        
        engine.session.commit()
        
        #
        # Search should also match the top
        test_query = engine.session.query(ndNode).filter(
            ndNode.nde_client_reference == 'abcdex')
        search = search_down(test_query, [node_set[0]])
        result = search.all()
        self.assert_(len(result) == 1,
                     "search down for 'abcdex' - expect 1 record"
                     " - found %d"%len(result))
        check_it = [node.nde_idx for node in result]
        self.assert_(idx_3 in check_it)

    def test_t201(self):
        """ test_t201 - Look for child nodes
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
        child_set = child_trees(root_set)
        self.assert_(len(child_set) == 2,
                     "Child set, expect length 2"
                     " - found %d"%len(child_set))
        self.assert_(child_set[0] in [node_set[1], node_set[2]],
                     "Child set[0] expect 2 or 3"
                     " - found %s"%child_set[0])
        self.assert_(child_set[1] in [node_set[1], node_set[2]],
                     "Child set[0] expect 2 or 3"
                     " - found %s"%child_set[1])
        #
        child_set = child_trees([node_set[2]])
        self.assert_(len(child_set) == 1,
                     "Child set of 3, expect length 1"
                     " - found %d"%len(child_set))
        self.assert_(child_set[0] == node_set[3],
                     "Child set[0] expect %s"
                     " - found %s"%(node_set[3], child_set[0]))

    def test_t301(self):
        """ test_t301 - Search here
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

        search_query = engine.session.query(ndNode).filter(
            ndNode.nde_name == idx_3)

        search_set = search_here(search_query, [idx_2]).all()
        self.assert_(len(search_set) == 0,
                     "Search the wrong node, expect no return"
                     " - found %d"%len(search_set))
        
        search_set = search_here(search_query, [idx_3]).all()
        self.assert_(len(search_set) == 1,
                     "Search the right node, expect 1 return"
                     " - found %d"%len(search_set))
        
        search_set = search_here(search_query, []).all()
        self.assert_(len(search_set) == 0,
                     "Search empty candidates, expect 0 return"
                     " - found %d"%len(search_set))
        
    def test_t302(self):
        """ test_t302 - Search children
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

        search_query = engine.session.query(ndNode).filter(
            ndNode.nde_name == idx_3)

        search_set = search_children(search_query, [idx_1]).all()
        self.assert_(len(search_set) == 1,
                     "Search the right tree, expect one return"
                     " - found %d"%len(search_set))

    def test_t401(self):
        """ test_t401 - path search using rooted paths
        """
        #
        #
        #
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
        #--------------------
        result = find_in_path("/%03", [node_set[0]])
        self.assert_(len(result) == 0,
                     "Find single element - expected 0 records"
                     " - found %d"%len(result))
        #--------------------
        result = find_in_path("/*/%03", [node_set[0]])
        self.assert_(len(result) == 1,
                     "Find single child element - expected 1 record"
                     " - found %d"%len(result))
        self.assert_(result[0] == node_set[1],
                     "Find single child element - expected %s"
                     " - found %s"%(node_set[1],
                                    result[0]))
        #--------------------        
        result = find_in_path("/**/%05", [node_set[0]])
        self.assert_(len(result) == 1,
                     "Find single lower element - expected 1 record"
                     " - found %d"%len(result))
        self.assert_(result[0] == node_set[3],
                     "Find single lower element - expected %s"
                     " - found %s"%(node_set[3],
                                    result[0]))
        #--------------------
        result = find_in_path("/**/%04/*", [node_set[0]])
        self.assert_(len(result) == 1,
                     "Find single lower element children - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == node_set[3],
                     "Find single lower element children - expected %s"
                     " - found %s"%(node_set[3],
                                    result[0]))

        #--------------------        
        result = find_in_path("/**/%05/*", [node_set[0]])
        self.assert_(len(result) == 0,
                     "Find single lower element - expected 0 records"
                     " - found %d"%len(result))

    def test_t402(self):
        """ test_t402 - path search, wild-card tail
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
        #-------------------- 
        result = find_in_path("/*", [node_set[0]])
        self.assert_(len(result) == 1,
                     "Find children of root '*' - expected 1 record"
                     " - found %s"%str(result))
        self.assert_(result[0] == node_set[0],
                     "Find children of root '*' - expected %s"
                     " - found %s"%(node_set[0], result[0]))
        #-------------------- 
        result = find_in_path("/**", [node_set[0]])
        self.assert_(len(result) == 1,
                     "Find children of root '**' - expected 2 records"
                     " - found %s"%str(result))
        self.assert_(result[0] == node_set[0],
                     "Find children of root '**' - expected %s"
                     " - found %s"%(node_set[0], result[0]))
        #--------------------
        result = find_in_path("/*", [node_set[0], node_set[1]])
        self.assert_(len(result) == 2,
                     "Find all children, two nodes, one empty - expect 2 records"
                     " - find %s"%str(result))
        self.assert_(node_set[1] in result,
                     "Find all children, two nodes, one empty - expect %s"
                     " - find %s"%(node_set[1], str(result)))
        
    def test_t403(self):
        """ test_t403 - path search using non-rooted paths
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
        #--------------------
        result = find_in_path("%03", [node_set[0]])
        self.assert_(len(result) == 1,
                     "Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == idx_2,
                     "Find single element - expect idx_2"
                     " - find %s"%result)
        #--------------------
        result = find_in_path("**/%03", [node_set[0]])
        self.assert_(len(result) == 1,
                     "Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == idx_2,
                     "Find single element - expect idx_2"
                     " - find %s"%result)
        #--------------------
        # /**/foo should match /foo
        result = find_in_path("%02", [node_set[0]])
        self.assert_(len(result) == 1,
                     "Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == idx_1,
                     "Find single element - expect '0000000001"
                     " - find %s"%result)

    def test_t404(self):
        """ test_404 - path search with trailing '/'
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

        result = find_in_path("%03", [node_set[0]])
        self.assert_(len(result) == 1,
                     "Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == idx_2,
                     "Find single element - expect idx_2"
                     " - find %s"%result)
        #
        # and again with trailing '/'
        result = find_in_path("%03/", [node_set[0]])
        self.assert_(len(result) == 1,
                     "Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == idx_2,
                     "Find single element - expect idx_2"
                     " - find %s"%result)

    def test_t405(self):
        """ test_405 - a sequence of paths through the tree
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
        #--------------------
        result = find_in_path("%02", [node_set[0]])
        self.assert_(len(result) == 1,
                     "#1 - Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == node_set[0],
                     "#1 - Find single element - expect %s"
                     " - find %s"%(node_set[0], str(result)))
        #--------------------
        result = find_in_path("%02/%03", [node_set[0]])
        self.assert_(len(result) == 1,
                     "#2 - Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == node_set[1],
                     "#2 - Find single element - expect %s"
                     " - find %s"%(node_set[1], str(result)))
        #--------------------
        # But 0002 has no children
        result = find_in_path("%02/%03/*", [node_set[0]])
        self.assert_(len(result) == 0,
                     "#3 - Find single element - expected 0 records"
                     " - found %d"%len(result))
        #--------------------
        result = find_in_path("%02/%04", [node_set[0]])
        self.assert_(len(result) == 1,
                     "#4 - Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == node_set[2],
                     "#4 - Find single element - expect %s"
                     " - find %s"%(node_set[2], str(result)))
        #--------------------
        result = find_in_path("%02/%04/*", [node_set[0]])
        self.assert_(len(result) == 1,
                     "#5 - Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == node_set[3],
                     "#5 - Find single element - expect %s"
                     " - find %s"%(node_set[3], str(result)))
        
        #--------------------
        result = find_in_path("%02/*/%05", [node_set[0]])
        self.assert_(len(result) == 1,
                     "#6 - Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == node_set[3],
                     "#6 - Find single element - expect %s"
                     " - find %s"%(node_set[3], str(result)))
                #--------------------
        result = find_in_path("%02/**/%05", [node_set[0]])
        self.assert_(len(result) == 1,
                     "#7 - Find single element - expected 1 records"
                     " - found %d"%len(result))
        self.assert_(result[0] == node_set[3],
                     "#7 - Find single element - expect %s"
                     " - find %s"%(node_set[3], str(result)))
        
    def test_t050(self):
        """ test_t050 - basic search up
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

        qy = engine.session.query(ndNode).filter(
            ndNode.nde_name.like('%02')
            )
        result = search_up(qy, [node_set[3]]).all()
        self.assert_(len(result) == 1,
                     "Search up for %%02, expected length 1"
                     " - found %d"%len(result))
        self.assert_(result[0].nde_idx == node_set[0],
                     "Search up for %%02, expected idx %s"
                     " - found %s"%(node_set[0],
                                    result[0].nde_idx))
        
        qy = engine.session.query(ndNode).filter(
            ndNode.nde_name.like('%03')
            )
        result = search_up(qy, [node_set[3]]).all()
        self.assert_(len(result) == 0,
                     "Search up for %%03, expected length 0"
                     " - found %d"%len(result))

    def test_t500(self):
        """ test_t500 - use a path specification in search_filter
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

        qy = search_filtered({'name': '=%05'})
        result = qy.all()
        self.assert_(len(result) == 1,
                     "Fiter for path /**/%%05 - expect 1"
                     " - find %d"%len(result))
        self.assert_(result[0][0].nde_name == idx_4,
                     "Fiter for path /**/%%05 - expect idx_4"
                     " - find %s"%result[0][0].nde_name)
                     
    def test_t501(self):
        """ test_t501 - use a longer path specification in search_filter
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

        qy = search_filtered({'name': '=/%02/%04/%05'})
        result = qy.all()
        self.assert_(len(result) == 1,
                     "Fiter for path /%%02/%%04/%%05 - expect 1"
                     " - find %d"%len(result))
        self.assert_(result[0][0].nde_name == idx_4,
                     "Fiter for path /%%02/%%04/%%05 - expect idx_4"
                     " - find %s"%result[0][0].nde_name)

    def test_t502(self):
        """ test_t502 : Search for tags
        """
        print
        print "========================================"
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        node_set.append(insert_node_data(idx_1, now))
        node_set.append(insert_node_data(idx_2, now, tags=['tag_one', 'tag_two']))
        node_set.append(insert_node_data(idx_3, now))
        node_set.append(insert_node_data(idx_4, now, tags=['tag_one', 'tag_three']))
        #
        # Link 2 and 3 under 1, and 4 under 3
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        make_link(node_set[3], node_set[2])
        
        engine.session.commit()

        qy = search_filtered({'nd_tags': 'tag_one'})
        result = qy.all()
        self.assert_(len(result) == 2,
                     "Fiter for tag tag_one - expect 2"
                     " - find %d"%len(result))
        self.assert_(result[0][0].nde_name in [idx_4, idx_2],
                     "Fiter for tag tag_one - expect idx_4 or idx_2"
                     " - find %s"%result[0][0].nde_name)
        self.assert_(result[1][0].nde_name in [idx_4, idx_2],
                     "Fiter for path /%%02/%%04/%%05 - expect idx_2 or idx_4"
                     " - find %s"%result[1][0].nde_name)
        
    def test_t503(self):
        """ test_t503 : Search for tags under specific node
        """
        print
        print "========================================"
        node_set = []
        now = '2000-10-16'
        idx_1 = '0000000002'
        idx_2 = '0000000003'
        idx_3 = '0000000004'
        idx_4 = '0000000005'
        node_set.append(insert_node_data(idx_1, now))
        node_set.append(insert_node_data(idx_2, now, tags=['tag_one', 'tag_two']))
        node_set.append(insert_node_data(idx_3, now))
        node_set.append(insert_node_data(idx_4, now, tags=['tag_one', 'tag_three']))
        #
        # Link 2 and 3 under 1, and 4 under 3
        make_link(node_set[1], node_set[0])
        make_link(node_set[2], node_set[0])
        make_link(node_set[3], node_set[2])
        
        engine.session.commit()

        qy = search_filtered({'nd_node': idx_1,
                              'nd_tags': 'tag_one'})
        result = qy.all()
        self.assert_(len(result) == 2,
                     "Fiter for tag tag_one - expect 2"
                     " - find %d"%len(result))
        self.assert_(result[0][0].nde_name in [idx_4, idx_2],
                     "Fiter for tag tag_one - expect idx_4 or idx_2"
                     " - find %s"%result[0][0].nde_name)
        self.assert_(result[1][0].nde_name in [idx_4, idx_2],
                     "Fiter for path /%%02/%%04/%%05 - expect idx_2 or idx_4"
                     " - find %s"%result[1][0].nde_name)
        

    def test_t601(self):
        """ test_t601 : search_nearest_up
        """
        # Build an inverted tree

        #
        #              n7=t3  n8=t2                   n9=t3
        #                |      \----------\/-----------/       
        #    n3=t0     n4=t2              n5=t2                   n6=t0
        #      \----\/---/                  \-----------\/----------/
        #          n1=t0                              n2=t0
        #            \----------------\/----------------/
        #                           n0=t1

        idx_0 = '0000000000'
        idx_1 = '0000000001'
        idx_2 = '0000000002'
        idx_3 = '0000000003'
        idx_4 = '0000000004'
        idx_5 = '0000000005'
        idx_6 = '0000000006'
        idx_7 = '0000000007'
        idx_8 = '0000000008'
        idx_9 = '0000000009'
        now = '2000-10-16'
        node_set = [
            insert_node_data(idx_0, now, nde_type='t1'),
            insert_node_data(idx_1, now, nde_type='t0'),
            insert_node_data(idx_2, now, nde_type='t0'),
            insert_node_data(idx_3, now, nde_type='t0'),
            insert_node_data(idx_4, now, nde_type='t2'),
            insert_node_data(idx_5, now, nde_type='t2'),
            insert_node_data(idx_6, now, nde_type='t0'),
            insert_node_data(idx_7, now, nde_type='t3'),
            insert_node_data(idx_8, now, nde_type='t2'),
            insert_node_data(idx_9, now, nde_type='t3'),
            ]
        make_link(node_set[0], node_set[1])
        make_link(node_set[0], node_set[2])
        make_link(node_set[1], node_set[3])
        make_link(node_set[1], node_set[4])
        make_link(node_set[2], node_set[5])
        make_link(node_set[2], node_set[6])
        make_link(node_set[4], node_set[7])
        make_link(node_set[5], node_set[8])
        make_link(node_set[5], node_set[9])

        type_t0 = 't0'
        def try_t0(obj):
            return obj.nde_type == type_t0
        type_t1 = 't1'
        def try_t1(obj):
            return obj.nde_type == type_t1
        type_t2 = 't2'
        def try_t2(obj):
            return obj.nde_type == type_t2
        type_t3 = 't3'
        def try_t3(obj):
            return obj.nde_type == type_t3
        type_t9 = 't9'
        def try_t9(obj):
            return obj.nde_type == type_t9

        res = search_nearest_up(node_set[0], try_t1)
        self.assertEqual(len(res[0]), 1)
        self.assertEqual(res[1], 0)
        self.assertEqual(res[0].pop().nde_idx, node_set[0])

        res = search_nearest_up(node_set[0], try_t0)
        self.assertEqual(len(res[0]), 2)
        self.assertEqual(res[1], 1)
        self.assert_(res[0].pop().nde_idx in (node_set[1], node_set[2]))

        res = search_nearest_up(node_set[0], try_t2)
        self.assertEqual(len(res[0]), 2)
        self.assertEqual(res[1], 2)
        self.assert_(res[0].pop().nde_idx in (node_set[4], node_set[5]))

        res = search_nearest_up(node_set[0], try_t3)
        self.assertEqual(len(res[0]), 2)
        self.assertEqual(res[1], 3)
        self.assert_(res[0].pop().nde_idx in (node_set[7], node_set[9]))

        res = search_nearest_up(node_set[0], try_t9)
        self.assertEqual(len(res[0]), 0)

        
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
