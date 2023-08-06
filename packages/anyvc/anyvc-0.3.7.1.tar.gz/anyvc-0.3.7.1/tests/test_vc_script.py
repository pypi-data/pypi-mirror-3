import py
import execnet


@py.test.mark.files({'setup.py':'pass'})
@py.test.mark.commited
def test_diff(wd):
    gw = execnet.makegateway()
    def remote(channel, cwd):
        import sys
        import os
        import anyvc
        #XXX to cause the imports in case of relatives
        #    this should get fixed in execnet
        anyvc.workdir.open(cwd)
        import anyvc.client
        os.chdir(cwd)
        channel.send(anyvc.client.main(['vc','diff']))

    ch = gw.remote_exec(remote, cwd = wd.path.strpath)
    ch.receive()
