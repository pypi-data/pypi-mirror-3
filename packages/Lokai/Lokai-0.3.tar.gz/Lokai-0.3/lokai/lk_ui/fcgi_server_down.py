#!/usr/bin/python
# Name:      lokai/lk_ui/fcgi_server_down.py
# Purpose:   Kill the server started by fcgi_server.py
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

""" Read the pid file for the server and issue a kill """

#-----------------------------------------------------------------------

import os
import signal

from lokai.lk_ui.fcgi_server_up import PID_FILE

#-----------------------------------------------------------------------

def main_():
    try:
        pidfile = open(PID_FILE)
        pidtext = pidfile.readline().strip()
        pidfile.close()
        pidvalue = int(pidtext)
        print "Closing fcgi process %d ... "%pidvalue,
        try:
            os.kill(pidvalue, signal.SIGKILL)
            print "Done"
        except OSError, e:
            print "Failed, %s"%str(e)
            return 1
        os.remove(PID_FILE)
    except :
        print "No pid file %s for fcgi server"%PID_FILE
        return 1
    return 0

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
