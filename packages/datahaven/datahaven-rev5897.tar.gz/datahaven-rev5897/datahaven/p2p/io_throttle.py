#!/usr/bin/python
#io_throttle.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#    When reconstructing a backup we don't want to take over everything
#    and make DHN unresponsive by requesting 1000's of files at once
#    and make it so no other packets can go out,
#    this just tries to limit how much we are sending out or receiving at any time
#    so that we still have control.
#    Before requesting another file or sending another one out
#    I check to see how much stuff I have waiting.  


import os
import time


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in io_throttle.py')


import lib.transport_control as transport_control
import lib.dhnio as dhnio
import lib.settings as settings
import lib.dhnpacket as dhnpacket
import lib.commands as commands
import lib.misc as misc
import lib.tmpfile as tmpfile
import lib.nameurl as nameurl


import contacts_status

#------------------------------------------------------------------------------ 


class FileToRequest:
    def __init__(self, callOnReceived, creatorID, packetID, ownerID, remoteID):
        self.callOnReceived = []
        self.callOnReceived.append(callOnReceived)
        self.creatorID = creatorID
        self.packetID = packetID
        self.ownerID = ownerID
        self.remoteID = remoteID
        self.backupID = packetID[0:packetID.find("-")]
        self.requestTime = None
        self.fileReceivedTime = None


class FileToSend:
    def __init__(self, fileName, packetID, remoteID, ownerID, callOnAck=None, callOnFail=None):
        self.fileName = fileName
        self.packetID = packetID
        self.remoteID = remoteID
        self.ownerID = ownerID
        self.callOnAck = callOnAck
        self.callOnFail = callOnFail
        self.sendTime = None
        self.ackTime = None


#TODO I'm not removing items from the dict's at the moment
class SupplierQueue:
    def __init__(self, supplierIdentity, creatorID):
        self.creatorID = creatorID
        self.supplierIdentity = supplierIdentity

        # all sends we'll hold on to, only several will be active, 
        # but will hold onto the next ones to be sent
        # self.fileSendQueueMaxLength = 32
        # active files 
        self.fileSendMaxLength = 1 # 1 mean sending files one by one! 
        # an array of packetId, preserving first in first out, 
        # of which the first maxLength are the "active" sends      
        self.fileSendQueue = []
        # dictionary of FileToSend's using packetId as index, 
        # hold onto stuff sent and acked for some period as a history?         
        self.fileSendDict = {}          

        # all requests we'll hold on to, 
        # only several will be active, but will hold onto the next ones to be sent
        self.fileRequestQueueMaxLength = 6
        # active requests 
        self.fileRequestMaxLength = 1 # do requests one by one   
        # an arry of PacketIDs, preserving first in first out
        self.fileRequestQueue = []      
        # FileToRequest's, indexed by PacketIDs
        self.fileRequestDict = {}       

        # in theory transport_control should handle resending, 
        # but in case it doesn't ...
        self.baseTimeout = settings.SendTimeOut()
        # 30 minutes 
        self.maxTimeout = 1800
        # when do we decide a request has timed out 
        # and what is the backoff for this supplier          
        self.timeout = self.baseTimeout 

        self.dprintAdjust = 0
        self.shutdown = False

        self.ackedCount = 0
        self.failedCount = 0
        
        self.sendFailedPacketIDs = []


#    def OkToQueueRequest(self):
#        return len(self.fileRequestQueue) < self.fileRequestQueueMaxLength


