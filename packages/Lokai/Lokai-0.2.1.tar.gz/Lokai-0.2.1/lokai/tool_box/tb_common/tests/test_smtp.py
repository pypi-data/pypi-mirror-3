# Name:      lokai/tool_box/tb_common/tests/test_smtp.py
# Purpose:   Test logging, including email
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

import os
import signal
import unittest
import logging
import StringIO
import email
import email.mime.text
import time
from subprocess import Popen
from lokai.tool_box.tb_common.tests.smtp_server import path_to_server

import lokai.tool_box.tb_common.configuration as config
from lokai.tool_box.tb_common.smtp import SmtpConnection

#-----------------------------------------------------------------------

cfg_text  = (
    "[all]\n"
    "smtp_host=localhost\n"
    "smtp_port=8025\n"
    "smtp_from_host=fred.com\n"
    #"smtp_debug=1\n"
    )

cfg_text2  = (
    "[all]\n"
    "smtp_host=red003.redholm.com\n"
    "smtp_port=25\n"
    "smtp_user=mike.sandford@redholm.com\n"
    "smtp_password=x4hatstand\n"
    "smtp_from_host=fred.com\n"
    )

#-----------------------------------------------------------------------

SMTP_CAPTURE = 'removable_mail_message_file'

def setup_module():

    global server_pid
    log_file = open('smtp.log', 'w')
    err_file = open('smtp.err', 'w')
    server_pid = Popen(['python',
                        path_to_server(),
                        '--target', SMTP_CAPTURE,
                        ],
                       stdout = log_file,
                       stderr = err_file).pid
    time.sleep(2)
    config.clear_global_config()
    config.set_global_config_file(StringIO.StringIO(cfg_text))

def teardown_module():
    os.kill(server_pid, signal.SIGKILL)
    pass

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        if os.path.exists(SMTP_CAPTURE):
            os.remove(SMTP_CAPTURE)

    def tearDown(self):
        pass

    def test_t001(self):
        """ test_t001 : Open an smtp connection """
        connection = SmtpConnection(config_section='all')
        self.assertEqual(connection.host, 'localhost')
        self.assertEqual(connection.port, '8025')
        self.assertEqual(connection.user, None)
        to_person = "someone@xyz.com"
        msg = email.mime.text.MIMEText("Arbitrary message")
        msg['Subject'] = "Arbitrary subject"
        msg['From'] = connection.make_from("noreply")
        msg['To'] = to_person
        connection.sendmail('noreply', [to_person], str(msg))
        msg = email.message_from_file(open(SMTP_CAPTURE))
        self.assertEqual(msg['From'], 'noreply@fred.com')
        self.assertEqual(msg['To'], to_person)
        self.assertEqual(msg.get_payload(),
                         'Arbitrary message\n')
    
#-----------------------------------------------------------------------

if __name__ == "__main__":

    import lokai.tool_box.tb_common.helpers as tbh
    options, test_set = tbh.options_for_publish()
    ### tbh.logging_for_publish(options)
    setup_module() 
    try:
        tbh.publish(options, test_set, TestObject)
    finally:
        teardown_module()
    
#-----------------------------------------------------------------------
