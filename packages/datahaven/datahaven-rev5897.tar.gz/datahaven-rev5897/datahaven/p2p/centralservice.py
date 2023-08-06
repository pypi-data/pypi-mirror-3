#!/usr/bin/python
#centralservice.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#
# This is for services with the central DHN.  Main services are:
#
# 1) register with central service
# 2) list suppliers or customers
# 3) fire a supplier, hire another supplier
# 4) account information and transfers  - done in account.py
# 5) nearnesscheck - meat of function done by nearnesscheck.py
#

import os
import sys
import time
import string

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in centralservice.py')

from twisted.internet.defer import Deferred, succeed
from twisted.internet.task import LoopingCall

import lib.misc as misc
import lib.dhnio as dhnio
import lib.settings as settings
import lib.dhnpacket as dhnpacket
import lib.nameurl as nameurl
import lib.packetid as packetid
import lib.commands as commands
import lib.contacts as contacts
import lib.eccmap as eccmap
import lib.transport_control as transport_control
import lib.transport_cspace as transport_cspace
import lib.bandwidth as bandwidth
from lib.diskspace import DiskSpace
import lib.identitycache as identitycache


import automats
import identitypropagate
import money
import localtester
import backup_monitor
import events
import customerservice
#import connectionmanager


_InitDone = False
_Connector = None
_HelloResponseWaiting = False
_SuppliersResponseWaiting = False
_HelloCount = 0
_HelloTask = None
_HelloPID = None
_HelloInterval = 60
_InitControlFunc = None
OnListSuppliersFunc = None
OnListCustomersFunc = None
_CentralStatusDict = {}

#-------------------------------------------------------------------------------

def init(hello_interaval=60):
    global _InitDone
    if _InitDone:
        return
    dhnio.Dprint(4, 'centralservice.init')
    transport_control.AddInboxCallback(inbox)
    bandwidth.init()
    _InitDone = True

def shutdown():
    return succeed(1)

#------------------------------------------------------------------------------

def inbox(newpacket, proto, host):
    commandhandled = False

    if newpacket.OwnerID != settings.CentralID():
        return False

    if newpacket.Command == commands.Ack():
        Ack(newpacket)
        commandhandled = True

    elif newpacket.Command == commands.Receipt():
        Receipt(newpacket)
        commandhandled = True

    elif newpacket.Command == commands.ListContacts():
        ListContacts(newpacket)
        commandhandled = True

    if commandhandled:
        dhnio.Dprint(12, "centralservice.inbox [%s] from %s://%s handled" % (newpacket.Command, proto, host))

    return commandhandled

def send2central(command, data, doAck=False, PacketID=None):
    MyID = misc.getLocalID()
    RemoteID = settings.CentralID()
    if PacketID is None:
        PacketID = packetid.UniqueID()
    packet = dhnpacket.dhnpacket(
        command,
        MyID,
        MyID,
        PacketID,
        data,
        RemoteID,)
    transport_control.outbox(packet, doAck)
    #del packet
    return PacketID

#------------------------------------------------------------------------------

def HelloRequestSuppliers():
    dhnio.Dprint(4, 'centralservice.HelloRequestSuppliers')
    SendRequestSuppliers('', True)


def LoopSendAlive():
    dhnio.Dprint(4, 'centralservice.LoopSendAlive')
    SendIdentity()
    reactor.callLater(settings.DefaultAlivePacketTimeOut(), LoopSendAlive)


#-- SENDING --------------------------------------------------------------------

# Register our identity with central
def SendIdentity(doAck=False):
    dhnio.Dprint(4, "centralservice.SendIdentity")
    LocalIdentity = misc.getLocalIdentity()
    data = LocalIdentity.serialize()
    ret = send2central(commands.Identity(), data, doAck, misc.getLocalID())
    return ret

# Say what eccmap we are using for recovery info
# How many suppliers we want (probably same as used by eccmap but just in case)
# Say how much disk we are donating now
def SendSettings(doAck=False, packetID=None):
    if packetID is None:
        packetID = packetid.UniqueID()
    sdict = {}
    sdict['s'] = str(settings.getCentralNumSuppliers())
    donated = DiskSpace(s=settings.getCentralMegabytesDonated())
    sdict['d'] = str(donated.getValueMb())
    needed = DiskSpace(s=settings.getCentralMegabytesNeeded())
    sdict['n'] = str(needed.getValueMb())
    sdict['e'] = settings.getECC()
    sdict['p'] = str(settings.BasePricePerGBDay())
    sdict['e1'] = str(settings.getEmergencyEmail())
    sdict['e2'] = str(settings.getEmergencyPhone())
    sdict['e3'] = str(settings.getEmergencyFax())
    sdict['e4'] = str(settings.getEmergencyOther()).replace('\n', '<br>')
    sdict['mf'] = settings.getEmergencyFirstMethod()
    sdict['ms'] = settings.getEmergencySecondMethod()
    sdict['ie'] = misc.readExternalIP()
    sdict['il'] = misc.readLocalIP()

    data = dhnio._pack_dict(sdict)
    pid = send2central(commands.Settings(), data, doAck, packetID)
    dhnio.Dprint(4, "centralservice.SendSettings PacketID=[%s]" % pid)
    return pid

