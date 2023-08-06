from __future__ import with_statement #for python 2.5

from Broker.Messages import Message, Subscribe, Unsubscribe, Acknowledge, Publish, Acknowledge, Notification, Poll, Fault, Ping, Pong, Accepted
from Broker.Transport import TCP, UDP
from Broker.Clients import Minimal

import collections

import threading
from Queue import Queue

from uuid import uuid1 as uuid

import logging

#Try to use the fastest serializer possible
try:
    from Broker.Codecs import Thrift as Codec
except ImportError:
    try:
        from Broker.Codecs import Protobuf as Codec
    except ImportError:
        raise NotImplementedError('No protocol serializer found')

class Client(threading.Thread):
    '''Basic client for Broker'''

    def __init__(self, transport, codec=Codec()):
        self.__log = logging.getLogger("Broker")
        threading.Thread.__init__(self)
        self.__minimal = Minimal(codec=codec, transport=transport)
        self.__rqueue = Queue(1)
        self.__wqueue = Queue(1)
        self.__callback_lock = threading.RLock()

        self.__callbacks = {
            'TOPIC' : {},
            'QUEUE' : {},
            'POLL'  : {},
            'PONG'  : {},
        }

        def __rloop():
            while True:
                self.__log.debug('__rloop reading')
                message = self.__minimal.receive()
                self.__log.debug('__rloop read %r', message)
                self.__rqueue.put(message)

        def __wloop():
            while True:
                self.__log.debug('__wloop reading')
                message = self.__wqueue.get()
                self.__log.debug('__wloop read %r', message)
                self.__minimal.send(message)
                self.__log.debug('__wloop sent %r', message)
                self.__wqueue.task_done()
        
        self.__rthread = threading.Thread(target=__rloop, name='broker_r')
        self.__rthread.setDaemon(True)

        self.__wthread = threading.Thread(target=__wloop, name='broker_w')
        self.__wthread.setDaemon(True)

        self.setDaemon(True)
        
        #start threads
        self.__log.debug('Starting threads')
        self.__rthread.start()
        self.__wthread.start()
        self.__log.debug('Threads started')

    def send(self, message, block=True, timeout=None):
        return self.__wqueue.put(message, block, timeout)

    def receive(self, block=True, timeout=None):
        msg = self.__rqueue.get(block=True, timeout=None)
        self.__rqueue.task_done()
        return msg

    def subscribe(self, destination, callback, destination_type='TOPIC', auto_acknowledge=True):
        self.__log.debug('subscribe(%r, %r, %r, %r)', destination, callback, destination_type, auto_acknowledge)
        
        with self.__callback_lock:
            #can't resubscribe a topic
            assert(destination not in self.__callbacks[destination_type])
            #can't subscribe a polled destination
            assert(destination not in self.__callbacks['POLL'])

            if 'QUEUE' == destination_type and auto_acknowledge:
                #I hate python's scope semantics
                orig_callback = callback
                def auto_ack_callback(msg):
                    #should I ack before or after processing?
                    self.acknowledge(msg)
                    orig_callback(msg)

                callback = auto_ack_callback

            self.__callbacks[destination_type][destination] = callback

        return self.send(Subscribe(destination=destination, destination_type=destination_type))

    #TODO implement timeout
    def poll(self, destination, callback, auto_acknowledge=True):
        with self.__callback_lock:
            #can't poll a subscribed destination
            assert(destination not in self.__callbacks['QUEUE'])
            
            if auto_acknowledge:
                orig_callback = callback
                def auto_ack_callback(msg):
                    #should I ack before or after processing?
                    self.acknowledge(msg)
                    orig_callback(msg)
                callback = auto_ack_callback
            
            polls = self.__callbacks['POLL']
            if destination in polls:
                polls[destination].append(callback)
            else:
                polls[destination] = collections.deque([callback])
    
        return self.send(Poll(destination=destination, timeout=1))

    def unsubscribe(self, destination, destination_type='TOPIC'):
        self.__log.debug('subscribe(%r, %r)', destination, destination_type)

        with self.__callback_lock:
            del self.__callbacks[destination_type][destination]

        return self.send(Unsubscribe(destination, destination_type))

    def publish(self, payload, destination, destination_type='TOPIC', expiration=None):
        message = Message(payload=payload, expiration=expiration)

        self.__log.debug('publish(%r, %r, %r, %r)', message, destination, destination_type, expiration)
        return self.send(Publish(message, destination, destination_type))

    def acknowledge(self, message):
        self.__log.debug('acknowledge(%r)', message)
        return self.send(Acknowledge(message_id=message.message.id, destination=message.destination))

    #TODO implement timeout
    def ping(self, callback):

        action_id = str(uuid())

        with self.__callback_lock:
            self.__callbacks['PONG'][action_id] = callback

        return self.send(Ping(action_id))

    #TODO take care of timeouts
    def __dispatch_fault(self, msg):
        raise msg

    def __dispatch_pong(self, msg):
        action_id = msg.action_id

        try:
            with self.__callback_lock:
                callback = self.__callbacks['PONG'][action_id]
                del self.__callbacks['PONG'][action_id]

        except KeyError:
            raise KeyError('Unknown pong callbackk for %r' % action_id)

        callback()

    def __dispatch_accepted(self, msg):
        raise NotImplementedError
        pass

    def handle_fault(self, fault):
        self.__log.error('Broker Fault: %r', fault)

    def __dispatch_notification(self, msg):
        try:
            with self.__callback_lock:
                if 'TOPIC' == msg.destination_type:
                    callback = self.__callbacks['TOPIC'][msg.subscription]
                elif 'QUEUE' == msg.destination_type:
                    if msg.subscription in self.__callbacks['QUEUE']:
                        callback = self.__callbacks['QUEUE'][msg.subscription]
                    else:
                        callback = self.__callbacks['POLL'][msg.subscription].popleft()

        except:
            raise KeyError('No handler for %s:%s' % (msg.destination_type, msg.subscription))
    
        return callback(msg)

    def run_once(self, block=True):
        self.__log.debug('loop_read_once(block=%r)', block)
        msg = self.receive(block)
        self.__log.debug('read message %r', msg)

        #dispatch message types
        try:
            return {
                Notification: self.__dispatch_notification,
                Fault:        self.__dispatch_fault,
                Pong:         self.__dispatch_pong,
                Accepted:     self.__dispatch_accepted,
                Fault:        self.handle_fault
            }[msg.__class__](msg)

        except KeyError:
            self.__log.error('Unknown message type %r', msg)
            raise

    def run(self):
        while True:
            self.run_once()
