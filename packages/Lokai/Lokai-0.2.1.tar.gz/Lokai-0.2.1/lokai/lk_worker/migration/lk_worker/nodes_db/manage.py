# Name:      lokai/lk_worker/migration/lk_worker/nodes_db/manage.py
# Purpose:   Manage versioning of the database 
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

""" The two folders above define the component and item within the
    .ini file for accessing the database
            
     Usage    : manage.py version_control (create version table in db)
                manage.py upgrade [--version=N]
                manage.py downgrade --version=N

              : The additional trigger ini=my_file / ini my_file / my_file.ini
                can be used to designate the ini file to use 
"""
#-----------------------------------------------------------------------
    
import os.path
from migrate.versioning.shell import main

from lokai.tool_box.tb_common.configuration import (handle_ini_declaration,
                                              get_global_config,
                                              )
handle_ini_declaration(prefix='lk')

from lokai.lk_worker.models import model

repo_path = os.path.dirname(os.path.abspath(__file__))
group_path, item_name= os.path.split(repo_path)
migrate_path, group_name = os.path.split(group_path)

configuration = get_global_config()
#model.init()

main(url=get_global_config()[group_name][item_name]['url'],
     repository=repo_path)

#-----------------------------------------------------------------------
