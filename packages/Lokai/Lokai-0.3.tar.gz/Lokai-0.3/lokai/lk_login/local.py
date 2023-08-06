# Name:      lokai/lk_login/local.py
# Purpose:   connect URL to login pages
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

from werkzeug import Local, LocalManager
from werkzeug.routing import Map

import lokai.tool_box.tb_common.configuration as config

import lokai.lk_ui.utils as utils
import lokai.lk_ui

#-----------------------------------------------------------------------

APPLICATION_NAME = 'login'

APPLICATION_PATH = None

APPLICATION_SCHEME = None

#-----------------------------------------------------------------------

local = Local()
local_manager = LocalManager([local])
publisher = local('publisher')

#-----------------------------------------------------------------------

url_map = Map()
url_adapter = None

def get_adapter():
    global url_adapter
    if not url_adapter:
        global APPLICATION_PATH
        APPLICATION_PATH = config.get_global_config(
            ).get(
            APPLICATION_NAME, {}
            ).get(
            'application_path')
        if APPLICATION_PATH and APPLICATION_PATH[0] != '/':
            APPLICATION_PATH = '/'+APPLICATION_PATH
        global APPLICATION_SCHEME
        APPLICATION_SCHEME = config.get_global_config(
            ).get(APPLICATION_NAME, {}).get(
            'application_scheme', 'http')
        url_adapter = url_map.bind(lokai.lk_ui.ServerName,
                                   APPLICATION_PATH,
                                   None,
                                   APPLICATION_SCHEME,
                                   )
    return url_adapter

expose = utils.make_expose(url_map)
url_for = utils.make_url_for(get_adapter)

#-----------------------------------------------------------------------
