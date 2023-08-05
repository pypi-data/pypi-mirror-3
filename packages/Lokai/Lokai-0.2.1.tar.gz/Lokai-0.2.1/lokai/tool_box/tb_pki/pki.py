# Name:      lokai/tool_box/tb_pki/pki.py
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

import os
import subprocess
import shutil
import glob
import yaml
import datetime
import copy

from lokai.tool_box.tb_common.dates import (now,
                                      timetostr,
                                      plus_days,
                                      DATE_FORM_ISO_COMPACT,
                                      )

#-----------------------------------------------------------------------

def rm_all(path):
    if os.path.isdir(path):
        fl = os.listdir(path)
        for f in fl:
            rm_all(os.path.join(path, f))
        os.rmdir(path)
    elif os.path.isfile(path):
        os.remove(path)
        
#-----------------------------------------------------------------------

base_pki_directory = 'pki' # assuming we are running in the
                           # appropriate working directory.

#-----------------------------------------------------------------------

OPENSSL = 'openssl'        # Command to be executed

#-----------------------------------------------------------------------

class PKI_Error(Exception):
    """Basic error response from these facilities"""
    pass

class PKI_Processing(PKI_Error):
    """Error return from one of the OpenSSL calls"""
    pass

class PKI_NotFound(PKI_Error):
    """ Cannot find some aspect of the pki details """
    pass

#-----------------------------------------------------------------------

