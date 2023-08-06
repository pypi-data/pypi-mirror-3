from execnet import makegateway
import pickle
from anyvc.remote.object import RemoteCaller

def test_remote_object():
    gw = makegateway('popen')
    channel = gw.remote_exec("""
    from anyvc.remote.object import RemoteHandler

    class TestHandler(RemoteHandler):
        def test(self, **kw):
            return kw
    newchan = channel.gateway.newchannel()
    handler = TestHandler(newchan)
    channel.send(newchan)
    """)
    caller = RemoteCaller(channel.receive())
    result = caller.test(a=1)
    assert result == {'a':1}


class TestChannel(object):

    def isclosed(self):
        return hasattr(self, 'next')

    def send(self, val):
        print val
        self.next = val

    def receive(self):
        result = self.next
        del self.next #XXX: crude hack
        return result

def test_caller():

    test_handler = RemoteCaller(TestChannel())
    method, args, kwargs = test_handler.test(a=1)

    assert method == 'test'
    assert kwargs == {'a': 1}
    assert args == ()
