# Name:      lokai/lk_worker/tests/structure_helper.py
# Purpose:   Initialise essential data for a common basic structure.
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

import StringIO

import lokai.lk_worker.sys_procs.lk_initial_data as lk_initial_data

#-----------------------------------------------------------------------

yml_input = StringIO.StringIO(
    "function:\n"
    "  sys_user: dummy system admin\n"
    "  nde_tasks: Project Managent using nb\n"
    "  nde_resource: Managing resources using nb\n"
    "  nde_search_full: Able to search all fields\n"
    "  nde_search_text: Able to search some fields\n"
    "\n"
    "role:\n"
    "  Site Administrator:\n"
    "    nde_tasks: 017\n"
    "  lkw_user: \n"
    "    nde_search_text: 000\n"
    "  lkw_manager: \n"
    "    sys_user: 001\n"
    "    nde_tasks: 017\n"
    "    nde_resource: 017\n"
    "    nde_search_full: 001\n"
    "  lkw_task:\n"
    "    nde_tasks: 017\n"
    "    nde_resource: 001\n"
    "    nde_search_full: 001\n"
    "  lkw_view:\n"
    "    nde_tasks: 001\n"
    "\n"
    "user:\n"
    "  fred_0:\n"
    "    password: useless\n"
    "    long_name: Fred Admin\n"
    "    roles:\n"
    "      - [lkw_manager, site]\n"
    "    \n"
    "  fred_1:\n"
    "    password: useless\n"
    "    long_name: Fred Manager\n"
    "    roles:\n"
    "      - [lkw_user, site]\n"
    "    \n"
    "  fred_2:\n"
    "    password: useless\n"
    "    long_name: Fred Worker\n"
    "    email: fred_2@home.com\n"
    "    roles:\n"
    "      - [lkw_user, site]\n"
    "    \n"
    "  fred_3:\n"
    "    password: useless\n"
    "    long_name: Fred Viewer\n"
    "    roles:\n"
    "      - [lkw_user, site]\n"
    "    \n"
    "  fred_4:\n"
    "    password: useless\n"
    "    long_name: Fred Viewer\n"
    "    roles:\n"
    "      - [lkw_user, site]\n"
    "    \n"
    "--- # Document break - force commit of function/role/user data\n"
    "\n"
    "#-----------------------------------------------------------------------\n"
    "# Basic node structure\n"
    "node:\n"
    "  -\n"
    "    nd_node:\n"
    "      nde_name: root \n"
    "      nde_type: generic\n"
    "      nde_description: >-\n"
    "        root node\n"
    "  -\n"
    "    nd_node:\n"
    "      nde_name: Lokai\n"
    "      nde_type: generic\n"
    "      nde_description: >-\n"
    "        Data owned by Lokai\n"
    "    parent: root\n"
    "    nd_resource:\n"
    "      - [fred_1, lkw_manager]\n"
    "  -\n"
    "    nd_node:\n"
    "      nde_name: Other Path\n"
    "      nde_client_reference: OtherPath\n"
    "      nde_type: generic\n"
    "      nde_description: >-\n"
    "        Data owned by someone else\n"
    "    parent: root\n"
    "  - \n"
    "    nd_node:\n"
    "      nde_name: product1\n"
    "      nde_type: generic\n"
    "      nde_client_reference: ProductOne\n"
    "      nde_description: >-\n"
    "        Everything to do with a specific product\n"
    "    parent: \n"
    "      - root\n"
    "      - Lokai\n"
    "    nd_resource:\n"
    "      - [fred_2, lkw_task]\n"
    "  - \n"
    "    nd_node:\n"
    "      nde_name: product2\n"
    "      nde_type: generic\n"
    "      nde_description: >-\n"
    "        Everything to do with a specific product\n"
    "    parent: \n"
    "      - root\n"
    "      - Lokai\n"
    "    nd_resource:\n"
    "      - [fred_2, lkw_task]\n"
    "      - [fred_3, lkw_view]\n"
    "\n"
    "  -\n"
    "    nd_node:\n"
    "      nde_name: data\n"
    "      nde_type: generic\n"
    "      nde_description: >-\n"
    "        Everything to do with data collection for product1.\n"
    "    parent: [root, Lokai, product1]\n"
    "    nd_assignment: {usa_user: fred_2}\n"
    "\n"
    "  -\n"
    "    nd_node:\n"
    "      nde_name: data\n"
    "      nde_type: generic\n"
    "      nde_description: >-\n"
    "        Everything to do with data collection for product2.\n"
    "    parent: [root, Lokai, product2]\n"
    "    nd_resource: \n"
    "      - [fred_3, lkw_task]\n"
    "\n"
    "  -\n"
    "    nd_node:\n"
    "      nde_name: R-P_1-D_2\n"
    "      nde_type: generic\n"
    "      nde_description: >-\n"
    "        Another data node for Product 1.\n"
    "    parent: [root, Lokai, product1]\n"
    "    nd_resource: \n"
    "      - [fred_4, lkw_manager]\n"
    )

#-----------------------------------------------------------------------

def make_initial_nodes_and_users():

    class Options(object):
        pass
    options = Options()
    yml_input.seek(0)
    options.file = yml_input
    options.ignore = False
    
    ids = lk_initial_data.InitialDataSet(options)

#-----------------------------------------------------------------------
