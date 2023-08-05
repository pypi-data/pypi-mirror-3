# Name:      lokai/tool_box/tb_database/orm_base_object.py
# Purpose:   Provide a dictionary like ORM object for a table
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
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func

#-----------------------------------------------------------------------

class OrmBaseObject(object):
    """ This object is designed to be mapped to a database table.

        Whereas a normal SQL Alchemy mapping object has the columns
        appearing as attibutes, this version supports both attribute
        and dictionary access.

        The object cannot be used unless and until it has been
        registered - see tb_database.ORMRegistry.
    """

    search_fields   = None # Unique fields for searching (without dates)

    def __init__(self, **kwargs):
        pass

    def __setitem__(self, key, value):
        if not key.startswith('_'):
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError, \
                      "Key %s not found in %s" % (
                        str(key),
                        str(self.__class__.__name__))
    
    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        return None

    def __contains__(self, key):
        return hasattr(self, key)

    def get(self, key, default=None):
        if hasattr(self, key):
            return getattr(self, key)
        return default
    
    def get_column_names(self):
        if hasattr(self, '_sa_class_manager'):
            return self._sa_class_manager.keys()
        return [] # Could not find through SQLAlchemy

    def keys(self):
        return self.get_column_names()

    def iteritems(self):
        for key in self.keys():
            yield (key, self.get(key))

    def get_mapped_table(self):
        if hasattr(self, '_sa_class_manager'):
            return self._sa_class_manager.mapper.mapped_table
        return None

    def get_mapped_bind(self):
        if hasattr(self, '_sa_class_manager'):
            return self._sa_class_manager.mapper.mapped_table.metadata.bind
        return None
    
    def as_dict(self):
        """ Return a dict of the fields and values.

            This provides an independent copy of the important bits of
            the object and avoids copying any underlying mapping that
           might suggest that the object can be shared.
        """
        op = {}
        for k,v in self.iteritems():
            op[k] = v
        return op

    def __str__(self):
        attrs = []
        attr_max_len = 0
        for key in self.__dict__:
            if not key.startswith('_'):
                attrs.append((key, getattr(self, key)))
                key_len = len(str(key))
                if key_len > attr_max_len:
                    attr_max_len = key_len
        ret = self.__class__.__name__ + ':' \
            + os.linesep \
            + os.linesep.join('  ' \
                              + x[0] \
                              + (' '*(attr_max_len-len(str(x[0])))) \
                              + ' = ' \
                              + repr(x[1]) for x in attrs)
        return str(ret)
    
#-----------------------------------------------------------------------

class OrmSequencedObject(OrmBaseObject):
    """ Extend the base object to provide a facility for automatically
        generating a sequential ID from a defined sequence.

        The derived table object must be given:

            seq_column = The column in the table to which the sequence
                applies.

            seq_width = The number of characters that the value will have.

            seq_prefix = (Optional) Some text that will appear at the
                start of the returned value.

        The sequence name is either

            {table}_{column}_{prefix}_seq or

            {table}_{column}_seq if no prefix is given

        The serial values are derived from a database defined
        sequence. For PostgreSQL this means using a SEQUENCE object
        and nextval.

        There is probalby a _very_ much better way of doing this.

    """

    seq_width       = None # Number of characters in the result
    seq_prefix      = None # Sequence prefix
    seq_column      = None # Self column that uses sequence

    # Assume the sequence is called by table and column
    # "%s_%s_seq" % (table_name, column_name) 
        
    def get_next_in_sequence(self):
        """ Return the next sequence id using self.seq_key and maybe
            also self.prefix
        """
        if hasattr(self, 'seq_column') and self.seq_column:
            table_name = self.get_mapped_table().name
            source_base = [table_name, self.seq_column]
            if hasattr(self, 'seq_prefix'):
                prefix = self.seq_prefix if self.seq_prefix else ''
                if prefix:
                    source_base.append(prefix)
            source = "%s_seq" % ('_'.join(source_base))
            num =  self.get_mapped_bind().execute(
                select(
                    [func.nextval(source).label('var')]
                    )
                ).fetchone().var
            ret_str = str(prefix)
            ret_str += str(num).zfill(self.seq_width)
            return ret_str
        else:
            raise KeyError, "self.seq_column not provided in %s" % (
                        str(self.__class__.__name__))

    def set_sequence(self, value):
        """ Set the sequence value """
        table_name = self.get_mapped_table().name
        source_base = [table_name, self.seq_column]
        if hasattr(self, 'seq_prefix'):
            prefix = self.seq_prefix if self.seq_prefix else ''
            if prefix:
                source_base.append(prefix)
        source = "%s_seq" % ('_'.join(source_base))
        num =  self.get_mapped_bind().execute(
            select(
                [func.setval(source, value)]
                ))

#-----------------------------------------------------------------------
