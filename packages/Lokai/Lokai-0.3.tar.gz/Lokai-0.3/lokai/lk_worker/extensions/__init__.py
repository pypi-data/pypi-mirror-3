# Name:      lokai/lk_worker/extensions/__init__.py
# Purpose:   Define things for extensions
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

""" This module contains:

    An extension mananger that can be used to import packages based on
    values in the configuration file.

    A set of interface definitions.

"""
class PluginIdCompare(object):
    """ MixIn class to provide ordering on self.id """
    
    def __lt__(self, other): 
        return self.id < other.id 
	 
    def __leq__(self, other): 
        return self.id <= other.id 

    def __eq__(self, other): 
        return self.id == other.id 

    def __hash__(self): 
        return self.id 
