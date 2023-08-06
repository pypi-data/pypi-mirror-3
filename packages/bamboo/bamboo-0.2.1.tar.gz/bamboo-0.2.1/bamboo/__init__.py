import eventlet

import logging
import inspect
import json
import sys


log = logging.getLogger('bamboo')
stderr = logging.StreamHandler()
#stderr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(message)s', '%Y-%m-%d %H:%M:%S'))
stderr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
log.addHandler(stderr)
log.setLevel(logging.INFO)


class Handler(object):
    def __init__(self, name):
        log.debug('%s: Initializing' % self.__class__.__name__)
        self.name = name

    def __str__(self):
        return '%s/%s' % (self.__class__.__name__, self.name)


class Source(Handler):
    def __init__(self, name):
        Handler.__init__(self, name)
        self.sinks = set()

    def process(self, key, ts, message):
        for sink in self.sinks:
            sink.send(key, ts, message)
            eventlet.sleep()

    def add_sink(self, sink):
        log.debug('%s: Adding sink %s' % (self, sink))
        self.sinks.add(sink)

    def remove_sink(self, sink):
        log.debug('%s: Removing sink %s' % (self, sink))
        self.sinks.remove(sink)

    def run(self):
        pass


class Sink(Handler):
    def reload(self):
        pass

    def send(self, key, ts, message):
        pass


class Controller(object):
    def __init__(self):
        self.all_handlers = {}
        self.handlers = {}
        self.running = True

    def load_handlers(self, modulename):
        module = __import__(modulename, fromlist=['bamboo'])
        for name, handler in inspect.getmembers(module,
            lambda x: inspect.isclass(x) and issubclass(x, Handler)):
            if handler == Sink or handler == Source:
                continue
            log.debug('Loaded %s.%s' % (modulename, name))
            self.all_handlers[name] = handler

    def load_config(self, fd):
        if fd.name.find('.') == -1:
            log.error('Config file name must end with .json, .yaml, or .py')
            return

        configtype = fd.name.rsplit('.', 1)[1]

        if configtype == 'json':
            try:
                self.config = json.load(fd)
                if not isinstance(self.config, dict):
                    log.error('Config is not a dict: %r' % config)
                    return
                return self.config
            except ValueError, e:
                log.error('Unable to parse config file: %s' % str(e))
                return

        if configtype == 'yaml':
            try:
                import yaml
                self.config = yaml.safe_load(fd)
                if not isinstance(self.config, dict):
                    log.error('Config is not a dict: %r' % config)
                    return
                return self.config
            except ImportError, e:
                log.error('PyYAML must be installed to use a .yaml config file')
                return
            except Exception, e:
                log.error('Unable to parse config file: %s' % str(e))
                return

        if configtype == 'py':
            try:
                self.config = eval(fd.read())
                if not isinstance(config, dict):
                    log.error('Config is not a dict: %r' % config)
                    return
                return self.config
            except Exception, e:
                log.error('Unable to parse config file: %s' % str(e))
                return

        log.error('Unknown config type %r' % configtype)
        return

    def reload(self, signum, frame):
        for handler in self.handlers.values():
            if hasattr(handler, 'reload'):
                log.info('%s: Reloading' % handler)
                handler.reload()

    def start(self):
        modules = ['bamboo.core']
        modules += self.config.get('modules', [])
        for module in modules:
            log.debug('Loading handlers in %s' % module)
            self.load_handlers(module)

        log.debug('Creating handlers')
        for name, options in self.config.iteritems():
            if name == 'modules':
                continue
            classname, name = name.split('/', 1)
            sinks = options.pop('sinks', [])

            if not classname in self.all_handlers:
                log.error('Unknown handler: %s %r' % (classname, repr(options)))
                return
            c = self.all_handlers[classname]

            try:
                self.handlers[name] = (c(name, **options), sinks)
            except Exception, e:
                log.error('Initializing %s %s: %s' % (classname, name, str(e)))
                return

        for name, handler in self.handlers.iteritems():
            handler, sinks = handler
            for sink in sinks:
                if not sink in self.handlers:
                    log.warning('Cannot attach sink %s to %s. %s does not exist'
                        % (sink, name, sink))
                    continue
                handler.add_sink(self.handlers[sink][0])

        for name, handler in self.handlers.iteritems():
            handler = handler[0]
            self.handlers[name] = handler
            if hasattr(handler, 'run'):
                log.debug('%s: Running' % handler)
                eventlet.spawn_n(handler.run)
        return self.handlers

    def stop(self, signum, frame):
        for name, handler in self.handlers.iteritems():
            log.debug('%s: Stopping' % handler)
            if hasattr(handler, 'stop'):
                handler.stop()
            del handler
        self.running = False
