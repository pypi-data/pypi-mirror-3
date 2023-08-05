# Name:      lokai/tool_box/tb_pki/make_cert.py
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

""" Command line interface to te PKI object. specifically for
    creating a new certificate.

    The command assumes that you are working in a single directory
    that contains the SSL environment. (option ssl-env) Within this
    directory there is a sub-directory for each target Common Name,
    including one for the certificate authority.

    You can use this program to create a self-signed authority, or you
    can install your own root certificate from some other source.

    The program does not allow you to enter distinguished name
    parts. You must create a yaml file, dn.txt, in the target
    directory.

    If you make a mistake, you can go and delete files yourself.
"""
#-----------------------------------------------------------------------

import optparse
import os
import yaml

from lokai.tool_box.tb_common.dates import date_parse, plus_days, timetostr
from lokai.tool_box.tb_pki.pki import PKCertSet

#-----------------------------------------------------------------------

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.description = "Create a PKI certificate"
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
    parser.add_option('-a', '--authority',
                      dest = 'authority',
                      help = ('Name (not a path) of the directory where '
                              'the root certificate can be found. '
                              'Required.')
                      )
    parser.add_option('-s', '--start',
                      dest = 'start_date',
                      help = ('Date that the certificate starts on. '
                              'This allows date substitution, so "ymd" is today.'
                              'Required.')
                      )
    parser.add_option('-l', '--life',
                      dest = 'life',
                      help = ('Number of days the certificate is valid for. '
                              'Default = 365.')
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
    parser.set_defaults(life=365, ssl_environment='.')

    (options, args) = parser.parse_args()

    if not options.target:
        parser.error('A target name is required')
    if not options.authority:
        parser.error('An authority name is required')
    if not options.start_date:
        parser.error('A start date is required')

    dn_path = os.path.join(options.ssl_environment, options.target, 'dn.txt')
    if not os.path.isfile(dn_path):
        parser.error("There is no distinguished name file (dn.txt) "
                     "in the target directory")

    dn_file = open(dn_path)
    dn_data = yaml.safe_load(dn_file)
    
    given_start = date_parse(options.start_date)

    given_end = plus_days(given_start, int(options.life))

    self_sign = False
    if options.target == options.authority:
        self_sign = True

    if not self_sign:
        auth_path = os.path.join(options.ssl_environment,
                                 options.authority,
                                 'pub.crt')
        if not os.path.isfile(auth_path):
            parser.error("The root certificate cannot be found in %s" %
                         auth_path)

    if options.talk_talk:
        print "Creating       : %s"% options.target
        print "Using          : %s"% options.authority
        print "In             : %s"% options.ssl_environment
        print "Start          : %s"% timetostr(given_start)
        print "End            : %s"% timetostr(given_end)
        print "Self sign?     : %s"% str(self_sign)

    if options.do_nothing:
        exit(0)

    if not self_sign:
        pki_obj = PKCertSet(os.path.join(options.ssl_environment,
                                         options.target),
                            os.path.join(options.ssl_environment,
                                         options.authority),
                            start_date = given_start,
                            lifetime = int(options.life),
                            )
    else:
        pki_obj = PKCertSet(os.path.join(options.ssl_environment,
                                         options.target),
                            None,
                            self_sign = True,
                            start_date = given_start,
                            lifetime = int(options.life),
                            )             
    pki_obj.register()

    if options.talk_talk:
        print "Done..."

#-----------------------------------------------------------------------
