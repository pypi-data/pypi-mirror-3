# Name:      lokai/tool_box/tb_common/dates.py
# Purpose:   Provides common date/time manipulation
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

"""
   Provides a set of date and datetime object generators that take
   string or date/datetime inputs and produce a date or datetime
   object. Particularly useful for interpreting a range of
   date/datetime string formats.
   
"""
#-----------------------------------------------------------------------
# Purpose : Provides common date/time manipulation helper functions
#
##    %a  	Locale's abbreviated weekday name.  	
##    %A 	Locale's full weekday name. 	
##    %b 	Locale's abbreviated month name. 	
##    %B 	Locale's full month name. 	
##    %c 	Locale's appropriate date and time representation. 	
##    %d 	Day of the month as a decimal number [01, 31]. 	
##    %H 	Hour (24-hour clock) as a decimal number [00, 23]. 	
##    %I 	Hour (12-hour clock) as a decimal number [01, 12]. 	
##    %j 	Day of the year as a decimal number [001, 366]. 	
##    %m 	Month as a decimal number [01, 12]. 	
##    %M 	Minute as a decimal number [00, 59]. 	
##    %p 	Locale's equivalent of either AM or PM.
##    %S 	Second as a decimal number [00, 61].
##    %U 	Week number of the year (Sunday as the first day of the week).
##              Given as a decimal number [00, 53]. All days in a new year
##              preceding the first Sunday are considered to be in week 0.
##    %w 	Weekday as a decimal number [0(Sunday), 6]. 	
##    %W 	Week number of the year (Monday as the first day of the week).
##              Given as a decimal number [00, 53]. All days in a new year
##              preceding the first Monday are considered to be in week 0.
##    %x 	Locale's appropriate date representation. 	
##    %X 	Locale's appropriate time representation. 	
##    %y 	Year without century as a decimal number [00, 99]. 	
##    %Y 	Year with century as a decimal number. 	
##    %Z 	Time zone name (no characters if no time zone exists). 	
##    %% 	A literal "%" character.
#-----------------------------------------------------------------------

import re
import datetime
        
#-----------------------------------------------------------------------

class DateError(Exception):
    """ General top level exception for this module"""
    pass

class ErrorInDateString(DateError):
    """ Specific error converting from a string"""
    pass

class InvalidDateObject(DateError):
    """ Specific error converting from a date object"""
    pass

#-----------------------------------------------------------------------

__all__ = [] # don't allow wildcards

#-----------------------------------------------------------------------

# (This is probably why date processing doesn't go public - so much
# depends on translation and localisation)

mnths = {
    'Jan':1,
    'Feb':2,
    'Mar':3,
    'Apr':4,
    'May':5,
    'June':6,
    'Jun':6,
    'July':7,
    'Jul':7,
    'Aug':8,
    'Sept':9,
    'Sep':9,
    'Oct':10,
    'Nov':11,
    'Dec':12}

output_formats = {
    'default'       :   "%Y-%m-%d %H:%M",
    'iso'           :   "%Y-%m-%dT%H:%M:%SZ",
    'iso-compact'   :   "%Y%m%d%H%M%SZ",
    'isodate'       :   "%Y-%m-%d",
    'compact'       :   "%Y%m%d%H%M%S",
    'compact-date'  :   "%Y%m%d",
    'dmy'           :   "%d/%m/%y",
    'dmyhm'         :   "%d/%m/%y %H:%M",
    'long'          :   "%Y-%m-%d %H:%M:%S",
    'jsdate'        :   "%a %d %b %Y",
    'jsmins'        :   "%a %d %b %Y %H:%M",
    'jsnoyear'      :   "%a %d %b",
    'jsshort'       :   "%a %d",
    'excel_csv'     :   "%d-%b-%y", }

DATE_FORM_ISO =     'iso'
DATE_FORM_ISO_COMPACT = 'iso-compact'
DATE_FORM_ISODATE = 'isodate'     
DATE_FORM_COMPACT = 'compact'       
DATE_FORM_COMPACT_DATE = 'compact-date' 
DATE_FORM_DMY = 'dmy'          
DATE_FORM_DMYHM = 'dmyhm'        
DATE_FORM_LONG = 'long'         
DATE_FORM_JSDATE = 'jsdate'       
DATE_FORM_JSMINS = 'jsmins'       
DATE_FORM_JSNOYEAR = 'jsnoyear'     
DATE_FORM_JSSHORT = 'jsshort'      
DATE_FORM_EXCEL_CSV = 'excel_csv'    

