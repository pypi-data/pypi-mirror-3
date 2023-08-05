# Name:      lokai/tool_box/tb_common/tests/test_dates.py
# Purpose:   Testing date formatting and arithmetic
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

import datetime
import lokai.tool_box.tb_common.dates as dates

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
    
    def test_t010( self ):
        """ test_t010: strtotime: conventional date formats
        """
        d = dates.strtotime( "2006-02-26 01:02" )
        self.assert_( isinstance( d, datetime.datetime ),
                      "#1 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 2006 and d.month == 2 and d.day == 26 ),
                      "#1 strtotime gets a date of %s"%str( d ) )
        #
        d = dates.strtotime( "30/03/2004" )
        self.assert_( isinstance( d, datetime.date ),
                      "#2 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 2004 and d.month == 3 and d.day == 30 ),
                      "#2 strtotime gets a date of %s"%str( d ) )
        #
        d = dates.strtotime( "199412150304" )
        self.assert_( isinstance( d, datetime.datetime ),
                      "#3 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 1994 and d.month == 12 and d.day == 15 ),
                      "#3 strtotime gets a date of %s"%str( d ) )
        #
        d = dates.strtotime( "040506" )
        self.assert_( isinstance( d, datetime.date ),
                      "#4 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 2006 and d.month == 5 and d.day == 4 ),
                      "#4 strtotime gets a date of %s"%str( d ) )

    #-------------------------------------------------------------------

    def test_t011( self ):
        """ test_t011: strtotime: some erroneous formats
        """
        self.assertRaises(  dates.ErrorInDateString,
                            dates.strtotime, "1867/6/8" )
        #
        self.assertRaises(  ValueError,
                            dates.strtotime, "20060132" )
        #
        self.assertRaises(  ValueError,
                            dates.strtotime, "20060229" )

    #-------------------------------------------------------------------

    def test_t012( self ):
        """ test_t012: strtotime: more date formats
        """
        # (bit strict, this first one - the day number must be 2 digits!)
        d = dates.strtotime( "Tue 04 July 2006" )
        self.assert_( isinstance( d, datetime.date ),
                      "#1 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 2006 and d.month == 7 and d.day == 4 ),
                      "#1 strtotime gets a date of %s"%str( d ) )
        #
        d = dates.strtotime( "Tue 03 Jun 05" )
        self.assert_( isinstance( d, datetime.date ),
                      "#2 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 2005 and d.month == 6 and d.day == 3 ),
                      "#2 strtotime gets a date of %s"%str( d ) )
        #
        d = dates.strtotime( "May 23 12:15:56 10 GMT" )
        self.assert_( isinstance( d, datetime.datetime ),
                      "#3 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 2010 and d.month == 5 and d.day == 23 ),
                      "#3 strtotime gets a date of %s"%str( d ) )

    #-------------------------------------------------------------------
        
    def test_t013( self ):
        """ test_t013: strtotime: inputs requiring no action
        """
        d = dates.strtotime( "Tue 04 July 2006" )
        x = dates.strtotime( d )
        self.assert_( isinstance( x, datetime.date ),
                      "#1 strtotime returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == d.year and x.month == d.month and
                        x.day == d.day ),
                      "#1 strtotime returns from datetime input: %s"%str( x ) )
        #
        d = dates.strtotime( "    " )
        self.assert_( d is None,
                      "#2 strtotime returns from empty input: %s: %s"%
                      ( str( d ), type( d ) ) )

    #-------------------------------------------------------------------

    def test_t014( self ):
        """ test_t014: strtotime: conventional date formats with seconds
        """
        d = dates.strtotime( "2006-02-26T01:02:45Z" )
        self.assert_( isinstance( d, datetime.date ),
                      "#1 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 2006 and d.month == 2 and
                        d.day == 26 and d.hour == 1 and
                        d.minute == 2 and d.second == 45 ),
                      "#1 strtotime gets a date of %s"%str( d ) )
        
        d = dates.strtotime( "2006-02-26T01:02:45" )
        self.assert_( isinstance( d, datetime.date ),
                      "#1 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 2006 and d.month == 2 and
                        d.day == 26 and d.hour == 1 and
                        d.minute == 2 and d.second == 45 ),
                      "#1 strtotime gets a date of %s"%str( d ) )
        
        d = dates.strtotime( "2006-02-26 01:02:45" )
        self.assert_( isinstance( d, datetime.date ),
                      "#1 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 2006 and d.month == 2 and
                        d.day == 26 and d.hour == 1 and
                        d.minute == 2 and d.second == 45 ),
                      "#1 strtotime gets a date of %s"%str( d ) )
        
        d = dates.strtotime( "2006-02-26 01:02:45Z" )
        self.assert_( isinstance( d, datetime.date ),
                      "#1 strtotime returns object of type %s"%str( type( d ) ) )
        self.assert_( ( d.year == 2006 and d.month == 2 and
                        d.day == 26 and d.hour == 1 and
                        d.minute == 2 and d.second == 45 ),
                      "#1 strtotime gets a date of %s"%str( d ) )

    #-------------------------------------------------------------------

    def test_t020( self ):
        """ test_t020: timetostr: selected formats
        """
        d = dates.strtotime( "1987-11-12T23:55:45Z" )
        op = dates.timetostr( d )
        self.assert_( op == '1987-11-12 23:55',
                      "#1 timtostr returns %s"%str( op ) )
        #
        op = dates.timetostr( d, 'iso' )
        self.assert_( op == '1987-11-12T23:55:45Z',
                      "#2 timtostr returns %s"%str( op ) )
        #
        op = dates.timetostr( d, 'iso-compact' )
        self.assert_( op == '19871112235545Z',
                      "#3 timtostr returns %s"%str( op ) )
        #
        op = dates.timetostr( d, 'compact' )
        self.assert_( op == '19871112235545',
                      "#4 timtostr returns %s"%str( op ) )
        #
        op = dates.timetostr( d, 'dmy' )
        self.assert_( op == '12/11/87',
                      "#5 timtostr returns %s"%str( op ) )

    #-------------------------------------------------------------------

    def test_t021(self):
        """ test_t021: timetostr: numeric time
        """
        op =  dates.timetostr(56789432.5, 'iso')
        self.assert_(isinstance(op, type('')),
                     "Returned item should be a string"
                     " - got %s"%type(op)
                     )
    
    #-------------------------------------------------------------------

    def test_t030( self ):
        """ test_t030: day differences
        """
        d = dates.strtotime( "1987-11-12T23:55:45Z" )
        x = dates.plus_days( d, 1 )
        self.assert_( isinstance( x, datetime.datetime ),
                      "#1 plus_days returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1987 and x.month == 11 and x.day == 13 ),
                      "#1 plus_days: returns %s"%str( x ) )
        #
        x = dates.plus_days( d, -1 )
        self.assert_( isinstance( x, datetime.datetime ),
                      "#2 plus_days returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1987 and x.month == 11 and x.day == 11 ),
                      "#2 plus_days: returns %s"%str( x ) )
        #
        x = dates.plus_days( d, -12 )
        self.assert_( isinstance( x, datetime.datetime ),
                      "#3 plus_days returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1987 and x.month == 10 and x.day == 31 ),
                      "#3 plus_days: returns %s"%str( x ) )
        #
        x = dates.plus_days( d, 19 )
        self.assert_( isinstance( x, datetime.datetime ),
                      "#4 plus_days returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1987 and x.month == 12 and x.day == 1 ),
                      "#4 plus_days: returns %s"%str( x ) )

    #-------------------------------------------------------------------

    def test_t031( self ):
        """ test_t031: yesterday - do not run near midnight!
        """
        d = dates.now(  )
        x = dates.yesterday(  )
        self.assert_( ( ( d.day == x.day+1 ) or
                        ( d.day == 1 and
                          ( ( d.month == x.month+1 ) or
                            ( d.month == 1 and x.month == 12 )
                            )
                          )
                        ),
                      "Yesterday is %s\n    Today is %s"%( str( x ), str( d ) ) )

    #-------------------------------------------------------------------

    def test_t_032( self ):
        """ test_t032: first of month
        """
        d = dates.strtotime( "1987-11-12T23:55:45Z" )
        x = dates.first_of_month( d )
        self.assert_( isinstance( x, datetime.date ),
                      "#1 first of month returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1987 and x.month == 11 and x.day == 1 ),
                      "#1 first of month returns %s"%str( x ) )

    #-------------------------------------------------------------------

    def test_t033( self ):
        """ test_t033: plus months - positive
        """
        d = dates.strtotime( "1987-11-12" )
        x = dates.plus_months( d, 1 )
        self.assert_( isinstance( x, datetime.date ),
                      "#1 plus months returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1987 and x.month == 12 and x.day == 12 ),
                      "#1 plus months returns %s"%str( x ) )
        #
        x = dates.plus_months( d, 2 )
        self.assert_( isinstance( x, datetime.date ),
                      "#2 plus months returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1988 and x.month == 1 and x.day == 12 ),
                      "#2 plus months returns %s"%str( x ) )
        #
        x = dates.plus_months( d, 14 )
        self.assert_( isinstance( x, datetime.date ),
                      "#3 plus months returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1989 and x.month == 1 and x.day == 12 ),
                      "#3 plus months returns %s"%str( x ) )
 
    #-------------------------------------------------------------------

    def test_t034( self ):
        """ test_t033: plus months - negative
        """
        d = dates.strtotime( "1987-11-12T23:55:45Z" )
        x = dates.plus_months( d, -1 )
        self.assert_( isinstance( x, datetime.date ),
                      "#1 plus months returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1987 and x.month == 10 and x.day == 12 ),
                      "#1 plus months returns %s"%str( x ) )
        #
        x = dates.plus_months( d, -11 )
        self.assert_( isinstance( x, datetime.date ),
                      "#2 plus months returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1986 and x.month == 12 and x.day == 12 ),
                      "#2 plus months returns %s"%str( x ) )
        #
        x = dates.plus_months( d, -24 )
        self.assert_( isinstance( x, datetime.date ),
                      "#3 plus months returns object of type %s"%str( type( x ) ) )
        self.assert_( ( x.year == 1985 and x.month == 11 and x.day == 12 ),
                      "#3 plus months returns %s"%str( x ) )

    def test_t035(self):
        """ test_t035: end of day
        """
        op = dates.timetostr(
            dates.end_of_day(
                datetime.date(2456, 10, 29)),
            'long'
            )
        self.assertEqual(op, '2456-10-29 23:59:59')
        #--------------------
        op = dates.timetostr(
            dates.end_of_day(
                datetime.datetime(2456, 10, 29, 1, 2, 3)),
            'long'
            )
        self.assertEqual(op, '2456-10-29 23:59:59')
        #--------------------
        op = dates.timetostr(
            dates.end_of_day(
                '2456-10-29 1:2:3'),
            'long'
            )
        self.assertEqual(op, '2456-10-29 23:59:59')
        
    #-------------------------------------------------------------------

    def test_t101(self):
        """ test_t101 - date_parse - Try basic date formats
        """
        self.assertEqual(dates.date_parse('2006-03-19'),
                         datetime.date(2006, 3, 19))
        self.assertEqual(dates.date_parse('20060319'),
                         datetime.date(2006, 3, 19))
        self.assertEqual(dates.date_parse('2006/03/19'),
                         datetime.date(2006, 3, 19))
        self.assertEqual(dates.date_parse('2006/03-19'),
                         datetime.date(2006, 3, 19))
        self.assertEqual(dates.date_parse('2006/0319'),
                         datetime.date(2006, 3, 19))
                
    def test_t102(self):
        """ test_t102 - date_parse - Try some offsets
        """
        self.assertEqual(dates.date_parse('2006-03-19-1d'),
                         datetime.date(2006, 3, 18))
        self.assertEqual(dates.date_parse('2006-03-19-19d'),
                         datetime.date(2006, 2, 28))
        self.assertEqual(dates.date_parse('2006-03-19-1m '),
                         datetime.date(2006, 2, 19))
        self.assertEqual(dates.date_parse('2006-03-19+1m '),
                         datetime.date(2006, 4, 19))
        self.assertEqual(dates.date_parse('2006-03-19-3m '),
                         datetime.date(2005, 12, 19))
        self.assertEqual(dates.date_parse('2006-03-19+12m '),
                         datetime.date(2007, 3, 19))
        self.assertEqual(dates.date_parse('2006-03-19+10y '),
                         datetime.date(2016, 3, 19))
        self.assertEqual(dates.date_parse('2006-03-19-10y '),
                         datetime.date(1996, 3, 19))

    def test_t103(self):
        """ test_t103 - date_parse - Try some more offsets
        """
        self.assertEqual(dates.date_parse('2006-03-19-24m'),
                         datetime.date(2004, 3, 19))
        self.assertEqual(dates.date_parse('2006-03-19-240m'),
                         datetime.date(1986, 3, 19))
        self.assertEqual(dates.date_parse('2006-03-19+240m'),
                         datetime.date(2026, 3, 19))
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
