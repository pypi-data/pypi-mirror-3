from bamboo import Source, Sink, log
from eventlet.green import zmq
import logging

log = log.getChild('zeromq')


class ZMQSource(Source):
    def __init__(self, endpoint, identity=None, bind=False):
        Source.__init__(self)
        self.endpoint = str(endpoint)
        self.identity = str(identity)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        if identity:
            self.socket.setsockopt(zmq.IDENTITY, self.identity)
        if bind:
            log.debug('%s: Binding socket to %s' % (self, self.endpoint))
            self.socket.bind(self.endpoint)
        else:
            log.debug('%s: Connecting socket to %s' % (self, self.endpoint))
            self.socket.connect(self.endpoint)

    def __str__(self):
        return 'ZMQSource(endpoint=%r, identity=%r)' % \
            (self.endpoint, self.identity)

    def run(self):
        while True:
            m = self.socket.recv_multipart()
            if len(m) != 3:
                log.warning('%s: Wrong number of parts in message: %r' % \
                    (self, m))
                continue
            else:
                key, ts, message = m
                self.process(key, int(ts), message)


class ZMQSink(Sink):
    def __init__(self, endpoint, identity=None, bind=False):
        Sink.__init__(self)
        self.endpoint = endpoint
        self.identity = identity
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        if bind:
            log.debug('%s: Binding socket to %s' % (self, endpoint))
            self.socket.bind(endpoint)
        else:
            log.debug('%s: Connecting socket to %s' % (self, endpoint))
            self.socket.connect(endpoint)

    def __str__(self):
        return 'ZMQSink(endpoint=%r, identity=%r)' % \
            (self.endpoint, self.identity)

    def send(self, key, ts, message):
        self.socket.send_multipart((key, str(ts), message))
