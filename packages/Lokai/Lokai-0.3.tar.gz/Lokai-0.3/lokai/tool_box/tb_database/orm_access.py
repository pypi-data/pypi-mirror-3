# Name:      lokai/tool_box/tb_database/orm_access.py
# Purpose:   Packaged access to an SQL Alchemy table
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

from lokai.tool_box.tb_database.orm_interface import DatabaseError, engine

#-----------------------------------------------------------------------

class DatabaseAccess(DatabaseError):
    pass

#-----------------------------------------------------------------------

def get_objects_from_query(query):
    """ Given an engine.session.query(object) return a list of used
        objects.
        
    """
    if hasattr(query, '_mapper_adapter_map'):
        map = query._mapper_adapter_map
        if isinstance(map, dict):
            return map.keys()
    return None

def query_from_row(sla_obj, given_fields):
    """ Support get_row and delete_row """
    if not sla_obj:
        raise DatabaseAccess, (
              "No object supplied to function")
    if not isinstance(given_fields, dict) and not hasattr(dict, '__getitem__'):
        raise DatabaseAccess, (
              "Invalid dictionary supplied to function")
    query = engine.session.query(sla_obj)
    objects = get_objects_from_query(query)
    if not isinstance(objects, list) or len(objects) != 1:
        raise DatabaseAccess, (
              "Could not determine single object from query")
    # Now we have the object
    used_object = objects[0]
    if used_object != sla_obj:
        raise DatabaseAccess, (
              "Query object is different to passed instance")
    # Determine what search fields to use
    used_fields = []
    if (hasattr(used_object, 'seq_column') and
        used_object.seq_column and
        given_fields.get(used_object.seq_column, None)):
        # The object uses a sequence, so we only use that
        used_fields.append(used_object.seq_column)
    if len(used_fields) == 0:
        # Check for search fields
        if hasattr(used_object, 'search_fields') \
           and isinstance(used_object.search_fields, (list, tuple)):
            used_fields = used_object.search_fields
    if len(used_fields) == 0:
        # Still no search fields to check
        raise DatabaseAccess, (
              "No usable search fields found")
    # Find the columns (as we need objects for the filter)
    try:
        object_columns = used_object._sa_class_manager.mapper.columns
    except:
        raise DatabaseAccess, (
              "Could not find columns within object")
    for column in object_columns:
        # Test if column name is in used_fields
        if column.name in used_fields:
            value = given_fields.get(column.name, None)
            # Add the filter as an equals
            query = query.filter(column==value)
    return query

def get_row(sla_obj, given_fields, debug=False):
    """ Read a single row from a table (defined by the SQL Alchemy
        object sla_obj) using entires in a dictionary.

        The key fields are defined in the sla_obj. To do this the
        object must be based on BaseObject.

        Search Criteria:
        
        1. If the object holds an attribute self.seq_column AND the
           dictionary holds a value for that key, the search is based
           on that field.
           
        2. Otherwise the search is based upon a list of fields
           supplied by the object in the attribute self.search_fields.

           If self.seq_column (accidentally) appears in
           self.search_fields, only the self.seq_column is used.

        3. If the search has no fields to check at this point, the
           function raises a DatabaseAccess error.

        4. The dictionary is tested for ALL keys found in the search
           fields and if any key yields None a KeyError is raised.

        A list is returned. The list may be zero length.
    """
    query = query_from_row(sla_obj, given_fields)
    rows = query.all()
    if rows:
        # rows should be one or more objects of type defined in obj
        if not isinstance(rows, (list, tuple)):
            rows = [rows]
        return rows
    # return empty result set
    return []

#-----------------------------------------------------------------------

MUST_EXIST = 1
MUST_NOT_EXIST = 0

def insert_or_update(sla_obj, given_fields, required_existing=None):
    """ Read the database based on the given SQL Alchemy object and
        the dictionary of fields (see get_row).

        If a row is found, update, otherwise insert.

        Returns a list of a single result object (for consistency
        with get_row).

        required_existing ==

            None

                Insert or Update depending on what is found

            0

                There must be zero existing records - insert is the
                only expected option.

                If there is an existing record, return this instead of
                the new record.

            1

                There must be one existing record - update is the
                only expected option.

                If there is no existing record, return an empty list.

    """
    # Much of the validation is going to be done by get_row :-)
    existing_set = get_row(sla_obj, given_fields)
    if len(existing_set) == 0 and required_existing != 1:
        # Insert a new object
        target_object = sla_obj()
        sequence_column = None
        if (hasattr(target_object, 'get_next_in_sequence') and
            hasattr(target_object, 'seq_column')):
            sequence_column = target_object.seq_column
            
        for k in target_object.get_column_names():
            if (sequence_column and  k == sequence_column and
                k not in given_fields):
                # Use a new sequence even if none provided in given fields
                target_object[k] = target_object.get_next_in_sequence()
            else:
                target_object[k] = given_fields.get(k, None)
        engine.session.add(target_object)
        return [target_object]
    elif len(existing_set) == 1 and required_existing != 0:
        # Update
        target_object = existing_set[0]
        sequence_column = None
        if (hasattr(target_object, 'get_next_in_sequence') and
            hasattr(target_object, 'seq_column')):
            sequence_column = target_object.seq_column
        for k, v in given_fields.iteritems():
            if sequence_column and k == sequence_column:
                # The found object sequence is still used
                continue
            elif k in target_object:
                target_object[k] = v
        engine.session.add(target_object)
        return [target_object]
    elif len(existing_set) > 1:
        raise DatabaseAccess, "Found multiple objects when updating"
    #--
    return existing_set

def delete_row(sla_obj, given_fields):
    """ Delete a single row that is fully identified by fields in the
        given set of fields.
    """
    query = query_from_row(sla_obj, given_fields)
    query.delete(synchronize_session='fetch')
    engine.session.flush()

#-----------------------------------------------------------------------

def get_from_row(row, column):
    """ Return a value from the result row of a query by column name
    
        Queries may return aliased columns, an object or even a tuple
        of objects - this function tries to return a value
    """
    # Dependent on the Query used to build u_set we need different
    # methods to determine the value
    #
    # It may be a dictionary or a BaseObject
    if column in row:
        return row[column]
        #>>>>>>>>>>>>>>>>>>>>
    if hasattr(row, column):
        return getattr(row, column)
        #>>>>>>>>>>>>>>>>>>>>
    # It may be a list of objects
    if isinstance(row, (list, tuple)):
        # See if the row contains any objects that might yield 
        # the column we are after
        for obj in row:
            if obj:
                try:
                    return get_from_row(obj, column)
                    #>>>>>>>>>>>>>>>>>>>>
                except (KeyError, TypeError):
                    # Catching TypeError here allows for the
                    # possibility that the item amy be an actual data
                    # item (such as an integer). Obviously that would
                    # not contain what we are looking for.

                    # KeyError is a standard error that get_from_row
                    # returns if it can't find anything
                    continue
    else:
        # Look for table name prefix
        if hasattr(row, '_sa_class_manager'):
            mt = str(row._sa_class_manager.mapper.mapped_table)
            if mt == str(column)[0:len(mt)]:
                return get_from_row(row, str(column)[len(mt)+1:])
                #>>>>>>>>>>>>>>>>>>>>
    raise KeyError

def get_column_value(row, column):
    """ Interface to get_from_row that returns None if nothing
        found instead of raising error.
    """
    try:
        return get_from_row(row, column)
    except KeyError:
        return None

#-----------------------------------------------------------------------
