# Name:      lokai/lk_ui/file_responder.py
# Purpose:   Return a file as a Response object
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

import os
from datetime import datetime
import mimetypes
from werkzeug import Headers, Response, http_date
import lokai.tool_box.tb_common.notification as notify

#-----------------------------------------------------------------------

def getFileResponse(file_path, stream=None,
                    mime_type=None,
                    fallback_mimetype='text/plain'):
    """ Given a path to a file, build a Response object that
        returns the file with proper headers.

        :file_path: relative or absolute path to file

        :mime_type: force use of this mimetype if given
        
        :fallback_mimetype: optional mimetype to use if we can't
            identify it from the file. Deafult 'text/plain'.
        
        We don't support e-tags.
    """
    actual_path = os.path.abspath(file_path)
    actual_name = os.path.basename(actual_path)
    
    if mime_type:
        actual_mime_type = mime_type
    else:
        guessed_type = mimetypes.guess_type(actual_path)
        actual_mime_type = guessed_type[0] or fallback_mimetype
    if stream:
        actual_source = stream
        try:
            file_size = stream.len
        except:
            file_size = 0
        mtime = datetime.now()
    else:
        actual_source = open(actual_path, 'r')
        file_size = os.path.getsize(actual_path)
        mtime = datetime.utcfromtimestamp(os.path.getmtime(actual_path))
    hh = Headers()
    hh.add('content-type', actual_mime_type)
    hh.add('content-length', file_size)
    hh.add('last-modified', mtime)
    hh.add('Content-Disposition', 'attachment', filename=actual_name)
    response = Response(headers=hh)
    for block in actual_source:
        response.stream.write(block)
    return response

#-----------------------------------------------------------------------
