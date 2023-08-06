#!/usr/bin/python
#contacts_status.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#

import os
import sys


import lib.dhnio as dhnio
import lib.nameurl as nameurl
import lib.transport_control as transport_control
import lib.contacts as contacts
from lib.automat import Automat

if transport_control._TransportCSpaceEnable:
    import lib.transport_cspace as transport_cspace


_ContactsByHost = {}
_ContactsStatusDict = {}


#------------------------------------------------------------------------------ 


def init():
    dhnio.Dprint(4, 'contacts_status.init')
    transport_control.AddInboxCallback(Inbox)
    transport_control.AddOutboxCallback(Outbox)
    transport_control.AddOutboxPacketStatusFunc(OutboxStatus)
    if transport_control._TransportCSpaceEnable:
        transport_cspace.SetContactStatusNotifyFunc(CSpaceContactStatus)


def shutdown():
    dhnio.Dprint(4, 'contacts_status.shutdown')
    global _ContactsStatusDict
    _ContactsStatusDict.clear()
    

def isOnline(idurl):
    return A(idurl).state == 'LIVE'


def isOffline(idurl):
    return A(idurl).state == 'OFFLINE'


def isChecking(idurl):
    return A(idurl).state == 'CHECKING'


def check_contacts(contacts_list):
    for idurl in contacts_list:
        A(idurl, 'check') 


def A(idurl, event=None, arg=None):
    global _ContactsStatusDict
    if not _ContactsStatusDict.has_key(idurl):
        _ContactsStatusDict[idurl] = ContactStatus('%s_status' % nameurl.GetName(idurl), 'OFFLINE', 6)
    if event is not None:
        _ContactsStatusDict[idurl].automat(event, arg)
    return _ContactsStatusDict[idurl]
      

class ContactStatus(Automat):
    def A(self, event, arg):
        #---LIVE---
        if self.state == 'LIVE':
            if event in ['sent-failed', 'cspace-offline']:
                self.state = 'OFFLINE'
            elif event == 'check':
                self.state = 'CHECKING'
        #---OFFLINE---
        elif self.state == 'OFFLINE':
            if event in ['inbox-packet']:
                self.state = 'LIVE'
            elif event in ['outbox-packet', 'check']:
                self.state = 'CHECKING'
        #---CHECKING---
        elif self.state == 'CHECKING':
            if event == 'inbox-packet':
                self.state = 'LIVE'
            elif event in ['sent-failed', 'cspace-offline']:
                self.state = 'OFFLINE'


def OutboxStatus(workitem, proto, host, status, error, message):
    global _ContactsByHost
    ident = contacts.getContact(workitem.remoteid)
    if ident is not None:
        for contact in ident.getContacts():
            _ContactsByHost[contact] = workitem.remoteid
    if status == 'finished':
        A(workitem.remoteid, 'sent-done', (workitem, proto, host))
    else:
        A(workitem.remoteid, 'sent-failed', (workitem, proto, host))


def Inbox(newpacket, proto, host):
    global _ContactsByHost
    ident = contacts.getContact(newpacket.OwnerID)
    if ident is not None:
        for contact in ident.getContacts():
            _ContactsByHost[contact] = newpacket.OwnerID
    A(newpacket.OwnerID, 'inbox-packet', (newpacket, proto, host))
    

def Outbox(outpacket):
    global _ContactsByHost
    ident = contacts.getContact(outpacket.RemoteID)
    if ident is not None:
        for contact in ident.getContacts():
            _ContactsByHost[contact] = outpacket.RemoteID
    A(outpacket.RemoteID, 'outbox-packet', outpacket)


def CSpaceContactStatus(keyID, status):
    global _ContactsByHost
    idurl = _ContactsByHost.get('cspace://' + keyID, None)
    if idurl is not None:
        A(idurl, 'cspace-'+status, keyID)





