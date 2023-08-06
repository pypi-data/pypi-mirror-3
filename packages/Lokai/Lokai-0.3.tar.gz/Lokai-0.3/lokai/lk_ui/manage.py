#!/usr/bin/ python
# Name:      lokai/lk_ui/manage.py
# Purpose:   
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

from werkzeug import script

def make_app():
    from lokai.lk_ui.publisher import Lokai
    return Lokai

action_runserver = script.make_runserver(make_app, use_reloader=True)

script.run()

#-----------------------------------------------------------------------