## YYYY-MM-DDTHH:MM:SSZ
## YYYY-M[M]-D[D] H[H]:M[M]
## YYYYMMDDHHMM[SS]
## YYYY-M[M]-D[D]
## YYYYMMDD
## Mon DD Jul[y] YY[YY]
## Jul[y] D[D] HH:MM:SS YY[YY] GMT
## YYYY/MM/DD
## YYYY/MM/DD HH:MM:SS
## D[D]/M[M]/YY[YY]
## DDMMYY
## DD-Jul[y]-YY
## DD-Jul[y]-YYYY
## YYYY-M[M]-D[D] H[H]:M[M]:S[S]
# Excel default output formats
## D[D]/M[M]/YY[YY] H[H]:M[M]:S[S]
date_patterns = (
    '^(\d{4,4})-(\d{2,2})-(\d{2,2})[T ](\d{2,2}):(\d{2,2}):(\d{2,2})Z?$'
    '|'
    '^(\d{4,4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2})$'
    '|'
    '^(\d{4,4})(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,4})$'
    # fix - should have above format with and without seconds
    '|'
    '^(\d{4,4})-(\d{1,2})-(\d{1,2})$'
    '|'
    '^(\d{4,4})(\d{2,2})(\d{2,2})$'
    '|'
    '^([A-Za-z]{3}) (\d{2}) ([A-Za-z]{3,4}) (\d{2,4})$'
    '|'
    '^([A-Za-z]{3,4}) (\d{1,2}) (\d{2}:\d{2}:\d{2}) (\d{2,4}) GMT$'
    '|'
    '^(\d{4,4})/(\d{2,2})/(\d{2,2})$'
    '|'
    '^(\d{4,4})/(\d{2,2})/(\d{2,2}) (\d{2,2}):(\d{2,2}):(\d{2,2})$'
    '|'
    '^(\d{1,2})/(\d{1,2})/(\d{2,4})$'
    '|'
    '^(\d{2,2})(\d{2,2})(\d{2,2})$'
    '|'
    '^(\d{2,2})-([A-Za-z]{3,4})-(\d{2,4})$'
    '|'
    '^(\d{4,4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})$' 
    '|'
    '^(\d{1,2})/(\d{1,2})/(\d{2,4}) (\d{1,2}):(\d{1,2}):(\d{1,2})$'
    '|'
    '^(\d{2,2})/(\d{2,2})/(\d{4,4}) (\d{2,2}):(\d{2,2})$'
    )
match_pattern = re.compile(date_patterns)

#-----------------------------------------------------------------------

