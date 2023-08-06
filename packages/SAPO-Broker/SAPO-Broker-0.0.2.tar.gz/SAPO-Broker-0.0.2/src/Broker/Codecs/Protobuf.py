from __future__ import absolute_import

from .autogen import protobuf_2
from ..Transport import Message as TransportMessage
from ..Messages import Message as BrokerMessage, Publish, Poll, Accepted, Acknowledge, Subscribe, Unsubscribe, Notification, Fault, Ping, Pong, Authentication

from calendar import timegm

Atom = protobuf_2.Atom

_string2kind = {
    'TOPIC' : Atom.TOPIC,
    'QUEUE' : Atom.QUEUE,
    'VIRTUAL_QUEUE' : Atom.VIRTUAL_QUEUE
}

#invert the dicitonary
_kind2string = dict([ (_string2kind[k], k) for k in _string2kind ])

def string2kind(skind):
    return _string2kind[skind]

def kind2string(kind):
    return _kind2string[kind]

def serialize_publish(message, action):
    action.action_type = action.PUBLISH

    publish = action.publish
    publish.destination = message.destination
    publish.destination_type = string2kind(message.destination_type)
    publish.message.payload = message.message.payload
    
    # XXX is it possible to specify the message id?
    if message.message.id is not None:
        publish.message.message_id = message.message.id

    def datetime2epoch(datetime):
        return int(timegm(datetime.timetuple())*1000) #broker expects milliseconds

    # XXX does it make sense to specify the timestamp at message production?
    if message.message.timestamp is not None:
        publish.message.timestamp = datetime2epoch(message.message.timestamp)
    if message.message.expiration is not None:
        publish.message.expiration = datetime2epoch(message.message.expiration)

    action_id = message.action_id
    if action_id is not None:
        action.action_id = action_id

def serialize_poll(message, action):
    action.action_type = action.POLL

    poll = action.poll
    poll.destination = message.destination
    poll.timeout = message.timeout

    action_id = message.action_id
    if action_id is not None:
        action.action_id = action_id

def parse_accepted(action):
    return Accepted(action_id=action.accepted.action_id)

def serialize_acknowledge(message, action):
    action.action_type = action.ACKNOWLEDGE_MESSAGE
    acknowledge  = action.ack_message

    acknowledge.message_id = message.message_id
    acknowledge.destination = message.destination

    action_id = message.action_id
    if action_id is not None:
        action.action_id = action_id

def serialize_subscribe(message, action):
    action.action_type = action.SUBSCRIBE

    subscribe = action.subscribe
    subscribe.destination = message.destination
    subscribe.destination_type = string2kind(message.destination_type)

    action_id = message.action_id
    if action_id is not None:
        action.action_id = action_id

def serialize_unsubscribe(message, action):
    action.action_type = action.UNSUBSCRIBE

    unsubscribe = action.unsubscribe
    unsubscribe.destination = message.destination
    unsubscribe.destination_type = string2kind(message.destination_type)

    action_id = message.action_id
    if action_id is not None:
        action.action_id = action_id

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
    action.action_type = action.PING
    action.ping.action_id = message.action_id

def parse_pong(action):
    pong = action.pong

    return Pong(action_id=pong.action_id)

def serialize_authentication(message, action):
    action.action_type = action.AUTH
    auth = action.auth

    auth.token = message.token
    auth.role.extend(message.role)

    user_id = message.user_id
    if user_id is not None:
        auth.user_id = message.user_id

    authentication_type = message.authentication_type
    if authentication_type is not None:
        auth.authentication_type = authentication_type

    action_id = message.action_id
    if action_id is not None:
        auth.action_id = action_id

class Codec:
    __all__ = ['__init__', 'serialize', 'deserialize']

    encoding_type = 1
    encoding_version = 0

    __dispatch_serialize = {
        Publish : serialize_publish,
        Poll : serialize_poll,
        Acknowledge : serialize_acknowledge,
        Subscribe : serialize_subscribe,
        Unsubscribe : serialize_unsubscribe,
        Ping : serialize_ping,
        Authentication : serialize_authentication,
    }

    __dispatch_deserialize = {
        Atom.Action.NOTIFICATION : parse_notification,
        Atom.Action.FAULT : parse_fault,
        Atom.Action.PONG : parse_pong,
        Atom.Action.ACCEPTED : parse_accepted,
    }

    def __init__(self):
        pass

    def serialize(self, message):
        '''Given a Broker Message returns a Message object properly serialized to be sent using a Transport'''

        atom = Atom()
        action = atom.action

        #now it depends on the message type

        code = self.__dispatch_serialize[message.__class__]
        code(message, action)

        #get the message binary payload
        payload = atom.SerializeToString()
        return TransportMessage(payload=payload, encoding_type=self.encoding_type, encoding_version=self.encoding_version)

    def deserialize(self, data):
        '''Given bytes returns the broker message they represent'''

        atom = Atom()
        atom.ParseFromString(data)
        action = atom.action

        return self.__dispatch_deserialize[action.action_type](action)
