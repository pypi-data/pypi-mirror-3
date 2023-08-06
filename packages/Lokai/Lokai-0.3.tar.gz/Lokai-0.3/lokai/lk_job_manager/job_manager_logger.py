# Name:      lokai/lk_job_manager/job_manager_logger.py
# Purpose:   Create job_manager_logger type
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

import logging
import sqlalchemy.orm.exc
import pyutilib.component.core as component

import lokai.lk_job_manager.notification as notify
import lokai.tool_box.tb_common.dates as dates
import lokai.tool_box.tb_common.configuration as config
import lokai.tool_box.tb_common.rest_support as rst
from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_access import insert_or_update

from lokai.lk_common.selection_map import SelectionMap
from lokai.lk_worker.models import ndNode
from lokai.lk_worker.models.builtin_data_resources import ndUserAssignment

from lokai.lk_worker import ndDataPathNotFound
from lokai.lk_worker.extensions.view_interface import IWorkerView
import lokai.lk_worker.nodes.graph as graph
from lokai.lk_worker.nodes.search import (search_children,
                                          find_in_path)

from lokai.lk_worker.nodes.data_interface import (put_node_dataset,
                                                  validate_node_dataset)

from lokai.lk_worker.nodes.node_data_functions import get_assigned_resource_list

#-----------------------------------------------------------------------

SEVERITY_ERROR = 'error'
SEVERITY_CRITICAL = 'critical'
SEVERITY_WARNING = 'warning'
SEVERITY_INFO = 'info'
SEVERITY_MONITOR = 'monitor'
SEVERITY_DEBUG = 'debug'

#-----------------------------------------------------------------------

def get_configured_target(group):
    """ Look for a config item called 'job_logging_target'

        look in [group] first. If not found look in ['all']. If not
        found, use default.
    """
    response = "**/Data Exceptions"
    try:
        section = config.get_global_config()[group]
        try:
            response = section['job_logging_target']
        except KeyError:
            section = config.get_global_config()['all']
            try:
                response = section['job_logging_target']
            except KeyError:
                pass
            
    except KeyError:
        pass
    return response.split('/')

#-----------------------------------------------------------------------

class JobManagerLogHandler(logging.Handler):
    """ emit records into a node structure in the lk_worker environment """

    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.title = None
        self.client_reference = None
        self.tags = None
        self.path = []
        self.logging_target = None
        self.config_group = None

    def execute(self, function, *args, **kwargs):
        """ Apply this function to the underlying hander and to the
            underlying formatter and handler
        """
        for c in (self.formatter, ):
            if c and hasattr(c, function):
                target = getattr(c, function)
                if callable(target):
                    yield target(*args, **kwargs)

    def execute_all(self, function, *args, **kwargs):
        """ call execute in a loop and throw away any responses.
        """
        for resp in self.execute(function, *args, **kwargs):
            pass


    def setAttributes(self, *args, **kwargs):
        """ Set some attributes here, and pass on down to others...
        """
        try:
            self.title = kwargs['title']
        except KeyError:
            pass
        try:
            self.client_reference = kwargs['client_reference']
        except KeyError:
            pass
        try:
            self.tags = kwargs['tags']
        except KeyError:
            pass
        try:
            self.path = kwargs['path']
        except KeyError:
            pass
        try:
            self.logging_target = kwargs['logging_target']
        except KeyError:
            pass
        try:
            self.config_group = kwargs['config_group']
        except KeyError:
            pass
        # Now down to other levels
        self.execute_all('setAttributes', *args, **kwargs)
        
    def emit(self, record):
        """ The record is supposedly pre-formatted, but we still call
            self.format anyway because we want to make sure that the
            whole thing is valid restructured text and that headers
            and footers are inserted.
        """
        self.time_now = dates.now()
        self.msg = self.format(record)
        #
        # Find the target
        group = 'all'
        if self.config_group:
            group = self.config_group
        logging_target = None
        if self.logging_target:
            loging_target = self.logging_target
        if logging_target is None:
            logging_target = get_configured_target(group)
        target_nodes = find_in_path(logging_target)
        try:
            target_node = target_nodes[0]
        except (LookupError, TypeError):
            # Probably an error in the configuration item
            target_node = None
        if not target_node:
            raise ndDataPathNotFound(logging_target)
        #
        # Look for path and set up the hierarchy as needed.
        sub_path = self.path
        top_node = target_node
        for path_name in sub_path:
            try:
                name_query = engine.session.query(ndNode).filter(
                    ndNode.nde_name == path_name)
                next_node = search_children(name_query, [top_node])
                res = next_node.one()
                top_node = res.nde_idx
            except sqlalchemy.orm.exc.NoResultFound:
                next_node = self._make_identifier_node(top_node, path_name)
                top_node = next_node
        #
        # Place the item under top_node
        nde_idx = self._make_exception_node(top_node)
        self._assign_user(nde_idx)
        
    def setFormatter(self, formatter):
        """ Set the formatter for this handler.
        """
        self.formatter = formatter
        
    def _make_identifier_node(self, group_node, id_name):
        """ Build a node that belongs to the identifier tree
        """
        data_set = {
            'nd_node': {
                'nde_type': 'generic',
                'nde_date_create': self.time_now,
                'nde_date_modify': self.time_now,
                'nde_name': id_name,
                'nde_description': 'Identification place-holder'
                },
            'message': {
                'hst_time_entry': self.time_now,
                'hst_type': 'system',
                'hst_user': 'system',
                'hst_text': 'Make new identifier node from logger',
                }
            }
        nde_idx = put_node_dataset(data_set)
        graph.make_link(nde_idx, group_node)
        return nde_idx

    def _assign_user(self, nde_idx):
        """ Look upwards for a responsible user to give this to.
        """
        user_set = get_assigned_resource_list(nde_idx)
        if len(user_set) >= 1:
            insert_or_update(
                ndUserAssignment,
                {'nde_idx': nde_idx,
                 'usa_user': user_set[0].usa_user
                 }
            )

    def _make_exception_node(self, parent_node):
        """ Build a node that forms an actual exception
        """
        data_set = self._get_node_to_store()
        validate_node_dataset(data_set)
        nde_idx = put_node_dataset(data_set)
        graph.make_link(nde_idx, parent_node)
        return nde_idx

    def _get_node_to_store(self):
        """ Convert the message and other data into a storable node.
        """
        view_extn = component.ExtensionPoint(ILoggerView)
        selection_maps = view_extn.service('activity').nd_view_selection_lists()

        status_map = selection_maps['status']
        priority_map = selection_maps['priority']
        severity_map = selection_maps['severity']

        stats = notify.getLogger().stats
        # Allocate a severity based on the most sever log level found
        # in the stats for the current logger.
        #
        # Scan the stats in order of increasing severity and set the
        # 'severity' status for each non-zero count found. The last
        # one (the most serious) wins.
        #
        # One of them must be non-zero, else what are we doing here?
        for name, target in [('DEBUG', SEVERITY_DEBUG),
                             ('MONITOR', SEVERITY_MONITOR),
                             ('INFO', SEVERITY_INFO),
                             ('WARNING', SEVERITY_WARNING),
                             ('ERROR', SEVERITY_ERROR),
                             ('CRITICAL', SEVERITY_CRITICAL),
                             ]:
            if stats[name] > 0:
                severity = severity_map.get_back_value(target)

        op = {
            'nd_node': {
                'nde_date_create': self.time_now,
                'nde_date_modify': self.time_now,
                'nde_name': self.title,
                'nde_description': self.msg,
                'nde_client_reference': self.client_reference,
                'nde_type': 'job_manager_logger',
                },
            'message': {
                'hst_time_entry': self.time_now,
                'hst_user': 'system',
                'hst_type': 'system',
                'hst_text': 'Make new exception node from logger'
                },
            'nd_activity': {
                'act_type': severity,
                'act_sub_type': None,
                'act_status': status_map.get_back_value('open'),
                'act_priority': priority_map.get_back_value('immediate'),
                'act_date_remind': self.time_now,
                },
            }
        if self.tags:
            op['nd_tags'] = self.tags
        return op

