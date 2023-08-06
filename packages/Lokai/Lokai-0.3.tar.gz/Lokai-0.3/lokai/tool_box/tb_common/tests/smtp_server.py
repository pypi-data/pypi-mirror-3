#! /usr/bin/python
# Name:      lokai/tool_box/tb_common/tests/smtp_server.py
# Purpose:   Local smtp service for testing
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

#
# Wait for messages - Print to a given file - Append or overwrite
#
#-----------------------------------------------------------------------

import asyncore
import smtpd
import inspect

def path_to_server():
    return inspect.getsourcefile(path_to_server)

class PrintingServer(smtpd.SMTPServer):

    def __init__(self, localport, target_file, append):
        self.append = append
        self.target_file = target_file
        smtpd.SMTPServer.__init__(self, ("localhost", localport), None)
        
    def process_message(self, peer, mailfrom, rcpttos, data):
        
        op = open(self.target_file, 'a' if self.append else 'w')
        inheaders = 1
        lines = data.split('\n')
        for line in lines:
            if inheaders and not line:
                op.write('X-Peer: %s\n' % peer[0])
                op.write('X-From: %s\n' % mailfrom)
                op.write('X-To: %s\n' % str(rcpttos))
                inheaders = 0
            op.write("%s\n" % line)

def main(target_file, smtp_port, append):
    server = PrintingServer(localport=smtp_port,
                            target_file=target_file,
                            append=-append)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass

    
if __name__ == '__main__':
    import optparse
    import os
    
    parser = optparse.OptionParser()
    parser.add_option("-t", "--target",
                      dest = "target_file",
                      help = "Save messages to here")
    parser.add_option("-a", "--append",
                      dest = "append",
                      action = "store_true")
    parser.add_option("--port",
                      dest = "smtp_port",
                      type = 'int',
                      help = "Post for server to listen on")

    parser.set_defaults(smtp_port=8025, append=False)
    (options, args) = parser.parse_args()

    main(options.target_file, options.smtp_port, options.append)

#-----------------------------------------------------------------------
    
