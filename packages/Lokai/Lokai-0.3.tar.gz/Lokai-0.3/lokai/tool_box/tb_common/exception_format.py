# Name:      lokai/tool_box/tb_common/exception_format.py
# Purpose:   Text versions of exception
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
import StringIO
import traceback

#-----------------------------------------------------------------------

def get_print_exc():
    """ Return a printable version of the traceback from the current
        error
    """
    buf = StringIO.StringIO()
    traceback.print_exc(file=buf)
    return buf.getvalue()

#-----------------------------------------------------------------------

def get_print_exc_plus(debug=False, showkeys=[]):
    """ Return a printable version of the traceback from the current
        error. followed by a listing of all the local variables in
        each frame.
    """
    ret = get_print_exc()
    if debug:
        if type(showkeys) != type([]):
            if type(showkeys) == type('str'):
                showkeys = [showkeys]
            else:
                showkeys = []
        tb = sys.exc_info()[2]
        stack = []
        while tb:
            stack.append(tb.tb_frame)
            tb = tb.tb_next
        for frame in stack:
            if (len(showkeys) == 0 or
                str(frame.f_code.co_name).find('Error') > -1):
                ret += "\nFrame %s in %s at line %s" % (
                            frame.f_code.co_name,
                            frame.f_code.co_filename,
                            frame.f_lineno)
            for key, value in frame.f_locals.iteritems():
                if len(showkeys) > 0 and not key in showkeys:
                    continue
                ret += "\n\t%20s = " % key
                # We have to be careful not to cause a new error in
                # our error printer! Calling str() on an unknown
                # object could cause an error we don't want.
                try:                   
                    ret += str(value)[0:200]
                except:
                    ret += "<ERROR WHILE PRINTING VALUE>"
    return ret

#-----------------------------------------------------------------------
