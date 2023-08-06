__all__ = []
try:
    from Protobuf import Codec as Protobuf
    Codec = Protobuf
    __all__.append('Protobuf')
except ImportError:
    pass

try:
    from Thrift import Codec as Thrift
    Codec = Thrift
    __all__.append('Thrift')
except ImportError:
    pass

if __all__:
    __all__.append('Codec')
else:
    raise ImportError('No Codec found. Please install thrift of protobufs.')
