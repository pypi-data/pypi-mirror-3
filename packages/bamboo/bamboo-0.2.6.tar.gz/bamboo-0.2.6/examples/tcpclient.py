import socket
import time

sock = socket.socket()
sock.connect(('127.0.0.1', 4200))
while True:
    sock.sendall('testkey:%i:testval\n' % int(time.time()))
