from datetime import datetime
from urllib import urlopen, urlencode
from xml.dom.minidom import parseString
import types

def todate(date):
    if date is None:
        return date
    elif isinstance( date, datetime ):
        return date
    elif type(date) in (types.IntType, types.FloatType):
        return datetime.utcfromtimestamp(date)
    else:
        #XXX warn
        return datetime.utcnow()

class Message:
    def __init__(self, payload, id=None, timestamp=None, expiration=None):
        """
        Creates a Broker message given the mandatory payload and destination.
        All other fields are optional.

        This object has as fields all the parameters used in this construtor.
        
        timestamp and expiration are supposed to be datetime objects and default to None and are thus optional.
        If these fields don't have timezone information, they are assumed to be in UTC.
        You can also pass seconds since the epoch.

        id is supposed to be a unique id of the message and defaults to None meaning that the Broker server will generate one automatically.

        This object should be constructed to send an event notification to the Server and is returned by the Client object when a new event is received.
        """

        self.payload       = payload
        self.id            = id
        self.timestamp     = timestamp
        self.expiration    = expiration

    def __set_timestamp(self, value):
        self.__timestamp = value
        return self

    def __get_timestamp(self):
        self.__timestamp = todate(self.__timestamp)
        return self.__timestamp

    def __set_expiration(self, value):
        self.__expiration = value
        return self

    def __get_expiration(self):
        self.__expiration = todate(self.__expiration)
        return self.__expiration

    timestamp  = property(fget=__get_timestamp, fset=__set_timestamp)
    expiration = property(fget=__get_expiration, fset=__set_expiration)

    def __str__(self):
        return self.payload

class Publish:
    def __init__(self, message, destination, destination_type, action_id=None):
        self.message = message
        self.destination = destination
        self.destination_type = destination_type
        self.action_id = action_id

class Poll:
    def __init__(self, destination, timeout, action_id=None):
        self.destination = destination
        self.timeout = timeout
        self.action_id = action_id

class Accepted:
    def __init__(self, action_id):
        self.action_id = action_id

class Acknowledge:
    def __init__(self, message_id, destination, action_id=None):
        self.message_id = message_id
        self.destination = destination
        self.action_id = action_id

class Subscribe:
    def __init__(self, destination, destination_type, action_id=None):
        self.destination = destination
        self.destination_type = destination_type
        self.action_id = action_id

class Unsubscribe:
    def __init__(self, destination, destination_type, action_id=None):
        self.destination = destination
        self.destination_type = destination_type
        self.action_id = action_id

class Notification:
    def __init__(self, destination, destination_type, subscription, message):
        self.destination = destination
        self.subscription = subscription
        self.destination_type = destination_type
        self.message = message

class Fault:
    def __init__(self, fault_code, fault_message, fault_detail=None, action_id=None):
        self.fault_code = fault_code
        self.fault_message = fault_message
        self.fault_detail = fault_detail
        self.action_id = action_id

    def __repr__(self):
        return '<%s(fault_code=%r, fault_message=%r, fault_detail=%r, action_id=%r)>' % (
            self.__class__,
            self.fault_code,
            self.fault_message,
            self.fault_detail,
            self.action_id
        )

class Ping:
    def __init__(self, action_id):
        self.action_id = action_id

class Pong:
    def __init__(self, action_id):
        self.action_id = action_id

class Authentication:
    __auth_url = r'https://services.sapo.pt/STS/GetToken?'

    def __init__(self, role, token, authentication_type, user_id=None, action_id=None):
        self.user_id = user_id
        self.role = role
        self.token = token
        self.authentication_type = authentication_type
        self.action_id = None

    @classmethod
    def from_sts_credentials(cls, username, password, role=[], authentication_type='SapoSTS', action_id=None):
        data = urlencode((('ESBUsername', username), ('ESBPassword', password)))
        url = cls.__auth_url+'?JSON=False&'+data
        xml = urlopen(url).read()

        dom = parseString(xml)

        top = dom.firstChild
        topname = top.nodeName
        if 'ESBToken' == topname:
            #xml OK
            token = top.firstChild.nodeValue.encode('ascii')
            return cls(role, token, authentication_type, None, action_id)

        elif 'fault' == topname:
            #try to get the faultstring
            for node in top.childNodes:
                if 'faultstring' == node.nodeName:
                    faultstring = node.firstChild.nodeValue
                    raise RuntimeError('Authentication error: %s' % faultstring)
