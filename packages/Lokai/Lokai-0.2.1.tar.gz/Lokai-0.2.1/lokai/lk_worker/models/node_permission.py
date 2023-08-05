# Name:      lokai/lk_worker/models/node_permission.py
# Purpose:   Define plugins for localised node permission
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

from lokai.tool_box.tb_database.orm_base_object import OrmBaseObject
from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update

from lokai.lk_worker.models import (
    ndNode,
    model,
    )

from lokai.lk_worker.extensions.data_interface import IWorkerData

#-----------------------------------------------------------------------

class ndPermission(OrmBaseObject):

    search_fields = ['nde_idx']

model.register(ndPermission, "nd_permission")

#-----------------------------------------------------------------------

class PiPermissionData(component.SingletonPlugin):
    """ Link to nde_activity """
    component.implements(IWorkerData, inherit=True)

    def __init__(self):
        self.name = 'local_permission'

    def nd_read_data_extend(self, result_object, **kwargs):
        result_map = {}
        if result_object and isinstance(result_object, (list, tuple)):
            for data_object in result_object:
                if isinstance(data_object, ndPermission):
                    result_map['local_permission'] = data_object.nde_permission
                    break
        return result_map

    def nd_read_query_extend(self, query_in, **kwargs):
        query_result = query_in.add_entity(ndPermission).outerjoin(
            (ndPermission, ndNode.nde_idx==ndPermission.nde_idx))
        return query_result

    def nd_write_data_extend(self, new_data, old_data=None):
        hist_response = []
        nde_idx = new_data['nd_node']['nde_idx']
        new_permission = new_data.get('local_permission')
        if new_permission:
            insert_or_update(ndPermission, {'nde_idx': nde_idx,
                                            'nde_permission': new_permission})
        elif old_data and 'local_permission' in old_data:
            engine.session.query(ndPermission).filter(
                ndPermission.nde_idx == nde_idx).delete()

    def nd_delete_data_extend(self, data_object):
        hist_response = []
        nde_idx = data_object['nd_node']['nde_idx']
        engine.session.query(ndPermission).filter(
            ndPermission.nde_idx == nde_idx).delete()
        return hist_response

#-----------------------------------------------------------------------
