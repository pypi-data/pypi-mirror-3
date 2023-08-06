#!/usr/bin/python
#automat.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#

import os
import sys

from twisted.internet import reactor
from twisted.internet.task import LoopingCall


_Counter = 0
_Index = {}


def get_new_index():
    global _Counter
    _Counter += 1
    return _Counter - 1


def create(name):
    global _Index
    id = name
    if _Index.has_key(id):
        i = 0
        while _Index.has_key(id+str(i)):
            i += 1
        id = name + str(i)
    _Index[id] = get_new_index()
    return id, _Index[id]


class Automat(object):
    #states_counter = 0
    #states = {}
    timers = {}
    def __init__(self, name, state, debug_level=18):
        self.id, self.index = create(name)
        #self.log(6, 'automat.create [%d] %s' % (_Index[id], id))
        self.name = name
        self.state = state
        #self.states[state] = self.states_counter
        #self.states_counter += 1
        self.debug_level = debug_level
        self._timers = {}
        self.init()
        self.startTimers()
        self.log(self.debug_level,  'new %s created with index %d' % (str(self), self.index))


    def __del__(self):
        global _Index
        id = self.id
        debug_level = self.debug_level
        if _Index is None:
            #self.log(debug_level, 'automat index is empty, %s should be destroyed now' % id)
            return
        index = _Index.get(id, None)
        if index is None:
            self.log(debug_level, 'automat.__del__ WARNING %s not found' % id)
            return
        del _Index[id]
        self.log(debug_level, '%s [%d] destroyed' % (id, index))

    def __repr__(self):
        #return 'A%d.%s.[%s%d]' % (self.index, self.name, self.state, self.states.get(self.state, -1))
        return '%s[%s]' % (self.id, self.state)

    def init(self):
        pass

    def state_changed(self, oldstate, newstate):
        pass

    def A(self, event, arg):
        raise NotImplementedError

    def automat(self, event, arg=None):
        reactor.callLater(0, self.event, event, arg)

    def event(self, event, arg):
        self.log(self.debug_level*2, '%s fired with event "%s"' % (self, event))# , sys.getrefcount(Automat)))
        old_state = self.state
        self.A(event, arg)
        new_state = self.state
        if old_state != new_state:
#            if not self.states.has_key(new_state):
#                self.states[new_state] = self.states_counter
#                self.states_counter += 1
            self.stopTimers()
            self.log(self.debug_level, '[%s]->[%s] in %s, event was "%s"' % (old_state, new_state, self, event))
            self.state_changed(old_state, new_state)
            self.startTimers()
            #reactor.callLater(0, self.state_changed, old_state, new_state)

    def timer_event(self, name, interval):
        if self.timers.has_key(name) and self.state in self.timers[name][1]:
            self.automat(name)
        else:
            self.log(self.debug_level, '%s.timer_event ERROR timer %s not found in self.timers')

    def stopTimers(self):
        for name, timer in self._timers.items():
            if timer.running:
                timer.stop()
                self.log(self.debug_level*2, '%s.stopTimers timer %s stopped' % (self, name))
        self._timers.clear()

    def startTimers(self):
        for name, (interval, states) in self.timers.items():
            if len(states) > 0 and self.state not in states:
                continue
            self._timers[name] = LoopingCall(self.timer_event, name, interval)
            self._timers[name].start(interval, False)
            self.log(self.debug_level*2, '%s.startTimers timer %s started' % (self, name))

    def restartTimers(self):
        self.stopTimers()
        self.startTimers()

    def log(self, level, text):
        try:
            from dhnio import Dprint
            Dprint(level, text)
        except:
            pass


#------------------------------------------------------------------------------

def test():
    dhnio.SetDebug(40)
    dhnio.LifeBegins()

    class Test(Automat):
        timers = {'timer-1sec':   (1,    ['STATE1', 'STATE2']),}

        def init(self):
            self.i = 0

        def A(self, event, arg):
            if self.state == 'STATE1':
                if event == 'timer-1sec' and self.i < 2:
                    self.i += 1
                    self.state = 'STATE2'
                elif event == 'timer-1sec' and self.i >= 2:
                    #reactor.callLater(1, lambda:reactor.stop())
                    self.state = 'FINISH'
            elif self.state == 'STATE2':
                if event == 'timer-1sec':
                    self.state = 'STATE1'

    class Run():
        def __init__(self):
            self.l = []
            reactor.callLater(0, self.add)
            reactor.callLater(0.5, self.add)
            reactor.callLater(10, self.remove)
            #LoopingCall(self.external_timer).start(1, False)

        def add(self):
            self.l.append(Test('TestAutomat', 'STATE1'))

        def remove(self):
            a = self.l.pop()

        def external_timer(self):
            self.l[0].automat('timer-1sec')


    r = Run()
    reactor.run()






