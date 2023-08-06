# Name:      lokai/tool_box/tb_common/tests/test_email_address_list.py
# Purpose:   Testing EmailAddressList object
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

import unittest
import sys

import logging

from lokai.tool_box.tb_common.email_address_list import EmailAddressList

#-----------------------------------------------------------------------

#-----------------------------------------------------------------------

def setup_module():
    pass

#-----------------------------------------------------------------------

class TestObject( unittest.TestCase ):

    def setUp( self ):
        pass
    
    #-------------------------------------------------------------------
    
    def tearDown( self ):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : Create the object and get back some results
        """
        emal = EmailAddressList('Person 1 <ap.one@base.com>,'
                                'Person 2 <ap.two@base.com>,'
                                'ano.ther@elsewhere.com')
        self.assertEqual(emal.as_list,
                         ['Person 1 <ap.one@base.com>',
                          'Person 2 <ap.two@base.com>',
                          'ano.ther@elsewhere.com'])
        self.assertEqual(emal.parsed,
                         [('Person 1', 'ap.one@base.com'),
                          ('Person 2', 'ap.two@base.com'),
                          ('', 'ano.ther@elsewhere.com')])

    def test_t002(self):
        """ test_t002 : empty object
        """
        emal = EmailAddressList()
        self.assertEqual(emal.as_list, [])
        self.assertEqual(emal.parsed, [])
        emal = EmailAddressList('')
        self.assertEqual(emal.as_list, [])
        self.assertEqual(emal.parsed, [])
        emal = EmailAddressList('   ')
        self.assertEqual(emal.as_list, [])
        self.assertEqual(emal.parsed, [])

    def test_t003(self):
        """ test_t003 : Some parsing checks
        """
        emal = EmailAddressList('"Person 1" <ap.one@base.com>,'
                                '"Person 2,3 & 4" <ap.two_plus@base.com>,'
                                'ano.ther@elsewhere.com')
        self.assertEqual(emal.as_list,
                         ['Person 1 <ap.one@base.com>',
                          '"Person 2,3 & 4" <ap.two_plus@base.com>',
                          'ano.ther@elsewhere.com'])
        self.assertEqual(emal.parsed,
                         [('Person 1', 'ap.one@base.com'),
                          ('Person 2,3 & 4', 'ap.two_plus@base.com'),
                          ('', 'ano.ther@elsewhere.com')])

    def test_t004(self):
        """ test_t004 : Add items to list
        """
        emal  = EmailAddressList()
        self.assertEqual(emal.as_list, [])
        self.assertEqual(emal.parsed, [])
        emal.append('"Person 1" <ap.one@base.com>')
        self.assertEqual(emal.as_list,
                         ['Person 1 <ap.one@base.com>'])
        self.assertEqual(emal.parsed,
                         [('Person 1', 'ap.one@base.com')])
        emal.append('"Person 2,3 & 4" <ap.two_plus@base.com>')
        self.assertEqual(emal.as_list,
                         ['Person 1 <ap.one@base.com>',
                          '"Person 2,3 & 4" <ap.two_plus@base.com>'])
        self.assertEqual(emal.parsed,
                         [('Person 1', 'ap.one@base.com'),
                          ('Person 2,3 & 4', 'ap.two_plus@base.com')])
        emal.append('ano.ther@elsewhere.com')
        self.assertEqual(emal.as_list,
                         ['Person 1 <ap.one@base.com>',
                          '"Person 2,3 & 4" <ap.two_plus@base.com>',
                          'ano.ther@elsewhere.com'])
        self.assertEqual(emal.parsed,
                         [('Person 1', 'ap.one@base.com'),
                          ('Person 2,3 & 4', 'ap.two_plus@base.com'),
                          ('', 'ano.ther@elsewhere.com')])
        
    def test_t005(self):
        """ test_t005 : Do not add duplicates
        """
        emal = EmailAddressList('Person 1 <ap.one@base.com>,'
                                'Person 2 <ap.two@base.com>,'
                                'ano.ther@elsewhere.com,'
                                'Person 1 <ap.one@base.com>,'
                                )
        self.assertEqual(emal.as_list,
                         ['Person 1 <ap.one@base.com>',
                          'Person 2 <ap.two@base.com>',
                          'ano.ther@elsewhere.com'])
        emal.append('Person 2 again <ap.two@base.com>')
        self.assertEqual(emal.as_list,
                         ['Person 1 <ap.one@base.com>',
                          'Person 2 <ap.two@base.com>',
                          'ano.ther@elsewhere.com'])

    def test_t006(self):
        """ test_t006 : Complain if not a useful address
        """
        try:
            emal = EmailAddressList('Person 1 <ap.one@base.com>,'
                                    'Person 2,'
                                    'ano.ther@elsewhere.com,')
            self.assert_(False) # Never get here
        except ValueError, e:
            self.assert_('Person 2' in str(e))
        
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
