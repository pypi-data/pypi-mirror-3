from bamboo import Source, Sink, log
from eventlet.green import socket, subprocess
import eventlet

from datetime import datetime
import resource
import logging
import os.path
import time
import sys
import os
import re

log = logging.getLogger('%s.core' % log.name)


class TCPSource(Source):
    def __init__(self, name, port=4200):
        Source.__init__(self, name)
        self.port = port
        self.sock = None
        self.running = True

    def handle(self, fd):
        while True:
            line = fd.readline()
            line = line.strip('\r\n ')
            if not line:
                break
            try:
                key, ts, message = line.split(':', 2)
                ts = int(ts)
            except ValueError, e:
                log.warning('%s: Malformed line: %s %r' % (self, e, line))
                fd.write('ERR %s\n' % str(e))
                fd.flush()
                continue
            self.process(key, ts, message)
        try:
            fd.close()
        except:
            pass

    def run(self):
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(2)
        while self.running:
            try:
                newsock, address = self.sock.accept()
                log.info('%s: Accepted connection from %s' % (self, address[0]))
                eventlet.spawn_n(self.handle, newsock.makefile('rw'))
            except socket.error, e:
                if self.running:
                    log.error('%s: Error accepting connection: %s' % (self, e))
                break

    def stop(self):
        self.running = False
        if self.sock is not None:
            self.sock.close()

    def reload(self):
        self.stop()
        eventlet.sleep(1)
        eventlet.spawn_n(self.run)


class UDPSource(Source):
    def __init__(self, name, port=4200):
        Source.__init__(self, name)
        self.port = port
        self.sock = None
        self.running = True

    def handle(self, line):
        line = line.strip('\r\n ')
        try:
            key, ts, message = line.split(':', 2)
            ts = int(ts)
        except ValueError, e:
            log.warning('%s: Malformed line: %s %r' % (self, e, line))
            return
        self.process(key, ts, message)

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.port))
        while self.running:
            try:
                data, address = self.sock.recvfrom(2048)
                self.handle(data)
            except socket.error, e:
                if self.running:
                    log.error('%s: Error receiving data: %s' % (self, e))
                break

    def stop(self):
        self.running = False
        if self.sock is not None:
            self.sock.close()

    def reload(self):
        self.stop()
        eventlet.sleep(1)
        eventlet.spawn_n(self.run)


class SyslogSource(UDPSource):
    def __init__(self, name, port=514):
        UDPSource.__init__(self, name, port)
        self.pattern = re.compile('^<(?P<prival>[0-9]{1,3})>(?P<timestamp>[A-z]{3} [0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}) (?P<hostname>.*) (?P<appname>.*): (?P<message>.*)$')
        self.facilities = {
            0: 'kernel', 1: 'user', 2: 'mail', 3: 'daemon', 4: 'auth',
            5: 'syslog', 6: 'lpd', 7: 'news', 8: 'uucp', 9: 'cron',
            10: 'authpriv', 11: 'ftp', 12: 'ntp', 13: 'audit', 14: 'alert',
            15: 'mark', 16: 'local0', 17: 'local1', 18: 'local2', 19: 'local3',
            20: 'local4', 21: 'local5', 22: 'local6', 23: 'local7',
        }
        self.severities = {
            0: 'emerg', 1: 'alert', 2: 'crit', 3: 'err', 4: 'warning',
            5: 'notice', 6: 'info', 7: 'debug',
        }

    def handle(self, packet):
        match = self.pattern.match(packet)
        if match is None:
            log.warning('%s: Unable to parse packet: %r' % (self, packet))
            return
        msg = match.groupdict()

        prival = int(msg['prival'])
        severity = self.severities[prival % 8]
        facility = self.facilities[prival / 8]
        appname = msg['appname']
        if appname.find('[') != -1:
            appname = appname.split('[', 1)[0]
        key = '%s.%s.%s' % (appname, facility, severity)

        ts = time.strptime(msg['timestamp'], '%b %d %H:%M:%S')
        ts = int(time.mktime((time.gmtime().tm_year, ts.tm_mon, ts.tm_mday,
            ts.tm_hour, ts.tm_min, ts.tm_sec, -1, -1, -1)))

        self.process(key, ts, msg['message'])


class ExecSource(Source):
    def __init__(self, name, key, command):
        Source.__init__(self, name)
        self.key = key
        self.command = command
        self.running = True
        self.proc = None

    def run(self):
        log.debug('%s: Spawning %s' % (self, self.command))
        self.proc = subprocess.Popen(self.command, shell=True, bufsize=0,
                                     stdout=subprocess.PIPE)
        while True:
            line = self.proc.stdout.readline()
            if not line:
                break
            self.process(self.key, int(time.time()), line.rstrip('\r\n '))
        
        ret = self.proc.wait()
        if ret != 0:
            log.warning('%s: Exited with return code %i' % (self,
                ret))
        else:
            log.info('%s: Exited with return code %i' % (self, ret))

    def reload(self):
        if self.proc is None:
            return
        log.debug('%s: Killing pid %i' % (self, self.proc.pid))
        self.stop()
        eventlet.spawn_n(self.run)

    def stop(self):
        self.proc.poll()
        if self.proc.returncode is None:
            self.proc.kill()

class StreamSink(Sink):
    def __init__(self, name, fd):
        Sink.__init__(self, name)
        if fd == 'stdout':
            fd = sys.stdout
        if fd == 'stderr':
            fd = sys.stderr
        self.fd = fd

    def send(self, key, ts, message):
        self.fd.write('%s:%i:%s\n' % (key, ts, message))
        self.fd.flush()



class FileSink(Sink):
    def __init__(self, name, path,
        fmt='{dt.year:04}/{dt.month:02}/{dt.day:02}/{key}.log',
        msgfmt='{key}:{ts}:{message}\n', sync=False, **kwargs):
        Sink.__init__(self, name)
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

    def stop(self):
        log.info('%s: Closing %i files' % (self, len(self.openfiles)))
        for filename, fd in self.openfiles.iteritems():
            fd.flush()
            fd.close()
        self.openfiles = {}

    def reload(self):
        self.stop()

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
