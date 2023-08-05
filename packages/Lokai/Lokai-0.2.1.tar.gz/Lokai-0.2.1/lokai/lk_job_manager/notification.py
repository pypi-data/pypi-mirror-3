# Name:      lokai/lk_job_manager/notification.py
# Purpose:   Provide tools for logging and notification
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
import logging
import lokai.tool_box.tb_common.notification as notify

#-----------------------------------------------------------------------

""" Set up notifiers that hold certain common information in a
    structured way that can be used for subsequent analysis. This is
    paving the way for posting log messages into structured storage.

    We assume that a job goes through one or more notification cycles
    (per input file or something else). Log messages are accumulated
    during each cycle. At the end of the cycle the log messages are
    formatted into a notification that is posted to some destination.

    Each notification is provided with the following detail:

        title = Text used to identify the notification to humans.
            This would appear, for example, as the subject of an
            email.

        client_reference = (optional) Text used as a unique name for
            the notification.  If given.this name must be unique in
            whatever namespace the target handler supports.  Assume
            this is system wide unless clearly told otherwise.

        tags = (optional) Space separated list of tags that can be
            used for searching.

        group = (optional) Top level configuration group that this
            instance belongs to and where the job_logging_target item
            can be found.

        path = (optional) List of text items that together identify a
            path in some hierarchical name space. The path is
            interpreted by the target handler to find the actual place
            to store the notification.

            The path is assumed to be relative to some base location
            that is set for the working environment. Thus, if a path
            is not given the notification will appear under this base
            location.

        links = (optional) Dictionary of name:url pairs. These are
            intended to provide a reference to further information
            (perhaps the original input file) that can be used to
            understand or respond to the notification. Links are
            formatted as part of the notification in whatever way the
            particular target can use.

        rubric = (optional) Text that can appear in the notification
            providing a human readable explanation of the context of
            the notification.
"""

class JobNotifier(notify.BulkHandler):

    def setAttributes(self, **kwargs):
        """ Set values for specific attributes, creating them if necessary.

            If the given value is None the attribute is deleted
        """ 
        for key in ['title', 'client_reference',
                    'tags', 'path', 'links', 'rubric',
                    'config_group', 'logging_target',
                    'toaddrs', 'temp_toaddrs']:
            try:
                value = kwargs[key]
                if value is not None:
                    setattr(self, key, value)
                else:
                    try:
                        delattr(self, key)
                    except AttributeError:
                        pass
            except KeyError:
                pass

    def getAttributes(self):
        op = {}
        for key in ['title', 'client_reference',
                    'tags', 'path', 'links', 'rubric',
                    'config_group', 'logging_target',
                    'toaddrs', 'temp_toaddrs']:
            try:
                op[key] = getattr(self, key)
            except AttributeError:
                pass
        return op

class TextFormatter(notify.BulkFormatter):

    def formatHeader(self, records):
        op = []
        for key in ['title', 'client_reference']:
            try:
                op.append("%s: %s" %
                          (key.capitalise(),
                           getattr(self.x_calling_handler, key)))
            except AttributeError:
                pass
        try:
            op.append(getattr(self.x_calling_handler, 'rubric'))
        except AttributeError:
            pass
        return '\n\n'.join(op)

    def formatFooter(self, records):
        op = []
        try:
            op.append("Tags: %s" % getattr(self.x_calling_handler, 'tags'))
        except AttributeError:
            pass
        try:
            op.append("Path: %s" %
                      '/'.join(getattr(self.x_calling_handler, 'path')))
        except AttributeError:
            pass
        try:
            link_set = getattr(self.x_calling_handler, 'links')
            ln = []
            for name, url in link_set.iteritems():
                ln.append("%s: %s" % (name, url))
            if ln:
                op.append(', '.join(ln))
        except AttributeError:
            pass
        return '\n\n'.join(op)

#-----------------------------------------------------------------------

MONITOR = notify.MONITOR # Name of reporting level
monitor = notify.monitor # Reporting function

critical = notify.critical
error = notify.error
exception = notify.exception
warning = notify.warning
info = notify.info
debug = notify.debug

setLogName = notify.setLogName
getLogName = notify.getLogName
getDebugName = notify.getDebugName

getLogger = notify.getLogger

#-----------------------------------------------------------------------
