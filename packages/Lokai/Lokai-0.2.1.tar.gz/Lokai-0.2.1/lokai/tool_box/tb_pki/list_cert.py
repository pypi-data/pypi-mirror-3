# Name:      lokai/tool_box/tb_pki/list_cert.py
# Purpose:   Tools to generate and manage public/private key pairs
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

""" Command line interface to te PKI object. specifically for listing
    details of a certificate or certificate set.
"""

#-----------------------------------------------------------------------

import optparse
import os

from lokai.tool_box.tb_pki.pki import PKCertSet

#-----------------------------------------------------------------------

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.description = "List details for PKI certificates"
    parser.usage = "%prog [options] node_name"
    parser.add_option('-e', '--ssl-env',
                      dest = 'ssl_environment',
                      help = ('Directory containing the required '
                              'sub-directories (see --target and '
                              '--authority). '
                              'Defaults to current working directory.')
                      )
    parser.add_option('-t', '--target',
                      dest = 'target',
                      help = ('Name (not a path) of the directory where '
                              'the certificate will be generated. '
                              'It contains the dn and previously '
                              'generated files. '
                              'If this is the same as the --authority '
                              'then a self-signed certificate is generated.'
                              'Required')
                      )
    parser.add_option('-s', '--serial',
                      dest = 'serial',
                      help = ('Integer value of serial number for '
                              'certificate to be displayed. '
                              'Optional.')
                      )
    parser.add_option('-a', '--all',
                      dest = 'list_all',
                      action = 'store_true',
                      help = ('Show details of all certificates. '
                              'The default shows the active certificate only '
                              'Optional.')
                      )
    parser.add_option('-v', '--verbose',
                      dest = 'talk_talk',
                      help = "Request some feed back from the process",
                      action = 'count'
                      )
    parser.add_option('-n',
                      dest = 'do_nothing',
                      help = 'Do nothing',
                      action = 'store_true'
                      )
    parser.set_defaults(ssl_environment='.', list_all=False)

    (options, args) = parser.parse_args()

    if not options.target:
        parser.error('A target name is required')
    serial = None
    if options.serial is not None:
        if not options.serial.isdigit():
            parser.error('Serial must be an integer')
            serial = int(options.serial)

    if options.talk_talk:
        print "Search         : %s"% options.target
        print "In             : %s"% options.ssl_environment
        if serial is not None:
            print "Serial         : %04d"% serial
        else:
            print "Serial         : not given"
        print "All?           : %s"% str(options.list_all)

    if options.do_nothing:
        exit(0)

    pki_obj = PKCertSet(os.path.join(options.ssl_environment,
                                     options.target),
                        None)
    for list_ptr in range(len(pki_obj)):
        properties = pki_obj[list_ptr]
        file_name = properties['file']
        file_serial = int(file_name[:4])
        if (options.list_all or
            (serial is not None and serial == file_serial) or
            (serial is None and properties['activated'])):
            print "%s: %s - from %s to %s   %s"% (
                options.target,
                properties['email'],
                properties['dte_start'],
                properties['dte_end'],
                properties['activated']
                )

    if options.talk_talk:
        print "Done..."

#-----------------------------------------------------------------------
