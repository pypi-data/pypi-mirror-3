from logging.handlers import SocketHandler
from threading import Thread
from Queue import Queue
import socket
import json
import sys


class BambooHandler(SocketHandler):
    def __init__(self, host, port, prefix=''):
        SocketHandler.__init__(self, host, port)
        self.closeOnError = 1
        self.prefix = prefix.format(hostname=socket.getfqdn())
        self.queue = Queue()
        self.thread = Thread(target=self.run)
        self.thread.setDaemon(True)
        self.thread.start()

    def makePickle(self, record):
        """
        Use JSON.
        """
        #ei = record.exc_info
        #if ei:
        #    dummy = self.format(record) # just to get traceback text into record.exc_text
        #    record.exc_info = None  # to avoid Unpickleable error
        s = '%s%s:%i:%s\n' % (self.prefix, record.name, int(record.created), self.format(record))
        #if ei:
        #    record.exc_info = ei  # for next handler
        return s

    def send(self, s):
        if self.queue.qsize() > 200:
            sys.stderr.write('Dropping bamboo log: Queue is full (%i)\n' %
                self.queue.qsize())
            return
        self.queue.put(s)

    def run(self):
        print 'Start logger thread'
        while True:
            s = self.queue.get()
            SocketHandler.send(self, s)
