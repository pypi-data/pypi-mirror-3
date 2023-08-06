from logging.handlers import DatagramHandler

class BambooUDPHandler(DatagramHandler):
    def __init__(self, host, port, key='{log.name}',
        fmt='{log.filename}:{log.lineno} {log.levelname} {log.msg}'):
        SocketHandler.__init__(self, host, port)
        self.key = key
        self.fmt = fmt

    def emit(self, record):
        try:
            s = '%s:%i:%s\n' % (
                self.key.format(log=record),
                int(record.created),
                self.fmt.format(log=record)
            )
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