def SettingsResponse(packet):
    words = packet.Payload.split('\n')
    try:
        status = words[0]
        last_receipt = int(words[1])
    except:
        status = ''
        last_receipt = -1
    dhnio.Dprint(4, "centralservice.SettingsResponse: status=[%s] last receipt=[%s]" % (status, str(last_receipt)))

def SendRequestSettings(doAck=False):
    dhnio.Dprint(4, 'centralservice.SendRequestSettings')
    return send2central(commands.RequestSettings(), '', doAck)

def SendReplaceSupplier(numORidurl, doAck=False):
    dhnio.Dprint(4, "centralservice.SendReplaceSupplier")
    if isinstance(numORidurl, str):
        idurl = numORidurl
    else:
        idurl = contacts.getSupplierID(numORidurl)
    if not idurl:
        dhnio.Dprint(2, "centralservice.SendReplaceSupplier ERROR supplier not found")
        return None
    data = 'S\n'+idurl+'\n'+str(contacts.numberForSupplier(idurl))
    return send2central(commands.FireContact(), data, doAck)

def SendChangeSupplier(numORidurl, newidurl, doAck=False):
    dhnio.Dprint(4, "centralservice.SendChangeSupplier")
    if isinstance(numORidurl, str):
        idurl = numORidurl
    else:
        idurl = contacts.getSupplierID(numORidurl)
    if not idurl or not newidurl:
        return None
    return send2central(commands.FireContact(), 'N\n'+idurl+'\n'+newidurl, doAck)

def SendReplaceCustomer(num, doAck=False):
    dhnio.Dprint(4, "centralservice.SendReplaceCustomer")
    idurl = contacts.getCustomerID(num)
    if not idurl:
        return None
    data = 'C\n'+idurl+'\n'+str(num)
    return send2central(commands.FireContact(), data, doAck)

def SendRequestSuppliers(data = '', doAck=False):
    dhnio.Dprint(4, "centralservice.SendRequestSuppliers")
    return send2central(commands.RequestSuppliers(), data, doAck)

def SendRequestCustomers(data = '', doAck=False):
    dhnio.Dprint(4, "centralservice.SendRequestCustomers")
    return send2central(commands.RequestCustomers(), data, doAck)


# Account
# User needs to be able to know his balance. We want to keep it on
#   this machine, not check central each time.  Might have a charge
#   for checking with central and keep date of last checkin so user
#   can not check in too often.
#
# Users who have been with DHN for more than 6 months will be able
#    to transfer some of his prepaid/earned balance to another user.
#    This is like a prepaid cellphone transfering balance to another phone.
#
#    A dhnpacket with a commands.Transfer()
#         The data portion says:
#             Amount: 23.4
#             To: http://foo.bar/baz.xml
#
#    With the dhnpacket signed, we know it is legit.  The ID of the destination is there.
#
#
def SendTransfer(DestinationID, Amount, doAck=False):
    dhnio.Dprint(4, "centralservice.SendTransfer  DestinationID=%s  Amount=%s" % (DestinationID, str(Amount)))
    data = DestinationID+'\n'+str(Amount)
    return send2central(commands.Transfer(), data, doAck)


def SendRequestReceipt(missing_receipts, doAck=False):
    dhnio.Dprint(4, 'centralservice.SendRequestReceipt ' + str(missing_receipts))
    data = string.join(list(missing_receipts), ' ')
    return send2central(commands.RequestReceipt(), data, doAck)



#--- RECEIVING -----------------------------------------------------------------


def Ack(packet):
    global _HelloResponseWaiting
    dhnio.Dprint(4, "centralservice.Ack packetID=[%s]" % packet.PacketID)


def Receipt(request):
    dhnio.Dprint(4, "centralservice.Receipt " )
    money.InboxReceipt(request)
    transport_control.SendAck(request)
    missing_receipts = money.SearchMissingReceipts()
    if len(missing_receipts) > 0:
        reactor.callLater(5, SendRequestReceipt, missing_receipts)


