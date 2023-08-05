import tempfile

import gtk

from twisted.internet import reactor, defer

def wait(time):
    d = defer.Deferred()
    reactor.callLater(time, d.callback, None)
    return d

class Robot(object):
    def __init__(self, darea):
        self._draw = darea
        self.speed = 0.1
        self.gc = darea.get_style().fg_gc[gtk.STATE_NORMAL]
        self.x = 5
        self.y = 5
        self.draw()
        self.direction = (1, 0)

    def draw(self):
        print self.x, self.y
        self._draw.window.draw_point(self.gc, self.x, self.y)

    @defer.inlineCallbacks
    def move(self, steps, d=None):
        for i in xrange(steps):
            yield wait(self.speed)
            dx, dy = self.direction
            self.x += dx
            self.y += dy
            self.draw()
        defer.returnValue(steps)


