# Name:      lokai/lk_common/selection_map.py
# Purpose:   Provides facilities for lists of data/display pairs
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

#-----------------------------------------------------------------------

from sqlalchemy import *

from lokai.tool_box.tb_database.orm_interface import engine

#-----------------------------------------------------------------------

class SelectionMap(object):
    """ Aimed primarily at supporting drop-down lists in
        displays. Also useful for data validation and reporting.

        ss = SelectionMap(object=None, **kwargs)

            object = sql alchemy object that is used to select stuff.

                The content of the object is described in the
                following 4 arguments.

            field_operator_list = list or tuple of triples, where each
                triple is (field name, operator, field value)

            order_list = list of (field name, asc/desc) pairs

            key_field = field name

            display_field = field_name

            found_data = list of tuples (store value, display value)

                   If found_data is given, database related arguments
                   are ignored.

        ss.get_options() returns a set of triples that can be used as a value
                  for a selection widget.

        ss.get_value(key) returns the display value for the given key

        ss.get_back_value(display) returns the key for the given display text

    """

    def __init__(self, **kwargs):
        self.data_object = kwargs.get('data_object', None)
        self.found_data = kwargs.get('found_data', None)
        self.fld_op_list = kwargs.get('field_operator_list', ())
        self.order_list = kwargs.get('order_list', ())
        self.key_field = kwargs.get('key_field', None)
        self.display_field = kwargs.get('display_field', None)
        self.set = None
        self.data = None

    def build_data(self):
        """ Read the content of the selection from a table in the database """
        # can override this to be more complex
        #
        qy = engine.session.query(self.data_object)
        for fop in self.fld_op_list:
            if hasattr(self.data_object, fop[0]):
                target = getattr(self.data_object, fop[0])
                value = fop[2]
                operator = fop[1]
                #
                # There must be a better way!
                if operator in ['=', '==']:
                    qy = qy.filter(target == value)
                elif operator in ['!=', '<>']:
                    qy = qy.filter(target != value)
                elif operator == '<':
                    qy = qy.filter(target < value)
                elif operator == '>':
                    qy = qy.filter(target > value)

        for ol in self.order_list:
            if hasattr(self.data_object, ol[0]):
                target = getattr(self.data_object, ol[0])
                operator = ol[1]
                if operator in ['ASC', 'asc']:
                    qy = qy.order_by(target.asc())
                elif operator in ['DSC', 'dsc']:
                    qy = qy.order_by(target.desc())
        self.data = qy.all()

    def build_set(self):
        if self.set is not None:
            return
        if self.found_data is not None:
            self.set = []
            for op in self.found_data:
                self.set.append((op[0], op[1], op[0]))
        elif self.key_field and self.display_field:
            if not self.data:
                self.build_data()
            self.set = []
            for row in self.data:
                key = getattr(row, self.key_field)
                display = getattr(row, self.display_field)
                if not display:
                    display = key
                self.set.append((key, display, key))

    def get_options(self, prepends=None, appends=None):
        self.build_set()
        if isinstance(prepends, list):
            op = prepends[:]
        else:
            op = [(u'', u'Select Below', u'')]
        op.extend(self.set)
        if isinstance(appends, list):
            op.extend(appends)
        return op

    def get_value(self, key):
        self.build_set()
        for row in self.set:
            if row[2] == key:
                return row[1]
        return None

    def get_back_value(self, key):
        self.build_set()
        try_val = key
        if hasattr(try_val, 'lower'):
            try_val = try_val.lower()
        for row in self.set:
            match = row[1]
            if hasattr(match, 'lower'):
                match = match.lower()
            if try_val == match:
                return row[2]
        return None

#-----------------------------------------------------------------------
