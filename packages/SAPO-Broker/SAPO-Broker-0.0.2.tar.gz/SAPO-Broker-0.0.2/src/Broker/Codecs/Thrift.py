from __future__ import absolute_import

from .autogen.thrift.broker import ttypes
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport

from ..Transport import Message as TransportMessage
from ..Messages import Message as BrokerMessage, Publish, Poll, Accepted, Acknowledge, Subscribe, Unsubscribe, Notification, Fault, Ping, Pong, Authentication

from calendar import timegm

_string2kind = {
    'TOPIC' : ttypes.DestinationType.TOPIC,
    'QUEUE' : ttypes.DestinationType.QUEUE,
    'VIRTUAL_QUEUE' : ttypes.DestinationType.VIRTUAL_QUEUE
}

#invert the dictionary
_kind2string = dict([ (_string2kind[k], k) for k in _string2kind ])

def string2kind(skind):
    return _string2kind[skind]

def kind2string(kind):
    return _kind2string[kind]

def serialize_publish(message, action):
    action.action_type = ttypes.ActionType.PUBLISH

    publish = ttypes.Publish()
    publish.destination = message.destination
    publish.destination_type = string2kind(message.destination_type)

    publish.message = ttypes.BrokerMessage()
    publish.message.payload = message.message.payload
    
    # XXX is it possible to specify the message id?
    if message.message.id is not None:
        publish.message.message_id = message.message.id

    def datetime2epoch(datetime):
        return timegm(datetime.timetuple())*1000 #broker expects milliseconds

    # XXX does it make sense to specify the timestamp at message production?
    if message.message.timestamp is None:
        # XXX thrift kludge
        publish.message.timestamp = -1
    else:
        publish.message.timestamp = datetime2epoch(message.message.timestamp)

    if message.message.expiration is None:
        publish.message.expiration = -1
    else:
        # XXX thrift kludge
        publish.message.expiration = datetime2epoch(message.message.expiration)

    action_id = message.action_id
    if action_id is not None:
        publish.action_id = action_id

    action.publish = publish

def serialize_poll(message, action):
    action.action_type = ttypes.ActionType.POLL

    poll = ttypes.Poll()
    poll.destination = message.destination
    poll.timeout = message.timeout

    action_id = message.action_id
    if action_id is not None:
        poll.action_id = action_id

    action.poll = poll

def parse_accepted(action):
    return Accepted(action_id=action.accepted.action_id)

def serialize_acknowledge(message, action):
    action.action_type = ttypes.ActionType.ACKNOWLEDGE

    acknowledge  = ttypes.Acknowledge()
    acknowledge.message_id = message.message_id
    acknowledge.destination = message.destination

    action_id = message.action_id
    if action_id is not None:
        acknowledge.action_id = action_id

    action.ack_message = acknowledge

def serialize_subscribe(message, action):
    action.action_type = ttypes.ActionType.SUBSCRIBE

    subscribe = ttypes.Subscribe()
    subscribe.destination = message.destination
    subscribe.destination_type = string2kind(message.destination_type)

    action_id = message.action_id
    if action_id is not None:
        subscribe.action_id = action_id

    action.subscribe = subscribe

def serialize_unsubscribe(message, action):
    action.action_type = ttypes.ActionType.UNSUBSCRIBE

    unsubscribe.destination = message.destination
    unsubscribe.destination_type = string2kind(message.destination_type)

    action_id = message.action_id
    if action_id is not None:
        unsubscribe.action_id = action_id

    action.unsubscribe = unsubscribe

def parse_notification(action):
    notification = action.notification
    msg = notification.message
    message = BrokerMessage(payload=msg.payload, id=msg.message_id, timestamp=msg.timestamp/1000., expiration=msg.expiration/1000.)
    return Notification(destination=notification.destination, destination_type=kind2string(notification.destination_type), subscription=notification.subscription, message=message)

def parse_fault(action):
    fault = action.fault
    retfault = Fault(fault_code=fault.fault_code, fault_message=fault.fault_message)
    
    if fault.fault_detail is not None:
        retfault.fault_detail = fault.fault_detail

    if fault.action_id is not None:
        retfault.fault_detail = fault.action_id

    return retfault

def serialize_ping(message, action):
    action.action_type = ttypes.ActionType.PING

    ping = ttypes.Ping()
    ping.action_id = message.action_id
    action.ping = ping

def parse_pong(action):
    pong = action.pong

    return Pong(action_id=pong.action_id)

def serialize_authentication(message, action):
    action.action_type = ttypes.ActionType.AUTH

    auth = ttypes.Authentication()
    auth.token = message.token
    auth.role = message.role

    user_id = message.user_id
    if user_id is not None:
        auth.user_id = message.user_id

    authentication_type = message.authentication_type
    if authentication_type is not None:
        auth.authentication_type = authentication_type

    action_id = message.action_id
    if action_id is not None:
        auth.action_id = action_id

    action.auth = auth


class Codec:
    __all__ = ['__init__', 'serialize', 'deserialize']

    encoding_type = 2
    encoding_version = 0

    __dispatch_serialize = {
        Publish : serialize_publish,
        Poll : serialize_poll,
        Acknowledge : serialize_acknowledge,
        Subscribe : serialize_subscribe,
        Unsubscribe : serialize_unsubscribe,
        Ping : serialize_ping,
        Authentication: serialize_authentication,
    }

    __dispatch_deserialize = {
        ttypes.ActionType.NOTIFICATION : parse_notification,
        ttypes.ActionType.FAULT : parse_fault,
        ttypes.ActionType.PONG : parse_pong,
        ttypes.ActionType.ACCEPTED : parse_accepted,
    }

    def __init__(self):
        pass

    def serialize(self, message):
        '''Given a Broker Message returns a Message object properly serialized to be sent using a Transport'''

        atom = ttypes.Atom()
        action = ttypes.Action()

        #now it depends on the message type

        code = self.__dispatch_serialize[message.__class__]
        code(message, action)

        atom.action = action

        #serialization objects
        transportOut = TTransport.TMemoryBuffer()
        protocolOut = TBinaryProtocol.TBinaryProtocol(transportOut)
        atom.write(protocolOut)

        #get the message binary payload
        payload = transportOut.getvalue()

        return TransportMessage(payload=payload, encoding_type=self.encoding_type, encoding_version=self.encoding_version)

    def deserialize(self, data):
        '''Given bytes returns the broker message they represent'''

        atom = ttypes.Atom()

        transportIn = TTransport.TMemoryBuffer(data)
        protocolIn = TBinaryProtocol.TBinaryProtocol(transportIn)

        atom.read(protocolIn)
        action = atom.action

        return self.__dispatch_deserialize[action.action_type](action)