def strtotime(string, force_time=None) :
    '''
    Return a datetime.datetime or datetime.date object from the passed string
    
    force_time can toggle datetime object type:
        True = datetime.datetime
        False = datetime.date (explicit False)
        (hours, mins, seconds set to 0 where applicable) 
        None = allow the string to define return object
    '''
    #
    #
    if string == None:
        return None
    if isinstance(string, (datetime.date, datetime.datetime, datetime.timedelta)):
        # assume no conversion needed
        return string
    #dst = 0 # assume UTC
    hh = 0 # Defaults for non HHMMSS formats
    mm = 0
    ss = 0 # generally we ignore seconds
    #
    # now convert the string
    source = string.strip()
    if len(source) == 0 : return None
    op = match_pattern.search(source)
    has_time = False
    if op :
        px = op.groups()
        if px[0] != None:
            ## YYYY-MM-DDTHH:MM:SSZ
            yy = int(px[0])
            mt = int(px[1])
            dd = int(px[2])
            hh = int(px[3])
            mm = int(px[4])
            ss = int(px[5])
            has_time = True
        elif px[6] != None:
            ## YYYY-M[M]-D[D] H[H]:M[M]
            yy = int(px[6])
            mt = int(px[7])
            dd = int(px[8])
            hh = int(px[9])
            mm = int(px[10])
            has_time = True
        elif px[11] != None:
            ## YYYYMMDDHHMM[SS]
            yy = int(px[11])
            mt = int(px[12])
            dd = int(px[13])
            hh = int(px[14])
            if len(px[15]) == 2:
                mm = int(px[15])
            else:
                mm = int(px[15][:2])
                ss = int(px[15][2:])
            has_time = True
        elif px[16] != None:
            ## YYYY-M[M]-D[D]
            yy = int(px[16])
            mt = int(px[17])
            dd = int(px[18])
        elif px[19] != None:
            ## YYYYMMDD
            yy = int(px[19])
            mt = int(px[20])
            dd = int(px[21])
        elif px[22] != None:
            ## Mon DD Jul[y] YY[YY]
            yy = int(px[25])
            mt = mnths[px[24]]
            dd = int(px[23])
        elif px[26] != None:
            ## Jul[y] D[D] HH:MM:SS YY[YY] GMT
            yy = int(px[29])
            mt = mnths[px[26]]
            dd = int(px[27])
            hh = int(px[28][0:2])
            mm = int(px[28][3:5])
            ss = int(px[28][6:8])
            has_time = True
        elif px[30] != None or px[33] != None:
            ## YYYY/MM/DD [HH24:MM:SS]
            pxnum = 30
            if px[33] != None:
                pxnum = 33
                hh = int(px[36])
                mm = int(px[37])
                ss = int(px[38])
                has_time = True
            yy = int(px[pxnum])
            mt = int(px[pxnum+1])
            dd = int(px[pxnum+2])
        elif px[39] != None:
            ## D[D]/M[M]/YY[YY]
            yy = int(px[41])
            mt = int(px[40])
            dd = int(px[39])
        elif px[42] != None:
            ## DDMMYY (must be 6 digits or would be seen as YYYYMMDD
            dd = int(px[42])
            mt = int(px[43])
            yy = int(px[44])
        elif px[45] != None:
            ## DD-MMM[M]-YY 
            dd = int(px[45])
            mt = mnths[px[46]]
            yy = int(px[47])
        elif px[48] != None:
            yy = int(px[48])
            mt = int(px[49])
            dd = int(px[50])
            hh = int(px[51])
            mm = int(px[52])
            ss = int(px[53])
            has_time = True
        elif px[54] != None:
            yy = int(px[56])
            mt = int(px[55])
            dd = int(px[54])
            hh = int(px[57])
            mm = int(px[58])
            ss = int(px[59])
            has_time = True
        elif px[60] != None:
            dd = int(px[60])
            mt = int(px[61])
            yy = int(px[62])
            hh = int(px[63])
            mm = int(px[64])
            has_time = True
        #-----------------------------------------
        if yy < 100:
            ## 2 digit year passed
            yy += 2000
        if yy < 1900:
            raise ValueError("Year must not be less than 1900") 
        if force_time == True:
            tx = datetime.datetime(yy, mt, dd, hh, mm, ss)
        elif force_time == False:
            # Explicit False
            tx = datetime.date(yy, mt, dd)
        elif has_time:
            tx = datetime.datetime(yy, mt, dd, hh, mm, ss)
        else:
            tx = datetime.date(yy, mt, dd)
        return tx
    else :
        raise ErrorInDateString, string

def reform(tx, i=None):
    """ convert any date string to a standard format
    """
    return timetostr(strtotime(tx), i)

def timetostr(var, i=None):
    """ Generate a string represetation of a date, datetime or float
    """
    if var != None and var != '':
        if isinstance(var, (str, unicode)):
            # still a string. reconvert anyway
            t = strtotime(var)
        elif isinstance(var, (int, float)):
            t = datetime.datetime.utcfromtimestamp(var)
        elif isinstance(var, (datetime.date, datetime.datetime)):
            t = var
        else:
            print var, type(var)
            raise InvalidDateObject, "%s: %s" % (str(var), type(var))
        if i in output_formats.keys():
            return t.strftime(output_formats[i])
        elif str(i).find('%') > -1:
            return t.strftime(i)
        else:
            return t.strftime(output_formats['default'])
    else:
        return ""

def now(tz_info=None):
    """ Datetime now. See datetime module for use of tz_info
    """
    return datetime.datetime.now(tz_info)

def utcnow():
    """ Return UTC time as a datetime object with empty tz data """
    return datetime.datetime.utcnow()

def yesterday():
    """ Datetime yesterday
    """    
    return plus_days(datetime.datetime.now(), -1)

def plus_days(curdate, numdays):
    """ Add a number of days to the given date/datetime
    """
    dd = strtotime(curdate)
    result = dd + datetime.timedelta(days = numdays)
    return result

def first_of_month(curdate):
    """ Set day = 1 for the given date/datetime
    """
    date_source = strtotime(curdate)
    return date_source.replace(day = 1)

