MAX_MESSAGE_SIZE = 2**(10+8)
import struct   #for pack/unpack

__all__ = ['Transport', 'Message']

try:
    bytes = bytes
except NameError:
    bytes = str

class Transport:
    """Basic class that abstracts a Transport.
    Only sends and receives data.
    
    By default nothing is implemented and subclasses MUST implement relevant methods."""

    def __init__(self):
        pass

    def send(self, message):
        raise NotImplementedError

    def receive(self):
        raise NotImplementedError

class Message:

    _packer = struct.Struct("!HHL")

    def __init__(self, payload, encoding_type=0, encoding_version=0):
        #TODO check types?
        self.type = encoding_type
        self.version = encoding_version
        self.payload = payload

    def get_header(self):
        return self._packer.pack(self.type, self.version, len(self.payload))

    def __bytes__(self):
        if isinstance(self.payload, bytes):
            return self.get_header() + self.payload
        else:
            raise TypeError("can only serialize bytes")

    __str__ = __bytes__

    @classmethod
    def meta_from_header(cls, data):
        return dict( zip( ['type', 'version', 'length'], cls._packer.unpack(data)))
