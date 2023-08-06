from bamboo import Source, Sink, log
import eventlet

from datetime import datetime
import resource
import logging
import os.path
import sys
import os

log = log.getChild('core')


class TCPSource(Source):
    def __init__(self, port=4200):
        Source.__init__(self)
        self.port = port

    def __str__(self):
        return 'TCPSource(port=%i)' % self.port

    def handle(self, fd):
        while True:
            line = fd.readline()
            line = line.strip('\r\n ')
            if not line:
                break
            try:
                key, ts, message = line.split(':', 2)
            except ValueError, e:
                log.warning('%s: Malformed line: %s %r' % (self, str(e), line))
                fd.write('ERR %s\n' % str(e))
                fd.flush()
                continue
            self.process(key, ts, message)
        try:
            fd.close()
        except:
            pass

    def run(self):
        server = eventlet.listen(('127.0.0.1', self.port))
        while True:
            newsock, address = server.accept()
            log.info('%s: Accepted connection from %s' % (self, address[0]))
            eventlet.spawn_n(self.handle, newsock.makefile('rw'))


class StreamSink(Sink):
    def __init__(self, fd):
        Sink.__init__(self)
        if fd == 'stdout':
            fd = file(sys.stdout, 'w')
        if fd == 'stderr':
            fd = file(sys.stderr, 'w')
        self.fd = fd

    def __str__(self):
        return 'StreamSink(fd=%r)' % self.fd.name

    def send(self, key, ts, message):
        self.fd.write('%s:%i:%s\n' % (key, ts, message))
        self.fd.flush()



class FileSink(Sink):
    def __init__(self, path, fmt='{dt.year}/{dt.month}/{dt.day}/{key}.log',
        msgfmt='{key}:{ts}:{message}\n', sync=False, **kwargs):
        Sink.__init__(self)
        self.path = path
        self.fmt = fmt
        self.msgfmt = msgfmt
        self.sync = sync
        self.kwargs = kwargs

        self.openfiles = {}
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.isdir(path):
            raise Exception('%s is not a directory!' % path)

    def __str__(self):
        return 'FileSink(path=%r, fmt=%r, msgfmt=%r, sync=%r, kwargs=%r)' % (
            self.path, self.fmt, self.msgfmt, self.sync, self.kwargs)

    def reload(self):
        log.info('%s: Reopening %i files' % (self, len(self.openfiles)))
        for filename, fd in self.openfiles.iteritems():
            fd.flush()
            fd.close()
        self.openfiles = {}

    def send(self, key, ts, message):
        dt = datetime.utcfromtimestamp(ts)
        filename = os.path.join(self.path,
            self.fmt.format(key=key, ts=ts, dt=dt, kwargs=self.kwargs))

        dname = os.path.dirname(filename)
        if not os.path.exists(dname):
            log.info('%s: Creating directory %s' % (self, dname))
            os.makedirs(dname)

        if filename in self.openfiles:
            fd = self.openfiles[filename]
        else:
            fd = file(filename, 'a')
            self.openfiles[filename] = fd

            # If half of the soft max open file limit is reached, close one
            if len(self.openfiles) > (resource.getrlimit(
                resource.RLIMIT_NOFILE)[0] / 2):
                p = self.openfiles.popitem()
                if p != fd:
                    log.info('%s: Closing %s to conserve file descriptors' % \
                        (self, p.name))
                    p.flush()
                    p.close()

        line = self.msgfmt.format(key=key, ts=ts, dt=dt, message=message)
        fd.write(line)
        if self.sync:
            fd.flush()
