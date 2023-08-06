# Name:      lokai/tool_box/tb_job_manager/utils.py
# Purpose:   Some useful things to help application programs.
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
import types

#-----------------------------------------------------------------------

def root_path():
    path_here = __file__
    upper_path = os.path.dirname(path_here)
    return upper_path

class ParamFile(object):

    def __init__(self, file_path):
        self._read_param_file(file_path)
        
    def _read_param_file(self, file_path):
        """ Read and execute the given file. Transfer result to our
            attributes. Avoid overwriting our methods.
        """
        dummy_global = {}
        argset = {}
        execfile(file_path, dummy_global, argset)
        for key, value in argset.iteritems():
            try:
                obj = getattr(self, key)
                if inspect.ismethod(obj):
                    continue
                setattr(self, key, value)
            except AttributeError:
                setattr(self, key, value)

def source_param_dir(working_directory='./',
                     general_param_file='job_environment.conf',
                     app_param_path=None):
    """ Find the path to the parameter file for the given app_name.

        This is a general tool that can be used by applications to
        find a path to give to a ParamFile object.
    """
    target_dir = app_param_path
    if not target_dir:
        job_conf = ParamFile(os.path.abspath(
            os.path.expanduser(
                os.path.join(
                    working_directory,
                    general_param_file
                    ))))
        if hasattr(job_conf, 'app_param_path'):
            target_dir = job_conf.app_param_path
        else:
            target_dir = 'job_environment.d'
    target_dir = os.path.abspath(
        os.path.expanduser(
            os.path.join(
                working_directory,
                target_dir,
                )))
    return target_dir
    
#-----------------------------------------------------------------------
