# Name:      lokai/tool_box/tb_common/file_handling.py
# Purpose:   Tools for handling files
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

#-----------------------------------------------------------------------

def ordered_walk(target_name, reverse=False):
    """ Walk depth first through a directory tree, sort each level as
        it is reached.

        Directories sorted separately from files!

        Yield a path to a file.

        The returned path is relative to the give target_name
    """
    name_list = os.listdir(target_name)
    dirs, nondirs = [], []
    for name in name_list:
        if os.path.isdir(os.path.join(target_name, name)):
            dirs.append(name)
        else:
            nondirs.append(name)
    for dir_next in sorted(dirs, reverse=reverse):
        path = os.path.join(target_name, dir_next)
        for result in ordered_walk(path, reverse):
            yield os.path.join(dir_next, result)
    for file_next in sorted(nondirs, reverse=reverse):
        yield file_next

#-----------------------------------------------------------------------
