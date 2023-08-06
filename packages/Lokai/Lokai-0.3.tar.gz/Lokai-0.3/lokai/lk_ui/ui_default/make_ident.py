# Name:      lokai/lk_ui/ui_default/make_ident.py
# Purpose:   Default identity details
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

import lokai.tool_box.tb_common.configuration as config

#-----------------------------------------------------------------------
def make_ident(request):
    """ Build a dictionary of useful values that can be used by the
        common page template.

        This default version picks up key stuff from the configuration
        file.
    
    """
    user = request.user
    user_name = None
    if user:
        user_name = (
            request.client_session.get('ident',
                                       {'user long name': user})['user long name'])
    all_block = config.get_global_config().get('skin', {})
    context = {'title': all_block.get('title', 'Lokai'),
               'site_name': all_block.get('site_name'),
               'user_name' : user_name,
               }
    context['logo_alt'] = all_block.get('logo_alt', context['site_name'])
    if 'logo_path' in all_block:
        context['logo_path'] =  all_block['logo_path']
    return context

#-----------------------------------------------------------------------
