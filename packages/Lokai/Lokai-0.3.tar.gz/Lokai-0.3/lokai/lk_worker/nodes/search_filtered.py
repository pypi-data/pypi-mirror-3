# Name:      lokai/lk_worker/nodes/search_filtered.py
# Purpose:   Search utilities for nodes
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

import csv
from sqlalchemy import and_, exists, or_

from lokai.tool_box.tb_database.orm_interface import engine

from lokai.tool_box.tb_common.cgi_interface import from_cgi

from lokai.lk_worker.models import ndNode
from lokai.lk_worker.models.builtin_data_activity import ndActivity, STATUS_RANGE
from lokai.lk_worker.models.builtin_data_resources import ndUserAssignment
from lokai.lk_worker.models.builtin_data_tags import ndNodeTag

from lokai.lk_worker.nodes.search import (_make_candidates,
                                          search_down,
                                          find_in_path
                                          )

#-----------------------------------------------------------------------

def get_node_basic(nde_idx=None):
    """ Return a query that joins a node to an activity.

        If nde_idx is given then the query is filtered by that node
        idx.
    """
    query = engine.session.query(ndNode, ndActivity).outerjoin(
        (ndActivity, ndNode.nde_idx == ndActivity.nde_idx))
    if nde_idx:
        query = query.filter(ndNode.nde_idx == nde_idx)
    return query

#-----------------------------------------------------------------------

import pyutilib.component.core as component
from lokai.lk_worker.extensions.data_interface import IWorkerData

data_extensions = component.ExtensionPoint(IWorkerData)

#-----------------------------------------------------------------------


def search_filtered(filter_set, tops=None):
    """ Create a search query using the given filter dictionary
    """
    query = get_node_basic()
    
    nde_idx = from_cgi(filter_set, 'nd_node')

    # 'candidates' is a list of nodes giving the start of one or more
    # search trees (we are searching 'down'). If candidates are not
    # given then the search starts at the top of the forest. Permitted
    # access to nodes to search comes from providing a candidate list
    # that captures the first time a user appears in each tree of the
    # forest.

    # The search does not take into account the possibility that a
    # single node might have its own 'function' restriction. The
    # search is only interested in read access.
    candidates = _make_candidates(nde_idx, tops)
    name = from_cgi(filter_set, 'name')
    if name:
        if name[0] == '=':
            path_list = []

            for element in csv.reader([name[1:]], delimiter='/').next():
                path_list.append(element)
            candidates = find_in_path(path_list, candidates)
        else:
            query = query.filter(ndNode.nde_name.ilike("%%%s%%"%name))
    status = from_cgi(filter_set, 'status')
    if status:
        chooser = STATUS_RANGE.get(status)
        if chooser:
            query = query.filter(and_(
                ndActivity.act_status >= chooser[0],
                ndActivity.act_status < chooser[1]))
    assignee = from_cgi(filter_set, 'assignee')
    if assignee and assignee != '**ignore**':
        query = query.join(
            (ndUserAssignment,
             ndUserAssignment.nde_idx == ndNode.nde_idx)).filter(
            ndUserAssignment.usa_user == assignee)

    bf_from = from_cgi(filter_set, 'bf_range_from')
    bf_to = from_cgi(filter_set, 'bf_range_to')
    if bf_from:
        query = query.filter(ndActivity.act_date_remind >= bf_from)
    if bf_to:
        query = query.filter(ndActivity.act_date_remind <= bf_to)
    st_from = from_cgi(filter_set, 'st_range_from')
    st_to = from_cgi(filter_set, 'st_range_to')
    if st_from:
        query = query.filter(ndActivity.act_date_create >= st_from)
    if st_to:
        query = query.filter(ndActivity.act_date_create <= st_to)
    md_from = from_cgi(filter_set, 'md_range_from')
    md_to = from_cgi(filter_set, 'md_range_to')
    if md_from:
        query = query.filter(ndActivity.act_date_modify >= md_from)
    if md_to:
        query = query.filter(ndActivity.act_date_modify <= md_to)

    tag_set = from_cgi(filter_set, 'nd_tags')
    if tag_set:
        tag_list = tag_set.split(' ')
        test_list = [(ndNodeTag.nde_tag_text.ilike('%%%s%%' % x)) for x in tag_list]
        tag_query = engine.session.query(ndNodeTag.nde_idx).filter(
            or_(*test_list))
        query = query.filter(
            exists().where(ndNode.nde_idx ==
                           tag_query.statement.alias('tags').c.nde_idx
                ))

    client_ref = from_cgi(filter_set, 'client_ref')
    if client_ref:
        query = query.filter(
            ndNode.nde_client_reference.ilike("%%%s%%"%client_ref))
    query = search_down(query,
                        candidates,
                        depth_first = False)
    return query

#-----------------------------------------------------------------------