class JobManagerLogFormatter(logging.Formatter):
    """ Pretty up the record to go into the database. Use restructured text.
    """

    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)
        self.rubric = None
        self.links = None

    def setAttributes(self, *args, **kwargs):
        try:
            self.rubric = kwargs['rubric']
        except KeyError:
            pass
        try:
            self.links = kwargs['links']
        except KeyError:
            pass
        
    def format(self, record):
        """ Assume the record is plain text (as it naturally will be
            from the accumulated log lines) and put restructured text
            around it.

            Add a header for the rubric.
            
            Add a footer for the links.
        """
        body_parts = []
        if self.rubric:
            body_parts.append(rst.as_raw_text(self.rubric))
            
        body_parts.append(rst.as_raw_text(record.getMessage()))
        if self.links:
            op = ['References']
            op.extend([rst.as_inline_link(name, tag) for
                       name, tag in self.links.iteritems()])
            body_parts.append(': '.join(op))
        return '\n\n'.join(body_parts)
        
#-----------------------------------------------------------------------

import pyutilib.component.core as component
class ILoggerView(component.Interface):
    pass

from lokai.lk_worker.ui.controllers.generic import PiGenericController
from lokai.lk_worker.ui.methods.display_page_activity import DisplayPage

class PiJobLoggerController(PiGenericController):
    
    def __init__(self):
        self.name = 'job_manager_logger'
        self.display_name = 'Job Manager Logger'
        self.view_interface = component.ExtensionPoint(ILoggerView)
        self.display_page = DisplayPage

from lokai.lk_worker.ui.views.activity import PiActivityView
class PiJobLoggerView(PiActivityView):
    """ Link to nde_activity - interface is mapped separately """

    def __init__(self):
        PiActivityView.__init__(self)
        severity_map = SelectionMap(found_data= [
            ('010', SEVERITY_CRITICAL),
            ('020', SEVERITY_ERROR),
            ('030', SEVERITY_WARNING),
            ('035', SEVERITY_INFO),
            ('040', SEVERITY_MONITOR),
            ('050', SEVERITY_DEBUG),
            ])
        self.selection_maps['severity'] = severity_map

#-----------------------------------------------------------------------

# Post the interface mappings

class GenericActivityView(PiJobLoggerView):
    component.implements(ILoggerView, inherit=True)

from lokai.lk_worker.ui.views.attachments import PiAttachmentsView
class GenericAttachmentsView(PiAttachmentsView):
    component.implements(ILoggerView, inherit=True)

from lokai.lk_worker.ui.views.node import PiNodeView
class GenericNodeView(PiNodeView):
    component.implements(ILoggerView, inherit=True)

from lokai.lk_worker.ui.views.resources import PiResourcesView
class GenericResourcesView(PiResourcesView):
    component.implements(ILoggerView, inherit=True)

from lokai.lk_worker.ui.views.subscribers import PiSubscribersView
class GenericSubscribersView(PiSubscribersView):
    component.implements(ILoggerView, inherit=True)

from lokai.lk_worker.ui.views.tags import PiTagsView
class GenericTagsView(PiTagsView):
    component.implements(ILoggerView, inherit=True)

#-----------------------------------------------------------------------
