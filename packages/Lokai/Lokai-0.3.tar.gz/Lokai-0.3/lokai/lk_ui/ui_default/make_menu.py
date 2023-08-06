# Name:      lokai/lk_ui/ui_default/make_menu.py
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

from lokai.lk_ui.menu_handler import MenuHandler

#-----------------------------------------------------------------------
def make_menu(request):
    """ Build html text for the dynamic main menu. This text will be
        passed to the common page template.

        request: request object

        values: dictionary of values extracted from the url
    """
    mh = MenuHandler(request)
    return mh.render()

#-----------------------------------------------------------------------
