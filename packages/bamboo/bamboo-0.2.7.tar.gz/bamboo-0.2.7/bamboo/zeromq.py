from bamboo import Source, Sink, log
from eventlet.green import zmq
from time import sleep
import eventlet
import logging

log = logging.getLogger('%s.zeromq' % log.name)


class ZMQPullSource(Source):
    def __init__(self, name, endpoint, identity=None, bind=False):
        Source.__init__(self, name)
        self.endpoint = str(endpoint)
        self.identity = str(identity)
        self.bind = bind
        self.running = True

    def open_socket(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        if self.identity:
            self.socket.setsockopt(zmq.IDENTITY, self.identity)
        if self.bind:
            log.debug('%s: Binding socket to %s' % (self, self.endpoint))
            self.socket.bind(self.endpoint)
        else:
            log.debug('%s: Connecting socket to %s' % (self, self.endpoint))
            self.socket.connect(self.endpoint)

    def reload(self):
        self.socket.close()
        sleep(1)
        eventlet.spawn_n(self.run)

    def stop(self):
        self.running = False
        self.socket.close()

    def run(self):
        self.open_socket()
        while self.running:
            try:
                m = self.socket.recv_multipart()
            except zmq.ZMQError, e:
                break

            if len(m) != 3:
                log.warning('%s: Wrong number of parts in message: %r' % \
                    (self, m))
                continue
            else:
                key, ts, message = m
                try:
                    ts = int(ts)
                except ValueError, e:
                    log.warning('%s: Malformed line: %s' % (self, e))
                    continue
                self.process(key, int(ts), message)
        log.debug('%s: Receive loop stopped' % self)


class ZMQPushSink(Sink):
    def __init__(self, name, endpoint, identity=None, bind=False):
        Sink.__init__(self, name)
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

    def send(self, key, ts, message):
        self.socket.send_multipart((key, str(ts), message))
