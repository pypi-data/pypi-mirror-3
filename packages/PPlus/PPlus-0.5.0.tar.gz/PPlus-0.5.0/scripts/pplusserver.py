#!/usr/bin/env python
"""PPlus Network Server"""

# Author: Vitalii Vanovschi <support@parallelpython.com>,
#         Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Grzegorz Zycinski <grzegorz.zycinski@disi.unige.it>
# License: BSD Style.

import logging
import argparse
import sys
import socket
import threading
import random
import string
import time
import os

from pplus import __version__ as version
from pplus.core import pp, ppauto, ppcommon, pptransport
from pplus.jobutils import detect_ncpus

LISTEN_SOCKET_TIMEOUT = 20

# compatibility with Python 2.6
try:
    import hashlib
    sha_new = hashlib.sha1
except ImportError:
    import sha
    sha_new = sha.new


class _NetworkServer(pp.Server):
    """Network Server Class
    """

    def __init__(self, ncpus="autodetect", interface="0.0.0.0",
                broadcast="255.255.255.255", port=None, secret=None,
                timeout=None, restart=False, proto=2):
        pp.Server.__init__(self, ncpus, secret=secret, restart=restart,
                proto=proto)
        self.host = interface
        self.bcast = broadcast
        if port is not None:
            self.port = port
        else:
            self.port = self.default_port
        self.timeout = timeout
        self.ncon = 0
        self.last_con_time = time.time()
        self.ncon_lock = threading.Lock()

        self.logger.debug("Starting network server interface=%s port=%i"
                % (self.host, self.port))
        if self.timeout is not None:
            self.logger.debug("pplusserver will exit in %i seconds if no "\
                    "connections with clients exist" % (self.timeout))
            ppcommon.start_thread("timeout_check",  self.check_timeout)

    def ncon_add(self, val):
        """Keeps track of the number of connections and time of the last one"""
        self.ncon_lock.acquire()
        self.ncon += val
        self.last_con_time = time.time()
        self.ncon_lock.release()

    def check_timeout(self):
        """Checks if timeout happened and shutdowns server if it did"""
        while True:
            if self.ncon == 0:
                idle_time = time.time() - self.last_con_time
                if idle_time < self.timeout:
                    time.sleep(self.timeout - idle_time)
                else:
                    self.logger.debug("exiting pplusserver due to timeout "
                                      "(no client connections in last %i sec)"
                                      % self.timeout)
                    os._exit(0)
            else:
                time.sleep(self.timeout)

    def listen(self):
        """Initiates listenting to incoming connections"""
        try:
            self.ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # following allows pplusserver to restart faster on the same port
            self.ssocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ssocket.settimeout(LISTEN_SOCKET_TIMEOUT)
            self.ssocket.bind((self.host, self.port))
            self.ssocket.listen(5)
        except socket.error, e:
            self.logger.error("Cannot create socket for "
                              "%s:%s, %s" % (self.host, self.port, e))

        try:
            while 1:
                csocket = None
                #accept connections from outside
                try:
                    (csocket, address) = self.ssocket.accept()
                except socket.timeout:
                    pass
                if self._exiting:
                    return
                #now do something with the clientsocket
                #in this case, we'll pretend this is a threaded server
                if csocket:
                    ppcommon.start_thread("client_socket",  self.crun,
                                          (csocket,))
        except:
            if pp.SHOW_EXPECTED_EXCEPTIONS:
                self.logger.debug("Exception in listen method "
                                  "(possibly expected)", exc_info=True)
            self.logger.debug("Closing server socket")
            self.ssocket.close()

    def crun(self, csocket):
        """Authenticates client and handles its jobs"""
        mysocket = pptransport.CSocketTransport(csocket)
        #send PP version
        mysocket.send(version)
        #generate a random string
        srandom = "".join([random.choice(string.ascii_letters)
                for i in xrange(16)])
        mysocket.send(srandom)
        answer = sha_new(srandom + self.secret).hexdigest()
        clientanswer = mysocket.receive()
        if answer != clientanswer:
            self.logger.warning("Authentication failed, client host=%s, "
                                "port=%i" % csocket.getpeername())
            mysocket.send("FAILED")
            csocket.close()
            return
        else:
            mysocket.send("OK")

        ctype = mysocket.receive()
        self.logger.debug("Control message received: " + ctype)
        self.ncon_add(1)
        try:
            if ctype == "STAT":
                #reset time at each new connection
                self.get_stats()["local"].time = 0.0
                mysocket.send(str(self.get_ncpus()))
                while 1:
                    mysocket.receive()
                    mysocket.send(str(self.get_stats()["local"].time))
            elif ctype == "EXEC":
                while 1:
                    sfunc = mysocket.creceive()
                    sargs = mysocket.receive()
                    fun = self.insert(sfunc, sargs)
                    sresult = fun(True)
                    mysocket.send(sresult)
        except:
            if self._exiting:
                return
            if pp.SHOW_EXPECTED_EXCEPTIONS:
                self.logger.debug("Exception in crun method "
                                  "(possibly expected)", exc_info=True)
            self.logger.debug("Closing client socket")
            csocket.close()
            self.ncon_add(-1)

    def broadcast(self):
        """Initiaates auto-discovery mechanism"""
        discover = ppauto.Discover(self)
        ppcommon.start_thread("server_broadcast",  discover.run,
                ((self.host, self.port), (self.bcast, self.port)))


