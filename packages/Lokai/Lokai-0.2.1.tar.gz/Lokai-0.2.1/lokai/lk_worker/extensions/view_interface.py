# Name:      lokai/lk_worker/extensions/view_interface.py
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

#-----------------------------------------------------------------------

class IWorkerView(component.Interface):

    def nd_view_selection_lists(self):
        """ Return a dictionary of selection map objects.
        """
        return {}

    def nd_view_form_extend(self, form):
        """ Add some elements to the form.

            form.detail defines a container object that should be used to
            contain your new elements.

            Use widgets as required.

            Put the new elements inside a fieldset (inside container) for stylistic
            consistency.
        """
        pass

    def nd_view_form_populate(self, form):
        """ Put values into the widgets created in nb_view_form_extend.

            Works with an **existing** dataset.
            
            The 'form' object contains form.obj, which is a
            dictionary with some elements under your control - see
            nb_read_data_extend.

            form.obj_ref is the identifier of the node we are working on.

            The form can be further extended here to allow for varaible
            length data sets.
        """
        pass

    def nd_view_form_default(self, form):
        """ Put values into the widgets created in nb_view_form_extend.

            Works with a **new** dataset.
            
            The 'form' object contains form.obj, which is a
            dictionary with some elements under your control - see
            nb_read_data_extend.

            form.obj_ref is the identifier of the node we are working on.

            The form can be further extended here to allow for varaible
            length data sets.
        """
        pass
        
    def nd_view_form_process(self, form):
        """ Validate user input.

            If any field has an error the error text must be stored in the
            error attribute of a relevant widget.

            Return a single value; the count of errors found.
        """
        return 0

    def nd_view_form_store(self, form):
        """ Store the values in the form into the database.

            Do _not_ commit. This is done elsewhere.

            Return a list of text strings, where each text string is an
            audit statement that must be stored in the history for this
            node. The texts are managed and stored by the generic
            aplication.

            the 'form' object contains:

            form.obj_ref: the node nde_idx for the owning node.

            form.obj: the current result of get_node_dataset. If this is
            None or empty then the store action is for a new node.

            form.detail: a composite widgert that contains the whole form
            to be processed.
        """
        return []

    def nd_display_main(self, form):
        """ Provide some text that can appear in the main body of the
            display page.

            Return a list of text elements that can be joined together
            by the caller.

            Text output is HTML.

            The 'form' object contains form.obj, which is a
            dictionary with some elements under your control - see
            nb_read_data_extend.

       """
        return []

    def nd_display_side(self, form):
        """ Provide some text that can appear in the side bar of the
            display page.

            Return a list of text elements that can be joined together
            by the caller.

            Text output is HTML.

            The 'form' object contains form.obj, which is a
            dictionary with some elements under your control - see
            nb_read_data_extend.

        """
        return []

#-----------------------------------------------------------------------
