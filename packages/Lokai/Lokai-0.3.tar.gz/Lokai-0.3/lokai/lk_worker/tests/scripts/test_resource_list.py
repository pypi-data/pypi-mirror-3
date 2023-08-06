# Name:      lokai/lk_worker/tests/scripts/test_resource_list.py
# Purpose:   Test ResourceList object
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

from lokai.lk_worker.models.builtin_data_resources import ResourceList

#-----------------------------------------------------------------------

def setup_module():
    pass

def teardown_module():
    pass

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        pass
        
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 - Create an empty object and add to it
        """
        rl = ResourceList()
        self.assertEqual(len(rl), 0)
        rl['k1'] = 'k1v1'
        self.assertEqual(len(rl), 1)
        self.assert_(rl.contains('k1', 'k1v1'))
        rl['k2'] = 'k2v1'
        self.assertEqual(len(rl), 2)
        self.assert_(rl.contains('k1', 'k1v1'))
        self.assert_(rl.contains('k2', 'k2v1'))
        # Extend the values ni k1
        rl['k1'] = 'k1v2'
        self.assertEqual(len(rl), 2)
        self.assert_(rl.contains('k1', 'k1v1'))
        self.assert_(rl.contains('k1', 'k1v2'))
        self.assert_(rl.contains('k2', 'k2v1'))
        expected = [('k1', 'k1v1'), ('k1', 'k1v2'), ('k2', 'k2v1'),]
        i = 0
        for k, v in rl.iteritems():
            self.assertEqual((k, v), expected[i])
            i += 1
        expected = ['k1', 'k2']
        self.assertEqual(rl.keys(), expected)
        self.assert_(not rl.contains('k3', 'vvv'))
        self.assert_(not rl.contains('k1', 'vvv'))

    def test_t002(self):
        """ test_t001 - Initialise a resource list
        """
        given = [('k1', 'k1v1'), ('k2', 'k2v1'), ('k1', 'k1v2'),]
        rl = ResourceList(given)
        expected = [('k1', 'k1v1'), ('k1', 'k1v2'), ('k2', 'k2v1'),]
        i = 0
        for k, v in rl.iteritems():
            self.assertEqual((k, v), expected[i])
            i += 1

    def test_t003(self):
        """ test_t003 : Normalise a resource list
        """
        rl1 = ResourceList(
            [('k1', 'k1v1'),
             ('k2', 'remove'),
             ('k3', 'k3v1'),
             ('k1', 'remove'),
             ])
        rl2 = rl1.normalise()
        expected = [('k1', 'k1v1'), ('k3', 'k3v1'),]
        i = 0
        for k,v in rl2.iteritems():
            self.assertEqual((k, v), expected[i])
            i += 1
            
    def test_t004(self):
        """ test_t004 : Compare two resource lists
        """
        rl1 = ResourceList(
            [('k1', 'k1v1'),
             ('k2', 'k2v1'),
             ('k3', 'k3v1'),
             ('k1', 'k1v2'),
             ])
        rl2 = ResourceList(
            [('k2', 'k2v1'),
             ('k3', 'k3v2'),
             ('k1', 'k1v2'),
             ('k4', 'k4v1'),
             ])
        resp = rl1.compare(rl2)
        exp_same = [('k1', 'k1v2'), ('k2', 'k2v1'),]
        self.assertEqual(len(resp.both), 2)
        i = 0
        for k,v in resp.both.iteritems():
            self.assertEqual((k,v), exp_same[i])
            i += 1
        exp_self = [('k1', 'k1v1'),  ('k3', 'k3v1'),]
        self.assertEqual(len(resp.self), 2)
        i = 0
        for k,v in resp.self.iteritems():
            self.assertEqual((k,v), exp_self[i])
            i += 1
        exp_other = [('k3', 'k3v2'), ('k4', 'k4v1'),]
        self.assertEqual(len(resp.other), 2)
        i = 0
        for k,v in resp.other.iteritems():
            self.assertEqual((k,v), exp_other[i])
            i += 1

    def test_t005(self):
        """ test_t005 : Alternative initialisation
        """
        rl = ResourceList(
            {'k1': 'k1v1',
             'k2': ['k2v1', 'k2v2'],
             'k3': []
             }
            )
        expected = [('k2', 'k2v1'), ('k2', 'k2v2'), ('k1', 'k1v1'),]
        i = 0
        for k, v in rl.iteritems():
            self.assertEqual((k, v), expected[i])
            i += 1

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
