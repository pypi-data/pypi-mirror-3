from twisted.protocols import amp
from twisted.internet import reactor, protocol, threads

class Move(amp.Command):
    arguments = [('steps', amp.Integer())]
    response = [('total', amp.Integer())]

class SetDirection(amp.Command):
    arguments = [('dx', amp.Integer()), ('dy', amp.Integer())]
    response = []

class RobotProtocol(amp.AMP):
    @Move.responder
    def move(self, steps):
        d = self.factory.robot.move(steps)
        return d.addCallback(lambda result: {'total': int(result)})

    @SetDirection.responder
    def setDirection(self, dx, dy):
        self.factory.robot.direction = (dx, dy)
        return {}

class ServerRobotFactory(protocol.Factory):
    protocol = RobotProtocol
    def __init__(self, robot):
        self.robot = robot

class ClientRobot(object):
    def __init__(self, p):
        self.p = p
        reactor.callInThread(self._startCode)
    
    def _startCode(self):
        import txusercode
        txusercode.run(self)

    def move(self, steps):
        result = threads.blockingCallFromThread(reactor, self.p.callRemote,
            Move, steps=steps)
        return result['total']

    def _setDirection(self, dxdy):
        dx, dy = dxdy
        result = threads.blockingCallFromThread(reactor, self.p.callRemote,
            SetDirection, dx=dx, dy=dy)
        print result
    direction = property(fset=_setDirection)

def startListening(reactor, serverRobot, port=5234):
    f = ServerRobotFactory(serverRobot)
    reactor.listenTCP(5234, f)
    return f

def startClient():
    d = protocol.ClientCreator(reactor, amp.AMP).connectTCP(
        '127.0.0.1', 5234).addCallback(ClientRobot)
    reactor.run()


