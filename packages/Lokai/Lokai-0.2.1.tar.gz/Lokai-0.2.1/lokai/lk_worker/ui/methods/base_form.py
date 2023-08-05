# Name:      lokai/lk_worker/ui/methods/base_form.py
# Purpose:   BaseDetailForm for building edit area
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

from lokai.tool_box.tb_forms.form import Form
from lokai.tool_box.tb_common.dates import now

#-----------------------------------------------------------------------

class NodeBaseForm(Form):
    
    def __init__(self, request, object_reference, data_object, **kwargs):
        """ Initialise a form. We must have an object reference and a
            data object relating to that reference before we do
            anything else.

        """
        assert self.__class__ is not NodeBaseForm, "abstract class"
        self.node_perm = perm = request.derived_locals['permissions']
        self.request = request
        self.obj = data_object
        self.obj_ref = object_reference
        self.new_obj = {}
        self.timestamp = now()
        self.title = kwargs.get('title')
        self.required_permission = kwargs.get('perm')
        # A title expressly sent as None or '' will make a fieldset with no
        # text legend - as this sits too high on the page a spacer is used
        
        self._interpret_perms()

        Form.__init__(self,
                      request_object=request,
                      action = self._identify_form_action(),
                      **kwargs)
        
        self.build_objects()
        self.build_form()

    def set_title(self, text):
        if text:
            self.attrs['title'] = text
        else:
            if 'title' in self.attrs:
                del self.attrs['title']

    def _interpret_perms(self):
        """ Look at permissions to see if we are limited in any way in
            what we can do.
        """
        assert self.required_permission
        self.can_edit = (self.obj_ref and
                    self.obj_ref != '**new**' and
                    self.node_perm.test_permit(self.required_permission, 'edit'))
        self.can_add = (self.obj_ref == '**new**' and
                   self.node_perm.test_permit(self.required_permission, 'add'))
   
    def build_data(self):
        if self.obj:
            self.populate_fields()
        else:
            self.populate_defaults()
        
#-----------------------------------------------------------------------
