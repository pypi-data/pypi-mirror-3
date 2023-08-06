###############################################################################
#
# Copyright (c) 2012 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import os
import sys
import errno
import socket
import select
import signal
import optparse
import StringIO
import ConfigParser

from cynic.utils import LOG_UNIX_SOCKET, get_console_logger, get_stream_logger

READ_ONLY = select.POLLIN
POLL_TIMEOUT = 500 # 0.5 sec
BACKLOG = 5

DEFAULT_CONFIG = """\
############################################################
# HTTP protocol specific                                   #
############################################################

[handler:httphtml]
# sends simple 'hello world!' HTML page over HTTP as a response
# and terminates
class = cynic.handlers.httphtml.HTTPHtmlResponse
#args = ('/tmp/test.html', )
host = 0.0.0.0
port = 2000

[handler:httpjson]
# sends simple 'hello world!' JSON over HTTP as a response
# and terminates
class = cynic.handlers.httpjson.HTTPJsonResponse
#args = ('/tmp/test.json', )
host = 0.0.0.0
port = 2001

[handler:httpnone]
# sends headers, but not the response body and terminates
class = cynic.handlers.httpnone.HTTPNoBodyResponse
host = 0.0.0.0
port = 2002

[handler:httpslow]
# sends one byte of the response every 30 seconds.
# when the data to be sent is exhausted - terminates
class = cynic.handlers.httpslow.HTTPSlowResponse
#args = ('/tmp/test.json', 'application/json', 1)
host = 0.0.0.0
port = 2003


############################################################
# Any TCP socket protocol                                  #
############################################################

[handler:reset]
# accepts a connection, sends an RST packet right away
# and terminates
class = cynic.handlers.reset.RSTResponse
host = 0.0.0.0
port = 2020

[handler:random]
# accepts a connection, sends 7 bytes from the /dev/urandom device
# and terminates
class = cynic.handlers.rnd.RandomDataResponse
host = 0.0.0.0
port = 2021

[handler:noresp]
# accepts a connection, but doesn't send any response back.
# sleeps for 24 hours and exits
class = cynic.handlers.noresp.NoResponse
host = 0.0.0.0
port = 2022

############################################################
# System handlers used internally by the Cynic server      #
############################################################

[handler:unixlog]
# a logging server that accepts connections over Unix socket
# from multiple local processes to output passed log records
class = cynic.handlers.log.LogRecordHandler
host = %(socketpath)s
port = 0
family = unix
""" % dict(socketpath=LOG_UNIX_SOCKET)

# Setup our console logger
logger = get_console_logger('server')


# taken from logging.config
def _resolve(name):
    """Resolve a dotted name to a global object."""
    name = name.split('.')
    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used = used + '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)
    return found


def _reap_children(signum, frame):
    """Collect zombie children."""
    while True:
        try:
            # wait for all children, do not block
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0: # no more zombies
                break
        except:
            # Usually this would be OSError exception
            # with 'errno' attribute set to errno.ECHILD
            # which means there are no more children
            break


def _load_config(fname):
    """Return an instance of ConfigParser."""
    config = ConfigParser.ConfigParser()
    if hasattr(fname, 'readline'):
        config.readfp(fname)
    else:
        config.read(fname)

    return config


class HandlerConfig(object):
    def __init__(self, klass, args, host, port, family):
        self.klass = klass
        self.args = args
        self.host = host
        self.port = port
        self.family = family
        self.socket = None # set up by the server


def _get_handler_configs(config):
    configs = []
    for section in config.sections():
        if not section.startswith('handler:'):
            continue

        clsname = config.get(section, 'class')
        klass = _resolve(clsname)
        host = config.get(section, 'host')
        port = config.getint(section, 'port')
        args = ()
        if config.has_option(section, 'args'):
            args = eval(config.get(section, 'args'), {})
        if config.has_option(section, 'family'):
            family = config.get(section, 'family')
        else:
            family = 'inet'
        hconfig = HandlerConfig(klass, args, host, port, family)
        configs.append(hconfig)

    return configs


