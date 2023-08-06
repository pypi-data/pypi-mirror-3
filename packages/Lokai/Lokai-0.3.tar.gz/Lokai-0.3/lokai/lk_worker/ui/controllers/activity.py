# Name:      lokai/lk_worker/ui/controllers/activity.py
# Purpose:   Responses to requests for type = 'activity'
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

from lokai.lk_worker.ui.methods.display_page_activity import DisplayPage

import pyutilib.component.core as component
from lokai.lk_worker.ui.controllers.generic import PiGenericController
from lokai.lk_worker.extensions.view_interface import IWorkerView

#-----------------------------------------------------------------------

class IActivityView(IWorkerView):
    pass

#-----------------------------------------------------------------------

from lokai.lk_worker.ui.views.activity import PiActivityView
class ActivityActivityView(PiActivityView):
    component.implements(IActivityView, inherit=True)

from lokai.lk_worker.ui.views.attachments import PiAttachmentsView
class ActivityAttachmentsView(PiAttachmentsView):
    component.implements(IActivityView, inherit=True)

from lokai.lk_worker.ui.views.node import PiNodeView
class ActivityNodeView(PiNodeView):
    component.implements(IActivityView, inherit=True)

from lokai.lk_worker.ui.views.resources import PiResourcesView
class ActivityResourcesView(PiResourcesView):
    component.implements(IActivityView, inherit=True)

from lokai.lk_worker.ui.views.subscribers import PiSubscribersView
class ActivitySubscribersView(PiSubscribersView):
    component.implements(IActivityView, inherit=True)

from lokai.lk_worker.ui.views.tags import PiTagsView
class ActivityTagsView(PiTagsView):
    component.implements(IActivityView, inherit=True)

#-----------------------------------------------------------------------

class PiActivityController(PiGenericController):

    def __init__(self):
        PiGenericController.__init__(self)
        self.name = 'activity'
        self.display_name = 'Activity'
        self.view_interface = component.ExtensionPoint(IActivityView)
        self.display_page = DisplayPage

#-----------------------------------------------------------------------
