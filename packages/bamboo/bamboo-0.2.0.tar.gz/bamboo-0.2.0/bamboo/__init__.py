import eventlet

import importlib
import logging
import inspect
import json
import sys


log = logging.getLogger('bamboo')
stderr = logging.StreamHandler()
stderr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s',
    '%Y-%m-%d %H:%M:%S'))
log.addHandler(stderr)
log.setLevel(logging.INFO)


class Handler(object):
    def __init__(self):
        log.debug('%s: Initializing' % self.__class__.__name__)

    def __str__(self):
        return self.__class__.__name__


class Source(Handler):
    def __init__(self):
        Handler.__init__(self)
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


def load_handlers(module, handlers):
    module = importlib.import_module(module, 'bamboo')
    for name, handler in inspect.getmembers(module,
        lambda x: inspect.isclass(x) and issubclass(x, Handler)):
        if handler == Sink or handler == Source:
            continue
        handlers[name] = handler


def load_config(fd):
    if fd.name.find('.') == -1:
        log.error('Config file name must end with .json, .yaml, or .py')
        return

    configtype = fd.name.rsplit('.', 1)[1]

    if configtype == 'json':
        try:
            config = json.load(fd)
            if not isinstance(config, dict):
                log.error('Config is not a dict: %r' % config)
                return
            return config
        except ValueError, e:
            log.error('Unable to parse config file: %s' % str(e))
            return

    if configtype == 'yaml':
        try:
            import yaml
            config = yaml.safe_load(fd)
            if not isinstance(config, dict):
                log.error('Config is not a dict: %r' % config)
                return
            return config
        except ImportError, e:
            log.error('PyYAML must be installed to use a .yaml config file')
            return
        except Exception, e:
            log.error('Unable to parse config file: %s' % str(e))
            return

    if configtype == 'py':
        try:
            config = eval(fd.read())
            if not isinstance(config, dict):
                log.error('Config is not a dict: %r' % config)
                return
            return config
        except Exception, e:
            log.error('Unable to parse config file: %s' % str(e))
            return

    log.error('Unknown config type %r' % configtype)
    return


def start(config):
    HANDLERS = {}
    modules = ['bamboo.core']
    modules += config.get('modules', [])
    for module in modules:
        log.debug('Loading handlers in %s' % module)
        load_handlers(module, HANDLERS)

    log.debug('Creating handlers')
    handlers = {}
    for name, options in config.iteritems():
        if name == 'modules':
            continue
        classname, name = name.split('/', 1)
        sinks = options.pop('sinks', [])

        if not classname in HANDLERS:
            log.error('Unknown handler: %s %r' % (classname, repr(options)))
            return
        c = HANDLERS[classname]

        try:
            handlers[name] = (c(**options), sinks)
        except Exception, e:
            log.error('Initializing %s %s: %s' % (classname, name, str(e)))
            return

    for name, handler in handlers.iteritems():
        handler, sinks = handler
        for sink in sinks:
            if not sink in handlers:
                log.warning('Cannot attach sink %s to %s. %s does not exist' % \
                    (sink, name, sink))
                continue
            handler.add_sink(handlers[sink][0])

    for name, handler in handlers.iteritems():
        handler = handler[0]
        handlers[name] = handler
        if hasattr(handler, 'run'):
            log.debug('%s: Running' % handler)
            eventlet.spawn_n(handler.run)
    return handlers