class PKCertSet:
    """ Operate on files for a single target.

        The files are held in a directory dedicated to the target.
        
        The target is defined by a distingished name, and optional
        extensions, held in a dn.txt file.

        Certificate files are generated into this directory, each new
        file given a serial number one greater than the serial number
        recorded in (a file in) the directory.

        The currently active files (the ones to use in whatever
        application) have no serial number and are hard linked to the
        relevant numbered files.

        target_directory, required, for where the files are held.

        authority_directory, required, for the cert authority files.

            If generating a self-signed certificate this must be the
            same as the target. This is required explicitly, just to
            be sure ...

            The authority directory contains a certificate and,
            perhaps, other things. It must be capable of being set
            read-only.

            The directory that contains the authority directory must
            be writable. This directory contains CA management
            information:

                a file called {authority_directory}.srl. This file
                contains the latest used value of the ca serial
                number. The file is created automatically if it does
                not already exist.

                a file called {authority_directory}.lock used to lock
                the ca during certificate generation.
    """

    def __init__(self,
                 target_directory,
                 authority_directory,
                 self_sign = False,
                 distinguished_name = {},
                 password = None,
                 start_date = None,
                 lifetime = 365,
                 ):
        #
        self.target = os.path.abspath(os.path.expanduser(target_directory))
        if not os.path.exists(self.target):
            raise PKI_Error, \
                  "%s (target directory) does not exist"%str(self.target)
        self.set_authority(authority_directory)
        self.self_sign = self_sign
        self.start_date = None
        self.end_date = None
        self.password = None
        self.key_size = 2048
        self.self_sign_life = 1825 # 5 years
        self.default_life = 365
        self.lifetime = lifetime
        self.data = []
        self.props    = {}
        
        self.serial_file = os.path.join(self.target, 'serial')
        self.has_read = False # Defer file access
        self.set_dn(distinguished_name)
        self.set_start(start_date)
        self.set_password(password)

        # Place where temp ca config is built
        self.pki_dir = self.target
        # Place where temp ca tree is built
        self.pki_dir = self.target
        # Place where authority serial number is kept
        self.ssl_dir = self.authority or self.target

    def set_authority(self, given_directory):
        """ given a directory path, record this path and extract the
            base name of the path.
        """
        if given_directory is None:
            self.authority = None
            self.authority_name = None
            self.ssl_dir = None
        else:
            if not os.path.exists(given_directory):
                raise PKI_Error,"Authority %s not found"%given_directory
            else:
                self.authority = os.path.abspath(
                    os.path.expanduser(
                        given_directory))
                self.ssl_dir, self.authority_name = os.path.split(self.authority)

    def set_dn(self, distinguished_name={}, extensions={}):
        """ Given a dict of dn elements, read the currently activated
            dn.txt on disc and pull the content into the object,
            update from the given elements.

            The dn.txt file may optionally contain an 'extensions'
            key. This contains a further dictionary of extension
            elements.
        """
        dn_content = {}
        extn_content = {}
        dn_path = os.path.join(self.target, 'dn.txt')
        if os.path.exists(dn_path):
            try:
                dn_file = open(dn_path)
                dn_content = yaml.load(dn_file)
            finally:
                dn_file.close()
            if 'extensions' in dn_content:
                extn_content = dn_content['extensions']
                del dn_content['extensions']
        dn_content.update(distinguished_name)
        extn_content.update(extensions)
        self.distinguished_name = dn_content
        self.extensions = extn_content
            
    def set_start(self, given_date):
        """ Set the date the certificate runs from.

            Optional - OpenSSL will use today's date.
            
            Use a date object.
        """
        assert(isinstance(given_date, (datetime.date, datetime.datetime)) or
               given_date is None)
        if isinstance(given_date, datetime.date):
            self.start_date = datetime.datetime(given_date.year,
                                               given_date.month,
                                               given_date.day)
        else:
            self.start_date = given_date

    def set_lifetime(self, given_days):
        """ Set the life expectancy of the certificate
        """
        if not given_days:
            if self.self_sign:
                self.lifetime = self.self_sign_life
            else:
                self.lifetime = self.default_life
        else:
            if not isinstance(given_days, int):
                self.lifetime = int(given_days)
            else:
                self.lifetime = given_days
        
    def set_password(self, password):
        """ set the password that is used to create the certificate.

            Leave as None for no password
        """
        self.password = password
        
    def __len__(self):
        """ Return the number of certificate pairs that are found in
            this directory
        """
        self.getList()
        return len(self.data)

    def __getitem__(self, k):
        """ Return details of the 'k'th certificate pair in this
            directory
        """
        return self.getData(k)

    def getList(self):
        """ Build a list of pub*.crt files and find which one is
            currently active.

            The list of files is just as found from the directory. Any
            gaps in the sequence will produce odd results.
        """
        if not self.has_read:
            self.data = glob.glob(
                os.path.join(self.target,'[0-9]'*4+'.pub.crt'))
            self.data.sort()
            self.has_read = True
            #
            # Find the activated key
            lnk_file = os.path.join(self.target, 'activated')
            if os.path.isfile(lnk_file):
                lnk_flh = file(lnk_file)
                self.activated = os.path.basename(lnk_flh.readline())
                lnk_flh.close()
            else:
                self.activated = None

    def getData(self, k):
        """ Return details of the 'k'th certificate pair in this
            directory. If there are gaps in the sequence then the
            'k'th pair may not actually be serial 'k'.

            Details are stored in self.props and self.props is
            returned.
        """
        self.getList()
        file_name = self.data[k]
        if not os.path.isfile(file_name):
            raise PKI_NotFound,"Using %s"%file_name
        self.props = {'file':os.path.basename(file_name), 'activated': ''}
        if self.activated and self.props['file'].startswith(self.activated):
            self.props['activated'] = 'Active'
        cmd = [OPENSSL,
               'x509',
               '-in',
               file_name,
               '-noout',
               '-enddate',
               '-startdate',
               '-email',
               ]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        pki_prp = p.stdout.readline().strip().split('=')
        self.props['dte_end'] = pki_prp[1]
        pki_prp = p.stdout.readline().strip().split('=')
        self.props['dte_start'] = pki_prp[1]
        pki_txt = p.stdout.readline().strip()
        self.props['email'] = pki_txt
        return self.props

    def make_rq_conf(self):
        """ Build a configuration file.
        
            This is where the common name for the certificate is
            passed in to the X509 process. The common name elements
            are taken from the distinguished name.
        """
        if not self.distinguished_name:
            raise PKI_Error, "Empty distinguished name"
        cfg_file = os.path.join(self.pki_dir, 'rq.conf')
        cf = file(cfg_file, 'w')
        conf_lines = ["[req]",
                      "prompt = no",
                      "distinguished_name = req_distinguished_name",
                      "req_extensions = req_extensions",
                      "x509_extensions = x509_extensions",
                      ]
        #
        # Build a distinguised name section
        conf_lines.append("[req_distinguished_name]")
        conf_lines.extend(["%s=%s"%(k,v) for
                           k,v in self.distinguished_name.items()])
        conf_lines.append("[req_extensions]")
        if not self.self_sign:
            #
            # Build request extensions (not-self_signed)
            req_ext = {"keyUsage": "digitalSignature",
                       "extendedKeyUsage": "emailProtection,serverAuth"}
            req_ext.update(self.extensions)
            conf_lines.extend(["%s=%s"%(k,v) for
                           k,v in req_ext.items()])
        #---
        conf_lines.append("[x509_extensions]")
        if self.self_sign:
            #
            # Build x509 extensions
            x509_ext = {"basicConstraints": "critical,CA:TRUE",
                       "keyUsage": "critical,keyCertSign",
                       }
            x509_ext.update(self.extensions)
            conf_lines.extend(["%s=%s"%(k,v) for
                           k,v in x509_ext.items()])
        #---
        conf_lines.append('') # force a trailing new-line
        cf.write("\n".join(conf_lines))
        cf.close()
        return cfg_file

    def make_ca_conf(self):
        """ Create a temporary config file, just for this object
        """
        cfg_file = os.path.join(self.pki_dir, 'ca.conf')
        ca_tree_dir = os.path.join(self.ssl_dir, 'ca_tree')
        tree_conf = [
            "dir           = %s"%ca_tree_dir,
            "certs         = %s"%os.path.join(ca_tree_dir, "certs"),
            "new_certs_dir = %s"%os.path.join(ca_tree_dir, "ca.db.certs"),
            "database      = %s"%os.path.join(ca_tree_dir, "ca.db.index"),
            "serial        = %s"%os.path.join(ca_tree_dir, "ca.db.serial"),
            "RANDFILE      = %s"%os.path.join(ca_tree_dir, "ca.db.rand"),
            "certificate   = %s"%os.path.join(self.authority, "pub.crt"),
            "private_key   = %s"%os.path.join(self.authority, "pvt.key"),
            ]
        policy_conf = [
            "countryName   = optional",
            "stateOrProvinceName = optional",
            "localityName  = optional",
            "organizationName = optional",
            "organizationalUnitName = optional",
            "commonName    = supplied",
            "emailAddress  = supplied",
            ]
        cf = file(cfg_file, 'w')
        conf_list = [
            "[ ca ]",
            "default_ca = CA_own",
            "[ CA_own ]",
            ]
        conf_list.extend(tree_conf)
        conf_list.extend([
            "default_days  = %d"% self.lifetime,
            "default_crl_days = 30",
            "default_md    = sha1",
            "preserve      = no",
            "copy_extensions = copy",
            "policy        = policy_anything",
            "[ policy_anything ]",
            ])
        conf_list.extend(policy_conf)
        conf_list.extend(['[x509_extensions]',
                          'basicConstraints = CA:FALSE'])
        conf_list.append('') # force a trailng new-line

        cf.write("\n".join(conf_list))
        cf.close()
        return cfg_file

    def make_ca_directories(self):
        """ Construct the ca directory tree and post essential
            starting data
        """
        ca_dir = os.path.join(self.ssl_dir, 'ca_tree')
        if not os.path.exists(ca_dir):
            os.mkdir(ca_dir)
        ca_certs = os.path.join(ca_dir, 'ca.db.certs')
        if not os.path.exists(ca_certs):
            os.mkdir(ca_certs)
        ca_tree = os.path.join(ca_dir, 'ca.db.index')
        if not os.path.exists(ca_tree):
            xx = file(ca_tree, 'w')
            xx.close()
        ca_serial = os.path.join(ca_dir, 'ca.db.serial')
        if not os.path.exists(ca_serial):
            ca_serial_save = os.path.join(self.ssl_dir, 'ca.db.serial')
            if not os.path.exists(ca_serial_save):
                xx = file(ca_serial, 'w')
                xx.write("01\n")
                xx.close()
            else:
                shutil.copyfile(ca_serial_save, ca_serial)
                
    def remove_ca_data(self):
        """ Tidy up after using the 'ca facility by capturing the
            latest serial number and removing the temp files
        """
        ca_serial_save = os.path.join(self.ssl_dir, 'ca.db.serial')
        ca_serial      = os.path.join(self.ssl_dir, 'ca_tree', 'ca.db.serial')
        if os.path.exists(ca_serial):
            shutil.copyfile(ca_serial, ca_serial_save)
        #
        # Now remove all trace
        ca_dir = os.path.join(self.ssl_dir, 'ca_tree')
        rm_all(ca_dir)

    def get_lock(self):
        """ Manage multi use by locking the pki_dir
        """
        self.lck = os.path.abspath(
            os.path.join(self.ssl_dir, self.authority_name+'.lock'))
        try:
            self.fc_lck = os.open(self.lck, os.O_CREAT+os.O_EXCL)
            return True
        except:
            return False

    def rel_lock(self):
        """ Unlock
        """
        os.close(self.fc_lck)
        os.remove(self.lck)

    def read_ca_serial(self):
        """ Read the CA serial number for this authority.
        """
        self.ca_serial_file = os.path.join(self.ssl_dir,
                                           self.authority_name+'.srl')
        if not os.path.isfile(self.ca_serial_file):
            return -1
        else:
            try:
                sfh = open(self.ca_serial_file, 'r')
                ln = sfh.readline().strip()
            finally:
                sfh.close()
            return int(ln)

    def write_ca_serial(self, v):
        """ Write the serial number for this target
        """
        try:
            sfh = open(self.ca_serial_file, 'w')
            sfh.write("%d"%v)
        finally:
            sfh.close()
        
    def read_serial(self):
        """ Read the serial number for this target.

            We rather assume that the serial file is correct. We don't
            go searching for a maximum.
        """
        if not os.path.isfile(self.serial_file):
            return -1
        else:
            try:
                sfh = open(self.serial_file, 'r')
                ln = sfh.readline().strip()
            finally:
                sfh.close()
            return int(ln)

    def write_serial(self, v):
        """ Write the serial number for this target
        """
        try:
            sfh = open(self.serial_file, 'w')
            sfh.write("%d"%v)
        finally:
            sfh.close()

    def activate(self, given_serial):
        """ Remove the current 'pub.crt' and point it to the requred
            target as defined by the given serial number.

            given_serial can be:

                integer - use directly

                text - take the 1st 4 characters and convert to integer.
                       this allows the use of a file name as input.
        """
        max_serial = self.read_serial()
        if type(given_serial) == type(''):
            #
            # Assume this is a file name, with the prefix serial number
            file_name = os.path.basename(given_serial)
            sn = int(file_name[0:4])
        else:
            sn = given_serial
        if sn < 0 or sn > max_serial:
            raise IndexError, "Serial %04d out of range"
        if not os.path.isfile(
            os.path.join(self.target, '%04d.%s'%(sn, 'pub.crt'))):
            raise IndexError, "Serial %04d not found"
        file_list = ['pub.crt', 'pvt.key', 'pub.p7c', 'cert.pfx', 'dn.txt']
        for file_base in file_list:
            file_new = os.path.join(self.target, file_base)
            if os.path.isfile(file_new):
                os.unlink(file_new)
            file_src = os.path.join(self.target, '%04d.%s'%(sn, file_base))
            #
            # Use a hard link in case of issues with OpenSSL
            if os.path.isfile(file_src):
                os.link(file_src, file_new)
        #
        #
        lnk_file = os.path.join(self.target, 'activated')
        lnk_flh = file(lnk_file, 'w')
        lnk_flh.write('%04d'%sn)
        self.has_read = False # to force re-read of data
        return 'ok'
    
    def OpenSSL(self, cmd, input_string=None):
        """ Run the OpenSSL command. Raise error and release the lock
            if the command fails.

            The returned text from the command is placed in
            self.ssl_return_ok and self.ssl_return_er, not because it
            is used anywhere, but to aid debugging.
        """
        cmd.insert(0, OPENSSL)
        sub = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE)
        self.ssl_retunrn_ok, self.ssl_return_er = sub.communicate(
            input=input_string)
        if sub.returncode:
            print cmd
            print "return code ",sub.returncode
            print self.ssl_return_er
            self.rel_lock()
            raise PKI_Processing, self.ssl_return_er

    def make_private_key(self, serial_prefix):
        """ Generate the required private key - return the name of the
            file
        """
        pvt_file = os.path.join(self.target, '%s.pvt.key'%serial_prefix)
        gen_list = ['genrsa',
                    '-out',pvt_file,
                    str(self.key_size)]
        if self.password:
            gen_list.extend(['-des3', '-passout','pass:%s'%self.password,])
        self.OpenSSL(gen_list)
        return pvt_file

    def make_certificate_request(self, pvt_file, serial_prefix):
        """ Make either a certificate request or a self signed
            certificate - return the name of the request file
        """
        cnf_file = self.make_rq_conf()
        csr_file = os.path.join(self.target, '%s.pub.csr'%serial_prefix)
        req_list = ['req',
                    '-new',
                    '-days','365',
                    '-key', pvt_file,
                    '-out', csr_file,
                    '-config',cnf_file]
        if self.self_sign:
            req_list.append('-x509')
        
        req_list.extend(['-days', '%d'%self.lifetime])
        if self.password:
            req_list.extend(['-passin','pass:%s'%self.password,])
        self.OpenSSL(req_list)
        return csr_file

    def sign_certificate(self, csr_file, serial_prefix):
        """ Use 'ca' process to sign the certificate - return the
            signed certificate file
        """
        local_ca_config = self.make_ca_conf()
        num_file = file(os.path.join(self.ssl_dir, 'ca_tree', 'ca.db.serial'))
        num_line = num_file.readline().strip()

        cmd = ['ca',
               '-config', local_ca_config,
               '-notext']
        if self.password:
            cmd.extend(['-passin', 'pass:%s'%self.password])
        if not self.start_date :
            self.start_date = now()
        cmd.extend(['-startdate', '%s'%
                    str(timetostr(self.start_date, DATE_FORM_ISO_COMPACT)[2:])])

        self.end_date = plus_days(self.start_date, self.lifetime)
        cmd.extend(['-enddate', '%s'%
                    str(timetostr(self.end_date, DATE_FORM_ISO_COMPACT)[2:])])

        cmd.extend(['-infiles', csr_file])
        print cmd
        self.OpenSSL(cmd, 'y\ny\n') # Answer 'y' to the prompts
        #
        pub_file = os.path.join(self.target,'%s.pub.crt'%serial_prefix)
        #
        # Copy to local directory
        shutil.copyfile(os.path.join(self.ssl_dir,
                                     'ca_tree/ca.db.certs/%s.pem'%num_line),
                        pub_file)
        return pub_file

    def make_alternatives(self, pvt_file, pub_file, serial_prefix):
        """ create pkcs12 version of full public and private keys for Linux
        """
        cert_file = os.path.join(self.target, '%s.cert.pfx'%serial_prefix)
        pkcs_list = ['pkcs12',
                       '-export',
                       '-in',pub_file,
                       '-inkey',pvt_file,
                       '-passin','pass:%s'%self.password,
                       '-passout','pass:%s'%self.password,
                       '-out',cert_file]
        self.OpenSSL(pkcs_list)
        #
        # 
        # create pkcs7 version of public key only for Linux
        pkcs_file = os.path.join(self.target,'%s.pub.p7c'%serial_prefix)
        self.OpenSSL(['crl2pkcs7',
                       '-nocrl',
                       '-certfile',pub_file,
                       '-outform','DER',
                       '-out',pkcs_file]
                     )

    def register(self):
        """ Construct a new certificate pair.
        
            Steps:
        
               Create the private key
        
               Turn the private keyn into a certificate request
        
               Create and sign a certificate
        
               Possibly create some alternative versions of the certificate
        
            The only way to set the date range for the certificate is
            at the signing stage. We need a start and end date.
        """
        if not os.path.exists(self.authority):
            raise PKI_Error,"Must provide an Authority"
        if ((self.self_sign and self.authority != self.target) or
            (not self.self_sign and self.authority == self.target)):
            raise PKI_Error,"Given authority not consistent with self signing"
        assert(self.distinguished_name and
               (self.self_sign == True or
                ('CN' in self.distinguished_name or
                 'commonName' in self.distinguished_name))
               ), "The commonName field needed to be supplied and was missing"
        #
        # Lock the process
        if not self.get_lock() : return 'Process locked'
        #
        self.remove_ca_data()
        self.make_ca_directories()
        #
        # Find the current serial number and increment so we can use it
        serial = self.read_serial()+1
        serial_text = "%04d"%serial
        #
        # Make a private key
        pvt_file = self.make_private_key(serial_text)
        #
        # Create certificate request
        csr_file = self.make_certificate_request(pvt_file, serial_text)
        #
        #
        if not self.self_sign:
            #
            # Create signed certificate
            pub_file = self.sign_certificate(csr_file, serial_text)
        else:
            #
            # The csr is actually the answer
            pub_file = os.path.join(
                os.path.dirname(csr_file),
                os.path.splitext(os.path.basename(csr_file))[0]+'.crt')
            shutil.copyfile(csr_file, pub_file)   
        #
        # Make some alternative versions
        self.make_alternatives(pvt_file, pub_file, serial_text)
        #
        self.write_serial(serial)
        dsn_file = os.path.join(self.target,'%s.dn.txt'%serial_text)
        dsn_fp = open(dsn_file, 'w')
        dsn_out = copy.copy(self.distinguished_name)
        if self.extensions:
            dsn_out['extensions'] = self.extensions
        yaml.dump(dsn_out, dsn_fp)
        dsn_fp.close()
        self.has_read = False # to force re-read of data
        self.rel_lock()
        return 'ok'

#-----------------------------------------------------------------------
