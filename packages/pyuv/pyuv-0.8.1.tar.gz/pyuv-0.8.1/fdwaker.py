
import errno
import fcntl
import os
import pyuv
import signal
import socket


class WinFDWaker(object):

    def __init__(self, loop):
        self.loop = loop
        self.read_fd = None
        self.write_fd = None
        self.handle = None

    def _cb(self, handle, events, error):
        if error is not None:
            return
        while True:
            try:
                os.read(self.read_fd, 8192)
            except OSError as e:
                if e.errno == errno.EAGAIN:
                    break
                raise

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        client.connect(server.getsockname())
        reader, clientaddr = server.accept()
        client.setblocking(0)
        reader.setblocking(0)
        self.reader_sock = reader
        self.client_sock = client
        self.read_fd = self.reader_sock.fileno()
        self.write_fd = self.client_sock.fileno()
        signal.set_wakeup_fd(self.write_fd)
        self.handle = pyuv.Poll(self.loop, self.read_fd)
        self.handle.start(pyuv.UV_READABLE, self._cb)
        self.handle.unref()

    def stop(self):
        signal.set_wakeup_fd(-1)
        self.handle.stop()
        self.client_sock.close()
        self.reader_sock.close()


class UnixFDWaker(object):

    def __init__(self, loop):
        self.loop = loop
        self.read_fd = None
        self.write_fd = None
        self.handle = None

    @classmethod
    def make_fd_nonblock(cls, fd):
        flags = fcntl.fcntl(fd, fcntl.F_GETFL, 0)
        flags = flags | os.O_NONBLOCK
        flags = fcntl.fcntl(fd, fcntl.F_SETFL, flags)

    def _cb(self, handle, events, error):
        if error is not None:
            return
        while True:
            try:
                os.read(self.read_fd, 8192)
            except OSError as e:
                if e.errno == errno.EAGAIN:
                    break
                raise

    def start(self):
        self.read_fd, self.write_fd = os.pipe()
        self.make_fd_nonblock(self.read_fd)
        self.make_fd_nonblock(self.write_fd)
        signal.set_wakeup_fd(self.write_fd)
        self.handle = pyuv.Poll(self.loop, self.read_fd)
        self.handle.start(pyuv.UV_READABLE, self._cb)
        self.handle.unref()

    def stop(self):
        signal.set_wakeup_fd(-1)
        self.handle.stop()
        os.close(self.read_fd)
        os.close(self.write_fd)


## -------------------------

loop = pyuv.Loop.default_loop()

def signal_cb(sig, frame):
    def cb(handle):
        if not handle.closed:
            handle.close()
    loop.walk(cb)

def timer_cb(handle):
    print "timer cb!"

timer = pyuv.Timer(loop)
timer.start(timer_cb, 5.0, 0.0)

#waker = UnixFDWaker(loop)
waker = WinFDWaker(loop)
waker.start()

signal.signal(signal.SIGINT, signal_cb)

loop.run()

