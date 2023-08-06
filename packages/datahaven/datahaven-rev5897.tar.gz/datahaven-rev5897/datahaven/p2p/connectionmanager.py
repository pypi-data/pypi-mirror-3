#!/usr/bin/env python
#connectionmanager.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#
#How about ...
#1. If we have had any incoming packets in the last 10 (15?) minutes,
#we assume our connection is ok.
#2. If we haven't, we can send an identity packet out to our contacts
#3. If no traffic after a minute, check stun for an ip change.
#4. If ip change, update identity, check for upnp (maybe they moved
#between wireless routers), resend identity.
#5. If no ip change, check upnp, maybe the restarted their router
#6. If still no traffic, then check to see if you can get to google.com
#7. If you can't get to google, you know there is a network issue, so
#we're not the problem.  If you can get to google, but still no traffic
#after the first 6 steps, then you really start wondering.  :-)
#
#
#States:
#at_startup - at startup we do not have any information
#first_doing_stun - at startup we are doing stun first time
#first_checking_upnp - at startup we may want to set upnp port forwarding
#waiting_hello - we are waiting "Hello" responce from the Central Server
#connected - internet connection is fine
#disconnected - we are sure internet is off
#doing_stun - waiting for stun results
#checking_upnp - waiting to finish configuring upnp device
#calling_single_contact - we are waiting for response from one of our contacts
#calling_contacts - we call our contacts if our identity was changed
#checking_google - waiting answer from www.google.com
#
#Events:
#init - this event fired from dhninit when we starting
#inbox-packet
#stun-success
#stun-failed
#timer1min - event fired every 1 minute
#timer10min - event fired every 10 minutes
#upnp-done
#google-success
#google-failed
#settings - event fired from guisettings when some transports was modified
#
#Control Functions and Variables:
#IPisLocal() - return True if external IP not equal to local IP
#TrafficIN(delay) - return True if there was any incomming packets in last "delay" seconds
#IPchanged() - return True if external IP changed after last stun
#IDchanged() - test user modifications or protocol state changed. Do we need to update local identity?
#CallCounter - how many times we called single contact
#TestWorkingProtos() - Do we want to use better contact method?
#UPNPatStartup() - We can start faster if skip updating upnp during startup
#
#Action Methods:
#do_stun()
#update_upnp()
#update_identity()
#update_transports()
#call_contacts()
#call_single_contact()
#check_google()
#push_ports_contact()
#unmark_changes()
#enable_gui()
#disable_gui()
#pop_working_proto()
#central_hello()
#restart_transports()


import os
import sys
import time
import random


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in networkmonitor.py')
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet import threads
from twisted.internet.task import LoopingCall


import lib.automat as automat
import lib.dhnio as dhnio
import lib.dhnnet as dhnnet
import lib.misc as misc
import lib.stun as stun
import lib.nameurl as nameurl
import lib.settings as settings
import lib.contacts as contacts
import lib.transport_control as transport_control
import lib.transport_tcp as transport_tcp
import lib.transport_ssh as transport_ssh
if transport_control._TransportHTTPEnable:
    import lib.transport_http as transport_http
if transport_control._TransportQ2QEnable:
    import lib.transport_q2q as transport_q2q
if transport_control._TransportCSpaceEnable:
    import lib.transport_cspace as transport_cspace


import automats
import p2p_connector

import centralservice
import identitypropagate
import run_upnpc


#-------------------------------------------------------------------------------

_State = 'at_startup'
_ExternalIPChanged = False
_InitCallback = None
_UpnpResult = {}
_CallCounter = 0
_SettingsChanges = set()
_GUIStateControlFunc = None
_DHNStateFunc = None
_WorkingProtocols = set()
_RevisionNumber = ''
_Loop1MinutePeriod = 60
_Loop10MinutesPeriod = 10 * _Loop1MinutePeriod

#-------------------------------------------------------------------------------

