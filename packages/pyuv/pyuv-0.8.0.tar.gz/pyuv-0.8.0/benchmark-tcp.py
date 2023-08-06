
import pyuv

NUM_REQS = 1000 * 100
DATA = "HELLO"*1000

def on_client_shutdown(handle, error):
    handle.close()

def on_client_send(handle, error):
    global write_cb_called
    assert error is None, "Send error: %s" % error
    write_cb_called += 1

def on_client_connect(handle, error):
    global client
    for i in xrange(NUM_REQS):
        client.write(DATA, on_client_send)
    client.shutdown(on_client_shutdown)

write_cb_called = 0
loop = pyuv.Loop.default_loop()
client = pyuv.TCP(loop)
client.connect(("127.0.0.1", 1234), on_client_connect)

start = pyuv.util.hrtime()
loop.run()
stop = pyuv.util.hrtime()

print "Writes: %s" % write_cb_called
assert write_cb_called==NUM_REQS, "BUG"
print "Time: %s" % ((stop-start)/10e8)

