# Name:      lokai/lk_worker/tests/scripts/test_subscribers.py
# Purpose:   Test subscriber extension code
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
import os
import signal
import StringIO
from subprocess import Popen
import time
import email

from werkzeug import Client, BaseResponse
from BeautifulSoup import BeautifulSoup

from lokai.tool_box.tb_database.orm_interface import engine

from lokai.tool_box.tb_common.tests.smtp_server import path_to_server
import lokai.tool_box.tb_common.configuration as config

from lokai.lk_worker.tests.structure_helper import make_initial_nodes_and_users
from lokai.lk_worker.tests.helpers import (
    module_ui_initialise,
    module_close,
    delete_table_content,
    delete_worker_table_content,
    )

from lokai.lk_worker.nodes.search import find_in_path
from lokai.lk_worker.nodes.data_interface import (get_node_dataset,
                                            put_node_dataset)

from lokai.lk_worker.tests.ui_helper import (
    basic_login,
    delete_user_table_content,
    pack,
    check_errors,
    )

from lokai.lk_worker.models.builtin_data_subscribers import(
    ndNodeSubscriber,
    PiSubscriberData,
    )
from lokai.lk_worker.models.builtin_data_activity import (get_subscribers,
                                                          HistoryStore,
                                                          ndHistory,
                                                          )

#-----------------------------------------------------------------------

cfg_text  = (
    "[all]\n"
    "smtp_host=localhost\n"
    "smtp_port=8025\n"
    "smtp_from_host=fred.com\n"
    #"smtp_debug=1\n"
    )

#-----------------------------------------------------------------------

SMTP_CAPTURE = 'removable_mail_message_file'

def setup_module():
    #
    # Start an email server
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
    module_ui_initialise()
    #
    # Add in the smtp details
    config.get_global_config().extend(StringIO.StringIO(cfg_text))

def teardown_module():
    os.kill(server_pid, signal.SIGKILL)
    module_close()

