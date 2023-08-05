# Name:      lokai/lk_worker/models/lk_register_extensions.py
# Purpose:   Register basic types and some data extensions
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

def lk_register_types():
    # Don't need anything here. The activity type is imported with the
    # model, and the generic type is imported with any other type.
    pass

def lk_register_models():
    import lokai.lk_worker.models.builtin_data_activity
    import lokai.lk_worker.models.builtin_data_tags
    import lokai.lk_worker.models.builtin_data_resources
    import lokai.lk_worker.models.builtin_data_attachments
    import lokai.lk_worker.models.builtin_data_subscribers
    import lokai.lk_worker.models.node_permission

#-----------------------------------------------------------------------
