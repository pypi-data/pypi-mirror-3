import tempfile
import shutil
import os
import sys

import gtk
from twisted.internet import gtk2reactor
gtk2reactor.install()

from twisted.internet import reactor
from txlearnbot import robot, runcode, amp_robot

class LearnIDE(object):
    def __init__(self, reactor):
        self.builder = gtk.Builder()
        path = os.path.dirname(os.path.abspath(__file__))
        self.builder.add_from_file(os.path.join(path, 'txlearnbot.xml'))
        self.builder.connect_signals(self)

        window = self.builder.get_object('window1')
        window.show()

        self.buffer = self.builder.get_object('textbuffer1')
        self.bot = robot.Robot(self.builder.get_object('drawingarea1'))
        amp_robot.startListening(reactor, self.bot)

    def on_runCode_clicked(self, widget, *ign):
        code = runcode.Runner(self.buffer.get_text(*self.buffer.get_bounds()))
        d = code.run()
        d.addBoth(lambda ign: widget.enable())

    def on_window1_destroy(self, widget, *ign):
        reactor.stop()

def main():
    p = LearnIDE(reactor)
    reactor.run()

