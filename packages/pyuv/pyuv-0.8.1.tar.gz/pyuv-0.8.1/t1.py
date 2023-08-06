
import signal
import pyuv


def prepare_cb(handle):
    try:
        print "aaaaaaaaaa"
    except KeyboardInterrupt:
        print "oooooooooooo"
    except Exception:
        print "lllllllllllllllllll"

def timer_cb(handle):
    print "timer cb!"

def signal_cb(handle, signum):
    print "signal!"

loop = pyuv.Loop.default_loop()
prepare = pyuv.Prepare(loop)
prepare.start(prepare_cb)
timer = pyuv.Timer(loop)
timer.start(timer_cb, 5.0, 5.0)
#sign = pyuv.Signal(loop)
#sign.start(signal_cb, signal.SIGINT)
loop.run()