def init():
    global _InitCallback
    global _DHNStateFunc
    global _RevisionNumber
    dhnio.Dprint(4, 'connectionmanager.init')
    #_InitCallback = callback
    #_DHNStateFunc = dhn_state_func
    #_RevisionNumber = dhnio.ReadTextFile(settings.RevisionNumberFile()).strip()
    #transport_control.AddInboxCallback(inbox)
    #if transport_control._TransportCSpaceEnable:
        #transport_cspace.SetStatusNotifyFunc(cspace_status_changed)

    #automats.network_connector('init')

#------------------------------------------------------------------------------

def mark_changes(changes):
    global _SettingsChanges
    _SettingsChanges.update(changes)

def clear_changes():
    global _SettingsChanges
    _SettingsChanges.clear()

#def proto_state_changed(proto, new_state):
#    return
#    dhnio.Dprint(6, 'connectionmanager.proto_state_changed %s the new state is %s' % (proto, str(new_state)))
#    #at the moment we want to know only about q2q protocol
#    #small trick. we want connectionmanager to check protocols again after q2q will be initialized
#    if proto == 'q2q' and new_state:
#        mark_changes(set(['transport.transport-q2q.transport-q2q-enable',]))
#        do('settings')
#    elif proto == 'cspace' and new_state:
#        mark_changes(set(['transport.transport-cspace.transport-cspace-enable',]))
#        do('settings')


#-------------------------------------------------------------------------------

def IPisLocal():
    externalip = misc.readExternalIP()
    localip = misc.readLocalIP()
    return localip != externalip

def TrafficIN(delay):
    tm = transport_control.TimeSinceLastReceive()
    result = tm < delay - 1
    dhnio.Dprint(10, 'connectionmanager.TrafficIN return %s (delta=%f delay=%f)' % (str(result), tm, delay))
    return result

def IPchanged():
    global _ExternalIPChanged
    return _ExternalIPChanged

def IDchanged(changes):
        s = set(changes)
        if s.intersection([
            'transport.transport-tcp.transport-tcp-enable',
            'transport.transport-ssh.transport-ssh-enable',
            'transport.transport-http.transport-http-enable',
            'transport.transport-email.transport-email-enable',
            'transport.transport-q2q.transport-q2q-enable',
            'transport.transport-cspace.transport-cspace-enable',
            'transport.transport-skype.transport-skype-enable',
            ]):
            return True
        if 'transport.transport-tcp.transport-tcp-port' in s and settings.enableTCP():
            return True
        if 'transport.transport-ssh.transport-ssh-port' in s and settings.enableSSH():
            return True
        if 'transport.transport-q2q.transport-q2q-username' in s and settings.enableQ2Q():
            return True
        if 'transport.transport-cspace.transport-cspace-key-id' in s and settings.enableCSpace():
            return True
        if 'transport.transport-http.transport-http-server-port' in s and settings.enableHTTP():
            return True
        if 'transport.transport-tcp.transport-tcp-port' in s and settings.enableTCP():
            return True
        return False

#    global _SettingsChanges
#    if _SettingsChanges.intersection([
#        'transport.transport-tcp.transport-tcp-enable',
#        'transport.transport-ssh.transport-ssh-enable',
#        'transport.transport-http.transport-http-enable',
#        'transport.transport-email.transport-email-enable',
#        'transport.transport-q2q.transport-q2q-enable',
#        'transport.transport-cspace.transport-cspace-enable',
#        'transport.transport-skype.transport-skype-enable',
#        ]):
#        return True
#    if 'transport.transport-tcp.transport-tcp-port' in _SettingsChanges and settings.enableTCP():
#        return True
#    if 'transport.transport-ssh.transport-ssh-port' in _SettingsChanges and settings.enableSSH():
#        return True
#    if 'transport.transport-q2q.transport-q2q-username' in _SettingsChanges and settings.enableQ2Q():
#        return True
#    if 'transport.transport-http.transport-http-server-port' in _SettingsChanges and settings.enableHTTP():
#        return True
#    if 'transport.transport-tcp.transport-tcp-port' in _SettingsChanges and settings.enableTCP():
#        return True
#    if 'transport.transport-cspace.transport-cspace-key-id' in _SettingsChanges and settings.enableCSpace():
#        return True
#    return False


