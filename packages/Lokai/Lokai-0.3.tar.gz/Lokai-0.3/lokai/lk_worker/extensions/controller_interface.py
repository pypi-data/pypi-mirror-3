# Name:      lokai/lk_worker/extensions/controller_interface.py
# Purpose:   Define the extension interface for the user interface
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

from lokai.lk_worker.nodes.graph import is_cycle

#-----------------------------------------------------------------------

class IWorkerController(component.Interface):

    function_tabs = [
        ('display', 'Display'),
        ('edit', 'Detail', [{'nde_tasks': 'edit'}]),
        ('list', 'List'),
        ('search', 'Search'),
        ]

    list_only_tabs = [
        ('add', '+Node', [{'nde_tasks': 'add'}], {'type': 'generic'}),
        ]

    def nd_controller_tabs(self, request, object_reference):
        """ Return a list of link/name/permission tuples that can be
            used to navigate to different functions for the given
            type.
        """
        self.current_target = request.derived_locals['current_target']
        if self.current_target == 'list':
            new_child = request.args.get('down')
            if not new_child:
                op = []
                op.extend(self.list_only_tabs)
                op.extend(self.function_tabs)
            else:
                if not is_cycle(new_child, object_reference):
                    query = {'object_id': new_child,
                             'up': object_reference,
                             'down': None}
                    op = [
                        ('link', 'Return', [], query)
                        ]
                else:
                    query = {'object_id': new_child,
                             'down': None}
                    op = [
                        ('default', 'Return', [], query)
                        ]
            return op
        else:
            if object_reference and object_reference != '**new**':
                return self.function_tabs
        return []

    def nd_controller_display_name(self):
        """ Return a string for display """
        return self.display_name

    def nd_controller_hidden(self):
        """ Return True if this controller type should not be visible
            in node type selection situations.

            Uses a 'hidden' attribute that can be True or False. If
            the 'hidden' attribute is not present then the extension
            is _not_ hidden.
        """
        try:
            return self.hidden
        except:
            return False

    def nd_view_selection_lists(self):
        """ Amalgamate all the selection lists from the underlying views """
        selection_set = {}
        for extn in self.view_interface:
            selection_set.update(extn.nd_view_selection_lists())
        return selection_set
            
    def nd_controller_display_edit(self, request,
                                   object_reference, data_object):
        """ Present a screen of editable fields (permissions allowing)
            that is used to modify an existing object.
        """
        pass

    def nd_controller_display_add(self, request,
                                  object_reference, data_object):
        """ Present a screen of editable fields (permissions allowing)
            that is used to create a new object.

            oject_reference <= **new**

            data_object = {}
        """
        pass

    def nd_controller_respond_update(self, request,
                                     object_reference, data_object):
        """ Given a form POST response, update the database and redirect
            to the edit page.
        """
        pass

    def nd_controller_respond_insert(self, request,
                                     object_reference, data_object):
        """ Given a form POST response, insert a new item into the
            database and redirect to the edit page.
        """
        pass

    def nd_controller_display_formatted(self, request,
                                        object_reference, data_object):
        """ Display a page of static text based on the given object.
        """
        pass

    def nd_controller_display_list(self, request,
                                   object_reference, data_object):
        """ Display a list of children for the given node.
        """
        pass

    def nd_controller_update_list(self, request,
                                   object_reference, data_object):
        """ Update from a (editable) list of children for the given
            node.
        """
        pass

    def nd_controller_display_default(self, request,
                                      object_reference, data_object):
        """ Call one of the other display functions depending on what
            might be considered the default for this type.
        """
        return self.nd_controller_display_formatted(
            request, object_reference, data_object)

    def nd_controller_download_file(self, request,
                                    object_reference, data_object):
        """ Return an attachment based on the component from the url
        """
        pass

#-----------------------------------------------------------------------