#    def OkToQueueSend(self):
#        return len(self.fileSendQueue) < self.fileSendQueueMaxLength


    def RemoveSupplierWork(self): 
        # in the case that we're doing work with a supplier who has just been replaced ...
        # Need to remove the register interests
        # our dosend is using acks?
        self.shutdown = True
        #newpacket = dhnpacket.dhnpacket(commands.Data(), fileToSend.ownerID, self.creatorID, fileToSend.packetID, Payload, fileToSend.remoteID)
        for i in range(min(self.fileSendMaxLength, len(self.fileSendQueue))):
            fileToSend = self.fileSendDict[self.fileSendQueue[i]]
            transport_control.RemoveSupplierRequestFromSendQueue(fileToSend.packetID, fileToSend.remoteID, commands.Data())
            transport_control.RemoveInterest(fileToSend.remoteID, fileToSend.packetID)
        for i in range(min(self.fileRequestMaxLength, len(self.fileRequestQueue))):
            fileToRequest = self.fileRequestDict[self.fileRequestQueue[i]]
            transport_control.RemoveSupplierRequestFromSendQueue(fileToRequest.packetID, fileToRequest.remoteID, commands.Retrieve())
            transport_control.RemoveInterest(fileToRequest.remoteID, fileToRequest.packetID)


    def QueueSendFile(self, fileName, packetID, supplierIdentity, ownerID, callOnAck=None, callOnFail=None):
        if self.shutdown: 
            return        
        #if not transport_control.ContactIsAlive(supplierIdentity):
        if contacts_status.isOffline(supplierIdentity):
            dhnio.Dprint(self.dprintAdjust+12, "IOThrottle.SupplierQueue.QueueSendFile %s is offline, so packet %s is failed" % (nameurl.GetName(supplierIdentity), packetID))
            if callOnFail is not None:
                reactor.callLater(.01, callOnFail, supplierIdentity, packetID)
            return
        if packetID in self.fileSendQueue:
            dhnio.Dprint(self.dprintAdjust+3, "IOThrottle.SupplierQueue.QueueSendFile WARNING packet %s already in the queue" % packetID)
            if callOnAck is not None:
                reactor.callLater(.01, callOnAck, None, supplierIdentity, packetID)
            return
        self.fileSendQueue.append(packetID)
        self.fileSendDict[packetID] = FileToSend(
            fileName, 
            packetID, 
            supplierIdentity, 
            ownerID, 
            callOnAck,
            callOnFail,)
        dhnio.Dprint(self.dprintAdjust+12, "IOThrottle.SupplierQueue.QueueSendFile " + packetID + ", queue length=" + str(len(self.fileSendQueue)))
        reactor.callLater(0.01, self.DoSend)
            

    def DoSend(self):
        if self.shutdown: 
            return
        packetsFialed = []
        packetsToRemove = []
        packetsSent = 0
        # let's check all packets in the queue        
        for i in range(len(self.fileSendQueue)):
            packetID = self.fileSendQueue[i]
            fileToSend = self.fileSendDict[packetID]
            # we got notify that this packet was failed to send
            if packetID in self.sendFailedPacketIDs:
                self.sendFailedPacketIDs.remove(packetID)
                packetsFialed.append(packetID)
                continue
            # we already sent the file
            if fileToSend.sendTime is not None:
                packetsSent += 1
                #and we go ack
                if fileToSend.ackTime is not None:
                    deltaTime = fileToSend.ackTime - fileToSend.sendTime
                    #so remove it from queue
                    packetsToRemove.append(packetID)
                # if we do not get an ack ...    
                else:
                    # ... we do not want to wait to long
                    if time.time() - fileToSend.sendTime > self.baseTimeout:
                        # so this packet is failed because no response on it 
                        packetsFialed.append(packetID)
                # we sent this packet already - check next one
                continue
            # the data file to send no longer exists - it is failed situation
            if not os.path.exists(fileToSend.fileName):
                dhnio.Dprint(self.dprintAdjust+7, "IOThrottle.SupplierQueue.DoSend WARNING file %s not exist" % (fileToSend.fileName))
                packetsFialed.append(packetID)
                continue
            # do not send too many packets, need to wait for ack
            # hold other packets in the queue and may be send next time
            if packetsSent > self.fileSendMaxLength:
                # if we sending big file - we want to wait
                # other packets must go without waiting in the queue
                # 10K seems fine, because we need to filter only Data and Parity packets here
                if os.path.getsize(fileToSend.fileName) > 1024 * 10:
                    continue
            # prepare the packet
            Payload = str(dhnio.ReadBinaryFile(fileToSend.fileName))
            newpacket = dhnpacket.dhnpacket(
                commands.Data(), 
                fileToSend.ownerID, 
                self.creatorID, 
                fileToSend.packetID, 
                Payload, 
                fileToSend.remoteID)
            # outbox will not resend, because no ACK, just data, 
            # need to handle resends on own
            transport_control.outboxNoAck(newpacket)  
            transport_control.RegisterInterest(
                self.FileSendAck, 
                fileToSend.remoteID, 
                fileToSend.packetID)
            # mark file as been sent
            fileToSend.sendTime = time.time()
            packetsSent += 1
        # process failed packets
        for packetID in packetsFialed:
            self.FileSendFailed(self.fileSendDict[packetID].remoteID, packetID)
            packetsToRemove.append(packetID)
        # remove finished packets    
        for packetID in packetsToRemove:
            self.fileSendQueue.remove(packetID)
            del self.fileSendDict[packetID]
        # if sending queue is empty - remove all records about packets failed to send
        if len(self.fileSendQueue) == 0:
            del self.sendFailedPacketIDs[:]
        # let's check queue again, but only if we sent something or do other jobs  
        if len(packetsToRemove) > 0 or packetsSent > 0: 
            reactor.callLater(0.1, self.DoSend)
        # erase temp lists    
        del packetsFialed
        del packetsToRemove
                    

    def FileSendAck(self, packet):    
        if self.shutdown: 
            return
        self.ackedCount += 1
        self.timeout = self.baseTimeout
        if packet.PacketID not in self.fileSendQueue:
            dhnio.Dprint(self.dprintAdjust+3, "IOThrottle.SupplierQueue.FileSendAck WARNING packet %s not in send queue" % packet.PacketID)
            return
        if packet.PacketID not in self.fileSendDict.keys():
            dhnio.Dprint(self.dprintAdjust+3, "IOThrottle.SupplierQueue.FileSendAck WARNING packet %s not in send dict" % packet.PacketID)
            return
        self.fileSendDict[packet.PacketID].ackTime = time.time()
        if self.fileSendDict[packet.PacketID].callOnAck:
            reactor.callLater(0, self.fileSendDict[packet.PacketID].callOnAck, packet, packet.OwnerID, packet.PacketID)
        reactor.callLater(0.01, self.DoSend)

        
    def FileSendFailed(self, RemoteID, PacketID):
        if self.shutdown: 
            return
        self.failedCount += 1
        if PacketID not in self.fileSendDict.keys():
            dhnio.Dprint(self.dprintAdjust+3, "IOThrottle.SupplierQueue.FileSendFailed WARNING packet %s not in send dict" % PacketID)
            return
        fileToSend = self.fileSendDict[PacketID]
        transport_control.RemoveSupplierRequestFromSendQueue(fileToSend.packetID, fileToSend.remoteID, commands.Data())
        transport_control.RemoveInterest(fileToSend.remoteID, fileToSend.packetID)
        if fileToSend.callOnFail:
            reactor.callLater(0, fileToSend.callOnFail, RemoteID, PacketID)
        reactor.callLater(0.01, self.DoSend)


    def QueueRequest(self, callOnReceived, creatorID, packetID, ownerID, remoteID):
        if self.shutdown: 
            return
        if packetID not in self.fileRequestQueue:
            self.fileRequestQueue.append(packetID)
            self.fileRequestDict[packetID] = FileToRequest(
                callOnReceived, 
                creatorID, 
                packetID, 
                ownerID, 
                remoteID)
            dhnio.Dprint(self.dprintAdjust+7, "IOThrottle.SupplierQueue.QueueRequest for packetID " + packetID + ", queue length=" + str(len(self.fileRequestQueue)))
            reactor.callLater(0.01, self.DoRequest)


    def DoRequest(self):
        if self.shutdown:
            return
        packetsToRemove = []
        for i in range(0,min(self.fileRequestMaxLength, len(self.fileRequestQueue))):
            packetID = self.fileRequestQueue[i]
            currentTime = time.time()
            if self.fileRequestDict[packetID].requestTime is not None:
                if self.fileRequestDict[packetID].fileReceivedTime is None:
                    if currentTime - self.fileRequestDict[packetID].requestTime > self.timeout:
                        self.fileRequestDict[packetID].requestTime = None
                        self.timeout = min(2 * self.timeout,self.maxTimeout)
                else:
                    packetsToRemove.append(packetID)
            if self.fileRequestDict[packetID].requestTime is None:
                if not os.path.exists(os.path.join(tmpfile.subdir('data-par'), packetID)): 
                    fileRequest = self.fileRequestDict[packetID]
                    dhnio.Dprint(self.dprintAdjust+7, "IOThrottle.SupplierQueue.DoRequest for packetID " + fileRequest.packetID)
                    transport_control.RegisterInterest(
                        self.DataReceived, 
                        fileRequest.creatorID, 
                        fileRequest.packetID)
                    newpacket = dhnpacket.dhnpacket(
                        commands.Retrieve(), 
                        fileRequest.ownerID, 
                        fileRequest.creatorID, 
                        fileRequest.packetID, 
                        "", 
                        fileRequest.remoteID)
                    transport_control.outboxNoAck(newpacket)  
                    fileRequest.requestTime = time.time()
                else:
                    # we have the data file, no need to request it
                    packetsToRemove.append(packetID)
        if len(packetsToRemove) > 0:
            for packetID in packetsToRemove:
                self.fileRequestQueue.remove(packetID)
            reactor.callLater(0.01, self.DoRequest)


    def DataReceived(self, packet):   # we requested some data from a supplier, just received it
        if self.shutdown: # if we're closing down this queue (supplier replaced, don't any anything new)
            return
        self.timeout = self.baseTimeout
        dhnio.Dprint(self.dprintAdjust+11, "IOThrottle.SupplierQueue.DataReceived packetID " + packet.PacketID)
        if packet.PacketID in self.fileRequestQueue:
            self.fileRequestQueue.remove(packet.PacketID)
            #dhnio.Dprint(self.dprintAdjust+2, "IOThrottle.SupplierQueue.DataReceived packet in fileRequestQueue " + str(self.fileRequestQueue))
        if self.fileRequestDict.has_key(packet.PacketID):
            self.fileRequestDict[packet.PacketID].fileReceivedTime = time.time()
            for callBack in self.fileRequestDict[packet.PacketID].callOnReceived:
                callBack(packet)
        if self.fileRequestDict.has_key(packet.PacketID):
            del self.fileRequestDict[packet.PacketID]
        reactor.callLater(0.01, self.DoRequest)


    def CheckOk(self):
        if self.shutdown: 
            # if we're closing down this queue 
            # (supplier replaced, don't any anything new)
            return
        currentTime = time.time()
        # do we need to do anything to check the data send queue since the DoSend is using the transport_control.outbox
        # that keeps trying until it gets an ACK, so at this time ... do nothing for the send queue?
        # running into trouble that the outbox that should retry until an ACK doesn't seem to be working right
        if True: # turn this off later if problem appears to be solved
            doSend = False
            for i in range(min(self.fileSendMaxLength, len(self.fileSendQueue))):
                packetID = self.fileSendQueue[i]
                if self.fileSendDict[packetID].sendTime is None:
                    doSend = True
                    break
                if self.fileSendDict[packetID].ackTime is None:
                    if (currentTime - self.fileSendDict[packetID].sendTime) > self.baseTimeout:
                        #self.fileSendDict[packetID].sendTime = None
                        #self.timeout = min(2 * self.timeout,self.maxTimeout)
                        doSend = True
                        break
        if doSend:
            reactor.callLater(0.01, self.DoSend)

        # now for the request queue...
        #dhnio.Dprint(self.dprintAdjust+11, "IOThrottle.SupplierQueue.CheckOk for supplier " + self.supplierIdentity + " at " + str(currentTime) + ", timeout=" + str(self.timeout))
        doRequest = False
        for i in range(min(self.fileRequestMaxLength, len(self.fileRequestQueue))):
            packetID = self.fileRequestQueue[i]
            #dhnio.Dprint(self.dprintAdjust+12, "IOThrottle.SupplierQueue.CheckOk request time for packet " + packetID + ", requested at " + str(self.fileRequestDict[packetID].requestTime))
            if self.fileRequestDict[packetID].requestTime is None:
                #dhnio.Dprint(self.dprintAdjust+13, "IOThrottle.SupplierQueue.CheckOk found a queued item that hadn't been sent")
                doRequest = True
                break
            elif self.fileRequestDict[packetID].fileReceivedTime is None:
                if currentTime - self.fileRequestDict[packetID].requestTime > self.timeout:
                    #dhnio.Dprint(self.dprintAdjust+11, "IOThrottle.SupplierQueue.CheckOk found a queued item that timed out ")
                    # this will mart file for request one more time
                    # TODO need to keep eye on this
                    self.fileRequestDict[packetID].requestTime = None
                    self.timeout = min(2 * self.timeout, self.maxTimeout)
                    doRequest = True
                    break
        if doRequest:
            reactor.callLater(0.01, self.DoRequest)


    def DeleteBackupRequests(self, backupName):
        if self.shutdown: 
            # if we're closing down this queue 
            # (supplier replaced, don't any anything new)
            return
        packetsToRemove = []
        for packetID in self.fileSendQueue:
            if packetID.find(backupName) == 0:
                self.FileSendFailed(self.fileSendDict[packetID].remoteID, packetID)
                packetsToRemove.append(packetID)
        for packetID in packetsToRemove:
            self.fileSendQueue.remove(packetID)
            del self.fileSendDict[packetID]
        packetsToRemove = []
        for packetID in self.fileRequestQueue:
            if packetID.find(backupName) == 0:
                packetsToRemove.append(packetID)
        for packetID in packetsToRemove:
            self.fileRequestQueue.remove(packetID)
            del self.fileRequestDict[packetID]
        if len(self.fileRequestQueue)>0:
            reactor.callLater(0.01, self.DoRequest)
        if len(self.fileSendQueue)>0:
            reactor.callLater(0.01, self.DoSend)


    def OutboxStatus(self, workitem, proto, host, status, error, message):
        packetID = workitem.packetid
        if status == 'failed' and packetID in self.fileSendQueue:
            self.sendFailedPacketIDs.append(packetID)
            reactor.callLater(0.01, self.DoSend)
            
    