def TestWorkingProtos():
    global _WorkingProtocols
    #if no incomming traffic - do nothing
    if len(_WorkingProtocols) == 0:
        return False
    lid = misc.getLocalIdentity()
    order = lid.getProtoOrder()
    #if no protocols in local identity - do nothing
    if len(order) == 0:
        return False
    first = order[0]
    #if first contact in local identity is not working yet
    #but there is another working methods - switch first method
    if first not in _WorkingProtocols:
        dhnio.Dprint(4, 'connectionmanager.TestWorkingProtos first contact (%s) is not working!   _WorkingProtocols=%s' % (first, str(_WorkingProtocols)))
        return True
    #if tcp contact is on first place and it is working - we are VERY HAPPY! - no need to change anything - return False
    if first == 'tcp' and 'tcp' in _WorkingProtocols:
        return False
    #but if tcp method is not the first ant it works - we want to TURN IT ON! - return True
    if first != 'tcp' and 'tcp' in _WorkingProtocols:
        dhnio.Dprint(4, 'connectionmanager.TestWorkingProtos tcp is not first but it works _WorkingProtocols=%s' % str(_WorkingProtocols))
        return True
    #next good solution is q2q, it should be faster than http.
    #we already deal with tcp, if we reach this line - tcp not in the _WorkingProtocols
    #So if q2q method is not the first but it works - switch to q2q
    if first != 'q2q' and 'q2q' in _WorkingProtocols:
        dhnio.Dprint(4, 'connectionmanager.TestWorkingProtos q2q is not first but it works _WorkingProtocols=%s' % str(_WorkingProtocols))
        return True
    #cspace should be better than q2q - but let's check it first
    if first != 'cspace' and 'cspace' in _WorkingProtocols:
        dhnio.Dprint(4, 'connectionmanager.TestWorkingProtos cspace is not first but it works _WorkingProtocols=%s' % str(_WorkingProtocols))
        return True
    #in other cases - do nothing
    return False

def UPNPatStartup():
    #if we run dhn first time after installation - we need to deal with upnp any way
    if settings.getCentralMegabytesDonated() == '0Mb':
        return True
    return settings.getUPNPatStartup()

#-------------------------------------------------------------------------------

def do_stun():
    def stun_success(externalip):
        global _ExternalIPChanged
        if externalip == '0.0.0.0':
            automats.network_connector('stun-failed')
            return
        _ExternalIPChanged = misc.readExternalIP == externalip
        localip = dhnnet.getLocalIp()
        dhnio.WriteFile(settings.ExternalIPFilename(), str(externalip))
        dhnio.WriteFile(settings.LocalIPFilename(), str(localip))
        automats.network_connector('stun-success')
    def stun_failed(x):
        automats.network_connector('stun-failed')
    stun.stunExternalIP().addCallbacks(stun_success, stun_failed)


def update_upnp():
    global _UpnpResult
    global _SettingsChanges

    dhnio.Dprint(8, 'connectionmanager.update_upnp ')

    #if we run dhn first time after installation
    #we need to deal with upnp any way
    if settings.getCentralNumSuppliers() <= 0:
        if not settings.enableUPNP():
            dhnio.Dprint(4, 'connectionmanager.update_upnp skip because UPNP disabled')
            _UpnpResult.clear()
            automats.network_connector('upnp-done')
            return

