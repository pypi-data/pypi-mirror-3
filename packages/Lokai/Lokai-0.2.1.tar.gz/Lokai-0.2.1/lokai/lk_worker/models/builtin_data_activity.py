# Name:      lokai/lk_worker/models/builtin_data_activity.py
# Purpose:   Define plugins on the IWorkerData interface
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

import pyutilib.component.core as component
from sqlalchemy import union
from werkzeug.routing import BuildError

from lokai.tool_box.tb_common.dates import strtotime, now
from lokai.tool_box.tb_database.orm_base_object import OrmBaseObject
from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update

from lokai.lk_common.selection_map import SelectionMap
from lokai.lk_worker.models import (
    ndNode,
    model,
    )

from lokai.lk_worker.ui.local import url_for

from lokai.lk_worker.extensions.data_interface import IWorkerData

#-----------------------------------------------------------------------

class ndActivity(OrmBaseObject):
    
    search_fields = ['nde_idx']

    def __init__(self):
        OrmBaseObject.__init__(self)

model.register(ndActivity, "nd_activity")

#-----------------------------------------------------------------------

class ndHistory(OrmBaseObject):
    
    search_fields = ['nde_idx', 'hst_time_entry', 'hst_type']

    def __init__(self):
        OrmBaseObject.__init__(self)

model.register(ndHistory, "nd_history")

#-----------------------------------------------------------------------

from sets import Set as set # Deprecated since 2.6
from lokai.lk_worker.models import ndParent
from lokai.lk_worker.models.builtin_data_subscribers import ndNodeSubscriber

def get_subscribers(given_idx):
    """ Find all the subscribers to this node, even from multiple
        parent trees.

        Duplicates are removed.
    """    
    q1 = engine.session.query(
        ndNodeSubscriber.nde_subscriber_list.label('nde_subscriber_list')
        ).join(
        (ndParent, ndParent.nde_parent == ndNodeSubscriber.nde_idx)
        ).filter(
        ndParent.nde_idx == given_idx)
    q2 = engine.session.query(
        ndNodeSubscriber.nde_subscriber_list.label('nde_subscriber_list')
        ).filter(
        ndNodeSubscriber.nde_idx == given_idx)
    query = q1.union(q2)
    i_set = query.all()
    s_set = set()
    for response in i_set:
        subs_list = response.nde_subscriber_list.split(',')
        s_set.update([x.strip() for x in subs_list]) # remove duplicates
    #-- done
    return list(s_set)

#-----------------------------------------------------------------------

from lokai.tool_box.tb_common.smtp import SmtpConnection
import email.mime.text

def respond_to_subscribers(given_idx, given_name, body):
    if not given_idx:
        return # >>>>>>>>>>>>>>>>>>>>
    toaddrs = get_subscribers(given_idx)
    if not toaddrs:
        return # >>>>>>>>>>>>>>>>>>>>
    try:
        node_url = url_for('display', {'object_id': given_idx})
    except BuildError:
        node_url = given_idx
    if given_name:
        text = "Updates for node %s (%s):\n\n"%(given_name, node_url)
    else:
        text = "Updates for node %s:\n\n"%node_url
    msg = email.mime.text.MIMEText(text+body)
    msg['Subject'] = "Automated status update from Lokai system"
    msg['To'] = ','.join(toaddrs)
    conn = SmtpConnection(config_section='all')
    msg['From'] = conn.make_from("noreply")
    conn.sendmail('noreply', toaddrs, str(msg))
    conn.quit()
    
#-----------------------------------------------------------------------

class HistoryStore(object):

    """ A class that can be used to accumulate history records so that
        they can be written out in one lump.
    """
    def __init__(self, nde_idx, user, nde_name=None, source='system'):
        self.system_messages = []
        self.time = now()
        self.user = user
        self.nde_idx = nde_idx
        self.source = source
        self.nde_name = nde_name

    def append(self, message):
        """ Add a history message to the store """
        if message != None:
            if isinstance(message, (type(''), type(u''))):
                if message:
                    self.system_messages.append(message)
            elif isinstance(message, type([])):
                if len(message) != 0:
                    self.system_messages += message
            elif isinstance(message, type(self)):
                self.append(message.system_messages)
            else:
                raise TypeError, str(type(message))

    def __str__(self):
        op = u"\n\n".join(self.system_messages)
        return op

    def __len__(self):
        return len(self.system_messages)
    
    def store(self):
        """ Write all the messages out to the history table """
        if len(self.system_messages):
            detail = {'nde_idx' : self.nde_idx,
                      'hst_user' : self.user,
                      'hst_time_entry' : self.time,
                      'hst_type' : self.source,
                      'hst_text' : str(self)
                      }
            op = insert_or_update(ndHistory, detail)
            respond_to_subscribers(self.nde_idx, self.nde_name, str(self))

