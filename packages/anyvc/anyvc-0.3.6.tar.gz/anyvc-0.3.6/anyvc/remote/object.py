"""
    anyvc.remote.object
    ~~~~~~~~~~~~~~~~~~~

    convience tool make execnet channels remote objects
"""
import pickle
from py.path import local

class RemoteCaller(object):
    def __init__(self, channel):
        self.channel = channel

    def _call_remote(self, name, *k, **kw):
        assert not self.channel.isclosed()

        if 'path' in kw:
            kw['path'] = str(kw['path'])

        data = (name, k, kw)
        self.channel.send(data)
        result = self.channel.receive()
        #XXX: again a job for py.execnet
        return result

    def __getattr__(self, name):
        def method(*k, **kw):
            return self._call_remote(name, *k, **kw)
        method.__name__ = name
        return method

class RemoteHandler(object):
    def __init__(self, channel):
        self.channel = channel
        channel.setcallback(self._channel_callback)

    def newchannel(self):
        return self.channel.gateway.newchannel()

    def _channel_callback(self, data):
        try:
            method, k, kw = data

            if 'path' in kw:
                kw['path'] = local(kw['path'])

            method = getattr(self, method)
            result = method(*k, **kw)
            self.channel.send(result)
        except Exception:
            #XXX: py.execnet should pass callback exceptions
            import traceback
            import sys
            excinfo = sys.exc_info()
            l = traceback.format_exception(*excinfo)
            errortext = "".join(l)
            self.channel.close(errortext)
        except:
            self.channel.close('unknown error')