#S list of suppliers after RequestSuppliers
#s list of suppliers after RequestSuppliers and have troubles (not found)
#fS list of suppliers after FireContact(supplier)
#fs list of suppliers after FireContact(supplier) and have troubles (not found)
#C list of customers after RequestCustomers
#c list of customers after RequestCustomers and have troubles (not found)
#fC list of customers after FireContact(customers)
#fc list of customers after FireContact(customers) and have troubles (not found)
#bS user was banned with negative balance
legal_codes = ['S','C','s','c','fS','fC','fs','fc','bS']
def ListContacts(request):
    global _CentralStatusDict
    global _SuppliersResponseWaiting
    global legal_codes
    global OnListSuppliersFunc
    global OnListCustomersFunc

    data = request.Payload
    words = data.split('\n', 1)
    if len(words) < 2:
        dhnio.Dprint(1, 'centralservice.ListContacts ERROR wrong data packet [%s]' % str(request.Payload))
        control('ListContactsError', request)
        return

    code = words[0]
    if not code in legal_codes:
        dhnio.Dprint(1, 'centralservice.ListContacts ERROR wrong data in the packet [%s] '  % str(request.Payload))
        control('ListContactsError', request)
        return

    dhnio.Dprint(4, "centralservice.ListContacts code=" + str(code) )

    clist, tail = dhnio._unpack_list(words[1])

    fire_flag = code.startswith('f')
    ban_flag = code.startswith('b')
    contact_type = code.lower()[-1]
    error_flag = code[-1].islower()

    spaceDict = None
    onlineArray = ''
    if tail is not None:
        spaceDict = dhnio._unpack_dict_from_list(tail)
        if spaceDict.has_key('online'):
            onlineArray = spaceDict.pop('online')
    
    dhnio.Dprint(12, 'centralservice.ListContacts fire:[%s] type:[%s] error:[%s]' % (str(fire_flag), str(contact_type), str(error_flag)))

    if contact_type == 's':
        current_contacts = contacts.getSupplierIDs()
        contacts.setSupplierIDs(clist)
        eccmap.init()
        contacts.saveSupplierIDs()
        for supid in contacts.getSupplierIDs():
            if supid.strip() == '':
                error_flag = True
        for newidurl in clist:
            if newidurl not in current_contacts:
                transport_control.ClearAliveTime(newidurl)
                misc.writeSupplierData(newidurl, 'connected', time.strftime('%d%m%y %H:%M:%S'))
                events.info('centralservice', 'new supplier %s connected' % nameurl.GetName(newidurl), '',)
        if backup_monitor.SetSupplierList is not None:
            backup_monitor.SetSupplierList(clist)
        if not fire_flag and current_contacts != clist:
            for newidurl in clist:
                identitycache.Remove(newidurl)
            identitypropagate.RealSendSuppliers()
        if OnListSuppliersFunc is not None:
            OnListSuppliersFunc()

    elif contact_type == 'c':
        current_contacts = contacts.getCustomerIDs()
        contacts.setCustomerIDs(clist)
        contacts.saveCustomerIDs()
        if spaceDict is not None:
            dhnio._write_dict(settings.CustomersSpaceFile(), spaceDict)
            reactor.callLater(3, localtester.TestUpdateCustomers)
        if not fire_flag and current_contacts != clist:
            for newidurl in clist:
                identitycache.Remove(newidurl)
            identitypropagate.RealSendCustomers()
        if OnListCustomersFunc is not None:
            OnListCustomersFunc()
        for oldidurl in current_contacts:
            if oldidurl not in clist:
                events.info('centralservice', 'customer %s were disconnected' % nameurl.GetName(oldidurl),)
        for newidurl in clist:
            if newidurl not in current_contacts:
                transport_control.ClearAliveTime(newidurl)
                events.info('centralservice', 'new customer %s connected' % nameurl.GetName(newidurl))

    if fire_flag:
        if contact_type == 's':
            index = -1
            for index in range(len(clist)):
                if clist[index] != current_contacts[index]:
                    break
            if index >= 0:
                # first we wish to update this contacts in identitycache
                # to know his real Identity. to know where to send
                # we just remove it now
                # later his ID will be downloaded automatically
                identitycache.Remove(clist[index])
                # we want to send our Identity to new supplier
                # and than ask a list of files he have
                # so it should start rebuilding backups immediately
                # right after we got ListFiles from him
                identitypropagate.SendSingleSupplier(clist[index],
                    lambda ack_packet: customerservice.RequestListFiles(ack_packet.OwnerID))

    if ban_flag:
        events.notify('centralservice', 'you have negative balance, all your suppliers was removed', '',)

    if error_flag:
        reactor.callLater(settings.DefaultNeedSuppliersPacketTimeOut(), SendRequestSuppliers)
        events.info('centralservice', 'could not find available supplier(s)',
                     'Central server can not find available suppliers for you.\nCheck your central settings.\n',)

