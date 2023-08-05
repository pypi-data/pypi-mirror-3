# Name:      lokai/lk_worker/models/builtin_data_tags.py
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

from sqlalchemy import and_

import pyutilib.component.core as component

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update
from lokai.tool_box.tb_database.orm_base_object import OrmBaseObject
from lokai.tool_box.tb_database.orm_access import get_row

from lokai.lk_worker.models import (
    ndNode,
    model,
    )

from lokai.lk_worker.extensions.data_interface import IWorkerData

#-----------------------------------------------------------------------

class ndNodeTag(OrmBaseObject):

    search_fields = ['nde_idx', 'nde_tag_text']

model.register(ndNodeTag, 'nd_node_tag')

#-----------------------------------------------------------------------
# Special code for node tags

def get_node_tag_list(nde_idx):
    """ Return a list of tags associated with this node.
    """
    qy = engine.session.query(ndNodeTag).filter(
        ndNodeTag.nde_idx == nde_idx)
    return qy.all()

#-----------------------------------------------------------------------

class PiTagData(component.SingletonPlugin):
    """ Link to nde_activity """
    component.implements(IWorkerData, inherit=True)

    def __init__(self):
        self.name = 'tags'

    def nd_read_data_extend(self, query_result, **kwargs):
        result_map = {}
        if query_result and isinstance(query_result, (list, tuple)):
            nde_idx = query_result[0].nde_idx
            tag_text_set = []
            temp_tag_set = get_node_tag_list(nde_idx)
            for tag_obj in temp_tag_set:
                tag_text_set.append(tag_obj.nde_tag_text)                    
            result_map['nd_tags'] = ' '.join(tag_text_set)
        return result_map
    
    def nd_write_data_extend(self, new_data, old_data=None):
        hist_response = []
        nde_idx = new_data['nd_node']['nde_idx']
        if 'nd_tags' in new_data:
            old_tag_text_list = []
            if old_data and 'nd_tags' in old_data:
                old_tag_text_list = old_data.get('nd_tags', '').strip().split(' ')
            old_len = len(old_tag_text_list)
            new_tag_text_list = new_data['nd_tags'].strip().split(' ')
            tags_added = []
            for new_tag in new_tag_text_list:
                if new_tag:
                    # Only do this for meaningful input
                    try:
                        old_tag_text_list.remove(new_tag)
                    except ValueError:
                        # Capture new tag but avoid duplicates and ''
                        if new_tag and new_tag not in tags_added:
                            tags_added.append(new_tag)
            if tags_added:
                hist_response.append(
                    "Tags added: %s"% ' '.join(tags_added))
                for tag_text in tags_added:
                    tag_obj = {'nde_idx': nde_idx,
                               'nde_tag_text': tag_text}
                    insert_or_update(ndNodeTag, tag_obj)
            if old_len > len(old_tag_text_list) and len(old_tag_text_list):
                hist_response.append(
                    "Tags removed: %s"% ' '.join(old_tag_text_list))
                for tag_text in old_tag_text_list:
                    engine.session.query(ndNodeTag).filter(
                        and_((ndNodeTag.nde_idx == nde_idx),
                              (ndNodeTag.nde_tag_text == tag_text)
                             )).delete()
            engine.session.flush()
        return hist_response

    def nd_delete_data_extend(self, data_object):
        hist_response = []
        nde_idx = data_object['nd_node']['nde_idx']
        engine.session.query(ndNodeTag).filter(
            ndNodeTag.nde_idx == nde_idx).delete()
        return hist_response

#-----------------------------------------------------------------------