#    protos_need_upnp = set(['tcp', 'ssh', 'http'])
    protos_need_upnp = set(['tcp',])

    #we want to update only enabled protocols
    if not settings.enableTCP():
        protos_need_upnp.discard('tcp')
    if not settings.enableSSH():
        protos_need_upnp.discard('ssh')
    if not settings.enableHTTPServer() or not transport_control._TransportHTTPEnable:
        protos_need_upnp.discard('http')

    dhnio.Dprint(6, 'connectionmanager.update_upnp want to update protocols: ' + str(protos_need_upnp))

    def _update_next_proto():
        if len(protos_need_upnp) == 0:
            dhnio.Dprint(4, 'connectionmanager.update_upnp done: ' + str(_UpnpResult))
            automats.network_connector('upnp-done')
            return
        dhnio.Dprint(14, 'connectionmanager._update_next_proto ' + str(protos_need_upnp))
        proto = protos_need_upnp.pop()
        protos_need_upnp.add(proto)
        if proto == 'tcp':
            port = settings.getTCPPort()
        elif proto == 'ssh':
            port = settings.getSSHPort()
        elif proto == 'http':
            port = settings.getHTTPPort()
        d = threads.deferToThread(_call_upnp, port)
        d.addCallback(_upnp_proto_done, proto)

    def _call_upnp(port):
        # start messing with upnp settings
        # success can be false if you're behind a router that doesn't support upnp
        # or if you are not behind a router at all and have an external ip address
        success, port = run_upnpc.update(port)
        return (success, port)

    def _upnp_proto_done(result, proto):
        dhnio.Dprint(10, 'connectionmanager._upnp_proto_done %s: %s' % (proto, str(result)))
        _UpnpResult[proto] = result[0]
        if _UpnpResult[proto] == 'upnp-done':
            if proto == 'tcp':
                settings.setTCPPort(result[1])
            elif proto == 'ssh':
                settings.setSSHPort(result[1])
            elif proto == 'http':
                settings.setHTTPPort(result[1])
        protos_need_upnp.discard(proto)
        reactor.callLater(0, _update_next_proto)

    _update_next_proto()


#if some transports was enabled or disabled we want to update identity contacts
#we empty all of the contacts and create it again in the same order
def update_identity():
    global _UpnpResult
    global _RevisionNumber

    #getting local identity
    lid = misc.getLocalIdentity()
    nowip = misc.readExternalIP()
    order = lid.getProtoOrder()
    lid.clearContacts()

    #prepare contacts data
    cdict = {}
    cdict['tcp'] = 'tcp://'+nowip+':'+settings.getTCPPort()
    if transport_control._TransportSSHEnable:
        cdict['ssh'] = 'ssh://'+nowip+':'+settings.getSSHPort()
    if transport_control._TransportHTTPEnable:
        cdict['http'] = 'http://'+nowip+':'+settings.getHTTPPort()
    if transport_control._TransportQ2QEnable:
        cdict['q2q'] = 'q2q://'+settings.getQ2Quserathost()
    if transport_control._TransportEmailEnable:
        cdict['email'] = 'email://'+settings.getEmailAddress()
    if transport_control._TransportCSpaceEnable:
        cdict['cspace'] = 'cspace://'+settings.getCSpaceKeyID()

    #making full order list
    for proto in cdict.keys():
        if proto not in order:
            order.append(proto)

    #add contacts data to the local identity
    #check if some transport is not installed -
    for proto in order:
        if settings.transportIsEnabled(proto):
            contact = cdict.get(proto, None)
            if contact is not None:
                lid.setProtoContact(proto, contact)

    misc.setLocalIdentity(lid)

    del order

    #if IP is not external and upnp configuration was failed for some reasons
    #we want to use another contact methods, NOT tcp or ssh
    if IPisLocal():
        if _UpnpResult.has_key('tcp') and _UpnpResult['tcp'] != 'upnp-done':
            dhnio.Dprint(4, 'connectionmanager.update_identity want to push tcp contact')
            lid.pushProtoContact('tcp')
            misc.setLocalIdentity(lid)

    #update software version number
    lid.version = dhnio.osinfo()
    if _RevisionNumber != '':
        lid.version = _RevisionNumber.strip() + ' ' + lid.version
    misc.setLocalIdentity(lid)

    #finally saving local identity
    misc.saveLocalIdentity()
    dhnio.Dprint(8, 'connectionmanager.update_identity  '+str(lid.contacts))
    #_UpnpResult.clear()


