from INET import Transport as INET

import socket
import logging

LOG = logging.getLogger('Broker.Transports.TCP')

DEFAULT_PORT = 3323
DEFAULT_HOST = 'localhost'

class Transport(INET):

    socket_type = socket.SOCK_STREAM

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, timeout=None):
        INET.__init__(self, host, port, timeout)

        try:
            #try some basic socket options
            #failure should be OK
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)

            #60 seconds of idle connection time before starting to send probes
            self.__socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 60)

            #send probes every 60 seconds
            self.__socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 60)

            #after 5 failed probes (5 minutes) the connection is considered to be dead
            self.__socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 5)

        except Exception, ex:
            LOG.warning("Socket options failed. %s", ex)

