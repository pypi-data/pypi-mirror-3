# Name:      lokai/lk_worker/tests/scripts/test_node_data.py
# Purpose:   Testing aspects of node data manipulation
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

from lokai.tool_box.tb_common.dates import strtotime
from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update

from lokai.lk_worker.models import (ndNode,
                                    ndEdge,
                                    ndParent,
                                    )

from lokai.lk_worker.nodes.graph import NodeFamily, make_link
from lokai.lk_worker.tests.helpers import (
    module_initialise,
    module_close,
    delete_table_content,
    same
    )

#-----------------------------------------------------------------------

setup_module = module_initialise
teardown_module = module_close

#-----------------------------------------------------------------------

def insert_some_data(name, this_date, parent_set=[]):
    node_detail = {'nde_date_modify' : this_date,
                   'nde_date_create' : this_date,
                   'nde_name'        : name
                   }
    node_set = insert_or_update(ndNode, node_detail)
    if len(node_set) > 0:
        node_obj = node_set[0]
        engine.session.flush()
        nde_idx =node_obj['nde_idx']
        #
        # Now the parents
        for p in parent_set:
            make_link(nde_idx, p)
    engine.session.commit()
    return nde_idx

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
        now = '2000-10-16 10:15'
        name = 'root node'
        insert_some_data(name, now)
        x = engine.session.query(ndNode).count()
        expect = 1
        self.assert_(x==expect, 
                     "Simple node fetch after first insert. "
                     "Expecting %d rows, got %d"%(expect, x))
        
        x = engine.session.query(ndNode).one()
        self.assert_(x.nde_name == name,
                     "First node insert name. ""Expecting %s, got %s"%(
                         name, x.nde_name))
        self.assert_(strtotime(x.nde_date_create) == strtotime(now),
                     "First node insert. ""Expecting %s, got %s"%(
                         strtotime(now), strtotime(x.nde_date_create)))
        nde_idx = x.nde_idx
        n1 = 'Inserted second'
        m1 = 'To be achild of the first'
        insert_some_data(n1, now, [nde_idx])
       
        x = engine.session.query(ndEdge).count()
        expect = 1
        self.assert_(x==expect, 
                     "Simple edge fetch after second insert. "
                     "Expecting %d rows, got %d"%(expect, x))
        x = engine.session.query(ndNode).filter(ndNode.nde_name==n1).count()
        expect = 1
        self.assert_(x==expect, 
                     "Simple node fetch after second insert. "
                     "Expecting %d rows, got %d"%(expect, x))
        x = engine.session.query(ndNode).filter(ndNode.nde_name==n1).one()
        expect = '0000000003'
        self.assert_(x.nde_idx==expect,
                     "Inserted second node. Expected idx %s, got %s"%(
                         expect, x.nde_idx))
        n1_idx = x.nde_idx
        x = engine.session.query(ndEdge).one()
        self.assert_(x.nde_parent==nde_idx,
                     "Inserted first child. "
                     "Expected parent %s, got %s"%(
                         nde_idx, x.nde_parent))
        self.assert_(x.nde_child==n1_idx,
                     "Inserted first child. "
                     "Expected child %s, got %s"%(
                         n1_idx, x.nde_child))
    def test_t002(self):
        """ test_t002 - confirm basic operation of NodeFamily
        """
        # Insert 3 potential parent nodes
        now = '2000-10-16 10:20'
        insert_some_data('n1', now)
        insert_some_data('n2', now)
        insert_some_data('n3', now)
        #
        # Find the idx values
        r_set = engine.session.query(ndNode).order_by(ndNode.nde_idx).all()
        p_idx_set = []
        p_nme_set = []
        for r in r_set:
            p_idx_set.append(r.nde_idx)
            p_nme_set.append(r.nde_name)
        #
        # Insert 3 potential children
        c_p_map = {'nx1' : p_idx_set,
                   'nx2' : p_idx_set[:2],
                   'nx3' : p_idx_set[:1]
            }
        insert_some_data('nx1', now, p_idx_set)
        insert_some_data('nx2', now, p_idx_set[:2])
        insert_some_data('nx3', now, p_idx_set[:1])
        #
        # Find some idx values
        r_set = engine.session.query(ndNode).filter(
            ndNode.nde_name.like('nx%')).order_by(
            ndNode.nde_idx).all()
        c_idx_set = []
        c_nme_set = []
        for r in r_set:
            c_idx_set.append(r.nde_idx)
            c_nme_set.append(r.nde_name)
        p_c_map = {'n1' : c_idx_set,
                   'n2' : c_idx_set[1:],
                   'n3' : c_idx_set[2:]
                   }
        #
        # nx1 has the most parents, and we choose to make the last one first
        nx1_f = NodeFamily(c_idx_set[c_nme_set.index('nx1')], c_p_map['nx1'][2])
        self.assert_(len(nx1_f.parents) == len(c_p_map['nx1']),
                     "nx1 - number of parents expected %s, got %s"%(
                         c_p_map['nx1'], nx1_f.parents))
        self.assert_(nx1_f.parents[0].nde_idx == c_p_map['nx1'][2],
                     "nx1 - principle parent expected %s, got %s"%( 
                         c_p_map['nx1'], nx1_f.parents[0].nde_idx))
        #
        # nx1 also has the most siblings, all to the right, but not so
        # many for the chosen parent
        self.assert_(len(nx1_f.siblings_left) == 0,
                     "nx1 - number of left siblings expected %s, got %s"%(
                         str(0), nx1_f.siblings_left))
        self.assert_(len(nx1_f.siblings_right) ==
                     len(p_c_map[p_nme_set[p_idx_set.index(nx1_f.parents[0].nde_idx)]])-1,
                     "nx1 - number of right siblings expected %s, got%s"%(
                         p_c_map[p_nme_set[p_idx_set.index(nx1_f.parents[0].nde_idx)]],
                         nx1_f.siblings_right))
        #
        # Look for many siblings, ignore parent because it should be
        # the one we expect anyway
        nx1_f = NodeFamily(c_idx_set[c_nme_set.index('nx1')])
        self.assert_(len(nx1_f.parents) == len(c_p_map['nx1']),
                     "nx1 - b - number of parents expected %s, got %s"%(
                         c_p_map['nx1'], nx1_f.parents))
        #
        # nx1 also has the most siblings, all to the right, but not so
        # many for the chosen parent
        self.assert_(len(nx1_f.siblings_left) == 0,
                     "nx1 - b - number of left siblings expected %s, got %s"%(
                         str(0), nx1_f.siblings_left))
        self.assert_(len(nx1_f.siblings_right) ==
                     len(
                         p_c_map[
                             p_nme_set[
                                 p_idx_set.index(nx1_f.parents[0].nde_idx)
                                 ]])-1,
                     "nx1 - b - number of right siblings expected %s, got%s"%(
                         p_c_map[
                             p_nme_set[
                                 p_idx_set.index(nx1_f.parents[0].nde_idx)
                                 ]],
                         nx1_f.siblings_right))

    def test_t003(self):
        """ test_t003 - confirm basic operation of NodeFamily - node <= None
        """
        # Insert 3 potential parent nodes
        now = '2000-10-16 10:25'
        insert_some_data('n1', now)
        insert_some_data('n2', now)
        insert_some_data('n3', now)
        #
        # Find the idx values
        r_set = engine.session.query(ndNode).order_by(ndNode.nde_idx).all()
        p_idx_set = []
        p_nme_set = []
        for r in r_set:
            p_idx_set.append(r.nde_idx)
            p_nme_set.append(r.nde_name)
        #
        # Insert 3 potential children
        c_p_map = {'nx1' : p_idx_set,
                   'nx2' : p_idx_set[:2],
                   'nx3' : p_idx_set[:1]
            }
        insert_some_data('nx1', now, p_idx_set)
        insert_some_data('nx2', now, p_idx_set[:2])
        insert_some_data('nx3', now, p_idx_set[:1])
        #
        # Find some idx values
        r_set = engine.session.query(ndNode).filter(
            ndNode.nde_name.like('nx%')).order_by(
            ndNode.nde_idx).all()
        c_idx_set = []
        c_nme_set = []
        for r in r_set:
            c_idx_set.append(r.nde_idx)
            c_nme_set.append(r.nde_name)
        p_c_map = {'n1' : c_idx_set,
                   'n2' : c_idx_set[1:],
                   'n3' : c_idx_set[2:]
                   }
        #
        # Find some siblings for a given parent
        n1_f = NodeFamily(parent=p_idx_set[0])
        self.assert_(len(n1_f.siblings_right) == 0,
                     "n1 - number of right siblings expected %s, got %s"%(
                         str(0), n1_f.siblings_right))
        self.assert_(len(n1_f.siblings_left) ==
                     len(p_c_map['n1']),
                     "n1 - number of left siblings expected %s, got%s"%(
                         p_c_map['n1'],
                         n1_f.siblings_left))
        self.assert_(same(n1_f.siblings_left, p_c_map['n1']),
                     "n1 - left siblings expected %s, got%s"%(
                         p_c_map['n1'],
                         n1_f.siblings_left))

    def test_t004(self):
        """ test_t004 - What happens when there is no parent
        """
        # Insert 3 nodes
        now = '2000-10-16 10:30'
        insert_some_data('n1', now)
        insert_some_data('n2', now)
        insert_some_data('n3', now)
        #
        r_set = engine.session.query(ndNode).order_by(ndNode.nde_idx).all()
        #
        # Use the first one
        nde_idx = r_set[0].nde_idx
        n_f = NodeFamily(node=nde_idx)
        self.assert_(len(n_f.parents) == 0,
                     "Parent set should be zero, got"%n_f.parents)

    def test_t005(self):
        """ test_t005 : Ordering of siblings
        """
        now = '2000-10-16 10:35'
        px1 = insert_some_data('p1', now)
        nx1 = insert_some_data('n1', now, [px1])
        nx2 = insert_some_data('n2', now, [px1])
        nx3 = insert_some_data('n3', now, [px1])

        # check children of px1 appear in order 1,2 3
        nfx = NodeFamily(parent=px1)
        self.assertEqual([x.nde_idx for x in nfx.siblings_left], [nx1, nx2, nx3, ])

        # put midle one to the end
        edg2 = engine.session.query(
            ndEdge
            ).filter(
            ndEdge.nde_child == nx2).one()
        edg2.nde_sequence = 300
        engine.session.add(edg2)
        engine.session.commit()
        nf2 = NodeFamily(parent=px1)
        self.assertEqual([x.nde_idx for x in nf2.siblings_left], [nx1, nx3, nx2, ])

        # Avoid possibility that the last one to appear is also the
        # last one actually changed by putting nx1 into the middle
        edg1 = engine.session.query(
            ndEdge
            ).filter(
            ndEdge.nde_child == nx1).one()
        edg1.nde_sequence = 200
        engine.session.add(edg1)
        engine.session.commit()
        nf1 = NodeFamily(parent=px1)
        self.assertEqual([x.nde_idx for x in nf1.siblings_left], [nx3, nx1, nx2, ])

        # Make nx2 the same as nx3 to resolve the secondary ordering
        # by idx
        edg3 = engine.session.query(
            ndEdge
            ).filter(
            ndEdge.nde_child == nx3).one()
        self.assertEqual(edg3.nde_sequence, 2)
        edg2 = engine.session.query(
            ndEdge
            ).filter(
            ndEdge.nde_child == nx2).one()
        
        edg2.nde_sequence = 2
        engine.session.add(edg2)
        engine.session.commit()
        nf2 = NodeFamily(parent=px1)
        self.assertEqual([x.nde_idx for x in nf2.siblings_left], [nx2, nx3, nx1, ])

        
        
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
