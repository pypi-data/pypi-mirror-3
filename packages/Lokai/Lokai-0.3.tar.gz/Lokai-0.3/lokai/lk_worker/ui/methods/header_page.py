# Name:      lokai/lk_worker/ui/methods/header_page.py
# Purpose:   Display a minimal header panel
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

from werkzeug import html

from lokai.tool_box.tb_common.dates import timetostr, DATE_FORM_DMYHM
from lokai.tool_box.tb_forms.widget import DisplayOnlyWidget
from lokai.lk_worker.ui.methods.base_form import NodeBaseForm

#-----------------------------------------------------------------------

__all__ = ['HeaderPage']

#-----------------------------------------------------------------------

class HeaderPage(NodeBaseForm):

    """ Basic display page to indicate what node is currently the focus
    """
    
    def __init__(self, request, object_reference, data_object, **kwargs):
        self.request = request
        self.up = request.args.get('up', None)
        NodeBaseForm.__init__(self,
                              request,
                              object_reference,
                              data_object,
                              enctype = "multipart/form-data",
                              title = kwargs.get('title', 'Node Header'),
                              perm = 'nde_tasks',
                              use_tokens=False,
                              )

    #-------------------------------------------------------------------
    # Main structure

    def _identify_form_action(self):
        """ Decide on the url that is going to respond to user input.
        """
        # Exept that this is not really a form, and we are not
        # expecting anything. Return None to get a default.
        return None
    
    def build_form(self):
        self.add_composite('detail',
                           title      = self.title,
                           fieldset   = {},
                          )
        self.detail = self.get_widget('detail')
        self.add_form_elements()

    def build_objects(self):
        """ Set up drop down lists such as depend on node type.
        """
        # Nothing to do here
        pass

    def add_form_elements(self):
        self.detail.add(DisplayOnlyWidget, 'dates',
                        title = 'Date',
                        disabled = True,
                        output = 'wide')

    def populate_fields(self):
        # intended to parse the empty form before we populate it 
        self.has_errors()
        #
        title_text = html("%s - " % self.obj_ref) + html.strong("%s" %
                              (str(self.obj and 'nd_node' in self.obj and
                               self.obj['nd_node'].nde_name)))
        
        self.detail.set_title(title_text)
        date_text = "No create or modify information available"
        if self.obj and 'nd_node' in self.obj:
            date_text = html("Created %s, Modified %s"% (
                timetostr(self.obj['nd_node'].nde_date_create, DATE_FORM_DMYHM),
                timetostr(self.obj['nd_node'].nde_date_modify, DATE_FORM_DMYHM)))
        self.detail.get_widget('dates').set_value(date_text)
                     
    def populate_defaults(self):
        # intended to parse the empty form before we populate it 
        self.has_errors()
        pass
    
#-----------------------------------------------------------------------
