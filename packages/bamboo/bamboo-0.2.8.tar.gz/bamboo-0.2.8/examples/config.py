{
  "modules": ["bamboo.zeromq"],
  "TCPSource/tcp": {
   "sinks": ["zmq1"]
  },
  "ZMQSink/zmq1": {
   "endpoint": "tcp://127.0.0.1:4201"
  },
  "ZMQSource/zmq2": {
   "endpoint": "tcp://*:4201",
   "identity": "zmq2",
   "bind": True,
   "sinks": ["archive"]
  },
  "FileSink/archive": {
   "path": "/tmp/logs"
  }
}
