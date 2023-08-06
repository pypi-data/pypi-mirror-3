
import errno
import fcntl
import os
import pyuv
import signal

def make_fd_nonblock(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL, 0)
    flags = flags | os.O_NONBLOCK
    flags = fcntl.fcntl(fd, fcntl.F_SETFL, flags)

rfd, wfd = os.pipe()
make_fd_nonblock(rfd)
make_fd_nonblock(wfd)

loop = pyuv.Loop.default_loop()

def signal_cb(signum, frame):
    print "got signa!"
    def close_handle(handle):
        if not handle.closed:
            handle.close()
    loop.walk(close_handle)

def poll_cb(handle, events, error):
    print "------------"
    print events
    print error
    print "------------"
    while True:
        try:
            os.read(rfd, 1024)
        except OSError as e:
            if e.errno == errno.EAGAIN:
                break
            raise

def pipe_cb(handle, data, error):
    print "--------------"
    print data
    print error
    print "--------------"

def timer_cb(handle):
    print "timer CB"

signal.set_wakeup_fd(wfd)
signal.signal(signal.SIGINT, signal_cb)

pipe = pyuv.Pipe(loop)
pipe.open(rfd)
pipe.start_read(pipe_cb)

#poll = pyuv.Poll(loop, rfd)
#poll.start(pyuv.UV_READABLE, poll_cb)

timer = pyuv.Timer(loop)
timer.start(timer_cb, 5.0, 0.0)

loop.run()

