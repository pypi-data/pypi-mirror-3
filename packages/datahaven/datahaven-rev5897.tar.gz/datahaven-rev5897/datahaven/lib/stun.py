#!/usr/bin/python
#stun.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#

import sys


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in stun.py')

from twisted.internet.defer import Deferred, succeed, fail
from twisted.python import log

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

import shtoom.stun
import shtoom.nat
import dhnio


#------------------------------------------------------------------------------ 

class IPStunProtocol(shtoom.stun.StunDiscoveryProtocol):
    def __init__(self, d):
        shtoom.stun.StunDiscoveryProtocol.__init__(self)
        self.d = d
        self.count = 0

    def finishedStun(self):
        try:
            ip = str(self.externalAddress[0])
            typ = str(self.natType.name)
        except:
            ip = "0.0.0.0"
            typ = 'unknown'
        dhnio.Dprint(6, 'stun.IPStunProtocol.finishedStun ip=%s NAT_type=%s' % (ip, str(typ)))
        if not self.d.called:
            if ip == '0.0.0.0':
                self.d.errback(ip)
            else:
                self.d.callback(ip)

    def _hostNotResolved(self, x):
        dhnio.Dprint(2, 'stun.IPStunProtocol._hostNotResolved ' + x.getErrorMessage())
        self.count += 1
        if self.count >= len(shtoom.stun.DefaultServers) / 2:
            if not self.d.called:
                self.d.errback(x)

_WorkingDefer = None
_UDPListener = None
_TimeOutTask = None
_StunClient = None
def stunExternalIP(timeout=60):
    global _WorkingDefer
    global _UDPListener
    global _StunClient
    global _TimeOutTask
    if _WorkingDefer is not None:
        dhnio.Dprint(6, 'stun.stunExternalIP WARNING already called')
        return _WorkingDefer
    _WorkingDefer = Deferred()

    dhnio.Dprint(8, 'stun.stunExternalIP')

    if dhnio.Debug(16):
        shtoom.stun.STUNVERBOSE = True
        shtoom.nat._Debug = True
    shtoom.nat._cachedLocalIP = None
    shtoom.nat.getLocalIPAddress.clearCache()
    
    result = Deferred()
    _StunClient = IPStunProtocol(result)

    try:
        _UDPListener = reactor.listenUDP(5061, _StunClient)
    except:
        dhnio.DprintException()
        try:
            l = reactor.listenUDP(0, stunClient)
        except:
            dhnio.DprintException()
            _WorkingDefer = None
            return fail('0.0.0.0')

    def finished(x):
        global _UDPListener
        global _TimeOutTask
        global _StunClient
        global _WorkingDefer
        dhnio.Dprint(10, 'stun.stunExternalIP.finished')
        try:
            if x == '0.0.0.0':
                _WorkingDefer.errback(x)
            else:
                _WorkingDefer.callback(x)
            _WorkingDefer = None
            if _UDPListener is not None:
                _UDPListener.stopListening()
                _UDPListener = None
            if not _TimeOutTask.called:
                _TimeOutTask.cancel()
            _TimeOutTask = None
            if _StunClient is not None:
                del _StunClient
                _StunClient = None
        except:
            dhnio.DprintException()

    def time_out(r):
        dhnio.Dprint(10, 'stun.stunExternalIP.time_out')
        if not r.called:
            r.errback('0.0.0.0')

    result.addBoth(finished)

    _TimeOutTask = reactor.callLater(timeout, time_out, result)
    
    reactor.callLater(0, _StunClient.startDiscovery)

    return _WorkingDefer


#------------------------------------------------------------------------------ 

def success(x):
    print 'stun.success', x
    reactor.callLater(5, main)
    #reactor.stop()

def fail(x):
    print 'stun.fail', x
    reactor.callLater(5, main)
    #reactor.stop()

def main():
    d = stunExternalIP()
    d.addCallback(success)
    d.addErrback(fail)


if __name__ == "__main__":
#    log.startLogging(sys.stdout)
    dhnio.SetDebug(15)
    main()
    reactor.run()