# all of the backup rebuilds will run their data requests through this 
# so it gets throttled, also to reduce duplicate requests
class IOThrottle:
    def __init__(self):
        self.creatorID = misc.getLocalID()
        self.supplierQueues = {} #
        self.dprintAdjust = 0
        reactor.callLater(60, self.CheckOk) # 1 minute


    def CheckOk(self):
        #if settings.getDoBackupMonitor() == "Y":
        for supplierIdentity in self.supplierQueues.keys():
            self.supplierQueues[supplierIdentity].CheckOk()
        reactor.callLater(60, self.CheckOk) 


    def DeleteSuppliers(self, supplierIdentities):
        for supplierIdentity in supplierIdentities:
            if self.supplierQueues.has_key(supplierIdentity):
                self.supplierQueues[supplierIdentity].RemoveSupplierWork()
                del self.supplierQueues[supplierIdentity]


    def DeleteBackupRequests(self, backupName):
        #if settings.getDoBackupMonitor() == "Y":
        for supplierIdentity in self.supplierQueues.keys():
            self.supplierQueues[supplierIdentity].DeleteBackupRequests(backupName)


    def QueueSendFile(self, fileName, packetID, supplierIdentity, ownerID, callOnAck=None, callOnFail=None):
#        if settings.getDoBackupMonitor() != "Y":
#            return
        if not os.path.exists(fileName):
            dhnio.Dprint(self.dprintAdjust+2, "IOThrottle.QueueSendFile ERROR %s not exist " % fileName)
            if callOnFail is not None:
                reactor.callLater(.01, callOnFail, ownerID, packetID)
            return
        if supplierIdentity not in self.supplierQueues.keys():
            self.supplierQueues[supplierIdentity] = SupplierQueue(supplierIdentity, self.creatorID)
        if packetID not in self.supplierQueues[supplierIdentity].fileSendQueue:
            dhnio.Dprint(self.dprintAdjust+12, "IOThrottle.QueueSendFile adding packet " + packetID)
            self.supplierQueues[supplierIdentity].QueueSendFile(
                fileName, 
                packetID, 
                supplierIdentity, 
                ownerID, 
                callOnAck, 
                callOnFail,)
        else:
            dhnio.Dprint(self.dprintAdjust+4, "IOThrottle.QueueSendFile WARNING packet %s already sent" % packetID)
            

    def QueueRequestFile(self, callOnReceived, creatorID, packetID, ownerID, remoteID):
        if remoteID not in self.supplierQueues.keys():
            self.supplierQueues[remoteID] = SupplierQueue(remoteID, self.creatorID)
        # make sure we don't add a second request for the same file, also that we don't actually already have the file
        # if (packetID not in self.supplierQueues[remoteID].fileRequestQueue) and not os.path.exists(os.path.join(tempfile.gettempdir(),packetID)):
        if packetID not in self.supplierQueues[remoteID].fileRequestQueue and not os.path.exists(os.path.join(tmpfile.subdir('data-par'), packetID)):
            dhnio.Dprint(self.dprintAdjust+12, "IOThrottle.QueueRequestFile adding packet " + packetID)
            self.supplierQueues[remoteID].QueueRequest(callOnReceived, creatorID, packetID, ownerID, remoteID)