#-----------------------------------------------------------------------

def  get_allocated_resources():
    """ Find all the users who have been assigned to activities
    """
    qy = engine.session.query(
        ndActivity.act_user).filter(
        ndActivity.act_user != None)
    return qy.all()

#-----------------------------------------------------------------------

class PiActivityData(component.SingletonPlugin):
    """ Link to nde_activity """
    component.implements(IWorkerData, inherit=True)

    def __init__(self):
        self.name = 'activity'

    def nd_read_data_extend(self, result_object, **kwargs):
        result_map = {}
        if result_object and isinstance(result_object, (list, tuple)):
            for data_object in result_object:
                if isinstance(data_object, ndActivity):
                    result_map['nd_activity'] = data_object
                    break
        return result_map

    def nd_read_query_extend(self, query_in, **kwargs):
        query_result = query_in.add_entity(ndActivity).outerjoin(
            (ndActivity, ndNode.nde_idx==ndActivity.nde_idx))
        return query_result

    def nd_write_data_extend(self, new_data, old_data=None):
        hist_response = []
        nde_idx = new_data['nd_node']['nde_idx']
        if 'nd_activity' in new_data:
            new_data['nd_activity']['nde_idx'] = nde_idx
            insert_or_update(ndActivity, new_data['nd_activity'])
            if 'message' in new_data:
                #
                # Use HistoryStore to send this to subscribers.
                hh = HistoryStore(
                    nde_idx, new_data['message']['hst_user'],
                    nde_name=new_data['nd_node'].get('nde_name'),
                    source='user')
                hh.append(new_data['message']['hst_text'])
                hh.store()
        return hist_response

    def nd_delete_data_extend(self, data_object):
        hist_response = []
        nde_idx = data_object['nd_node']['nde_idx']
        engine.session.query(ndActivity).filter(
            ndActivity.nde_idx == nde_idx).delete()
        engine.session.query(ndHistory).filter(
            ndHistory.nde_idx == nde_idx).delete()
        return hist_response

    def nd_validate_data_extend(self, new_data, old_data):
        if new_data['nd_activity']:
            dt = new_data['nd_activity'].get('act_date_start', None)
            if dt:
                try:
                    dt =  baldwin.util.dates.strtotime(dt)
                except baldwin.util.dates.ErrorInDateString:
                    raise nb.util.data_exceptions.ndDataValidation, (
                        'Bad activity start date: %s'%str(dt))
            dt = new_data['nd_activity'].get('act_date_finish', None)
            if dt:
                try:
                    dt =  baldwin.util.dates.strtotime(dt)
                except baldwin.util.dates.ErrorInDateString:
                    raise nb.util.data_exceptions.ndDataValidation, (
                        'Bad activity finish date: %s'%str(dt))
            dt = new_data['nd_activity'].get('act_date_remind', None)
            if not dt:
                try:
                    dt =  baldwin.util.dates.strtotime(dt)
                except baldwin.util.dates.ErrorInDateString:
                    raise nb.util.data_exceptions.ndDataValidation, (
                        'Bad activity reminder date: %s'%str(dt))    

#-----------------------------------------------------------------------

STATUS_OPEN = u'000'
STATUS_ACTIVE = u'100'
STATUS_CLOSED = u'900'

STATUS_RANGE = {'10': (STATUS_OPEN, STATUS_ACTIVE),
                '20': (STATUS_OPEN, STATUS_CLOSED),
                '30': (STATUS_ACTIVE, STATUS_CLOSED),
                '40': (STATUS_CLOSED, '1000'),
                }

#-----------------------------------------------------------------------
