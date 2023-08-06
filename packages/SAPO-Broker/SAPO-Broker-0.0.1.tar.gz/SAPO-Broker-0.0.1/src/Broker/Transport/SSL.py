from TCP import Transport as TCP

import logging
try:
    from ssl import wrap_socket
except ImportError:
    #try old socket.ssl interface
    from socket import ssl as wrap_socket

LOG = logging.getLogger('Broker.Transports.TCP')
DEFAULT_PORT = 3390
DEFAULT_HOST = 'localhost'

class Transport(TCP):

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, timeout=None):
        TCP.__init__(self, host, port, timeout)

        #now try to warp the socket into SSL stuf
        self.__socket = wrap_socket(self.__socket)
        #ssl doesn't have a recv method so emulate it
        self.__socket.recv = self.__socket.read