def plus_months(curdate, num):
    """ Add a number of months to the given date/datetime
    """
    tgt = strtotime(curdate)
    end_month_from_zero = tgt.month + num -1
    year = tgt.year + int(end_month_from_zero/12)
    month = (end_month_from_zero)%12 + 1
    return tgt.replace(year=year, month=month)

def is_today(date):
    """ return result of comparing date with today
    """
    date_obj = strtotime(date)
    today_obj = now()
    return (date_obj.year == today_obj.year and
            date_obj.month == today_obj.month and
            date_obj.day == today_obj.day)

def end_of_day(date):
    """ return datetime with time set to 23:59:59
    """
    date_source = strtotime(date)
    return datetime.datetime.combine(date_source, datetime.time(23, 59, 59))

def force_date(date):
    """ Ensure that the given item is a date and not a date time.

        This done by truncating the value given and does not involve
        time zone conversion.
    """
    date_source = strtotime(date)
    if isinstance(date_source, datetime.datetime):
        return datetime.date(date_source.year,
                             date_source.month,
                             date_source.day)
    return date_source

#-----------------------------------------------------------------------

COMMAND_LINE_DATE_STRING = (
    "^(\d{4,4}|[Yy]{1,4})[/-]?(\d{1,2}|[Mm]{1,2})[/-]?(\d{2,4}|[Dd]{1,2})"
    "(?:([+-])(\d*)([YyMmDd]))?$"
    )
COMMAND_LINE_DATE_MATCH = re.compile(COMMAND_LINE_DATE_STRING)

def date_parse(given_string):
    """ Parse the given string to produce a date object.

        Dates only.

        String is in two parts:
            a date specification and
            an optional offset.

        Date specification can contain replacement characters. These
        are replaced by the equivalent value from the current date.

        Dates are year month day, delimted by '/', '-' or nothing at all.

        Years are 4 digits, months and days one or two digits.

        Thus: 2006/03/19, 20060319, 2006-03-19 are all the same.

        Warning: 2006319 gives you 2006-31-09, so the format without a
        delimite can lead to problems.

        Offsets are + or - followed by a number and a unit. The units
        are:

           d = days
           m = months
           y = years

        Thus:

           2006/3/1-1d takes 1 day from the 1st March to give 28 (29?)
              February

           2006/1/1+3m takes you to the 2nd quarter of 2006

        Substitution characters are:

           Y,y in the year position (1 to 4 allowed)
           M,m in the month position (1 or 2 allowed)
           D,d in the day position (1 or 2 allowed)

        Thus:

           ymd is today
           ym1 is the first of the current month
           y1225-1y is Christmas last year
           y/1/1 is the start of the current year

    """

    if given_string is None:
        return None
    if isinstance(given_string,
                  (datetime.date, datetime.datetime, datetime.timedelta)):
        # assume no conversion needed
        return given_string
    # now convert the string
    source = given_string.strip()
    if len(source) == 0 : return None
    op = COMMAND_LINE_DATE_MATCH.search(source)
    if op:
        now = datetime.date.today()
        this_year = now.year
        this_month = now.month
        this_day = now.day

        group_set = op.groups()
        #
        # Work out the basic date from the first three group items
        year_txt = group_set[0]
        month_txt = group_set[1]
        day_txt = group_set[2]
        if year_txt.lower()[0] == 'y':
            target_year = this_year
        else:
            try:
                target_year = int(year_txt)
            except ValueError:
                raise ErrorInDateString, given_string
        if month_txt.lower()[0] == 'm':
            target_month = this_month
        else:
            try:
                target_month = int(month_txt)
            except ValueError:
                raise ErrorInDateString, given_string
        if day_txt.lower()[0] == 'd':
            target_day = this_day
        else:
            try:
                target_day = int(day_txt)
            except ValueError:
                raise ErrorInDateString, given_string
        #
        # Set up a possible return
        result = datetime.date(target_year, target_month, target_day)
        #
        # Check if offset exists, and then process
        if group_set[3]:
            operation = group_set[3]
            try:
                offset = int(group_set[4])
            except ValueError:
                raise ErrorInDateString, given_string
            if operation == '-':
                offset = -offset
            step_size = group_set[5].lower()
            if step_size == 'y':
                result = result.replace(year=(target_year + offset))
            elif step_size == 'm':
                result = plus_months(result, offset)
            else:
                result = plus_days(result, offset)
        return result
    else:
        raise ErrorInDateString, given_string

#-----------------------------------------------------------------------
