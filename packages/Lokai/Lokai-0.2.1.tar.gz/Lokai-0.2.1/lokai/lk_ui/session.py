# Name:      lokai/lk_ui/session.py
# Purpose:   Use cookies to store session data
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
import datetime

from werkzeug import BaseRequest, CommonRequestDescriptorsMixin, cached_property
from werkzeug.contrib.wrappers import RoutingArgsRequestMixin
from werkzeug.contrib.securecookie import SecureCookie

import lokai.tool_box.tb_common.configuration as config

#-----------------------------------------------------------------------

__all__ = ['SessionRequest']

#-----------------------------------------------------------------------

def get_session_key():
    """ Read from config file or static file in working directory.

        Looking for:
        [all]
        session_key = ... # String of bytes

        If session key is not found look in (hidden) file '.lokai_session'

        If file does not exist, create it witha random string.
    """
    all_block = config.get_global_config()['all']
    session_key = all_block.get('session_key', None)
    if session_key is None:
        key_file = '.lokai_session'
        try:
            fp = open(key_file, 'r')
            session_key = fp.readline()
        except IOError:
            fp = open(key_file, 'w')
            session_key = os.urandom(20)
            fp.write(session_key)
    return session_key

def get_session_life():
    """ Read from config file or static file in working directory.

        Looking for:
        [all]
        session_life = nnn # Number of minutes session stays alive
                           # zero or unspecirfied = forever
                           
    """
    all_block = config.get_global_config()['all']
    return all_block.get('session_life', 0)
            
    
class SessionRequest(BaseRequest,
                     CommonRequestDescriptorsMixin,
                     RoutingArgsRequestMixin):
    """ A form of the request object that contains details of the
        session.

        Also handles:

        - Ian Bicking's Routing Args.

        - Other session/request related derived values, such as the
          user's permissions.

        Bind the environ to this instead of an ordinary request
        object.
    """

    @cached_property
    def __session_key(self):
        return get_session_key()

    @cached_property
    def __session_life(self):
        return get_session_life()

    @cached_property
    def client_session(self):
        """ Return a session that looks like a dictionary.

            Returns either the existing one or a new one as
            appropriate.

            The secret key that is used in the secure cookie
            implementation is _not_stored in the code - far too
            public. It is stored in the working direcrory for the
            site, either in the config file or a hidden (under *nix)
            text file. The value can be changed from time to time to
            reduce the impact of compromised cookies.
        """
        data = self.cookies.get('session_data')
        if not data:
            return SecureCookie(secret_key=self.__session_key)
        return SecureCookie.unserialize(data, self.__session_key)

    def store_session(self, response):
        """ Save the content of the session, linking it to the given
            response object.

            Calculate a session_expires based on session_life. This
            has two uses:

                To force the user to re-sign on after not using the
                system fo rsome period of time.

                To make it more difficult for a third party to pick up
                the cookie and use it. This is only, more difficult -
                not impossible - so other security methods may be
                appropriate.

            The cookie is not given an expires date, so it disappears
            at the end of the browser session.
        """
        if self.client_session.should_save:
            if self.__session_life > 0:
                dt = (datetime.datetime.now() +
                      datetime.timedelta(minutes=self.__session_life))
            else:
                dt = None
                
            session_data = self.client_session.serialize(dt)
            response.set_cookie('session_data', session_data,
                                httponly=True)

    def get_user(self):
        """ Return the current value of the 'user' data attribute. """
        return self.client_session.get('user', None)

    def set_user(self, value):
        """ Set a value into the 'user' data attribute. """
        self.client_session['user'] = value

    def del_user(self):
        """ Delete the 'user' data attribute. """
        del self.client_session['user']

    user = property(get_user, set_user, del_user, 'The current loggged in user')

    def get_form_tokens(self):
        """ Return the current value of the 'form_tokens' data attribute.

            Since the calling code assumes that the atribute exists
            because it is going to append something, so we
            automatically create it if it is accessed at all.
        """
        if not '_form_tokens' in self.client_session:
            self.client_session['_form_tokens'] = []
        return self.client_session['_form_tokens']

    def set_form_tokens(self, value):
        """ Set a value into the 'form_tokens' data attribute. """
        self.client_session['_form_tokens'] = value

    def del_form_tokens(self):
        """ Delete the 'form_tokens' data attribute. """
        del self.client_session['_form_tokens']

    _form_tokens = property(get_form_tokens, set_form_tokens, del_form_tokens,
                         'A list of form identifiers used to control form access')

    MAX_FORM_TOKENS = 16

    def get_locals(self):
        """ Return the current 'locals' dictionary """
        if not hasattr(self, '_locals'):
            self._locals = {}
        return self._locals

    def set_locals(self, locals_dict):
        """ Set the 'locals' dictionary to a dictionary like object """
        self._locals = locals_dict

    def del_locals(self):
        """ Remove the 'locals' object """
        if hasattr(self, '_locals'):
            del self._locals

    derived_locals = property(get_locals, set_locals, del_locals,
                              'A dir of values that can be passed around '
                              'with the request')
        
#-----------------------------------------------------------------------
