# Name:      lokai/lk_worker/ui/views/activity.py
# Purpose:   Provide user interviews specific to a node type
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

import lokai.tool_box.tb_common.dates as dates
from lokai.tool_box.tb_forms.widget import(
    CompositeWidget,
    RawCompositeWidget,
    DateWidget,
    SingleSelectWidget,
    TextWidget,
    )

from lokai.lk_common.selection_map import SelectionMap

import pyutilib.component.core as component
from lokai.lk_worker.extensions import PluginIdCompare
from lokai.lk_worker.extensions.view_interface import IWorkerView

from lokai.lk_worker.extensions.data_interface import IWorkerData
data_extensions = component.ExtensionPoint(IWorkerData)

#-----------------------------------------------------------------------

def gather_activity_data(form):
    """ Simply places the data from the form into a dictionary.

        Allows for testing emptiness and posting to data structure.
    """
    container = form.detail.get_widget('activity_data')

    range_box = container.get_widget('act_date_range')
    detail = {'act_date_start' : range_box['start_date'],
              'act_date_finish' : range_box['finish_date'],
              'act_date_remind' : container['remind_date']
              }
    if 'priority' in container:
        detail['act_priority'] = container['priority']
    if 'status' in container:
        detail['act_status'] = container['status']
    if 'act_type' in container:
        detail['act_type'] = container['act_type']
    return detail

#-----------------------------------------------------------------------

ACTION_FIELDS = ['act_date_start', 'act_date_finish', 'act_date_remind',
                 'act_priority', 'act_status', 'act_type', 'act_sub_type',
                 'act_date_work']

