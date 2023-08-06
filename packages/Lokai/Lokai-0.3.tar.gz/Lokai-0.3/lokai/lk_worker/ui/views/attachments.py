# Name:      lokai/lk_worker/ui/views/attachments.py
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

import os

from lokai.tool_box.tb_forms.widget import(
    RowWidget,
    CompositeWidget,
    FileWidget,
    StringWidget,
    CheckboxWidget,
    )

from lokai.lk_worker.ui.link_widget import LinkWidget 

from werkzeug import html
from lokai.lk_worker.ui.local import url_for

import pyutilib.component.core as component
from lokai.lk_worker.extensions import PluginIdCompare
from lokai.lk_worker.nodes.node_data_functions import extract_identifier
from lokai.lk_worker.extensions.view_interface import IWorkerView

from lokai.lk_worker.models.builtin_data_attachments import NodeAttachment

#-----------------------------------------------------------------------

class PiAttachmentsView(PluginIdCompare, component.SingletonPlugin):

    def __init__(self):
        self.name = 'attachments'
        self.selection_maps = {} # Selection maps, if required.
        
    def nd_view_selection_lists(self):
        return self.selection_maps

    def nd_view_form_extend(self, form):
        if not form.obj_ref or form.obj_ref == '**new**':
            return
        task_title = "Add attachments"
        form.detail.add(CompositeWidget, 'attachments',
                        title = task_title,
                        fieldset = {'expand' : 'closed'}
                        )
        container = form.detail.get_widget('attachments')

        container.add(FileWidget, 'attach_file',
                      title = 'File name')
        container.add(StringWidget, 'attach_description',
                      title = "Additional description")
        if form.obj and form.obj.get('attachments'):
            row = 0
            for nda in form.obj['attachments']:
                row += 1
                row_name = "row%03d"% row
                container.add(RowWidget, row_name)
                row_box = container.get_widget(row_name)
                row_box.add(LinkWidget, "1%s"% row_name)
                row_box.add(StringWidget, "2%s"% row_name,
                            readonly=True)
                row_box.add(CheckboxWidget, 'del%s'% row_name,
                            title = 'del')
            if row > 0:
                container.fieldset['expand'] = 'open'

    def nd_view_form_populate(self, form):
        if not form.obj_ref or form.obj_ref == '**new**':
            return
        container = form.detail.get_widget('attachments')
        if form.obj and form.obj.get('attachments'):
            row = 0
            for nda in form.obj['attachments']:
                row += 1
                row_name = "row%03d"% row
                row_box = container.get_widget(row_name)
                url_parts = {'object_id': form.obj_ref,
                             'file_path': os.path.basename(nda.get_target_path())}
                file_link = row_box.get_widget("1%s"% row_name)
                file_link.set_value("%s <%s>"% (nda.file_name, nda.file_version))
                file_link.target = 'get_file'
                file_link.url_parts = url_parts
                row_box.get_widget("2%s"% row_name).set_value(nda.description)
                row_box.get_widget('del%s'% row_name).set_value(False)

    def nd_view_form_default(self, form):
        pass

    def nd_view_form_process(self, form):
        """ Validate user input.

            If any field has an error the error text must be stored in the
            error attribute of a relevant widget.

            Return a single value; the count of errors found.
        """
        if not form.obj_ref or form.obj_ref == '**new**':
            return 0
        input_errors = {}
        return len(input_errors)

    def nd_view_form_store(self, form):
        hist_response = []
        if not 'attachments' in form.detail:
            return hist_response
        container = form.detail.get_widget('attachments')
        row = 0
        attach_set = form.obj and form.obj.get('attachments')
        update_data = []
        remove_data = []
        if attach_set:
            for nda in form.obj['attachments']:
                row += 1
                row_name = "row%03d"% row
                row_box = container.get_widget(row_name)
                if row_box['del%s' % row_name]:
                    remove_data.append(nda)
                    hist_response.append(
                        "Deleting file %s>%s>%s (%s)"% (
                            nda.base_location,
                            nda.other_location,
                            nda.file_name,
                            nda.version))
                
        if container['attach_file']:
            upload_object = container['attach_file']
            new_nda = NodeAttachment('node',
                                     form.obj_ref,
                                     upload_object.filename,
                                     description = container['attach_description'],
                                     user_name = form.request.user,
                                     )
            new_nda.set_file_source(upload_object.stream)
            update_data.append(new_nda)
            hist_response.append(
                "Uploaded file %s (%s)"% (upload_object.filename,
                                         str(container['attach_description'])))
            if update_data:
                form.new_obj['attachments'] = update_data
            if remove_data:
                form.new_obj['attachments_to_remove'] = remove_data
        return hist_response

    def nd_display_main(self, form):
        return []

    def nd_display_side(self, form):
        response_list = []
        if form.obj and form.obj.get('attachments'):
            for nda in form.obj['attachments']:
                if nda.description:
                    value = "%s - %s - version %d"% (nda.description,
                                                     nda.file_name,
                                                     nda.file_version)
                else:
                    value = "%s - version %d"% (nda.file_name,
                                                nda.file_version)
                target = 'get_file'
                url_parts = {'object_id': extract_identifier(form.obj),
                             'file_path': os.path.basename(nda.get_target_path())}
                path = url_for('get_file', url_parts)
                response_list.append(html.a(value, href=path))

        return response_list        

#-----------------------------------------------------------------------