#    if ban_flag or fire_flag:
#        transport_cspace.close_not_needed_streams()

    #identitypropagate.FetchNecesaryContacts()

    for i in range(len(onlineArray)):
        if i < len(clist):
            _CentralStatusDict[clist[i]] = onlineArray[i]  
            
    transport_control.SendAck(request)

    if contact_type == 's':
        automats.central_connector('list-suppliers', request)
    elif contact_type == 'c':
        automats.central_connector('list-customers', request)

    if _SuppliersResponseWaiting and contact_type == 's':
        control('ListContacts', request)
        _SuppliersResponseWaiting = False


#--- NEARNESS ------------------------------------------------------------------

#  NearnessCheck request coming from central
#  When request comes in we start the check with callback
#  going to NearnessResult which will send results to central.
def NearnessCheck(request):
    dhnio.Dprint(4, "centralservice.NearnessCheck")

def NearnessResult():
    dhnio.Dprint(4, "centralservice.NearnessResult")

#--- BANDWIDTH -----------------------------------------------------------------

def LoopSendBandwidthReport():
    pid = SendBandwidthReport()
    if pid is not None:
        transport_control.RegisterInterest(ReceiveBandwidthAck, settings.CentralID(), pid)
    reactor.callLater(settings.DefaultBandwidthReportTimeOut(), LoopSendBandwidthReport)

def SendBandwidthReport():
    listin, listout = bandwidth.files2send()
    if len(listin) == 0 and len(listout) == 0:
        dhnio.Dprint(4, 'centralservice.SendBandwidthReport skip')
        return None
    dhnio.Dprint(4, 'centralservice.SendBandwidthReport')
    src = ''
    for filepath in listin:
        filename = os.path.basename(filepath)
        if len(filename) != 6:
            dhnio.Dprint(6, 'centralservice.SendBandwidthReport WARNING incorrect filename ' + filepath)
            continue
        s = dhnio.ReadBinaryFile(filepath)
        if not s:
            dhnio.Dprint(6, 'centralservice.SendBandwidthReport WARNING %s is empty' % filepath)
            continue
        src += '[in] %s\n' % filename
        src += s.strip()
        src += '\n[end]\n'
    for filepath in listout:
        filename = os.path.basename(filepath)
        if len(filename) != 6:
            dhnio.Dprint(6, 'centralservice.SendBandwidthReport WARNING incorrect filename ' + filepath)
            continue
        s = dhnio.ReadBinaryFile(filepath)
        if not s:
            dhnio.Dprint(6, 'centralservice.SendBandwidthReport WARNING %s is empty' % filepath)
            continue
        src += '[out] %s\n' % filename
        src += s.strip()
        src += '\n[end]\n'
    dhnio.Dprint(4, '\n' + src)
    if src.strip() == '':
        dhnio.Dprint(4, 'centralservice.SendBandwidthReport WARNING src is empty. skip.')
        return None
    return send2central(commands.BandwidthReport(), src)

def ReceiveBandwidthAck(packet):
    dhnio.Dprint(4, 'centralservice.ReceiveBandwidthAck')
    for line in packet.Payload.split('\n'):
        try:
            typ, filename = line.strip().split(' ')
        except:
            continue
        if typ == '[in]':
            filepath = os.path.join(settings.BandwidthInDir(), filename)
        elif typ == '[out]':
            filepath = os.path.join(settings.BandwidthOutDir(), filename)
        else:
            dhnio.Dprint(2, 'centralservice.ReceiveBandwidthAck ERROR typ=%s filename=%s' % (typ, filename))
            continue
        if not os.path.isfile(filepath):
            dhnio.Dprint(2, 'centralservice.ReceiveBandwidthAck ERROR %s not found' % filepath)
            continue
        if os.path.isfile(filepath+'.sent'):
            dhnio.Dprint(2, 'centralservice.ReceiveBandwidthAck WARNING %s already sent' % filepath)
            continue
        try:
            os.rename(filepath, filepath+'.sent')
        except:
            dhnio.Dprint(2, 'centralservice.ReceiveBandwidthAck ERROR can not rename %s' % filepath)
            dhnio.DprintException()
        dhnio.Dprint(6, 'centralservice.ReceiveBandwidthAck %s renamed' % filepath)


#-------------------------------------------------------------------------------


def main():
    try:
        from twisted.internet import reactor
    except:
        sys.exit('Error initializing twisted.internet.reactor in centralservice.py')

    transport_control.init()
    SendIdentity()
    reactor.run()


if __name__ == '__main__':
    main()