class PiActivityView(PluginIdCompare, component.SingletonPlugin):

    def __init__(self):
        self.name = 'activity'
        self.selection_maps = {}
        status_map = SelectionMap(found_data= [
            (u'000', 'open'),
            (u'100', 'active'),
            (u'900', 'closed'),
            (u'910', 'resolved - ok'),
            (u'920', 'resolved - nok'),
            ])
        self.selection_maps['status'] = status_map
        priority_map = SelectionMap(found_data= [
            (u'000', 'immediate'),
            (u'020', 'high'),
            (u'050', 'medium'),
            (u'090', 'low'),
            (u'999', 'parked'),
            ])
        self.selection_maps['priority'] = priority_map

    def nd_view_selection_lists(self):
        """ Return a dictionary of selection map objects.
        """
        return self.selection_maps

    def nd_view_form_extend(self, form):
        task_title = "Add task or activity data"
        activity = form.obj and form.obj.get('nd_activity')
        if activity:
            task_title = "Modify task or activity data"
        form.detail.add(CompositeWidget, 'activity_data',
                        title = task_title,
                        fieldset = {'expand' : 'closed'}
                        )
        container = form.detail.get_widget('activity_data')

        #
        # Set up option lists - use default type if necessary
        selection_sets = self.nd_view_selection_lists()
        priority_options = selection_sets.get('priority')
        status_options = selection_sets.get('status')
        act_type_options = selection_sets.get('severity')
        container.add(RawCompositeWidget, 'act_date_range',
                      title = "Start Date - End Date"
                      )
        range_box = container.get_widget('act_date_range')
        range_box.add(DateWidget, 'start_date',
                      )
        range_box.add(DateWidget, 'finish_date',
                      )
        container.add(DateWidget, 'remind_date',
                      title = 'Review Date (Bring Forward)'
                      )
        if priority_options:
            container.add(SingleSelectWidget, 'priority',
                          title = 'Priority',
                          options = priority_options.get_options()
                          )
        if status_options:
            container.add(SingleSelectWidget, 'status',
                          title = 'Status',
                          options = status_options.get_options()
                          )
        if act_type_options:
            container.add(SingleSelectWidget, 'act_type',
                           title = 'Severity',
                           options = act_type_options.get_options()
                      )
        container.add(TextWidget, 'new_message',
                        title = 'Message',
                        rows = 10,
                        cols = 50
                        )

    def nd_view_form_populate(self, form):
        activity = form.obj and form.obj.get('nd_activity')
        container = form.detail.get_widget('activity_data')
        if activity:
            container.fieldset['expand'] = 'open'
            range_box = container.get_widget('act_date_range')
            range_box.get_widget('start_date').set_value(activity.act_date_start)
            range_box.get_widget('finish_date').set_value(activity.act_date_finish)
            container.get_widget('remind_date').set_value(activity.act_date_remind)
            val = activity.act_priority != None and activity.act_priority or None
            container.get_widget('priority').set_value(val)
            val = activity.act_status != None and activity.act_status or None
            container.get_widget('status').set_value(val)
            act_type_widget = container.get_widget('act_type')
            if act_type_widget:
                act_type_widget.set_value(activity.act_type)
            container.get_widget('new_message').set_value('')

    def nd_view_form_default(self, form):
        pass

    def nd_view_form_process(self, form):
        """ Validate user input.

            If any field has an error the error text must be stored in the
            error attribute of a relevant widget.

            Return a single value; the count of errors found.
        """
        detail = gather_activity_data(form)
        container = form.detail.get_widget('activity_data')
        input_errors = {}
        range_box = container.get_widget('act_date_range')
        start_date = range_box['start_date']
        start_date_ok = False
        finish_date = range_box['finish_date']
        finish_date_ok = False
        if start_date:
            try:
                check_start = dates.strtotime(start_date)
                start_date_ok = True
            except dates.ErrorInDateString:
                input_errors['act_date_range'] = (
                    "%s is not a valid start date"% start_date)
        if finish_date:
            try:
                check_finish = dates.strtotime(finish_date)
                finish_date_ok = True
            except dates.ErrorInDateString:
                input_errors['act_date_range'] = (
                    "%s is not a valid finish date"% finish_date)
        if start_date_ok and finish_date_ok:
            if check_start > check_finish:
                input_errors['act_date_range'] = (
                    "Start %s is after finish %s"% (start_date, finish_date))
        remind_date = container['remind_date']
        if remind_date:
            try:
                dates.strtotime(remind_date)
            except dates.ErrorInDateString:
                input_errors['remind_date'] = (
                    "%s is not a valid review date"% remind_date)
        message = container.get_widget('new_message').value
        if message is None:
            message = ''
        message = message.strip()
        for k, v in detail.items():
            if k != 'nde_idx' and v is not None and v.strip() != '':
                #
                # Only test this if not empty
                if not message:
                    text = "%s text must be given" % (
                        container.get_widget('new_message').title)
                    input_errors['new_message'] = text
                    container.get_widget('new_message').set_error(text)
                elif len(message) < 10:
                    text = "%s text is too short" % (
                        container.get_widget('new_message').title)
                    input_errors['new_message'] = text
                    container.get_widget('new_message').set_error(text)
                break
        for k in input_errors:
            container.get_widget(k).set_error(input_errors[k])
        error_count = len(input_errors)
        if error_count:
            container.fieldset['expand'] = 'open'
        return error_count

    def nd_view_form_store(self, form):
        hist_response = []
        detail = gather_activity_data(form)
        container = form.detail.get_widget('activity_data')
        message = container.get_widget('new_message').value
        if message is None:
            message = ''
        message = message.strip()
        if message:
            message_data = {
                'hst_user' : form.request.user,
                'hst_time_entry' : form.this_date,
                'hst_type' : 'user',
                'hst_text' : str(message)
                }
        for k, v in detail.items():
            if k != 'nde_idx' and v is not None and v.strip() != '':
                #
                # Only store this if not empty
                form.new_obj['nd_activity'] = detail
                form.new_obj['message'] = message_data
                break
        changed = False
        new_data = form.new_obj.get('nd_activity')
        old_data = form.obj.get('nd_activity')
        if new_data and old_data:
            for field in ACTION_FIELDS:
                new = new_data.get(field)
                old = old_data.get(field)
                if new != old:
                    changed = True
                    hist_response.append(
                        'Activity item %s - was "%s", now "%s"' %
                        (field, old, new))
            if form.new_obj['message']:
                hist_response.append(
                    'Activity change message added')
            elif changed:
                hist_response.append(
                    'Activity change message not given')
        return hist_response

    def nd_display_main(self, form):
        return []

    def nd_display_side(self, form):
        activity = form.obj.get('nd_activity')
        node = form.obj['nd_node']
        response_list = []
        if activity:
            selection_sets = self.nd_view_selection_lists()
            priority_options = selection_sets.get('priority')
            status_options = selection_sets.get('status')
            act_type_options = selection_sets.get('severity')
            status_value = activity.act_status
            status_text = status_options.get_value(status_value)
            response_list.append("Status: %s" % status_text)
            priority_value = activity.act_priority
            priority_text = priority_options.get_value(priority_value)
            response_list.append("Priority: %s" % priority_text)
            if act_type_options:
                severity_value = activity.act_type
                severity_text = act_type_options.get_value(severity_value)
                response_list.append("Severity: %s"%severity_text)
            if activity.act_date_remind:
                response_list.append("Bring forward to: %s" %
                                     activity.act_date_remind)
            if activity.act_date_start:
                response_list.append("Start date: %s" % activity.act_date_start)
            if activity.act_date_finish:
                response_list.append("End date: %s" % activity.act_date_finish)
        return response_list

#-----------------------------------------------------------------------
