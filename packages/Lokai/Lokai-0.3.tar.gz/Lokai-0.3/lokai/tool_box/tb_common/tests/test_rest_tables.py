# -*- coding: utf-8 -*-
# Name:      lokai/tool_box/tb_common/tests/test_rest_tables.py
# Purpose:   Testing a table api for ReST output
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

from lokai.tool_box.tb_common.rest_support import (RstTable,
                                             RstTableEmpty,
                                             RstTableSpanClash)

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
        """ test_t001 - load up some type data
        """
        t = RstTable()
        self.assertRaises(RstTableEmpty, t.render)
        # One cell
        t.cell(1, 1, 'x')
        op = t.render()
        self.assertEqual(op,
                         "+-+\n"
                         "|x|\n"
                         "+-+"
                         )
        # One more on diagonal
        t.cell(2, 2, 'x')
        op = t.render()
        self.assertEqual(op,
                         "+-+-+\n"
                         "|x| |\n"
                         "+-+-+\n"
                         "| |x|\n"
                         "+-+-+"
                         )
        # Add a full heigh column on right
        t.span(3, 1, 3, 2)
        op = t.render()
        self.assertEqual(op,
                         "+-+-+-+\n"
                         "|x| | |\n"
                         "+-+-+ +\n"
                         "| |x| |\n"
                         "+-+-+-+"
                         )
        # Add another diagonal entry - wider this time
        t.cell(3, 3, 'yx')
        op = t.render()
        self.assertEqual(op,
                         "+-+-+--+\n"
                         "|x| |  |\n"
                         "+-+-+  +\n"
                         "| |x|  |\n"
                         "+-+-+--+\n"
                         "| | |yx|\n"
                         "+-+-+--+"
                         )
        # Merge the two bottom left cells
        t.span(1, 3, 2, 3)
        op = t.render()
        self.assertEqual(op,
                         "+-+-+--+\n"
                         "|x| |  |\n"
                         "+-+-+  +\n"
                         "| |x|  |\n"
                         "+-+-+--+\n"
                         "|   |yx|\n"
                         "+-+-+--+"
                         )
        # Create a span on the right and watch the line below fill in
        # automatically
        t.span(4,1,6,2)
        op = t.render()
        self.assertEqual(op,
                         "+-+-+--+-+-+-+\n"
                         "|x| |  |     |\n"
                         "+-+-+  +     +\n"
                         "| |x|  |     |\n"
                         "+-+-+--+-+-+-+\n"
                         "|   |yx| | | |\n"
                         "+-+-+--+-+-+-+"
                         )
        # After the event - add text to the top right and confirm
        # expansion.
        t.cell(4,1,'long value here')
        op = t.render()
        self.assertEqual(op,
                         "+-+-+--+---------------+-+-+\n"
                         "|x| |  |long value here    |\n"
                         "+-+-+  +                   +\n"
                         "| |x|  |                   |\n"
                         "+-+-+--+---------------+-+-+\n"
                         "|   |yx|               | | |\n"
                         "+-+-+--+---------------+-+-+"
                         )
        # Place multi-line text
        t.cell(4,3,
       ".. image:: /path/to/some/image.jpg\n"
       "   :height: 100px\n"
       "   :width: 150px")
        op = t.render()
        self.assertEqual(op,
                         "+-+-+--+----------------------------------+-+-+\n"
                         "|x| |  |long value here                       |\n"
                         "+-+-+  +                                      +\n"
                         "| |x|  |                                      |\n"
                         "+-+-+--+----------------------------------+-+-+\n"
                         "|   |yx|.. image:: /path/to/some/image.jpg| | |\n"
                         "|   |  |   :height: 100px                 | | |\n"
                         "|   |  |   :width: 150px                  | | |\n"
                         "+-+-+--+----------------------------------+-+-+"
                         )
        # An empty colum on the left
        t.span(-3,1,0,4)
        op = t.render()
        self.assertEqual(
            op,
            "+-+-+-+-+-+-+--+----------------------------------+-+-+\n"
            "|       |x| |  |long value here                       |\n"
            "+       +-+-+  +                                      +\n"
            "|       | |x|  |                                      |\n"
            "+       +-+-+--+----------------------------------+-+-+\n"
            "|       |   |yx|.. image:: /path/to/some/image.jpg| | |\n"
            "|       |   |  |   :height: 100px                 | | |\n"
            "|       |   |  |   :width: 150px                  | | |\n"
            "+-+-+-+-+-+-+--+----------------------------------+-+-+"
            )
        # Cannot overlap spans
        self.assertRaises(RstTableSpanClash, t.span, -1, 1, 2, 2)

    def test_t002(self):
        """ test_t002 : make span after cell content has been placed top left
        """
        t = RstTable()
        # One cell
        t.cell(1, 1, 'x')
        # Other cell
        t.cell(2, 2, 'y')
        op = t.render()
        self.assertEqual(op,
                         "+-+-+\n"
                         "|x| |\n"
                         "+-+-+\n"
                         "| |y|\n"
                         "+-+-+"
                         )
        t.span(1, 1, 1, 2)
        op = t.render()
        self.assertEqual(op,
                         "+-+-+\n"
                         "|x| |\n"
                         "+ +-+\n"
                         "| |y|\n"
                         "+-+-+"
                         )

    def test_t003(self):
        """ test_t003 : make span after cell content has been placed elsewhere
        """
        t = RstTable()
        # One cell
        t.cell(2, 1, 'x')
        # Other cell
        t.cell(1, 2, 'y')
        op = t.render()
        self.assertEqual(op,
                         "+-+-+\n"
                         "| |x|\n"
                         "+-+-+\n"
                         "|y| |\n"
                         "+-+-+"
                         )
        t.span(1, 1, 1, 2)
        op = t.render()
        self.assertEqual(op,
                         "+-+-+\n"
                         "| |x|\n"
                         "+ +-+\n"
                         "|y| |\n"
                         "+-+-+"
                         )

    def test_t004(self):
        """ test_t004 : make span after cell content has been placed everywhere
        """
        t = RstTable()
        t.cell(1, 1, 'w')
        t.cell(1, 2, 'x')
        t.cell(2, 1, 'y')
        t.cell(2, 2, 'z')
        op = t.render()
        self.assertEqual(op,
                         "+-+-+\n"
                         "|w|y|\n"
                         "+-+-+\n"
                         "|x|z|\n"
                         "+-+-+"
                         )
        t.span(1, 1, 1, 2)
        op = t.render()
        self.assertEqual(op,
                         "+-+-+\n"
                         "|w|y|\n"
                         "+ +-+\n"
                         "|x|z|\n"
                         "+-+-+"
                         )

    def test_t005(self):
        """ test_t005 : table within a table
        """
        t = RstTable()
        t.cell(1, 1, 'w')
        t.cell(1, 2, 'x')
        t.cell(2, 1, 'y')
        t.cell(2, 2, 'z')
        inner = t.render()
        u = RstTable()
        u.cell(2, 2, 'bottom left')
        u.cell(1, 1, inner)
        op = u.render()
        self.assertEqual(op,
                         "+-----+-----------+\n"
                         "|+-+-+|           |\n"
                         "||w|y||           |\n"
                         "|+-+-+|           |\n"
                         "||x|z||           |\n"
                         "|+-+-+|           |\n"
                         "+-----+-----------+\n"
                         "|     |bottom left|\n"
                         "+-----+-----------+"
                         )

    def test_t006(self):
        """ test_t006 : heading rows
        """
        t = RstTable()
        t.cell(1, 1, 'w')
        t.cell(1, 2, 'x')
        t.cell(2, 1, 'y')
        t.cell(2, 2, 'z')
        t.cell(1, 3, 'a')
        t.cell(1, 4, 'b')
        t.cell(2, 3, 'c')
        t.cell(2, 4, 'd')
        op = t.render()
        self.assertEqual(op,
                         "+-+-+\n"
                         "|w|y|\n"
                         "+-+-+\n"
                         "|x|z|\n"
                         "+-+-+\n"
                         "|a|c|\n"
                         "+-+-+\n"
                         "|b|d|\n"
                         "+-+-+"
                         )
        t.heading_row=2
        op = t.render()
        self.assertEqual(op,
                         "+-+-+\n"
                         "|w|y|\n"
                         "+-+-+\n"
                         "|x|z|\n"
                         "+=+=+\n"
                         "|a|c|\n"
                         "+-+-+\n"
                         "|b|d|\n"
                         "+-+-+"
                         )
        
    def test_t007(self):
        """ test_t007 : Use None as cell content
        """
        t = RstTable()
        self.assertRaises(RstTableEmpty, t.render)
        # One cell
        t.cell(1, 1, 'x')
        op = t.render()
        self.assertEqual(op,
                         "+-+\n"
                         "|x|\n"
                         "+-+"
                         )
        # One None on diagonal
        t.cell(2, 2, None)
        op = t.render()
        self.assertEqual(op,
                         "+-+-+\n"
                         "|x| |\n"
                         "+-+-+\n"
                         "+-+-+"
                         )

    def test_t008(self):
        """ test_t008 : Unicode matters
        """
        t = RstTable()
        self.assertRaises(RstTableEmpty, t.render)
        # One cell
        t.cell(1, 1, u'á')
        op = t.render()
        self.assertEqual(op,
                         u"+-+\n"
                         u"|á|\n"
                         u"+-+"
                         )
        # One None on diagonal
        t.cell(2, 2, None)
        op = t.render()
        self.assertEqual(op,
                         u"+-+-+\n"
                         u"|á| |\n"
                         u"+-+-+\n"
                         u"+-+-+"
                         )
        # Extend the 1st colum width (to force some extra spaces
        t.cell(1, 2, "longer")
        op = t.render()
        self.assertEqual(op,
                         u"+------+-+\n"
                         u"|á     | |\n"
                         u"+------+-+\n"
                         u"|longer| |\n"
                         u"+------+-+"
                         )

    def test_t009(self):
        """ test_t009 : Encoding of inputs
        """
        t = RstTable()
        self.assertRaises(RstTableEmpty, t.render)
        # One cell
        content = u'á'
        t.cell(1, 1, content)
        op = t.render()
        self.assertEqual(op,
                         u"+-+\n"
                         u"|á|\n"
                         u"+-+"
                         )
        # One None on diagonal
        t.cell(2, 2, None)
        op = t.render()
        self.assertEqual(op,
                         u"+-+-+\n"
                         u"|á| |\n"
                         u"+-+-+\n"
                         u"+-+-+"
                         )
        # Extend the 1st colum width (to force some extra spaces
        t.cell(1, 2, "longer")
        op = t.render()
        self.assertEqual(op,
                         u"+------+-+\n"
                         u"|á     | |\n"
                         u"+------+-+\n"
                         u"|longer| |\n"
                         u"+------+-+"
                         )
        
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
