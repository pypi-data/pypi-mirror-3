# Name:      lokai/lk_worker/extensions/data_interface.py
# Purpose:   Define the extension interface for data
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

class IWorkerData(component.Interface):

    def nd_read_query_extend(self, query_in, **kwargs):
        """ Extend the query used to find data for a single node.

            Normally add an entity and a join.
        """
        return query_in

    def nd_read_data_extend(self, query_result, **kwargs):
        """ Extend the data object for a single node.

            Given result list from the query, create a single new entry
            for this data set. The entry is created in a form that can be
            used in an update statement to add to the data boject that is
            passed to code that needs it.

            The query result is a list of data objects. The objects are in
            no particular order, so use this data_extend facility to find
            the object and reference it. The exception to this is that the
            ndNode object is always first.

            It all gets interpreted by the other perts
            of the same extension anyway, so the structure within the new
            entry is up to you.
        """
        return {}

    def nd_write_data_extend(self, new_data_object, old_data_object=None):
        """ Given a data object of the same structure as the extended data
            object produced by _nd_read_data_extend, write the data back
            to the database.

            Normally used for creating new database entries. If the data
            is a set of associated entries, and update is required,
            special action will be needed to handle delete of unwanted
            objects. This can be done by comparing new with old.

            Return a list of text strings, where each text string is an
        audit statement that must be stored in the history for this
        node. The texts are managed and stored by the generic
        aplication.
    
        """
        return []

    def nd_delete_data_extend(self, data_object):
        """ Given a data object, extract the node idx and delete all
            associated data for the node (for this model)

            Data stored on disc is alo deleted.

            Return a list of text strings, where each text string is an
        audit statement that must be stored in the history for the
        _parent_ node. The texts are managed and stored by the generic
        aplication.
        """
        return []

    def nd_validate_data_extend(self, new_data_object, old_data_object):
        """ Given a data obect of the same structure as the extended data
            object produced by _nd_read_data_extend, check the contents
            for reasonableness.

            Designed for use in behind the scenes validation - raise
            errors if problems are found.

            The old object is provided to support validation that depends
            on the previous value.
        """

    def nd_search_query_extend(query_in, filter):
        """ Extend the query used to find data for multiple nodes.

            Normally add an entity and a join, and then add extra
            conditions based on filter entries defined in
            nb_search_form_store.
        """
        return query_in

#-----------------------------------------------------------------------
