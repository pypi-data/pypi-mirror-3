# Name:      lokai/tool_box/tb_pki/activate_cert.py
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

""" Command line interface to te PKI object. specifically for issuing
    (making active) a certificate.
"""

#-----------------------------------------------------------------------

import optparse
import os

from lokai.tool_box.tb_pki.pki import PKCertSet

#-----------------------------------------------------------------------

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.description = "Activate a PKI certificate"
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
                              'certificate to be issued (activated). '
                              'Required.')
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
    parser.set_defaults(ssl_environment='.')

    (options, args) = parser.parse_args()

    if not options.target:
        parser.error('A target name is required')
    if options.serial is None:
        parser.error('A serial number is required')
    if not options.serial.isdigit():
        parser.error('Serial must be an integer')
    serial = int(options.serial)
    
    if options.talk_talk:
        print "Issuing        : %s"% options.target
        print "In             : %s"% options.ssl_environment
        print "Serial         : %04d"% serial

    if options.do_nothing:
        exit(0)

    pki_obj = PKCertSet(os.path.join(options.ssl_environment,
                                     options.target),
                        None)
    pki_obj.activate(serial)

    if options.talk_talk:
        print "Done..."

#-----------------------------------------------------------------------
