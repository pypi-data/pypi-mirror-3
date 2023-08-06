# Name:      lokai/lk_ui/tests/trial_publisher.py
# Purpose:   A publisher application place holder
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

from werkzeug import Response, ClosingIterator

#-----------------------------------------------------------------------

TRIAL_PAGE = (
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"\n'
    '      "http://www.w3.org/TR/html4/strict.dtd">\n'
    '<html>\n'
    '<head>\n'
    '<title>Lokai Testing</title>\n'
    '</head>\n'
    '<body>\n'
    '<p>Welcome to the Lokai test page</p>\n'
    '</body>\n'
    )
#-----------------------------------------------------------------------

class Publisher(object):

    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        response = Response(TRIAL_PAGE)
        return ClosingIterator(response(environ, start_response)
                               )

#-----------------------------------------------------------------------

publisher = Publisher()

def get_trial_publisher():
    return publisher

#-----------------------------------------------------------------------

menu_builder = [
    {'title': 'Main Menu',
     'children': [
         {'title': 'Sub Menu 1',
          'link': '/u/r/l/1',
          },
         {'title': 'Sub Menu 2',
          'link': '/u/r/l/2',
          'position': 20,
          },
         ]
     }
    ]

#-----------------------------------------------------------------------
