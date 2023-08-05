# Name:      lokai/lk_worker/ui/controllers/generic_view_maps.py
# Purpose:   Map appropriate views to the IWorkerView interface
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

import pyutilib.component.core as component
from lokai.lk_worker.extensions.view_interface import IWorkerView

#-----------------------------------------------------------------------

from lokai.lk_worker.ui.views.activity import PiActivityView
class GenericActivityView(PiActivityView):
    component.implements(IWorkerView, inherit=True)

from lokai.lk_worker.ui.views.attachments import PiAttachmentsView
class GenericAttachmentsView(PiAttachmentsView):
    component.implements(IWorkerView, inherit=True)

from lokai.lk_worker.ui.views.node import PiNodeView
class GenericNodeView(PiNodeView):
    component.implements(IWorkerView, inherit=True)

from lokai.lk_worker.ui.views.resources import PiResourcesView
class GenericResourcesView(PiResourcesView):
    component.implements(IWorkerView, inherit=True)

from lokai.lk_worker.ui.views.subscribers import PiSubscribersView
class GenericSubscribersView(PiSubscribersView):
    component.implements(IWorkerView, inherit=True)

from lokai.lk_worker.ui.views.tags import PiTagsView
class GenericTagsView(PiTagsView):
    component.implements(IWorkerView, inherit=True)

#-----------------------------------------------------------------------