def update_transports():
    dhnio.Dprint(8, 'connectionmanager.update_transports ')
    result = Deferred()
    lid = misc.getLocalIdentity()

    # let's stop transport not needed anymore
    # also need to stop transport if its options was changed
    stoplist = []
    for proto in transport_control.ListSupportedProtocols():
        contact = misc.getLocalIdentity().getProtoContact(proto)
        if contact is None:
            dhnio.Dprint(4, 'connectionmanager.update_transports want to stop transport %s because not present in local identity' % proto)
            stoplist.append(transport_control.StopProtocol(proto))
            continue
        proto_, host, port, filename = nameurl.UrlParse(contact)
        o = transport_control.ProtocolOptions(proto)
        if proto != proto_:
            dhnio.Dprint(8, 'connectionmanager.update_transports WARNING identity contact is %s, but proto is %s' % (contact, proto))
            continue
        if proto == 'tcp':
            if o[0] != host:
                dhnio.Dprint(4, 'connectionmanager.update_transports want to stop transport [tcp] because IP changed')
                stoplist.append(transport_control.StopProtocol(proto))
                continue
            if o[1] != port:
                dhnio.Dprint(4, 'connectionmanager.update_transports want to stop transport [tcp] because port changed')
                stoplist.append(transport_control.StopProtocol(proto))
                continue
        if proto == 'cspace':
            if o[0] != host:
                dhnio.Dprint(4, 'connectionmanager.update_transports want to stop transport [cspace] because keyID changed')
                stoplist.append(transport_control.StopProtocol(proto))
                continue

    # let's start transport that isn't started yet
    def _start_transports(x):
        startlist = []
        for contact in misc.getLocalIdentity().getContacts():
            proto, host, port, filename = nameurl.UrlParse(contact)
            o = transport_control.ProtocolOptions(proto)
            if not transport_control.ProtocolIsSupported(proto):
                if settings.transportIsEnabled(proto) and settings.transportIsInstalled(proto):
                    if proto == 'tcp':
                        def _tcp_started(l, o):
                            dhnio.Dprint(4, 'connectionmanager.update_transports._tcp_started')
                            if l is not None:
                                transport_control.StartProtocol('tcp', l, o[0], o[1], o[2])
                        def _tcp_failed(x):
                            dhnio.Dprint(4, 'connectionmanager.update_transports._tcp_failed WARNING: '+str(x))
                        if o is None:
                            o = (misc.readExternalIP(), '', '')
                        o = list(o)
                        o[0] = misc.readExternalIP()
                        o[1] = settings.getTCPPort()
                        d = transport_tcp.receive(int(o[1]))
                        d.addCallback(_tcp_started, o)
                        d.addErrback(_tcp_failed)
                        startlist.append(d)
                        del o
                    elif proto == 'cspace' and transport_control._TransportCSpaceEnable:
                        def _cspace_started(l_, o):
                            dhnio.Dprint(4, 'connectionmanager.update_transports._cspace_started')
                            l = transport_cspace.getListener()
                            if l is None:
                                l = l_
                            if l is not None:
                                transport_control.StartProtocol('cspace', l, o[0], o[1], o[2])
                        def _cspace_failed(x):
                            dhnio.Dprint(4, 'connectionmanager.update_transports._cspace_failed WARNING: ' + str(x))
                        if o is None:
                            o = (settings.getCSpaceKeyID(), '', '')
                        o = list(o)
                        o[0] = settings.getCSpaceKeyID()
                        d = transport_cspace.init()
                        d.addCallback(_cspace_started, o)
                        d.addErrback(_cspace_failed)
                        startlist.append(d)
                        del o

        #need to wait before all listeners will be started
        dl2 = DeferredList(startlist)
        #we are ready now
        dl2.addBoth(result.callback)

    #need to wait before all listeners will be stopped
    dl1 = DeferredList(stoplist)
    #than we can begin to start listening
    dl1.addBoth(_start_transports)

    return result


