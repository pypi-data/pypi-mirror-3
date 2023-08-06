# -*- coding: utf-8 -*-
# Name:      lokai/tool_box/tb_common/tests/test_notification.py
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
import time
from subprocess import Popen
from smtp_server import path_to_server
import email

import lokai.tool_box.tb_common.notification as notify

#-----------------------------------------------------------------------

SMTP_CAPTURE = 'removable_mail_message_file'
LOG_CAPTURE = 'removable_log_capture_file'

server_pid = None

#-----------------------------------------------------------------------

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

def teardown_module():
    os.kill(server_pid, signal.SIGKILL)
    pass

#-----------------------------------------------------------------------

class TestObject(unittest.TestCase):

    def setUp(self):
        if os.path.exists(LOG_CAPTURE):
            os.remove(LOG_CAPTURE)
        if os.path.exists(SMTP_CAPTURE):
            os.remove(SMTP_CAPTURE)
         
        logging.basicConfig(level=logging.CRITICAL)
        notify.setLogName('app_log')
        test_logger = logging.getLogger(notify.getLogName())
        test_logger.stats = {'CRITICAL': 0,
                             'ERROR': 0,
                             'WARNING': 0,
                             'INFO': 0,
                             'MONITOR': 0,
                             'DEBUG': 0}
        hdlr_set = test_logger.handlers[:]
        for hdlr in hdlr_set:
            test_logger.removeHandler(hdlr)
            
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : Log to a file with new root name
        """
        logging.getLogger(notify.getLogName()).setLevel(logging.WARNING)
        handler = logging.FileHandler(LOG_CAPTURE, mode='a')
        handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
        logging.getLogger(notify.getLogName()).addHandler(handler)
        notify.error('error message')
        logging.shutdown()
        lf = open(LOG_CAPTURE, 'r')
        self.assertEqual(lf.readline(),
                         'ERROR:app_log:error message\n')
        lf.close()

    def test_t002(self):
        """ test_t002 : Bulk Log to a file with new root name
        """
        logging.getLogger(notify.getLogName()).setLevel(logging.WARNING)
        handler = notify.BulkHandler(
            target = logging.FileHandler(LOG_CAPTURE, mode='a'),
            formatter = notify.BulkFormatter(
                linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n")
                )
            )
        handler.setFormatter(notify.BulkFormatter(
                linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n")))
        handler.target.setFormatter(notify.nullFormatter())
        logging.getLogger(notify.getLogName()).addHandler(handler)
        notify.error('error message')
        logging.shutdown()
        lf = open(LOG_CAPTURE, 'r')
        self.assertEqual(lf.readline(),
                         'ERROR:error message\n')
        lf.close()

    def test_t003(self):
        """ test_t003 : Log to email
        """
        logging.getLogger(notify.getLogName()).setLevel(logging.WARNING)

        mailer = notify.BulkHandler(
            target = notify.checkingSMTPHandler(
                ('localhost', 8025),
                'from@my_place',
                'to@your_place',
                'subject of email'),
            formatter = notify.BulkFormatter(
                linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n")
                )
            )
        logging.getLogger(notify.getLogName()).addHandler(mailer)

        notify.error('error message')
        logging.shutdown()
        msg = email.message_from_file(open(SMTP_CAPTURE))
        self.assertEqual(msg['From'], 'from@my_place')
        self.assertEqual(msg['To'], 'to@your_place')
        self.assertEqual(msg.get_payload(),
                         'ERROR:error message\n')

    def test_t004(self):
        """ test_t004 : Log to email - multiple messages
        """
        logging.getLogger(notify.getLogName()).setLevel(logging.WARNING)
        
        mailer = notify.BulkHandler(
            target = notify.checkingSMTPHandler(
                ('localhost', 8025),
                'from@my_place',
                'to@your_place',
                'subject of email'),
            formatter = notify.BulkFormatter(
                linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n")
                )
            )
        logging.getLogger(notify.getLogName()).addHandler(mailer)
    
        notify.error('error message')
        notify.warning('warning message')
        
        logging.shutdown()
        msg = email.message_from_file(open(SMTP_CAPTURE))
        self.assertEqual(msg.get_payload(),
                         'ERROR:error message\n'
                         'WARNING:warning message\n')

    def test_t005(self):
        """ test_t005 : Log to email - multiple messages - cutoff filter
        """
        logging.getLogger(notify.getLogName()).setLevel(logging.WARNING)
        
        mailer = notify.BulkHandler(
            target = notify.checkingSMTPHandler(
                ('localhost', 8025),
                'from@my_place',
                'to@your_place',
                'subject of email'),
            formatter = notify.BulkFormatter(
                linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n")
                )
            )
        mailer.addFilter(notify.FilterMax(logging.ERROR))
        logging.getLogger(notify.getLogName()).addHandler(mailer)
    
        notify.error('error message')
        notify.warning('warning message')
        logging.shutdown()
        msg = email.message_from_file(open(SMTP_CAPTURE))
        self.assertEqual(msg.get_payload(),
                         'WARNING:warning message\n')

    def test_t006(self):
        """ test_t006 : statistics
        """
        logging.getLogger(notify.getLogName()).setLevel(logging.DEBUG)
        
        mailer = notify.BulkHandler(
            target = notify.checkingSMTPHandler(
                ('localhost', 8025),
                'from@my_place',
                'to@your_place',
                'subject of email'),
            formatter = notify.BulkFormatter(
                linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n")
                )
            )
        mailer.addFilter(notify.FilterMax(logging.ERROR))
        logging.getLogger(notify.getLogName()).addHandler(mailer)
        notify.critical('critical message')
        notify.error('error message')
        notify.warning('warning message')
        notify.info('info message')

        stats = logging.getLogger(notify.getLogName()).stats
        self.assertEqual(stats['CRITICAL'], 1)
        self.assertEqual(stats['ERROR'], 1)
        self.assertEqual(stats['WARNING'], 1)
        self.assertEqual(stats['INFO'], 1)
        self.assertEqual(stats['MONITOR'], 0)
        notify.warning('another warning')
        self.assertEqual(stats['WARNING'], 2)
        notify.monitor('A monitoring message')
        self.assertEqual(stats['MONITOR'], 1)
        logging.shutdown()

    def test_t007(self):
        """ test_t007 : Set attributes in the handler
        """
        logging.getLogger(notify.getLogName()).setLevel(logging.INFO)
        
        mailer = notify.BulkHandler(
            target = notify.checkingSMTPHandler(
                ('localhost', 8025),
                'from@my_place',
                'to@your_place',
                'subject of email'),
            formatter = notify.BulkFormatter(
                linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n")
                )
            )
        this_logger = logging.getLogger(notify.getLogName())
        this_logger.addHandler(mailer)
            
        notify.error('error message')
        attr_first = this_logger.execute_one('getAttributes')
        self.assertEqual(attr_first['subject'], 'subject of email')

        attr_next = {'header': 'header text\n',
                     'footer': 'footer text',
                     'subject': 'subject text'}
        this_logger.execute_all('setAttributes', **attr_next)
        attr_resp = this_logger.execute_one('getAttributes')
        self.assertEqual(attr_resp ['header'], 'header text\n')
        self.assertEqual(attr_resp['footer'], 'footer text')
        self.assertEqual(attr_resp['subject'], 'subject text')
        
        logging.shutdown()
        msg = email.message_from_file(open(SMTP_CAPTURE))
        self.assertEqual(msg.get_payload(),
                         'header text\n'
                         'ERROR:error message\n'
                         'footer text\n')
        
        self.assertEqual(msg['subject'], 'subject text')

    def test_t008(self):
        """ test_t008 : Two handlers at once
        """
        this_logger = logging.getLogger(notify.getLogName())
        this_logger.setLevel(logging.INFO)

        mail_handler =  notify.BulkHandler()
        mail_target = notify.checkingSMTPHandler(
            ('localhost', 8025),
            'from@my_place',
            'to@your_place',
            'subject of email')
        mail_formatter =  notify.BulkFormatter(
            linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n"))
        mail_handler.setTarget(mail_target)
        mail_handler.setFormatter(mail_formatter)
        this_logger.addHandler(mail_handler)
        
        file_handler =  notify.BulkHandler()
        file_target = logging.FileHandler(LOG_CAPTURE, mode='a')
        file_formatter = notify.BulkFormatter(
            linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n"))
        file_handler.setTarget(file_target)
        file_handler.setFormatter(file_formatter)
        this_logger.addHandler(file_handler)
        
        notify.error('error message')
        notify.warning('warning message')
        
        logging.shutdown()
        msg = email.message_from_file(open(SMTP_CAPTURE))
        self.assertEqual(msg.get_payload(),
                         'ERROR:error message\n'
                         'WARNING:warning message\n')
        lf = open(LOG_CAPTURE, 'r')
        self.assertEqual(lf.readlines(),
                         ['ERROR:error message\n',
                         'WARNING:warning message\n',
                          '\n'])

    def test_t009(self):
        """ test_t009 : Formatted output using autoflush
        """
        logging.getLogger(notify.getLogName()).setLevel(logging.INFO)
        mailer = notify.BulkHandler(
            target = notify.checkingSMTPHandler(
                ('localhost', 8025),
                'from@my_place',
                'to@your_place',
                'subject of email'),
            formatter = notify.BulkFormatter(
                linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n")
                ),
            capacity = 0 # Force autoflush for every record
            )
        this_logger = logging.getLogger(notify.getLogName())
        this_logger.addHandler(mailer)
            
        attr_first = this_logger.execute_one('getAttributes')
        self.assertEqual(attr_first['subject'], 'subject of email')

        attr_next = {'header': 'header text\n',
                     'footer': 'footer text',
                     'subject': 'subject text'}
        this_logger.execute_all('setAttributes', **attr_next)
        attr_resp = this_logger.execute_one('getAttributes')
        self.assertEqual(attr_resp ['header'], 'header text\n')
        self.assertEqual(attr_resp['footer'], 'footer text')
        self.assertEqual(attr_resp['subject'], 'subject text')
        notify.error('error message')
        
        msg = email.message_from_file(open(SMTP_CAPTURE))
        self.assertEqual(msg.get_payload(),
                         'header text\n'
                         'ERROR:error message\n'
                         'footer text\n')
        logging.shutdown()

    def test_t010(self):
        """ test_t010 : dynamic to address on email
        """
        logging.getLogger(notify.getLogName()).setLevel(logging.WARNING)

        mailer = notify.BulkHandler(
            target = notify.checkingSMTPHandler(
                ('localhost', 8025),
                'from@my_place',
                'to@your_place',
                'subject of email'),
            formatter = notify.BulkFormatter(
                linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n")
                )
            )
        logging.getLogger(notify.getLogName()).addHandler(mailer)

        attrs = notify.getLogger().execute_one('getAttributes') # only one handler
        self.assert_('temp_toaddrs' not in attrs)
        notify.getLogger().execute_all('setAttributes',
                                       **{'temp_toaddrs':
                                          ['temp_address@example.com']})
        attrs = notify.getLogger().execute_one('getAttributes')
        self.assertEqual(attrs['temp_toaddrs'], ['temp_address@example.com'])
        notify.error('error message')
        logging.shutdown()
        msg = email.message_from_file(open(SMTP_CAPTURE))
        self.assertEqual(msg['From'], 'from@my_place')
        self.assertEqual(msg['To'], 'temp_address@example.com')
        self.assertEqual(msg.get_payload(),
                         'ERROR:error message\n')
        attrs = notify.getLogger().execute_one('getAttributes')
        self.assert_('temp_toaddrs' not in attrs)

    def test_t011(self):
        """ test_t011 : Line formatting using UnicodeToStrFormatter
        """
        my_record = logging.LogRecord('MAIN', 50, 'module', 1,
                                      'Message with no problem',
                                      [], None)
        my_formatter = notify.UnicodeToStrFormatter(fmt=(
                        "%(levelname)s:%(pathname)s:%(lineno)d:"
                        "%(message)s\n")
                    )
        op = my_formatter.format(my_record)
        self.assertEqual(op,
                         'CRITICAL:module:1:Message with no problem\n')
        my_record = logging.LogRecord('MAIN', 50, 'module', 1,
                                      u'Message with ümlaut',
                                      [], None)
        op = my_formatter.format(my_record)
        self.assertEqual(op,
                         'CRITICAL:module:1:Message with \\xfcmlaut\n')
        
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
