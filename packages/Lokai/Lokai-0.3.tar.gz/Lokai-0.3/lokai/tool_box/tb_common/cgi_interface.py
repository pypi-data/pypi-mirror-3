# Name:      lokai/tool_box/tb_common/cgi_interface.py
# Purpose:   Tool(s) to help with cgi data
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

def from_cgi(dict, key, default=None):
    """ Return the value found in dict using key. If the value is a
        list, return only the first element of the list.

        This is required because the cgi parser that is used to
        extract the filter from the url gives a list for each named
        value, whereas the original dictionary does not have such
        lists. search_filtered can be called from different places,
        and it may be passed the original or a decoded version of the
        filter.
    """
    op = dict.get(key, default)
    if isinstance(op, (type([]), type(()))):
        if len(op):
            return op[0]
        else:
            return default
    else:
        return op

#-----------------------------------------------------------------------