def call_contacts(x=None):
    dhnio.Dprint(8, 'connectionmanager.call_contacts')
    identitypropagate.SendServers()
    centralservice.SendIdentity()
    identitypropagate.SendToIDs(contacts.getRemoteContacts())
    return x

#def call_single_contact(x=None):
#    allcontacts = contacts.getRemoteContacts()
#    if len(allcontacts) == 0:
#        dhnio.Dprint(2, 'connectionmanager.call_single_contact WARNING no contacts to call - send to central')
#        centralservice.SendIdentity(True)
#        return x
#    if len(allcontacts) == 1:
#        contact = allcontacts[0]
#        dhnio.Dprint(4, 'connectionmanager.call_single_contact WARNING only one contact!: ' + contact)
#        identitypropagate.SendToIDs([contact])
#        return x
#    attempts = 0
#    contact = ''
#    while True:
#        if attempts > 5:
#            break
#        attempts += 1
#        random_index = random.randint(0, len(allcontacts)-1)
#        contact = allcontacts[random_index]
#        if not transport_control.ContactIsAlive(contact):
#            continue
#    if contact != '':
#        dhnio.Dprint(10, 'connectionmanager.call_single_contact want to call ' + contact)
#        identitypropagate.SendToIDs([contact])
#    else:
#        dhnio.Dprint(2, 'connectionmanager.call_single_contact WARNING no available contacts found')
#    return x

def check_google():
    dhnio.Dprint(4, 'connectionmanager.check_google')
    if dhnnet.TestInternetConnection():
        automats.network_connector('google-success')
    else:
        automats.network_connector('google-failed')

def push_ports_contact():
    dhnio.Dprint(4, 'connectionmanager.push_ports_contact')
    lid = misc.getLocalIdentity()
    lid.pushProtoContact('tcp')
    lid.pushProtoContact('ssh')
##    lid.pushProtoContact('http')
    misc.setLocalIdentity(lid)
    misc.saveLocalIdentity()

def unmark_changes(x=None):
    clear_changes()
    return x

def enable_gui(x=None):
    global _GUIStateControlFunc
    if _GUIStateControlFunc is not None:
        _GUIStateControlFunc(True)
    return x

def disable_gui(x=None):
    global _GUIStateControlFunc
    if _GUIStateControlFunc is not None:
        _GUIStateControlFunc(False)
    return x

def pop_working_proto():
    global _WorkingProtocols
    lid = misc.getLocalIdentity()
    order = lid.getProtoOrder()
    first = order[0]
    wantedproto = ''
    #if first contact in local identity is not working yet
    #but there is another working methods - switch first method
    if first not in _WorkingProtocols:
        #take (but not remove) any item from the set
        wantedproto = _WorkingProtocols.pop()
        _WorkingProtocols.add(wantedproto)
    #if q2q method is not the first but it works - switch to q2q
    if first != 'q2q' and 'q2q' in _WorkingProtocols:
        wantedproto = 'q2q'
    #if cspace method is not the first but it works - switch to cspace
    if first != 'cspace' and 'cspace' in _WorkingProtocols:
        wantedproto = 'cspace'
    #if tcp method is not the first but it works - switch to tcp
    if first != 'tcp' and 'tcp' in _WorkingProtocols:
        wantedproto = 'tcp'
    dhnio.Dprint(4, 'connectionmanager.pop_working_proto will pop %s contact   order=%s _WorkingProtocols=%s' % (wantedproto, str(order), str(_WorkingProtocols)))
    lid.popProtoContact(wantedproto)
    misc.setLocalIdentity(lid)
    misc.saveLocalIdentity()

