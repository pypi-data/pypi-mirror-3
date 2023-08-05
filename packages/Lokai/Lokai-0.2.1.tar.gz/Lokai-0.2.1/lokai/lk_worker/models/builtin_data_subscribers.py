# Name:      lokai/lk_worker/models/builtin_data_subscribers.py
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

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_base_object import OrmBaseObject
from lokai.tool_box.tb_database.orm_access import insert_or_update
from lokai.lk_worker.models import (
    ndNode,
    model,
    )

from lokai.lk_worker.extensions.data_interface import IWorkerData

#-----------------------------------------------------------------------

class ndNodeSubscriber(OrmBaseObject):

    search_fields = ['nde_idx']

model.register(ndNodeSubscriber, 'nd_node_subscriber')

#-----------------------------------------------------------------------

class PiSubscriberData(component.SingletonPlugin):
    component.implements(IWorkerData, inherit=True)

    def __init__(self):
        self.name = 'subscribers'

    def nd_read_data_extend(self, result_object, **kwargs):
        result_map = {}
        if result_object and isinstance(result_object, (list, tuple)):
            for data_object in result_object:
                if isinstance(data_object, ndNodeSubscriber):
                    result_map['nd_node_subscriber'] = data_object
                    break
        return result_map

    def nd_read_query_extend(self, query_in, **kwargs):
        query_result = query_in.add_entity(ndNodeSubscriber).outerjoin(
            (ndNodeSubscriber, ndNode.nde_idx==ndNodeSubscriber.nde_idx))
        return query_result

    def nd_write_data_extend(self, new_data, old_data=None):
        hist_response = []
        nde_idx = new_data['nd_node']['nde_idx']
        if 'nd_node_subscriber' in new_data:
            new_data['nd_node_subscriber']['nde_idx'] = nde_idx
            insert_or_update(ndNodeSubscriber, new_data['nd_node_subscriber'])
        return hist_response

    def nd_delete_data_extend(self, data_object):
        hist_response = []
        nde_idx = data_object['nd_node']['nde_idx']
        engine.session.query(ndNodeSubscriber).filter(
            ndNodeSubscriber.nde_idx == nde_idx).delete()
        return hist_response

#-----------------------------------------------------------------------
