# Name:      lokai/lk_worker/ui/controllers/presentation.py
# Purpose:   Responses to requests for type = 'presentation'
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

import lokai.tool_box.tb_common.notification as notify

import pyutilib.component.core as component

#-----------------------------------------------------------------------

from lokai.lk_worker.ui.controllers.text import PiTextController

#-----------------------------------------------------------------------

PRESENTATION_TEMPLATE = 'lk_worker_app_presentation.html'

#-----------------------------------------------------------------------

class PiPresentationController(PiTextController):

    navigation_template = PRESENTATION_TEMPLATE
    
    def __init__(self):
        PiTextController.__init__(self)
        self.name = 'presentation'
        self.display_name = 'Presentation'
    
#-----------------------------------------------------------------------