def central_hello():
    centralservice.Hello()

def restart_transports():
    dhnio.Dprint(4, 'connectionmanager.restart_transports')
    result = Deferred()

    def _start_transports(x, l):
        resultlist = []
        for proto in l:
            if proto == 'tcp':
                def _tcp_started(l, o):
                    if l is not None:
                        transport_control.StartProtocol('tcp', l, o[0], o[1], o[2])
                o = transport_control.ProtocolOptions('tcp')
                if o is None:
                    o = (misc.readExternalIP(), '', '')
                o = list(o)
                o[1] = settings.getTCPPort()
                d = transport_tcp.receive(int(o[1]))
                d.addBoth(_tcp_started, o)
                resultlist.append(d)
                del o

            if proto == 'ssh':
                def _ssh_started(l, o):
                    if l is not None:
                        transport_control.StartProtocol('ssh', l, o[0], o[1], o[2])
                o = transport_control.ProtocolOptions('ssh')
                if o is None:
                    o = (misc.readExternalIP(), '', '')
                o = list(o)
                o[1] = settings.getSSHPort()
                d = transport_ssh.receive(int(o[1]))
                d.addBoth(_ssh_started, o)
                resultlist.append(d)
                del o

            if proto == 'http':
                if transport_control._TransportHTTPEnable:
                    d = transport_http.start_http_server(int(settings.getHTTPPort()))
                    resultlist.append(d)
        #need to wait before all listeners will be started
        dl2 = DeferredList(resultlist)
        #we are ready
        dl2.addBoth(result.callback)

    #at this moment we need only to restart tcp, ssh and http
    startlist = []
    stoplist = []
    if transport_control.ProtocolIsSupported('tcp'):
        stoplist.append(transport_control.StopProtocol('tcp'))
        startlist.append('tcp')
    if transport_control.ProtocolIsSupported('ssh'):
        stoplist.append(transport_control.StopProtocol('ssh'))
        startlist.append('ssh')
    if settings.enableHTTPServer():
        if transport_control._TransportHTTPEnable:
            stoplist.append(transport_http.stop_http_server())
            startlist.append('http')

    #need to wait before all listeners will be stopped
    dl1 = DeferredList(stoplist)
    #than we can begin to start listening
    dl1.addBoth(_start_transports, startlist)
    return result


#-------------------------------------------------------------------------------

def inbox(newpacket, proto, host, status=None, message=None):
    global _WorkingProtocols
    _WorkingProtocols.add(proto)
    #reactor.callLater(0, do, 'inbox-packet')
    p2p_connector.A('inbox-packet', (newpacket, proto, host, status, message))

##def cspace_status_changed(status):
##    dhnio.Dprint(4, 'connectionmanager.cspace_status_changed [%s]' % status.upper())
##    automats.network_connector('cspace-status', status)


#------------------------------------------------------------------------------



#def loop1min():
#    global _Loop1MinutePeriod
#    reactor.callLater(_Loop1MinutePeriod, loop1min)
#    reactor.callLater(0, do, 'timer1min')
#
#def loop10min():
#    global _Loop10MinutesPeriod
#    reactor.callLater(_Loop10MinutesPeriod, loop10min)
#    reactor.callLater(0, do, 'timer10min')

#def centralservice_control(state, data):
#    # TODO
#    # may be we need to improove here
#    # and pass incomming data into state machine
#    # like this:
#    # reactor.callLater(0, do, 'centralservice ' + state.lower())
#    global _DHNStateFunc
#    if _DHNStateFunc is None:
#        return
#    if state in ['HelloAck', 'Failed']:
#        _DHNStateFunc('ready')



