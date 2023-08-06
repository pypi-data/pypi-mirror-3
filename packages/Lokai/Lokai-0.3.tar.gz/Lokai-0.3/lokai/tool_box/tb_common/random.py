# Name:      lokai/tool_box/tb_common/random.py
# Purpose:   Define randbytes
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

# based on:
# """$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/quixote/util.py $
# $Id: form.py, v 1.14 2007/01/31 09:46:59 mark Exp $
#
# Provides the Form class and related classes.  Forms are a convenient
# way of building HTML forms that are composed of Widget objects.
#
#-----------------------------------------------------------------------

import os
import binascii

if hasattr(os, 'urandom'):
    # available in Python 2.4 and also works on win32
    def randbytes(bytes):
        """Return bits of random data as a hex string."""
        return binascii.hexlify(os.urandom(bytes))

elif os.path.exists('/dev/urandom'):
    # /dev/urandom is just as good as /dev/random for cookies (assuming
    # SHA-1 is secure) and it never blocks.
    def randbytes(bytes):
        """Return bits of random data as a hex string."""
        return binascii.hexlify(open("/dev/urandom").read(bytes))

else:
    # this is much less secure than the above function
    import sha
    class _PRNG:
        def __init__(self):
            self.state = sha.new(str(time.time() + time.clock()))
            self.count = 0

        def _get_bytes(self):
            self.state.update('%s %d' % (time.time() + time.clock(),
                                         self.count))
            self.count += 1
            return self.state.hexdigest()

        def randbytes(self, bytes):
            """Return bits of random data as a hex string."""
            s = ""
            chars = 2*bytes
            while len(s) < chars:
                s += self._get_bytes()
            return s[:chars]

    randbytes = _PRNG().randbytes

#-----------------------------------------------------------------------
