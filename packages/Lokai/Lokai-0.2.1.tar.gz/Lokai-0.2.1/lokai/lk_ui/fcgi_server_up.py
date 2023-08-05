#!/usr/bin/python
# Name:      lokai/lk_ui/fcgi_server.py
# Purpose:   A pre-forked fcgi server
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

""" This server provides a pre-forked fcgi server that can be used as
    a back end for any httpd server.

    Using a pre-forked server means we don't have to rely on the
    application being thread-safe.

    If you are running with whatever the distribution gives you then
    this can be set executable and run automatically by the httpd
    server using whatever configuration that server allows.

    Conversely, if you are running with virtualenv then using the
    global python executable will not work (it will see the wrong
    environment), so you need to run with the python from whichever
    virtualenv you want to pick up.

    Generally, this is probably best done by running this fgci_server
    as a daemon in your working environment. One way to achieve this
    in a production environment is to run the server automatically at
    boot using the crontab 'reboot' time setting.

    e.g.::
    
        @reboot /home/site_manager/site_wrapper path/to/server.py

    Where ``site_wrapper`` sets up the virtualenv and does other
    essentials such as setting $PYTHONPATH and entering the working
    directory before running python.

    An example site_wrapper for bash might look like::

        cd `dirname $0`
        export PYTHONPATH=`pwd`/application
        prog=$1
        shift
        python $prog "$@"

    When running fcgi_server as a daemon you need to tell it what to
    listen for. This can either be a unix socket file, or an
    address/port pair. Whatever you do must be matched with the
    settings for the httpd server.

    Listen settings are defined in the configuration file, in group
    ``server``. You provide either::

        socket = {{some file name}}

    or::
        listen = {{host address}}
        port = {{port number}}

    If you give both ``socket`` and ``listen`` then ``socket`` is ignored.

    To run this with lighttpd you need something like the following in
    your server configuration (where port 4001 is actually whatever
    you set up in the lokai config file)::

      fastcgi.server = (
                    "/" =>
                     ("localhost" =>
                       (
                         "host" => "127.0.0.1",
                         "port" => 4001,
                         "check-local" => "disable",
                         "fix-root-scriptname" => "enable"
                       )
                     )
                     )


"""

#-----------------------------------------------------------------------

PID_FILE = '__fcgi_server__.pid'

#-----------------------------------------------------------------------
import sys
import os
from flup.server.fcgi_fork import WSGIServer

import lokai.tool_box.tb_common.configuration as config
import lokai.tool_box.tb_common.exception_format as exc_fmt
import lokai.tool_box.tb_common.notification as notify
 
from lokai.lk_ui.publisher import make_app

#-----------------------------------------------------------------------

class LokaiServer(WSGIServer):

    def error(self, req):
        err_text = sys.exc_info()[1]
        err_stuff = ["LokaiServer:%s: %s"% (str(sys.exc_info()[0]),
                                err_text),]
        err_stuff.append(exc_fmt.get_print_exc_plus())
        err_str = '\n\n'.join(err_stuff)
        notify.critical(err_str)
        notify.getLogger().flush()
        super(LokaiServer, self).error(req)
    
#-----------------------------------------------------------------------

def main_():
    config.handle_ini_declaration(prefix='lk')
    cs = config.get_global_config()
    server_block = cs.get('server', {})

    try:
        listen = server_block['listen']
        try:
            port =  server_block['port']
            bind_address = (listen, int(port))
        except KeyError:
            raise KeyError("A port number must be provided with a listen address")
    except KeyError:
        try:
            socket = server_block['socket']
            bind_address = socket
        except KeyError:
            bind_address = None

    print "------ WSGIServer ------"
    print "bind_address = ", bind_address


    server = LokaiServer(make_app(),
                        bindAddress = bind_address,
                        )
    if os.path.exists(PID_FILE):
        # We can delete it because we only get here if the socket
        # doesn't fail, which means that there is not another server
        # running here.
        os.remove(PID_FILE)
    pidfile = open(PID_FILE, 'w')
    pidfile.write('%s'%os.getpid())
    pidfile.close()
    print "-fcgi- connection", server._connectionClass
    server.run() # forever

if __name__ == '__main__':
    main_()

#-----------------------------------------------------------------------
