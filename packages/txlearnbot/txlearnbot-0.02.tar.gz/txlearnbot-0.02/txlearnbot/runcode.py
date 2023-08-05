import tempfile
import os
import sys
import shutil

from twisted.internet import protocol, defer, reactor

class Runner(protocol.ProcessProtocol):
    def __init__(self, code):
        self.code = code
        self._path = tempfile.mkdtemp(prefix='coderunner')
        fullname = os.path.join(self._path, 'txusercode.py')
        with open(fullname, 'w') as f:
            f.write('def run(bot):\n')
            for line in code.splitlines():
                f.write('\t%s\n' % (line,))
        self.running = None

    def run(self):
        if not self.running:
            filename = 'txlearnbotclient.py'
            self.running = defer.Deferred()
            reactor.spawnProcess(self, 
                sys.executable,
                args=[
                    sys.executable, 
                    '-c',
                    "from txlearnbot import amp_robot ; amp_robot.startClient()"
                ],
                env=os.environ, 
                path=self._path,
                childFDs={0: 0, 1: 1, 2: 2})
        return self.running
    
    def processEnded(status):
        self.cleanup()
        self.running.callback(status.value.exitCode)
        self.running = None

    def cleanup(self):
        shutil.rmtree(self._path)
