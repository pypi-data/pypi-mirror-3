# Name:      lokai/tool_box/tb_common/email_address_list.py
# Purpose:   EmailAddressList object
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

import email.utils
import types

class EmailAddressList(object):
    """ EmailAddressList object

        Instatiate with a comma delimited string from, say, a
        configuration file.

        Get back lists of addresses that can be used in smtplib or,
        possibly, elsewhere.

        Add addresses singly to the list.

        Addresses are parsed for validity.
    """

    def __init__(self, given_data=[]):
        """ Loop through the content of the given data and append to
            internal data.
        """
        self._tpl_list = []
        self._real_map = {}
        
        self.append(given_data)

    def append(self, given_data):
        """ Parse a possibly multiple address and append it to the
            internal list.

            Ignore it if the real address is already there.
        """
        if isinstance(given_data, types.StringTypes):
            given_list = [given_data]
        else:
            given_list = given_data
        parsed_thing_list = email.utils.getaddresses(given_list)
        for parsed_thing in parsed_thing_list:
            name_part, real_part = parsed_thing
            if ((name_part and not real_part) or
                (real_part and '@' not in real_part)):
                raise ValueError("No valid address found in %s" % given_data)
            if real_part and real_part not in self._real_map:
                self._tpl_list.append(parsed_thing)
                self._real_map[real_part] = parsed_thing[0]

    def __len__(self):
        return len(self._tpl_list)

    @property
    def as_list(self):
        """ Return a list of formatted addresses"""
        op = []
        for found_thing in self._tpl_list:
            op.append(email.utils.formataddr(found_thing))
        return op

    @property
    def parsed(self):
        """ Return a list of parsed tuples """
        return self._tpl_list

#-----------------------------------------------------------------------
