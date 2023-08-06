# Name:      lokai/lk_worker/ui/main_controller.py
# Purpose:   connect URL to worker pages
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

""" Map URL forms to the controller interfaces.

    Check basic permissions when a URL is matched.

    The detailed work is done elswhere. This module is more readable
    by being limited to the two functions described, and anyway makes
    it easy for the same controller to be used for more than one URL
    form.
"""
#-----------------------------------------------------------------------

from lokai.lk_worker.ui.local import expose, is_allowed, check_guest_access

#-----------------------------------------------------------------------

from lokai.lk_worker.ui.pages import (node_display,
                                      node_properties,
                                      node_add,
                                      node_update,
                                      node_insert,
                                      node_list,
                                      node_list_post,
                                      node_add,
                                      node_default_view,
                                      node_link,
                                      node_unlink,
                                      node_new_resource,
                                      node_download_file,
                                      node_collection,
                                      node_set_filter,
                                      )

#-----------------------------------------------------------------------

@expose("/<object_id>")
@is_allowed([{'nde_tasks': 'read'}])
def display(request):
    request.derived_locals['current_target'] = 'display'
    return node_display(request)

@expose("/<object_id>/default", methods=['GET'])
@expose("/<object_id>/", methods=['GET'])
@is_allowed([{'nde_tasks': 'read'}])
def default(request):
    # Need to be sure that the default view is not an edit view!
    request.derived_locals['current_target'] = 'default'
    return node_default_view(request)

@expose("/<object_id>/edit", methods=['GET'])
@is_allowed([{'nde_tasks': 'edit'}])
def edit(request):
    request.derived_locals['current_target'] = 'edit'
    return node_properties(request)

@expose("/<object_id>/edit", methods=['POST'])
@is_allowed([{'nde_tasks': 'edit'}])
def edit_post(request):
    request.derived_locals['current_target'] = 'edit'
    return node_update(request)

@expose("/<object_id>/add", methods=['GET'])
@is_allowed([{'nde_tasks': 'add'}])
def add(request):
    request.derived_locals['current_target'] = 'add'
    return node_add(request)

@expose("/<object_id>/add", methods=['POST'])
@is_allowed([{'nde_tasks': 'add'}])
def add_post(request):
    request.derived_locals['current_target'] = 'add'
    return node_insert(request)

@expose("/add", methods=['GET'])
@is_allowed([{'nde_tasks': 'add'}])
def add_top(request):
    request.derived_locals['current_target'] = 'add'
    return node_add(request)

@expose("/add", methods=['POST'])
@is_allowed([{'nde_tasks': 'add'}])
def add_top_post(request):
    request.derived_locals['current_target'] = 'add'
    return node_insert(request)

@expose("/<object_id>/list", methods=['GET'])
@is_allowed([{'nde_tasks': 'read'}])
def list(request):
    request.derived_locals['current_target'] = 'list'
    return node_list(request)

@expose("/<object_id>/list", methods=['POST'])
@is_allowed([{'nde_tasks': 'read'}])
def list_post(request):
    request.derived_locals['current_target'] = 'list'
    return node_list_post(request)

@expose("/<object_id>/search", methods=['GET'])
@is_allowed([{'nde_search_full': 'read'}, {'nde_search_text': 'read'}])
def search(request):
    request.derived_locals['current_target'] = 'search'
    return node_collection(request)

@expose("/<object_id>/search", methods=['POST'])
@is_allowed([{'nde_search_full': 'read'}, {'nde_search_text': 'read'}])
def search_post(request):
    request.derived_locals['current_target'] = 'search'
    return node_set_filter(request)

@expose("/search", methods=['GET'])
def search_top(request):
    perm = [{'nde_search_full': 'read'}, {'nde_search_text': 'read'}]
    check_guest_access(request, perm)
    request.derived_locals['current_target'] = 'search_top'
    return node_collection(request)

@expose("/search", methods=['POST'])
def search_top_post(request):
    perm = [{'nde_search_full': 'read'}, {'nde_search_text': 'read'}]
    check_guest_access(request, perm)
    request.derived_locals['current_target'] = 'search_top'
    return node_set_filter(request)

@expose("/<object_id>/link")
@is_allowed([{'nde_tasks': 'edit'}])
def link(request):
    request.derived_locals['current_target'] = 'link'
    return node_link(request)

@expose("/<object_id>/unlink")
@is_allowed([{'nde_tasks': 'edit'}])
def unlink(request):
    request.derived_locals['current_target'] = 'unlink'
    return node_unlink(request)

@expose("/<object_id>/resource")
@is_allowed([{'nde_resource': 'edit'}])
def add_resource(request):
    request.derived_locals['current_target'] = 'resource'
    return node_new_resource(request)

@expose("/<object_id>/file/<file_path>")
@is_allowed([{'nde_tasks': 'read'}])
def get_file(request):
    request.derived_locals['current_target'] = 'get_file'
    return node_download_file(request)

@expose('/error', methods=['GET'])
def raise_error(request):
     assert False
     return None

#-----------------------------------------------------------------------