#-----------------------------------------------------------------------
class TestObject(unittest.TestCase):

    def setUp(self):
        delete_worker_table_content()
        delete_user_table_content()
        make_initial_nodes_and_users()
        if os.path.exists('lokai_ui.log'):
            os.remove('lokai_ui.log')
        
    #-------------------------------------------------------------------
    
    def tearDown(self):
        pass

    #-------------------------------------------------------------------

    def test_t001(self):
        """ test_t001 : Store subscriber data directly
        """
        extn = PiSubscriberData()
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        extn.nd_write_data_extend({'nd_node': {'nde_idx': nde_idx},
                               'nd_node_subscriber': {'nde_subscriber_list':
                                                      'a@b.com, c@d.com'}
                                   })
        engine.session.commit()
        subs_set = engine.session.query(ndNodeSubscriber).filter(
            ndNodeSubscriber.nde_idx == nde_idx).all()
        self.assertEqual(len(subs_set), 1)
        self.assertEqual(subs_set[0].nde_subscriber_list, 'a@b.com, c@d.com')

    def test_t002(self):
        """ test_t002 : store and retrieve subscriber data
        """
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        put_node_dataset({'nd_node': {'nde_idx': nde_idx},
                                   'nd_node_subscriber': {'nde_subscriber_list':
                                                          'a@b.com, c@d.com'}
                                   })
        engine.session.commit()
        res_obj = get_node_dataset(nde_idx)
        self.assertEqual(res_obj['nd_node_subscriber']['nde_subscriber_list'],
                         'a@b.com, c@d.com')

    def test_t003(self):
        """ test_t003 : Find parental subscribers.
        """
        root_idx = find_in_path(['', 'root'])[0]
        #
        # Add subscribers to a high level node
        put_node_dataset({'nd_node': {'nde_idx': root_idx},
                                   'nd_node_subscriber': {'nde_subscriber_list':
                                                          'a@b.com, c@d.com'}
                                   })
        engine.session.commit()
        nde_idx = find_in_path(['', 'root', 'Lokai', 'product1'])[0]
        subs_list = get_subscribers(nde_idx)
        self.assertEqual(len(subs_list), 2)
        self.assert_('a@b.com' in subs_list)
        self.assert_('c@d.com' in subs_list)
        #
        # Add subscribers to an intermediate node (with a duplicate)
        nxt_idx = find_in_path(['', 'root', 'Lokai'])[0]
        put_node_dataset({'nd_node': {'nde_idx': nxt_idx},
                                   'nd_node_subscriber': {'nde_subscriber_list':
                                                          'e@f.com, c@d.com'}
                                   })
        engine.session.commit()
        subs_list = get_subscribers(nde_idx)
        self.assertEqual(len(subs_list), 3)
        self.assert_('a@b.com' in subs_list)
        self.assert_('c@d.com' in subs_list)
        self.assert_('e@f.com' in subs_list)
        #
        # Add subscribers to self
        put_node_dataset({'nd_node': {'nde_idx': nde_idx},
                                   'nd_node_subscriber': {'nde_subscriber_list':
                                                          'e@f.com, g@h.com'}
                                   })
        engine.session.commit()
        subs_list = get_subscribers(nde_idx)
        self.assertEqual(len(subs_list), 4)
        self.assert_('a@b.com' in subs_list)
        self.assert_('c@d.com' in subs_list)
        self.assert_('e@f.com' in subs_list)
        self.assert_('g@h.com' in subs_list)

    def test_t004(self):
        """ test_t004 : Try the UI
        """
        nde_idx = find_in_path(['', 'root', 'Lokai'])[0]
        put_node_dataset({'nd_node': {'nde_idx': nde_idx},
                                   'nd_node_subscriber': {'nde_subscriber_list':
                                                          'e@f.com, c@d.com'}
                                   })
        engine.session.commit()
        source = basic_login('fred_0', 'useless', 'Fred Manager')
        res = source.get(str('/pages/%s/edit'%nde_idx))
        self.assertEqual(res.status_code, 200)
        html = BeautifulSoup(pack(res))
        field_set = html.findAll(
            attrs={'name': 'detail___notification_subscribers___nd_node_subscriber'})
        self.assertEqual(len(field_set), 1)
        self.assertEqual(field_set[0]['value'],
                         'e@f.com, c@d.com')      
        query_set = {'detail___node_edit___nde_name': 'Lokai',
                     'detail___node_edit___node_type': 'generic',
                     'detail___notification_subscribers___nd_node_subscriber': 'fred_2, e@f.com'}
        res = source.post('/pages/%s/edit'%nde_idx, data=query_set,
                          follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        html = BeautifulSoup(pack(res))
        self.assertEqual(check_errors(html), [])
        field_set = html.findAll(
            attrs={'name': 'detail___notification_subscribers___nd_node_subscriber'})
        self.assertEqual(len(field_set), 1)
        subs_text = field_set[0]['value']
        subs_list = subs_text.split(',')
        subs_list = [x.strip() for x in subs_list]
        self.assertEqual(len(subs_list), 2)
        self.assert_('e@f.com' in subs_list)
        self.assert_('fred_2@home.com' in subs_list)      

    def test_t005(self):
        """ test_t005 : Try the UI with user with no email
        """
        nde_idx = find_in_path(['', 'root', 'Lokai'])[0]
        put_node_dataset({'nd_node': {'nde_idx': nde_idx},
                                   'nd_node_subscriber': {'nde_subscriber_list':
                                                          'e@f.com, c@d.com'}
                                   })
        engine.session.commit()
        source = basic_login('fred_0', 'useless', 'Fred Manager')
        res = source.get(str('/pages/%s/edit'%nde_idx))
        self.assertEqual(res.status_code, 200)
        html = BeautifulSoup(pack(res))
        field_set = html.findAll(
            attrs={'name': 'detail___notification_subscribers___nd_node_subscriber'})
        self.assertEqual(len(field_set), 1)
        self.assertEqual(field_set[0]['value'],
                         'e@f.com, c@d.com')      
        query_set = {'detail___node_edit___nde_name': 'Lokai',
                     'detail___node_edit___node_type': 'generic',
                     'detail___notification_subscribers___nd_node_subscriber': 'fred_1, e@f.com'}
        res = source.post('/pages/%s/edit'%nde_idx, data=query_set,
                          follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        html = BeautifulSoup(pack(res))
        self.assertEqual(check_errors(html), ['No email found for fred_1'])

    def test_t006(self):
        """ test_t006 : Link with History
        """
        nde_idx = find_in_path(['', 'root', 'Lokai'])[0]
        put_node_dataset({'nd_node': {'nde_idx': nde_idx},
                                   'nd_node_subscriber': {'nde_subscriber_list':
                                                          'e@f.com, c@d.com'}
                                   })
        engine.session.commit()
        
        # This works best after login because that ensures that the
        # url mapping is in place for use in the HistoryStore.
        hh = HistoryStore(nde_idx, 'fred_1')
        source = basic_login('fred_1', 'useless', 'Fred Manager')

        # Now we can continue with the test.
        hh.append("A message to our readers")
        hh.append("With overzealous follow-up")
        hh.store()
        engine.session.commit()
        h_resp = engine.session.query(
            ndHistory
            ).filter(
            ndHistory.nde_idx == nde_idx).one()
        self.assertEqual(h_resp.hst_text,
                         "A message to our readers\n\n"
                         "With overzealous follow-up")
        self.assertEqual(h_resp.hst_user, 'fred_1')
        self.assertEqual(h_resp.hst_type, 'system')
        msg = email.message_from_file(open(SMTP_CAPTURE))
        self.assertEqual(msg['From'], 'noreply@fred.com')
        self.assert_('e@f.com' in msg['To'])
        self.assertEqual(msg.get_payload(),
                         "Updates for node %s:\n\n"
                         "A message to our readers\n\n"
                         "With overzealous follow-up\n"%
                         ('/pages/%s'%nde_idx))

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