#    def OkToQueueRequest(self, supplierIdentity):
##        if settings.getDoBackupMonitor() == "Y":
#        if supplierIdentity not in self.supplierQueues.keys():
#            self.supplierQueues[supplierIdentity] = SupplierQueue(supplierIdentity, self.creatorID)
#        return self.supplierQueues[supplierIdentity].OkToQueueRequest()
##        return False


#    def OkToQueueSend(self, supplierIdentity):
#        #if settings.getDoBackupMonitor() == "Y":
#        if supplierIdentity not in self.supplierQueues.keys():
#            self.supplierQueues[supplierIdentity] = SupplierQueue(supplierIdentity, self.creatorID)
#        return self.supplierQueues[supplierIdentity].OkToQueueSend()
#        #return False


    def InboxStatus(self, newpacket, status, proto, host, error, message):
        pass
        
    
    def OutboxStatus(self, workitem, proto, host, status, error, message):
#        if settings.getDoBackupMonitor() == "Y":
        for supplierIdentity in self.supplierQueues.keys():
            self.supplierQueues[supplierIdentity].OutboxStatus(workitem, proto, host, status, error, message)

#------------------------------------------------------------------------------ 

QueueSendFile = None
QueueRequestFile = None
#OkToQueueRequest = None
#OkToQueueSend = None
DeleteBackupRequests = None
DeleteSuppliers = None
InboxStatus = None
OutboxStatus = None

def init():
    dhnio.Dprint(4,"io_throttle.init")
    global QueueSendFile
    global QueueRequestFile
#    global OkToQueueRequest
#    global OkToQueueSend
    global DeleteBackupRequests
    global DeleteSuppliers
    global InboxStatus
    global OutboxStatus
    _throttle = IOThrottle()
    QueueSendFile = _throttle.QueueSendFile
    QueueRequestFile = _throttle.QueueRequestFile
#    OkToQueueRequest = _throttle.OkToQueueRequest
#    OkToQueueSend = _throttle.OkToQueueSend
    DeleteBackupRequests = _throttle.DeleteBackupRequests
    DeleteSuppliers = _throttle.DeleteSuppliers
    InboxStatus = _throttle.InboxStatus
    OutboxStatus = _throttle.OutboxStatus
    #transport_control.AddInboxPacketStatusFunc(InboxStatus)
    transport_control.AddOutboxPacketStatusFunc(OutboxStatus)
    
    