def create_network_server(argv):
    parser = argparse.ArgumentParser(
        description="PPlus Network Server (pplus-%s)" % version)

    # Options
    parser.add_argument('-d, --debug', dest='debug', action='store_true',
                        help='set log level to debug')
    parser.add_argument('-a, --auto', dest='auto', action='store_true',
                        help='enable auto-discovery service')
    parser.add_argument('-r, --restart', dest='restart', action='store_true',
                        help='restart worker process after each '
                             'task completion')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + version)

    # Network configuration
    parser.add_argument('-i, --interface', dest='interface', action='store',
                        default="0.0.0.0",
                        help='interface to listen')
    parser.add_argument('-p, --port', dest='port', action='store',
                        type=int,
                        help='port to listen')
    parser.add_argument('-b, --broadcast', dest='broadcast', action='store',
                        default="255.255.255.255",
                        help='broadcast address for auto-discovery service')

    # Workers configuration
    parser.add_argument('-w, --workers', dest='workers', action='store',
                        type=int, default=-1,
                        choices=range(1, detect_ncpus()+1),
                        help='number of workers to start')
    parser.add_argument('-s, --secret', dest='secret', action='store',
                        help='secret for authentication')
    parser.add_argument('-t, --timeout', dest='timeout', action='store',
                        help='timeout to exit if no connections with'
                             'clients exist')
    parser.add_argument('-n, --nproto', dest='protonum', action='store',
                        type=int, default=2,
                        help='protocol number for pickle module')

    args = parser.parse_args()

    # Logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_level = logging.WARNING # default
    if args.debug:
        log_level = logging.DEBUG
        pp.SHOW_EXPECTED_EXCEPTIONS = True

    # Autodiscovery
    autodiscovery = args.auto

    # Server Args
    server_args = {
        'interface':args.interface,
        'secret':args.secret,
        'port':args.port,
        'ncpus':"autodetect" if args.workers < 0 else args.workers,
        'restart':args.restart,
        'broadcast':args.broadcast,
        'proto':args.protonum,
        'timeout':args.timeout
    }

    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger("pplus").setLevel(log_level)
    logging.getLogger("pplus").addHandler(log_handler)

    server = _NetworkServer(**server_args)
    if autodiscovery:
        server.broadcast()
    return server

if __name__ == "__main__":
    server = create_network_server(sys.argv[1:])
    server.listen()
    #have to destroy it here explicitly otherwise an exception
    #comes out in Python 2.4
    del server
