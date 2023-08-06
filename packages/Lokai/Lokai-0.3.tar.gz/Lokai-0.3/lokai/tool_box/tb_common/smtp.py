# Name:      lokai/tool_box/tb_common/smtp.py
# Purpose:   Provide tools for smtp connections
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

""" Provide a mechanism for setting up and smtp connection that uses
    at least some of the possible connection options that smtp
    supports.

    The primary gain from this particular tool is that is uses a
    configuration read in by tb_common.configuration.
    
"""

#-----------------------------------------------------------------------

import smtplib

import lokai.tool_box.tb_common.configuration as config
import lokai.tool_box.tb_common.notification as notify

#-----------------------------------------------------------------------

class SmtpConnection(smtplib.SMTP):
    """ Extend the basic SMTP object to override with a potential
        connection to the local configuration
    """
    def __init__(self,
                 host=None,
                 port=None,
                 user=None,
                 password=None,
                 local_hostname=None,
                 timeout=None,
                 from_host=None,
                 config_section=None):
        """ The parameters are the same as for SMTP, with the addition of:

            :config_section: The name of the section of the
                configuration file that contains the possible
                settings. If this is given then the internal values
                are set from the configuration. Any values not given
                in the configuration are left unchanged.

                :smtp_host: The name of the mail server we try to
                    connect to.

                :smtp_port: The server port.
                
                :smtp_user: A username to use if the server supports
                    AUTH.
                
                :smtp_password: A password to go with the username.
                
                :smtp_from_host: A host_name part to be used to build
                    a from address when sending stuff. This is not
                    strictly part of the connection protocol, but this
                    object is a good place to store the information
                    from the configuration file. See method
                    `make_from`.
                
                :smtp_local_host: The apparent name of the place the
                    email is being sent from.         

                :smtp_debug: Set non-empty to request debug print
                    output - smtplib puts this on stderr.

        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.local_hostname = local_hostname
        self.timeout = timeout
        self.from_host = from_host
        self.debug = False
        if config_section:
            self.use_config(config_section)
        smtplib.SMTP.__init__(self, host=self.host, port=self.port,
                              local_hostname=self.local_hostname,
                              timeout=self.timeout)

    def use_config(self, config_section):
        self.config_section = config_section
        c_source = config.get_global_config().get(self.config_section, {})
        #notify.debug("smtp configuration - %s"%str(c_source))
        self.host = c_source.get('smtp_host', self.host)
        self.port = c_source.get('smtp_port', self.port)
        self.user = c_source.get('smtp_user', self.user)
        self.password = c_source.get('smtp_password', self.password)
        self.from_host = c_source.get('smtp_from_host', self.from_host)
        self.local_hostname = c_source.get('smtp_local_hostname',
                                           self.local_hostname)
        self.debug = c_source.get('smtp_debug', self.debug)
        if self.debug:
            self.set_debuglevel(True)

    def make_from(self, given_from):
        """ Useful method to add the from_host to a user name.

            :given_from: is a string purporting to be a from address
                or from username. If the string already has an '@' in
                it nothing is change, otherwise the current from_host
                is appended.

            Returns the new from address.
        """
        if '@' in given_from:
            use_from = given_from
        else:
            use_from = "%s@%s"%(given_from, self.from_host)
        return use_from

    def connect(self, host=None, port=None):
        # This gets called as self.connect from inside the SMTP
        # object, so we need to pretend a degree of compatability.
        #notify.debug("smtp - in connection method - %s:%s"%(host, port))
        self.host = host or self.host
        self.port = port or self.port
        #
        conn_code, conn_msg = smtplib.SMTP.connect(self, self.host, self.port)
        #notify.debug("smtp - make connection - %s, %s"%(str(conn_code), conn_msg))
        ehlo_code, ehlo_msg = self.ehlo(self.local_hostname)
        #notify.debug("smtp - 1st ehlo - %s, %s"%(str(ehlo_code), ehlo_msg))
        if ehlo_code == 502:
            self.helo(self.local_hostname)
        if self.has_extn('STARTTLS'):
            self.starttls()
            res = self.ehlo(self.local_hostname)
        if self.has_extn('AUTH') and self.user:
            self.login(self.user, self.password)
        return conn_code, conn_msg

    def sendmail(self, from_addr, to_addr, msg,
                 mail_options=None, rcpt_options=None):
        """ Override the original sendmail without changing the
            parameter list. However, the use of from_addr is changed.

            :from_addr: either a full email address (contains '@') or
                 a name without the host part. In the latter case, the
                 name is used with self.from_host.
        """
        use_from = self.make_from(from_addr)
        kwargs = {}
        if mail_options:
            kwargs['mail_options'] = mail_options
        if rcpt_options:
            kwargs['rcpt_options'] = rcpt_options
        smtplib.SMTP.sendmail(self, use_from,  to_addr, msg, **kwargs)

#-----------------------------------------------------------------------