class IOLoop(object):
    """Main IO loop.

    Spawns 'crafty' children to handle client requests.
    """
    def __init__(self, handler_configs):
        self.handler_configs = handler_configs
        self.fd2config = {}
        self.poller = None
        self._setup()

    def _get_address(self, hconfig):
        address = {
            'inet': (hconfig.host, hconfig.port),
            'unix': hconfig.host,
            }.get(hconfig.family)
        return address

    def _get_family(self, hconfig):
        family = {
            'inet': socket.AF_INET,
            'unix': socket.AF_UNIX
            }.get(hconfig.family)
        return family

    def _unlink_file(self, hconfig):
        if hconfig.family == 'unix':
            try:
                os.unlink(hconfig.host)
            except:
                pass

    def _setup(self):
        signal.signal(signal.SIGCHLD, _reap_children)

        self.poller = poller = select.poll()

        for config in self.handler_configs:
            server = socket.socket(
                self._get_family(config), socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.setblocking(0)

            logger.info(
                'Starting %-20r on port %s',
                config.klass.__name__, config.port or config.host
                )

            self.fd2config[server.fileno()] = config

            # this is only for Unix socket
            self._unlink_file(config)

            server.bind(self._get_address(config))

            server.listen(BACKLOG)

            # save the listen socket for further use
            config.socket = server

            poller.register(server, READ_ONLY)


    def run(self):
        try:
            child_pids = []
            while True:
                try:
                    events = self.poller.poll(POLL_TIMEOUT)
                except select.error as e:
                    code, msg = e.args
                    if code == errno.EINTR:
                        continue
                    else:
                        raise

                for fd, flag in events:
                    # we're interested only in READ events
                    if not flag & READ_ONLY:
                        continue

                    # retrieve the actual socket and handler class
                    # from its file descriptor
                    handler_config = self.fd2config[fd]

                    # socket is ready to accept a connection
                    socket = handler_config.socket
                    try:
                        conn, client_address = socket.accept()
                    except IOError as e:
                        code, msg = e.args
                        if code == errno.EINTR:
                            continue
                        else:
                            raise

                    # spawn a child that will handle the request (connection)
                    pid = os.fork()
                    if pid == 0: # child
                        for config in self.fd2config.values():
                            config.socket.close()
                        # run a handler
                        klass = handler_config.klass
                        handler = klass(
                            conn, client_address, *handler_config.args)
                        try:
                            handler.handle()
                        except KeyboardInterrupt:
                            pass
                        except:
                            log = get_console_logger(klass.__name__)
                            log.exception('Exception when handling a request')
                        # off we go
                        os._exit(0)
                    else:
                        # this is parent
                        child_pids.append(pid)
                        # close unused connected socket
                        conn.close()
        except KeyboardInterrupt:
            for pid in child_pids:
                try:
                    os.kill(pid, signal.SIGTERM)
                except:
                    pass


def main():
    parser = optparse.OptionParser(
        description='Test harness to make your system under test cynical ')
    parser.add_option(
        '-c', '--config', dest='config_path',
        help=(
            'Path to an INI configuration file. If no configuration '
            'file is provided then default configuration is applied. '
            'To see the default configuration use -d option described below.'
            )
        )
    parser.add_option(
        '-d', '--dump', dest='dump', action='store_true',
        default=False, help='Dump default configuration to STDOUT'
        )

    options, args = parser.parse_args()

    if options.dump:
        print DEFAULT_CONFIG
        sys.exit(0)

    path = options.config_path
    if path is None:
        path = StringIO.StringIO(DEFAULT_CONFIG)

    config = _load_config(path)
    handlers = _get_handler_configs(config)
    ioloop = IOLoop(handlers)
    ioloop.run()

