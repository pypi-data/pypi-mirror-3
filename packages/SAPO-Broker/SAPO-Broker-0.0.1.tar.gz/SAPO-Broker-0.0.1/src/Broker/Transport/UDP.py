from INET import Transport as INET

DEFAULT_PORT=3323
DEFAULT_HOST='localhost'

import socket
import logging
LOG = logging.getLogger('Broker.Transports.UDP')

class Transport(INET):

    socket_type = socket.SOCK_DGRAM

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, timeout=None):
        INET.__init__(self, host, port, timeout)

    def send(self, message):
        header = message.get_header()
        return self.__socket.sendall(header + message.payload)
