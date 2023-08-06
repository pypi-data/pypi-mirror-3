#!/usr/bin/env python
#initializer.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#

import os
import sys

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in automat.py')
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet.task import LoopingCall

import lib.dhnio as dhnio
from lib.automat import Automat

import network_connector
import p2p_connector
import automats

import dhninit

_Initializer = None

#------------------------------------------------------------------------------

def A(event=None, arg=None, use_reactor=True):
    global _Initializer
    if _Initializer is None:
        _Initializer = Initializer('initializer', 'AT_STARTUP', 2)
    if event is not None:
        if use_reactor:
            _Initializer.automat(event, arg)
        else:
            _Initializer.event(event, arg)
    return _Initializer


class Initializer(Automat):
    def state_changed(self, oldstate, newstate):
        automats.set_global_state('INIT ' + newstate)

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'run':
                self.doInitLocal(arg)
                self.state = 'LOCAL'
        #---LOCAL---
        elif self.state == 'LOCAL':
            if event == 'init-local-done' and self.isInstalled():
                self.doInitContacts()
                self.state = 'CONTACTS'
            elif event == 'init-local-done' and not self.isInstalled():
                self.doInitInstall()
                automats.installer('init')
                self.state = 'INSTALL'
        #---CONTACTS---
        elif self.state == 'CONTACTS':
            if event == 'init-contacts-done':
                self.doInitConnection()
                p2p_connector.A('init')
                network_connector.A('init')
                self.state = 'CONNECTION'
            elif event == 'init-contacts-failed':
                self.doExit()
##                self.doDestroyMe()
                self.state = 'STOPPING'
        #---CONNECTION---
        elif self.state == 'CONNECTION':
            if event == 'p2p_connector.state' and arg in ['CONNECTED', 'DISCONNECTED']:
                self.doInitModules()
                self.state = 'MODULES'
        #---MODULES---
        elif self.state == 'MODULES':
            if event == 'init-modules-done':
                self.state = 'READY'
        #---INSTALL---
        elif self.state == 'INSTALL':
            if event == 'installer.state' and arg == 'DONE':
                self.doInitContacts()
                self.state = 'CONTACTS'
        #---READY---
        elif self.state == 'READY':
            if event == 'reactor-stopped':
                self.doDestroyMe()
                self.state = 'EXIT'
        #---STOPPING
        elif self.state == 'STOPPING':
            if event == 'reactor-stopped':
                self.doDestroyMe()
                self.state = 'EXIT'
        #---EXIT---
        elif self.state == 'EXIT':
            pass

    def isInstalled(self):
        return dhninit.check_install()

    def doInitLocal(self, arg):
        maybeDeferred(dhninit.init_local, arg).addCallback(
            lambda x: self.automat('init-local-done'))

    def doInitContacts(self):
        dhninit.init_contacts(
            lambda x: self.automat('init-contacts-done'),
            lambda x: self.automat('init-contacts-failed'),
            )

    def doInitConnection(self):
        dhninit.init_connection()

    def doInitModules(self):
        maybeDeferred(dhninit.init_modules).addCallback(
            lambda x: self.automat('init-modules-done'))

    def doInitInstall(self):
        dhninit.init_install()

    def doExit(self):
        dhninit.shutdown_exit()

    def doDestroyMe(self):
        global _Initializer
        del _Initializer
        _Initializer = None



