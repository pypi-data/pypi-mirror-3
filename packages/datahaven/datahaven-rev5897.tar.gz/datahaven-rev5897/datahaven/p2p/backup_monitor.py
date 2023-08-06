#!/usr/bin/python
#backup_monitor.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#This does a bunch of things.  
#1)  monitor the lists of file sent back from suppliers,
#    if there is a gap we need to try to fix it
#    * main class is _BackupMonitor,
#      it saves the lists of files in _BackupListFiles,
#      breaks down the lists of files into info on a single backup in _SupplierBackupInfo
#    * _BlockRebuilder takes care of a single broken block,
#      request what we have available, builds whatever we can
#      and stops either when we have fixed everything
#      or there is nothing more we can do
#    * _BlockRebuilder requests files through io_throttle and sends out the fixed files
#      also through io_throttle
#
#2)  if a backup is unfixable, not enough information, we delete it CleanupBackups in _BackupMonitor
#
#3)  every hour it requests a list of files from each supplier - _hourlyRequestListFiles
#
#4)  every hour it tests a file from each supplier,
#    seeing if they have the data they claim,
#    and that it is correct
#    * data is stored in _SuppliersSet and _SupplierRemoteTestResults,
#    was data good, bad, being rebuilt, or they weren't online 
#    and we got no data on the result
#    * if a supplier hasn't been seen in settings.FireInactiveSupplierIntervalHours()
#    we replace them


import os
import sys
import time
import random


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in backup_monitor.py')

from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet import threads


import lib.dhnio as dhnio
import lib.misc as misc
import lib.nameurl as nameurl
import lib.transport_control as transport_control
import lib.settings as settings
import lib.contacts as contacts
import lib.eccmap as eccmap
import lib.tmpfile as tmpfile
from lib.automat import Automat


import raidread
import centralservice
import customerservice
import io_throttle
import backup_db
import contacts_status


#------------------------------------------------------------------------------ 

_Monitor = None
InitDone = False
IncomingListFiles = None
AddBackupInProcess = None
RemoveBackupInProcess = None
IsBackupInProcess = None
DeleteBackup = None
DeleteLocalBackup = None
GetBackupStats = None
GetBackupBlocksAndPercent = None 
GetBackupIds = None
SetBackupStatusNotifyCallback = None
SetStatusCallBackForGuiBackup = None
SetSupplierList = None
#GetAllBackupsSpace = None
#GetBackupSpace = None
GetBackupLocalStats = None
#IncomingDataPacket = None       
#GetBackupInProcessStats = None  
OnIncomingListFilesFunc = None   
OnIncomingDataPacketFunc = None
OnNewBackupListFilesFunc = None
NoteToUpdate = None 
ReadLocalFiles = None

#------------------------------------------------------------------------------ 

def monitor():
    global _Monitor
    if _Monitor is None:
        _Monitor = _BackupMonitor()
    return _Monitor

def init():
    dhnio.Dprint(4, "backup_monitor.init")
    global InitDone
#    global IncomingDataPacket
    global IncomingListFiles
    global AddBackupInProcess
    global RemoveBackupInProcess
    global IsBackupInProcess
    global DeleteBackup
    global DeleteLocalBackup
    global GetBackupStats
    global GetBackupBlocksAndPercent
    global GetBackupIds
    global SetBackupStatusNotifyCallback
    global SetStatusCallBackForGuiBackup
    global SetSupplierList
#    global GetAllBackupsSpace
#    global GetBackupSpace
    global GetBackupLocalStats
#    global GetBackupInProcessStats
    global NoteToUpdate
    global ReadLocalFiles
    if InitDone:
        return
    monitor()
    IncomingListFiles = monitor().IncomingListFiles
    AddBackupInProcess = monitor().AddBackupInProcess
    RemoveBackupInProcess = monitor().RemoveBackupInProcess
    IsBackupInProcess = monitor().IsBackupInProcess
    DeleteBackup = monitor().DeleteBackup
    DeleteLocalBackup = monitor().DeleteLocalBackup
    GetBackupStats = monitor().GetBackupStats 
    GetBackupBlocksAndPercent = monitor().GetBackupBlocksAndPercent
    GetBackupIds = monitor().GetBackupIds
    SetBackupStatusNotifyCallback = monitor().SetBackupStatusNotifyCallback
    SetStatusCallBackForGuiBackup = monitor().SetStatusCallBackForGuiBackup
    SetSupplierList = monitor().SetSupplierList
#    GetAllBackupsSpace = monitor().GetAllBackupsSpace
#    GetBackupSpace = monitor().GetBackupSpace
    GetBackupLocalStats = monitor().GetBackupLocalStats
#    IncomingDataPacket = monitor().IncomingDataPacket
#    GetBackupInProcessStats = monitor().GetBackupInProcessStats
    NoteToUpdate = monitor().NoteToUpdate
    ReadLocalFiles = monitor().ReadLocalFiles
    InitDone = True

def start():
    monitor().automat('start')

#------------------------------------------------------------------------------ 

class _SupplierRemoteTestResults:
    def __init__(self, supplierIdentity):
        self.supplierIdentity = supplierIdentity
        self.success_count = 0
        self.fail_count = 0
        self.rebuilding_count = 0
        self.nodata_count = 0

    def report(self):
        dhnio.Dprint(8, self.supplierIdentity + " success_count=" + str(self.success_count) + ", fail_count = " + str(self.fail_count) + ", rebuilding_count = " + str(self.rebuilding_count) + ", nodata_count = " + str(self.nodata_count))


#------------------------------------------------------------------------------ 
# this should represent the set of suppliers for either the user or for a customer the user
# is acting as a scrubber for
class _SuppliersSet:
    def __init__(self, supplierList):
        self.suppliers = supplierList
        self.supplierCount = len(self.suppliers)
        self.activeArray = []
        self.activeTime = time.time() - 10000.0
        self.bootTime = time.time()
        self._populateLookup()
        #self.fireInterval = settings.FireInactiveSupplierIntervalHours()

    def _populateLookup(self):
        self.supplierCount = len(self.suppliers)
        self.supplierNoLookup = {}
        self.supplierRemoteTests = {}
        for i in range(self.supplierCount):
            self.supplierNoLookup[self.suppliers[i]] = i
            self.supplierRemoteTests[self.suppliers[i]] = _SupplierRemoteTestResults(self.suppliers[i])

    def GetActiveArray(self):
        activeArray = [0] * self.supplierCount
        for i in range(self.supplierCount):
            #if transport_control.ContactIsAlive(self.suppliers[i]):
            if contacts_status.isOnline(self.suppliers[i]):
                activeArray[i] = 1
            else:
                activeArray[i] = 0
        return activeArray
#        # if it has been longer than x seconds 
#        # since the last time we checked active array
#        if time.time() - self.activeTime > 15.0: 
#            #self.fireInterval = float(settings.FireInactiveSupplierIntervalHours()) * 3600
#            self.activeArray = [0] * self.supplierCount
#            for i in range(self.supplierCount):
#                if transport_control.ContactIsAlive(self.suppliers[i]):
#                    self.activeArray[i] = 1
#                else:
#                    self.activeArray[i] = 0
#                    #supplierActiveTime = transport_control.GetContactAliveTime(self.suppliers[i])
#                    # commented out by Veselin
#                    # firehire.py - will monitor the suppliers 
#                    # no need to do this here 
#                    #if supplierActiveTime == 0:
#                    #    supplierActiveTime = self.bootTime
#                    #if  supplierActiveTime < (time.time() - self.fireInterval):
#                    #    dhnio.Dprint(2, "_SuppliersSet.GetActiveArray replacing inactive supplier number " + str(i) + ", id=" + str(self.suppliers[i]))
#                    #    centralservice.SendReplaceSupplier(i)
#            self.activeTime = time.time()
#        return self.activeArray

    def ChangedArray(self, supplierList):
        changedArray = [0] * self.supplierCount
        changedIdentities = []
        for i in range(0,self.supplierCount):
            if supplierList[i] != self.suppliers[i]:
                changedArray[i] = 1
                changedIdentities.append(supplierList[i])
        return changedArray, changedIdentities

    def SuppliersChanged(self, supplierList):
        if len(supplierList) != self.supplierCount:
            return True
        for i in range(self.supplierCount):
            if supplierList[i] != self.suppliers[i]:
                return True
        return False

    # if suppliers 1 and 3 changed, return [1,3]
    def SuppliersChangedNumbers(self, supplierList):
        changedList = []
        for i in range(0,self.supplierCount):
            if supplierList[i] != self.suppliers[i]:
                changedList.append(i)
        return changedList

    def SupplierCountChanged(self):
        if len(supplierList) != self.supplierCount:
            return True
        else:
            return False

    def UpdateSuppliers(self, supplierList):
        self.suppliers = supplierList
        self._populateLookup()

    def RemoteTestFail(self, supplierIdentity):
        self.supplierRemoteTests[supplierIdentity].fail_count += 1

    def RemoteTestSuccess(self, supplierIdentity):
        self.supplierRemoteTests[supplierIdentity].success_count += 1

    def RemoteTestRebuilding(self, supplierIdentity):
        self.supplierRemoteTests[supplierIdentity].rebuilding_count += 1

    def RemoteTestNoData(self, supplierIdentity):
        self.supplierRemoteTests[supplierIdentity].nodata_count += 1

    def RemoteTestReport(self):
        for supplier in self.suppliers:
            self.supplierRemoteTests[supplier].report()

#------------------------------------------------------------------------------ 

class _SupplierBackupInfo:             # only info for this backup for this supplier
    def __init__(self, backupId, supplierNum, supplierId):
        self.backupId = backupId
        self.supplierNum = supplierNum
        #self.supplierId = supplierId   # probably not needed
        self.rawDataListFile = ""      #
        self.rawParityListFile = ""    #
        self.missingData = []          #
        self.missingParity = []        #
        self.listMaxDataBlock = -1
        self.listMaxParityBlock = -1
        self.inProcessData = []        # block currently being worked on
        self.inProcessParity = []      # block currently being worked on
        self.tryLaterData = []         # blocks we don't have enough online data to fix
        self.tryLaterParity = []       # blocks we don't have enough online data to fix
        self.maxBlockNo = -1
        self.listFilesTime = time.time()
        self.dprintAdjust = 0

    def IncomingSupplierListFiles(self, listFileText, currentMaxBlock=-1):
        #go through data from listFiles relevant to this backup
        self.listFilesTime = time.time()
        self.rawDataListFile = ""
        self.rawParityListFile = ""
        self.missingData = []
        self.missingParity = []
        self.tryLaterData = []
        self.tryLaterParity = []
        for line in listFileText.splitlines():
            if line.find(self.backupId) == 0 and line.find("-" + str(self.supplierNum) + "-") > 0:
                if line.find("-Data") > 0:
                    self.rawDataListFile = line
                if line.find("-Parity") > 0:
                    self.rawParityListFile = line
        self.listMaxDataBlock = self.GetLineMaxBlockNum(self.rawDataListFile)
        self.listMaxParityBlock  = self.GetLineMaxBlockNum(self.rawParityListFile)
        #dhnio.Dprint(8+self.dprintAdjust, "maxDataBlock-" + str(self.listMaxDataBlock) + ",maxParityBlock-" + str(self.listMaxParityBlock) + ",currentMaxBlock-" + str(currentMaxBlock))
        self.ApplyMaxBlockNo(currentMaxBlock)

    # this will give a "102/104" showing the "health" of the backup for this supplier
    def GetBackupStats(self):
        #dhnio.Dprint(12+self.dprintAdjust,"_BackupListFiles.GetBackupStats for backup Id " + self.backupId)
        totalBlocks = 2*(self.maxBlockNo+1)   # +1 since zero based and 2* because data and parity
        totalMissing = len(self.missingData) + len(self.missingParity) + len(self.tryLaterData) + len(self.tryLaterParity) + len(self.inProcessData) + len (self.inProcessParity)
        #return str(100*(totalBlocks-totalMissing)/totalBlocks) + '%'
        return '%d/%d' % (int(float(totalBlocks-totalMissing)/2.0), int(totalBlocks/2.0))

    # this will give a "102/104" showing the "health" of the backup for this supplier
    def GetBackupStatsInt(self):
        #dhnio.Dprint(12+self.dprintAdjust,"_BackupListFiles.GetBackupStats for backup Id " + self.backupId)
        totalBlocks = 2*(self.maxBlockNo+1)   # +1 since zero based and 2* because data and parity
        totalMissing = len(self.missingData) + len(self.missingParity) + len(self.tryLaterData) + len(self.tryLaterParity) + len(self.inProcessData) + len (self.inProcessParity)
        return 100*(totalBlocks-totalMissing)/totalBlocks

    # if we get a line "F20090709034221PM-0-Data from 0-1000"
    # or "F20090709034221PM-0-Data from 0-1000 missing 1,3,"
    # this will return 1000
    def GetLineMaxBlockNum(self, line):
        maxBlock = -1
        if line == "":
            return -1
        try:
            workLine = line
            if line.find(" missing ") > 0:
                workLine = line[0:line.find(" missing ")]
            lineMax = int(workLine[workLine.rfind("-")+1:])
            if lineMax > maxBlock:
                maxBlock = lineMax
            return maxBlock
        except:
            return -1

    def GetMissing(self, line, lineMax, backupMax):
        missingArray = []
        if line.find(" missing ") != -1:
            missingArray = line[line.find(" missing ")+9:].split(",")
        if "" in missingArray:
            missingArray.remove("")
        if backupMax > lineMax:
            intMissingArray = range(lineMax+1,backupMax+1)
            for i in intMissingArray:
                missingArray.append(str(i))
        return missingArray


    def ApplyMaxBlockNo(self, currentMaxBlock):
        self.maxBlockNo = max(self.listMaxDataBlock, self.listMaxParityBlock, currentMaxBlock)
        #dhnio.Dprint(8+self.dprintAdjust, "maxBlockNo " + str(self.maxBlockNo))
        self.missingData = self.GetMissing(self.rawDataListFile, self.listMaxDataBlock, self.maxBlockNo)
        self.missingParity = self.GetMissing(self.rawParityListFile, self.listMaxParityBlock, self.maxBlockNo)
        for inProcData in self.inProcessData:
            if inProcData in self.missingData:
                self.missingData.remove(inProcData)
        for inProcPar in self.inProcessParity:
            if inProcPar in self.missingParity:
                self.missingParity.remove(inProcPar)
        self.listMaxDataBlock = self.maxBlockNo
        self.listMaxParityBlock = self.maxBlockNo
        dhnio.Dprint(8+self.dprintAdjust, "backup_monitor.ApplyMaxBlockNo(%d) supplier %d  maxBlockNum is %d  missingData=%s missingParity=%s" % (
            currentMaxBlock, self.supplierNum, self.maxBlockNo, self.missingData, self.missingParity))


    def GetSupplierBlockAvailability(self, blockNum): 
        dataAvailable = 1
        parityAvailable = 1
        #dhnio.Dprint(8+self.dprintAdjust, "_SupplierBackupInfo.GetBlockAvailability backupId " + self.backupId + " blockNum " + str(blockNum) + " supplierNum " + str(self.supplierNum))
        if self.rawDataListFile == "" or str(blockNum) in self.missingData:
            dataAvailable = 0
        if self.rawParityListFile == "" or str(blockNum) in self.missingParity:
            parityAvailable = 0
        #dhnio.Dprint(8+self.dprintAdjust, "_SupplierBackupInfo.GetBlockAvailability = " + str(dataAvailable) + ", " + str(parityAvailable))
        return dataAvailable, parityAvailable


    def NextBlockToRepair(self): # returns a str
        #dhnio.Dprint(6+self.dprintAdjust, "NextBlockToRepair backupId " + self.backupId + ", supplierNum-" + str(self.supplierNum))
        #dhnio.Dprint(6+self.dprintAdjust, "len missingData-" + str(len(self.missingData)) + ", len missingParity-" + str(len(self.missingParity)))
        if len(self.missingData) > 0:
            if len(self.missingParity) > 0:
                #dhnio.Dprint(10+self.dprintAdjust, "min1=" + str(min(int(self.missingData[0]),int(self.missingParity[0]))))
                return str(min(int(self.missingData[0]), int(self.missingParity[0])))
            else:
                return self.missingData[0]
        elif len(self.missingParity) > 0:
            #dhnio.Dprint(10+self.dprintAdjust, "min2=" + str(self.missingParity[0]))
            return str(self.missingParity[0])
        else:
            return "-1"


    def WorkOnBlock(self, blockNo):
        if blockNo in self.missingData:
            self.inProcessData.append(blockNo)
            self.missingData.remove(blockNo)
        if blockNo in self.missingParity:
            self.inProcessParity.append(blockNo)
            self.missingParity.remove(blockNo)


    def BlockRebuildSuccess(self, blockNo, dataOrParity="all"):
        if dataOrParity.lower() != "parity":
            if blockNo in self.missingData:
                self.missingData.remove(blockNo)
            if blockNo in self.inProcessData:
                self.inProcessData.remove(blockNo)
        if dataOrParity.lower() != "data":
            if blockNo in self.missingParity:
                self.missingParity.remove(blockNo)
            if blockNo in self.inProcessParity:
                self.inProcessParity.remove(blockNo)


    # this is called when the rebuild gives up, 
    # too much time without progress
    def BlockRebuildFail(self, blockNo): 
        if blockNo in self.inProcessData:
            self.inProcessData.remove(blockNo)
            if blockNo not in self.missingData:
                self.missingData.append(blockNo)
        if blockNo in self.inProcessParity:
            self.inProcessParity.remove(blockNo)
            if blockNo not in self.missingParity:
                self.missingParity.append(blockNo)


    def BlockFixed(self, blockNo):
        if (blockNo not in self.inProcessData) and (blockNo not in self.inProcessParity):
            if (blockNo not in self.missingData) and (blockNo not in self.missingParity): 
                # should only be in inProcess stuff, but we'll check
                return True
        return False

    def HasRetryWork(self):
        if len(self.tryLaterData) > 0 or len(self.tryLaterParity)  > 0 :
            return True
        else:
            return False

    def TryLater(self, blockNo):
        if blockNo in self.inProcessData:
            self.inProcessData.remove(blockNo)
            self.tryLaterData.append(blockNo)
        if blockNo in self.inProcessParity:
            self.inProcessParity.remove(blockNo)
            self.tryLaterParity.append(blockNo)
        if blockNo in self.missingData:
            self.missingData.remove(blockNo)
            self.tryLaterData.append(blockNo)
        if blockNo in self.missingParity:
            self.missingParity.remove(blockNo)
            self.tryLaterParity.append(blockNo)

    def ResetTryLater(self): # all that is left is the stuff we couldn't work on before
        self.missingData = self.tryLaterData
        self.missingParity = self.tryLaterParity
        self.tryLaterData = []
        self.tryLaterParity = []

#------------------------------------------------------------------------------ 

class _BackupListFiles:
    def __init__(self, backupId, supplierSet, eccMap, 
                 StatusCallBackForGuiBackup = None, BackupStatusNotifyCallback = None):
        self.backupId = backupId
        self.supplierSet = supplierSet
        self.rawListFiles = {}    # only info for this backup, by supplier number
        self.maxblockNum = 0
        self.StatusCallBackForGuiBackup = StatusCallBackForGuiBackup
        self.BackupStatusNotifyCallback = BackupStatusNotifyCallback
        self.eccMap = eccMap
        self.dprintAdjust = 0

    # this will give a "102/104" per supplier, showing the "health" of the backup, so ["102/104","104/104"]
    def GetBackupStats(self):
        #dhnio.Dprint(12+self.dprintAdjust,"_BackupListFiles.GetBackupStats for backup Id " + self.backupId)
        backupStats = ['']*self.supplierSet.supplierCount
        for i in range(self.supplierSet.supplierCount):
            if self.rawListFiles.has_key(i):
                backupStats[i] = self.rawListFiles[i].GetBackupStats()
        return backupStats
    
    # much info we have versus how much we should have as a percent
    def GetBackupIdStats(self):
        #dhnio.Dprint(12+self.dprintAdjust,"_BackupListFiles.GetBackupIdStats for backup Id " + self.backupId)
        totPercent = 0
        for i in range(self.supplierSet.supplierCount):
            if self.rawListFiles.has_key(i):
                totPercent += self.rawListFiles[i].GetBackupStatsInt()
        return self.maxblockNum, totPercent/self.supplierSet.supplierCount

    def RemoveSupplierListFiles(self, supplierNum):
        if supplierNum in self.rawListFiles:
            del self.rawListFiles[supplierNum]

    def DisplayStats(self):
        backupStatus = self.GetBackupStats()
        if self.BackupStatusNotifyCallback != None:
            dhnio.Dprint(10+self.dprintAdjust,"_BackupListFiles.DisplayStats about to do callback ... ")
            self.BackupStatusNotifyCallback(self.backupId, backupStatus)
        else:
            for stats in backupStatus:
                dhnio.Dprint(12+self.dprintAdjust,"_BackupListFiles.DisplayStats display backupStats no gui " + str(stats))
        uniqueBackupStats = set(backupStatus) # remove duplicates
        # if more than 1 unique value 
        # means not everything is 100%, 
        # if only 1 and not 100% 
        # then everything has some message
        if len(uniqueBackupStats)>1 or ("100%" not in uniqueBackupStats):
            if self.StatusCallBackForGuiBackup != None:
                # only most recent backup for a directory shown, 
                # so many of these won't show
                self.StatusCallBackForGuiBackup(self.backupId, 'rebuilding') 
            else: 
                # no gui, but should report
                dhnio.Dprint(8+self.dprintAdjust, "_BackupListFiles.DisplayStats  backup " + self.backupId + "is rebuilding")
        else:
            if self.StatusCallBackForGuiBackup != None:
                 # we're going to try to set the status on all backups, 
                 # but only most recent is shown on guibackup
                self.StatusCallBackForGuiBackup(self.backupId, 'done') 
            else: # no gui, but should report
                dhnio.Dprint(8, "_BackupListFiles.DisplayStats  backup " + self.backupId + "is whole")

    def IncomingBackupListFiles(self, supplierNum, supplierId, listFileText):
        if not self.rawListFiles.has_key(supplierNum):
            self.rawListFiles[supplierNum] = _SupplierBackupInfo(self.backupId, supplierNum, supplierId)
        self.rawListFiles[supplierNum].IncomingSupplierListFiles(listFileText, self.maxblockNum)
        if self.rawListFiles[supplierNum].maxBlockNo > self.maxblockNum:
            self.maxblockNum = self.rawListFiles[supplierNum].maxBlockNo
            for suppNo in self.rawListFiles.keys():
                if suppNo != supplierNum:
                    self.rawListFiles[suppNo].ApplyMaxBlockNo(self.maxblockNum)

    def ReportFixed(self, blockId, supplierNum, dataOrParity):
        if supplierNum in self.rawListFiles:
            self.rawListFiles[supplierNum].BlockRebuildSuccess(blockId, dataOrParity)
            self.DisplayStats()

    def ReportNotFixed(self, blockId, supplierNum, dataOrParity):
        if supplierNum in self.rawListFiles:
            self.rawListFiles[supplierNum].BlockRebuildFail(blockId)

    def UpdateAvailable(self, availableInfo, activeArray, doMaybe = False):
        newAvailable = [0]*len(availableInfo)
        for i in range(len(availableInfo)):
            newAvailable = (availableInfo[i] and activeArray[i])
        return newAvailable

    # this handles the situation of a supplier offline 
    # so "maybe" there is still data out there, 
    # so don't give up hope
    def BlockRebuildPossible(self, blockNum): 
        supplierCount = self.supplierSet.supplierCount
        availableData = [1]*supplierCount
        availableParity = [1]*supplierCount
        for i in range(supplierCount):
            if self.rawListFiles.has_key(i):
                availableData[i], availableParity[i] = self.rawListFiles[i].GetSupplierBlockAvailability(blockNum)
        return self.eccMap.Fixable(availableData, availableParity)

    def GetBlockAvailability(self, blockNum):
        supplierCount = self.supplierSet.supplierCount
        supplierActiveArray = self.supplierSet.GetActiveArray()
        #dhnio.Dprint(8+self.dprintAdjust, "_BackupListFiles.GetBlockAvailability supplierActiveArray " + str(supplierActiveArray))
        availableData = [0]*supplierCount
        availableParity = [0]*supplierCount
        for i in range(supplierCount):
            if self.rawListFiles.has_key(i):
                #dhnio.Dprint(14+self.dprintAdjust, "_BackupListFiles.GetBlockAvailability has key for supplier " + str(i))
                availableData[i], availableParity[i] = self.rawListFiles[i].GetSupplierBlockAvailability(blockNum)
                availableData[i] = (availableData[i] and supplierActiveArray[i])
                availableParity[i] = (availableParity[i] and supplierActiveArray[i])
        return availableData, availableParity

#    def GetNextMissingBlock(self):
#        minBlockNo = -1
#        supplierActiveArray = self.supplierSet.GetActiveArray()
#        for supplierNum in self.rawListFiles.keys():
#            if supplierActiveArray[supplierNum] == 1:
#                #dhnio.Dprint(6+self.dprintAdjust, "_BackupListFiles.GetNextMissingBlock about to get next block")
#                blockNo = self.rawListFiles[supplierNum].NextBlockToRepair()
#                #dhnio.Dprint(6+self.dprintAdjust, "_BackupListFiles.GetNextMissingBlock " + str(blockNo))
#                if minBlockNo == -1:
#                    #dhnio.Dprint(6+self.dprintAdjust, "_BackupListFiles.GetNextMissingBlock new min" + str(blockNo))
#                    minBlockNo = int(blockNo)
#                    #dhnio.Dprint(6+self.dprintAdjust, "_BackupListFiles.GetNextMissingBlock new min" + str(blockNo))
#                elif int(blockNo) != -1 and int(blockNo) < minBlockNo:
#                    #dhnio.Dprint(6+self.dprintAdjust, "_BackupListFiles.GetNextMissingBlock new min2" + str(blockNo))
#                    minBlockNo = int(blockNo)
#                    #dhnio.Dprint(6+self.dprintAdjust, "_BackupListFiles.GetNextMissingBlock new min2" + str(blockNo))
#        dhnio.Dprint(6+self.dprintAdjust, "backup_monitor.GetNextMissingBlock returned %d" % minBlockNo)
#        return minBlockNo

#    def IdentifyOnHandData(self, backupId, blockNum):
#        supplierCount = self.supplierSet.supplierCount
#        onHandData = [0] * supplierCount
#        onHandParity = [0] * supplierCount
#        dirList = os.listdir(tmpfile.subdir('data-par'))
#        for fileName in dirList:
#            # file from this backup and block that we're dealing with
#            if fileName.find(backupId + "-" + blockNum + "-") == 0: 
#                try:
#                    # F20090625010647PM-368-0-Data - should grab 0
#                    segmentNumber = int((fileName.split("-"))[2])              
#                    if fileName.endswith("-Data"):
#                        onHandData[segmentNumber] = 1
#                    elif fileName.endswith("-Parity"):
#                        onHandParity[segmentNumber] = 1
#                except:
#                    dhnio.Dprint(2, "_BackupListFiles.IdentifyOnHandData exception fileName=" + fileName + ", supplierCount=" + str(supplierCount))
#                    dhnio.DprintException()
#        return onHandData, onHandParity

    def IdentifyWorkableMissing(self, availableData, availableParity): # workable missing being someone online.
        supplierCount = self.supplierSet.supplierCount
        supplierActiveArray = self.supplierSet.GetActiveArray()
        missingData = [0] * supplierCount
        missingParity = [0] * supplierCount
        for i in range(0,supplierCount):
            if availableData[i] == 0 and supplierActiveArray[i] == 1:
                missingData[i] = 1
            if availableParity[i] == 0 and supplierActiveArray[i] == 1:
                missingParity[i] = 1
        return missingData, missingParity

    def TryLater(self, blockNo):
        for supplierNum in self.rawListFiles.keys():
            self.rawListFiles[supplierNum].TryLater(blockNo)

    def WorkOnBlock(self, blockNo):
        for supplierNum in self.rawListFiles.keys():
            self.rawListFiles[supplierNum].WorkOnBlock(blockNo)

    def HasRetryWork(self):
        for supplierNum in self.rawListFiles.keys():
            if self.rawListFiles[supplierNum].HasRetryWork():
                return True
        return False

    def ResetTryLater(self):
        for supplierNum in self.rawListFiles.keys():
            self.rawListFiles[supplierNum].ResetTryLater()

#------------------------------------------------------------------------------ 

class _BlockRebuilder(Automat):
    timers = {#'timer-1min':     (60*1,  ['SENDING']), 
              'timer-1min':     (60*1,  ['REQUEST_FILES',]),
              'timer-1sec':     (1,     ['REQUEST_FILES', 'SENDING']),}
    
    def __init__(self,  eccMap, backupID, blockNum, supplierSet, 
                        remoteData, remoteParity,
                        localData, localParity, 
                        creatorId = None, ownerId = None):
        self.eccMap = eccMap
        self.backupID = backupID
        self.blockNum = blockNum
        self.supplierSet = supplierSet
        self.supplierCount = len(self.supplierSet.suppliers)
        self.remoteData = remoteData
        self.remoteParity = remoteParity
        self.localData = localData
        self.localParity = localParity
        self.creatorId = creatorId
        self.ownerId = ownerId
        # at some point we may be dealing with when we're scrubbers
        if self.creatorId == None:
            self.creatorId = misc.getLocalID()
        if self.ownerId == None:
            self.ownerId = misc.getLocalID()
        # this files we want to rebuild
        # need to identify which files to work on
        self.missingData = [0] * self.supplierCount
        self.missingParity = [0] * self.supplierCount
        # list of packets ID we requested
        self.requestFilesList = []
        # list of files to be send
        self.outstandingFilesList = []
        # time when we start sending files
        self.sendingStartedTime = 0
        # timeout to send a single file to supplier
        self.timeoutSending = int(settings.PacketSizeTarget() / settings.SendingSpeedLimit())
        # 1 if we sent a Data file to single supplier, 2 if get Ack from him, 3 if it was failed   
        self.dataSent = [0] * self.supplierCount
        # same for Parity files
        self.paritySent = [0] * self.supplierCount
        self.dprintAdjust = 0
        dhnio.Dprint(8+self.dprintAdjust, 'backup_monitor._BlockRebuilder blockNum=%s remote:{%s %s} local:{%s %s}' % (self.blockNum, self.remoteData, self.remoteParity, self.localData, self.localParity))
        Automat.__init__(self, 'block_rebuilder', 'AT_STARTUP', 6)
        
    def state_changed(self, oldstate, newstate):
        monitor().automat('block_rebuilder.state', newstate)
    
    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'start':
                self.doIdentifyMissingFiles()
                self.state = 'IDENTIFY_MISSING'
        #---IDENTIFY_MISSING---
        elif self.state == 'IDENTIFY_MISSING':
            if event == 'missing-files-identified' and not self.isMissingFilesOnHand():
                self.doRequestMissingFiles()
                self.state = 'REQUEST_FILES'
            elif event == 'missing-files-identified' and self.isMissingFilesOnHand():
                self.doRebuild()
                self.state = 'REBUILDING'
        #---REQUEST_FILES---
        elif self.state == 'REQUEST_FILES':
            if event == self.isUpdated() and (event == 'timer-1min' or (event == 'file-received' and self.isAllFilesReceived())):
                self.doRebuild()
                self.state = 'REBUILDING'
            elif event == 'timer-1sec' and not self.isUpdated():
                self.doDestroyMe()
                self.state = 'STOPPED'
        #---REBUILDING---
        elif self.state == 'REBUILDING':
            if event == 'rebuilding-finished' and self.isOutstandingFiles():
                self.doSendOutstandingFiles()
                self.state = 'SENDING'
            elif event == 'rebuilding-finished' and not self.isOutstandingFiles():
                self.doDestroyMe()
                self.state = 'FINISHED'
        #--SENDING---
        elif self.state == 'SENDING':
            if event == 'file-sent-report' and self.isAllFilesSent():
                self.doWorkDoneReport()
                self.doDestroyMe()
                self.state = 'DONE'
            elif event == 'timer-1sec' and not self.isUpdated():
                self.doWorkDoneReport()
                self.doDestroyMe()
                self.state = 'STOPPED'
            elif event == 'timer-1sec' and self.isTimeoutSending():
                self.doWorkDoneReport()
                self.doDestroyMe()
                self.state = 'FINISHED'
        #---FINISHED---
        elif self.state == 'FINISHED':
            pass
        #---STOPPED---
        elif self.state == 'STOPPED':
            pass
        #---DONE---
        elif self.state == 'DONE':
            pass
        
    def isUpdated(self):
        return monitor().updated
    
    def isMissingFilesOnHand(self):
        for supplierNum in range(self.supplierCount):
            # if supplier do not have the Data but is on line 
            if self.missingData[supplierNum] == 1:
                # ... and we also do not have the Data 
                if self.localData[supplierNum] != 1:
                    # return False - will need request the file   
                    return False
            # same for Parity                
            if self.missingParity[supplierNum] == 1:
                if self.localParity[supplierNum] != 1:
                    return False
        dhnio.Dprint(self.dprintAdjust+8, 'backup_monitor.isMissingFilesOnHand return True')
        return True
        
    def isAllFilesReceived(self):
        return len(self.requestFilesList) == 0
    
    def isAllFilesSent(self):
        return (1 not in self.dataSent) and (1 not in self.paritySent)
    
    def isOutstandingFiles(self):
        return len(self.outstandingFilesList) > 0
    
    def isTimeoutSending(self):
        return time.time() - self.sendingStartedTime > self.timeoutSending
    
    def doIdentifyMissingFiles(self):
        def do_identify():
            self.availableSuppliers = self.supplierSet.GetActiveArray()
            for supplierNum in range(self.supplierCount):
                if self.availableSuppliers[supplierNum] == 0:
                    continue
                # if remote Data file not exist and supplier is online
                # we mark it as missing and will try to rebuild this file and send to him
                if self.remoteData[supplierNum] != 1:
                    # mark file as missing  
                    self.missingData[supplierNum] = 1
                # same for Parity file
                if self.remoteParity[supplierNum] != 1:
                    self.missingParity[supplierNum] = 1
            return True
        maybeDeferred(do_identify).addCallback(
            lambda x: self.automat('missing-files-identified'))
        
    def doRequestMissingFiles(self):
        self.availableSuppliers = self.supplierSet.GetActiveArray()
        # at the moment I'm download
        # everything I have available and needed
        for supplierNum in range(self.supplierCount):
            # if supplier is not alive - we can't request from him           
            if self.availableSuppliers[supplierNum] == 0:
                continue
            supplierID = self.supplierSet.suppliers[supplierNum]      
            # if the remote Data exist and is available because supplier is on line,
            # but we do not have it on hand - do request  
            if self.remoteData[supplierNum] == 1 and self.localData[supplierNum] == 0:
                PacketID = self.BuildFileName(supplierNum, 'Data')
                io_throttle.QueueRequestFile(self.FileReceived, misc.getLocalID(), PacketID, self.ownerId, supplierID)
                self.requestFilesList.append(PacketID)
            # same for Parity
            if self.remoteParity[supplierNum] == 1 and self.localParity[supplierNum] == 0:
                PacketID = self.BuildFileName(supplierNum, 'Parity')
                io_throttle.QueueRequestFile(self.FileReceived, misc.getLocalID(), PacketID, self.ownerId, supplierID)
                self.requestFilesList.append(PacketID)
        
    def doRebuild(self):
#        threads.deferToThread(self.AttemptRepair).addCallback(
#            lambda x: self.automat('rebuilding-thread-finished'))
        maybeDeferred(self.AttemptRebuild).addCallback(
            lambda x: self.automat('rebuilding-finished'))
        
    def doSendOutstandingFiles(self):
        for FileName, PacketID, supplierNum in self.outstandingFilesList:
            self.SendFile(FileName, PacketID, supplierNum)
        del self.outstandingFilesList
        self.outstandingFilesList = [] 
        self.sendingStartedTime = time.time()

    def doDestroyMe(self):
        reactor.callLater(0, monitor().RemoveRebuilder, self)
    
    def doWorkDoneReport(self):
        monitor().RebuildReport(self.backupID, self.blockNum, self.remoteData, self.remoteParity) 

    #------------------------------------------------------------------------------ 

    def HaveAllData(self, parityMap):
        for segment in parityMap:
            if self.localData[segment] == 0:
                return False
        return True


    def AttemptRebuild(self):
        #dhnio.Dprint(self.dprintAdjust+6, 'backup_monitor.AttemptRepair BEGIN')
        madeProgress = True
        while madeProgress:
            madeProgress = False
            # will check all data packets we have 
            for supplierNum in range(self.supplierCount):
                dataFileName = self.BuildRaidFileName(supplierNum, 'Data')
                # if we do not have this item on hands - we will reconstruct it from other items 
                if self.localData[supplierNum] == 0:
                    parityNum, parityMap = self.eccMap.GetDataFixPath(self.localData, self.localParity, supplierNum)
                    if parityNum != -1:
                        rebuildFileList = []
                        rebuildFileList.append(self.BuildRaidFileName(parityNum, 'Parity'))
                        for supplierParity in parityMap:
                            if supplierParity != supplierNum:
                                rebuildFileList.append(self.BuildRaidFileName(supplierParity, 'Data'))
                        raidread.RebuildOne(rebuildFileList, len(rebuildFileList), dataFileName)
                    #send the rebuilt file back, set the missing to zero
                    if os.path.exists(dataFileName):
                        self.localData[supplierNum] = 1
                        madeProgress = True
                        dhnio.Dprint(8+self.dprintAdjust, 'backup_monitor.AttemptRebuild made progress with supplier %d' % supplierNum)
                # now we check again if we have the data on hand after rebuild at it is missing - send it            
                if self.localData[supplierNum] == 1 and self.missingData[supplierNum] == 1:
                    dhnio.Dprint(8+self.dprintAdjust, "backup_monitor.AttemptRebuild new outstanding Data for supplier %d" % supplierNum)
                    self.outstandingFilesList.append((dataFileName, self.BuildFileName(supplierNum, 'Data'), supplierNum))
                    self.dataSent[supplierNum] = 1
        # now with parities ...            
        for supplierNum in range(self.supplierCount):
            parityFileName = self.BuildRaidFileName(supplierNum, 'Parity')
            if self.localParity[supplierNum] == 0:
                parityMap = self.eccMap.ParityToData[supplierNum]
                if self.HaveAllData(parityMap):
                    rebuildFileList = []
                    for supplierParity in parityMap:
                        rebuildFileList.append(self.BuildRaidFileName(supplierParity, 'Data'))
                    raidread.RebuildOne(rebuildFileList, len(rebuildFileList), parityFileName)
                    if os.path.exists(parityFileName):
                        dhnio.Dprint(8+self.dprintAdjust, 'backup_monitor.AttemptRebuild parity file found after rebuilding for supplier %d' % supplierNum)
                        self.localParity[supplierNum] = 1
            # so we have the parity on hand and it is missing - send it
            if self.localParity[supplierNum] == 1 and self.missingParity[supplierNum] == 1:
                dhnio.Dprint(8+self.dprintAdjust, "backup_monitor.AttemptRebuild new outstanding Parity for supplier %d" % supplierNum)
                self.outstandingFilesList.append((parityFileName, self.BuildFileName(supplierNum, 'Parity'), supplierNum))
                self.paritySent[supplierNum] = 1
        return True


    def SendFile(self, FileName, PacketID, supplierNum):
        io_throttle.QueueSendFile(FileName, 
                                  PacketID, 
                                  self.supplierSet.suppliers[supplierNum], 
                                  self.ownerId, 
                                  self.SendFileAcked, 
                                  self.SendFileFailed,)
        dhnio.Dprint(8+self.dprintAdjust, "backup_monitor.SendFile to supplier %d" % supplierNum)


    def SendFileAcked(self, packet, remoteID, packetID):
        dhnio.Dprint(8+self.dprintAdjust, 'backup_monitor.SendFileAcked to %s with %s' % (nameurl.GetName(remoteID), packetID))
        try:
            backupID, blockNum, supplierNum, dataORparity = packetID.split("-")
            blockNum = int(blockNum)
            supplierNum = int(supplierNum)
            if dataORparity == 'Data':
                self.missingData[supplierNum] = 0
                self.remoteData[supplierNum] = 1
                self.dataSent[supplierNum] = 2
            elif dataORparity == 'Parity':
                self.missingParity[supplierNum] = 0
                self.remoteParity[supplierNum] = 1
                self.paritySent[supplierNum] = 2
            else:
                dhnio.Dprint(8+self.dprintAdjust, "backup_monitor.SendFileAcked WARNING odd PacketID? -" + str(packetID))
        except:
            dhnio.DprintException()
        self.automat('file-sent-report')


    def SendFileFailed(self, creatorID, packetID):
        dhnio.Dprint(8+self.dprintAdjust, 'backup_monitor.SendFileFailed to %s with %s' % (nameurl.GetName(creatorID), packetID))
        try:
            backupID, blockNum, supplierNum, dataORparity = packetID.split("-")
            blockNum = int(blockNum)
            supplierNum = int(supplierNum)
            if dataORparity == 'Data':
                self.missingData[supplierNum] = 1
                self.remoteData[supplierNum] = 0
                self.dataSent[supplierNum] = 3
            elif dataORparity == 'Parity':
                self.missingParity[supplierNum] = 1
                self.remoteParity[supplierNum] = 0
                self.paritySent[supplierNum] = 3
            else:
                dhnio.Dprint(8+self.dprintAdjust, "backup_monitor.SendFileFailed WARNING odd PacketID? -" + str(packetID))
        except:
            dhnio.DprintException()
        self.automat('file-sent-report')


    def FileReceived(self, packet):
        self.requestFilesList.remove(packet.PacketID)
        filename = os.path.join(tmpfile.subdir('data-par'), packet.PacketID)
        if packet.Valid():
            dhnio.Dprint(8+self.dprintAdjust, "backup_monitor.FileReceived %s,  requestFilesList=%s" % (packet.PacketID, self.requestFilesList))
            # if we managed to rebuild a file 
            # before a request came in don't overwrite it
            if os.path.exists(filename):
                dhnio.Dprint(4+self.dprintAdjust, "backup_monitor.FileReceived WARNING file already existed " + filename)
                try: 
                    os.remove(filename)
                except:
                    dhnio.DprintException()
            dhnio.WriteFile(filename, packet.Payload)
            try: 
                supplierNum = int((packet.PacketID.split("-"))[2])
                if packet.PacketID.endswith("-Data"):
                    self.localData[supplierNum] = 1
                elif packet.PacketID.endswith("-Parity"):
                    self.localParity[supplierNum] = 1
            except:
                dhnio.DprintException()              
        else:
            # TODO 
            # if we didn't get a valid packet ... re-request it or delete it?
            dhnio.Dprint(8+self.dprintAdjust, "backup_monitor.FileReceived WARNING" + filename + " not valid")
            try: 
                os.remove(filename)
            except:
                dhnio.DprintException()
            #io_throttle.QueueRequestFile(self.FileReceived, misc.getLocalID(), packet.PacketID, self.ownerId, packet.RemoteID)


    def BuildRaidFileName(self, supplierNumber, dataOrParity):
        return os.path.join(tmpfile.subdir('data-par'), self.BuildFileName(supplierNumber, dataOrParity))


    def BuildFileName(self, supplierNumber, dataOrParity):
        return self.backupID + "-" + str(self.blockNum) + "-" + str(supplierNumber) + "-" + dataOrParity

#------------------------------------------------------------------------------ 

class _BackupMonitor(Automat):
    timers = {'timer-1hour':    (60*60, ['RUN']), 
              'timer-20sec':    (20,    ['LIST_FILES']),
              'timer-1sec':     (1,     ['RUN']),
              'timer-01sec':    (0.1,   ['NEXT_BLOCK', 'NEXT_BACKUP']), }

    def __init__(self):
        self.dprintAdjust = 0
        self.requestedListFilesPacketIDs = set()
        self.backupIDsQueue = []                # list of backup ids to work on
        self.currentBackupID = None             # currently working on this backup
        self.currentBlockNumber = -1            # currently working on this block
        self.workingBlocksQueue = []            # list of missing blocks we work on for current backup 
        self.queueBlockRebuilders = []          # list of BlockRebuilder objects 
        #self.currentBlockRebuilder = None       # instance of _BlockRebuilder which is working at the moment
        self.maxBlockRebuilderQueueLength = 1   # TODO - need to sort out what is an appropriate length
        self.rebuildWasSuccess = False          # if we did some rebuilds successfully (sent any files)
                                                # we want to request all ListFiles again on next iteration 
        self.updated = False                    # set to False and backup_monitor will stop working and go to state RUN
        self.updatedBackupIDs = set()           # add backupID here and GUI will be notified to update it 
        self.myID = misc.getLocalID()
        self.eccMap = None
        self.mySupplierSet = _SuppliersSet(contacts.getSupplierIDs())
        self.backupsInProcess = []              # currently working backups (started from dobackup.py)
        self.remoteFiles = {}                   # 0 or 1 indexed by [backupID][blockNum]['D' or 'P'][supplierNum]
        self.remoteMaxBlockNumbers = {}         # max block number for every remote backup ID
        self.localFiles = {}                    # same for local files    
        self.localMaxBlockNumbers = {}          # also block numbers
        self.localBackupsSize = {}

        self.BackupStatusNotifyCallback = None
        self.StatusCallBackForGuiBackup = None
        reactor.callLater(2, self.RepaintingProcess)

        Automat.__init__(self, 'backup_monitor', 'AT_STARTUP', self.dprintAdjust + 6)
        
    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'start':
                self.doRequestListFiles()
                self.state = 'LIST_FILES'
        #---LIST_FILES---
        elif self.state == 'LIST_FILES':
            if event == 'timer-20sec' or (event == 'incomming-list-files' and self.isAllFilesReceived()):
                self.doReadLocalFiles()
                self.doGetBackups()
                self.doUpdate()
                self.doUnmarkResult()
                self.state = 'RUN'
        #---RUN---
        elif self.state == 'RUN':
            if event == 'timer-1sec' and self.isUpdated() and self.isMoreBackups():
                self.state = 'NEXT_BACKUP'
            elif (event == 'timer-1sec' and ( self.isResultSuccess() or not self.isUpdated() ) ) or event == 'timer-1hour':
                self.doRequestListFiles()
                self.state = 'LIST_FILES'
        #---NEXT_BACKUP---
        elif self.state == 'NEXT_BACKUP':
            if event == 'timer-01sec' and self.isUpdated() and self.isMoreBackups():
                self.doTakeNextBackup()
                self.doTakeNextBlock() 
                self.state = 'NEXT_BLOCK'
            elif event == 'timer-01sec' and ( not self.isMoreBackups() or not self.isUpdated() ):
                self.state = 'RUN'
        #---NEXT_BLOCK---
        elif self.state == 'NEXT_BLOCK':
            if event == 'timer-01sec' and self.isUpdated() and self.isMoreBlocks() and self.isSpaceForNewRebuilder():
                self.doCreateNewRebuilder('start')
                self.state = 'REBUILDING'
            elif event == 'timer-01sec' and ( ( not self.isMoreBackups() and not self.isMoreBlocks() ) or not self.isUpdated() ):
                self.state = 'RUN'
            elif event == 'timer-01sec' and self.isUpdated() and not self.isMoreBlocks() and self.isMoreBackups():
                self.state = 'NEXT_BACKUP'
        #---REBUILDING---
        elif self.state == 'REBUILDING':
            if event == 'block_rebuilder.state' and arg in ['FINISHED', 'STOPPED', 'DONE']:
                self.doTakeNextBlock()
                self.doMarkResult(arg)
                self.state = 'NEXT_BLOCK'

    def isUpdated(self):
        return self.updated

    def isResultSuccess(self):
        return self.rebuildWasSuccess

    def isAllFilesReceived(self):
        dhnio.Dprint(6+self.dprintAdjust, 'backup_monitor.isAllFilesReceived %s' % self.requestedListFilesPacketIDs)
        return len(self.requestedListFilesPacketIDs) == 0

    def isMoreBackups(self):
        return len(self.backupIDsQueue) > 0
    
    def isMoreBlocks(self):
        # because started from 0,  -1 means not found 
        return self.currentBlockNumber > -1 
    
    def isSpaceForNewRebuilder(self):
        return len(self.queueBlockRebuilders) < self.maxBlockRebuilderQueueLength

    def doRequestListFiles(self):
        self.RequestListFiles()

    def doReadLocalFiles(self):
        self.ReadLocalFiles()

    def doUpdate(self):
        self.updated = True
        if self.eccMap is None:
            self.eccMap = eccmap.Current()
            
    def doUnmarkResult(self):
        self.rebuildWasSuccess = False
        
    def doMarkResult(self, arg):
        if arg == 'DONE':
            self.rebuildWasSuccess = True
        
    def doGetBackups(self):
        # take remote and local backups and get union from it 
        allBackupIDs = set(self.localFiles.keys() + self.remoteFiles.keys())
        # take only backups from data base
        allBackupIDs.intersection_update(backup_db.GetBackupIds())
        # remove running backups
        allBackupIDs.difference_update(self.backupsInProcess)
        # sort it in reverse order - newer backups should be repaired first
        allBackupIDs = misc.sorted_backup_ids(list(allBackupIDs), True)
        # add backups to the queue
        self.backupIDsQueue.extend(allBackupIDs)

    def doTakeNextBackup(self):
        # take a first backup from queue to work on it
        backupID = self.backupIDsQueue.pop(0)
        # if remote data structure is not exist for this backup - create it
        # this mean this is only local backup!
        if not self.remoteFiles.has_key(backupID):
            self.remoteFiles[backupID] = {}
            # we create empty remote info for every local block
            # range(0) should return []
            for blockNum in range(self.localMaxBlockNumbers.get(backupID, -1) + 1):
                self.remoteFiles[backupID][blockNum] = {
                    'D': [0] * self.mySupplierSet.supplierCount,
                    'P': [0] * self.mySupplierSet.supplierCount }
        # clear blocks queue from previous iteration
        self.currentBlockNumber = -1
        del self.workingBlocksQueue 
        # detect missing blocks from remote info
        self.workingBlocksQueue = self.ScanMissingBlocks(backupID)
        # find the correct max block number for this backup
        # we can have remote and local files
        # will take biggest block number from both 
        backupMaxBlock = max(self.remoteMaxBlockNumbers.get(backupID, -1),
                             self.localMaxBlockNumbers.get(backupID, -1))
        # now need to remember this biggest block number
        # remote info may have less blocks - need to create empty info for missing blocks
        for blockNum in range(backupMaxBlock + 1):
            if self.remoteFiles[backupID].has_key(blockNum):
                continue
            self.remoteFiles[backupID][blockNum] = {
                'D': [0] * self.mySupplierSet.supplierCount,
                'P': [0] * self.mySupplierSet.supplierCount }
        # really take next backup
        self.currentBackupID = backupID
        
       
    def doTakeNextBlock(self):
        if len(self.workingBlocksQueue) > 0:
            # self.currentBlockNumber = self.workingBlocksQueue.pop(0)
            # let's take last blocks first ... 
            # such way we can propagate how big is whole backup as soon as possible!
            # remote machine can multiply [file size] * [block number] 
            # and calculate the whole size to be received ... smart!
            # ... remote supplier should not use last file to calculate
            self.currentBlockNumber = self.workingBlocksQueue.pop()
        else:
            self.currentBlockNumber = -1

    def doCreateNewRebuilder(self, arg):
        remoteData = self.GetRemoteDataArray(self.currentBackupID, self.currentBlockNumber)
        remoteParity = self.GetRemoteParityArray(self.currentBackupID, self.currentBlockNumber)
        localData = self.GetLocalDataArray(self.currentBackupID, self.currentBlockNumber)
        localParity = self.GetLocalParityArray(self.currentBackupID, self.currentBlockNumber)
        rebuilder = _BlockRebuilder(
            self.eccMap, self.currentBackupID, self.currentBlockNumber,
            self.mySupplierSet,
            remoteData, remoteParity,
            localData, localParity,)
        self.queueBlockRebuilders.append(rebuilder)    
        rebuilder.automat(arg)
#        dhnio.Dprint(8+self.dprintAdjust, 'backup_monitor.doCreateNewRebuilder for %s blockNum=%s refcount=%d' % ( 
#                     self.currentBackupID, self.currentBlockNumber, sys.getrefcount(_BlockRebuilder)))
        
        
#    def doForgetCurrentRebuilder(self):
#        self.currentBlockRebuilder = None

    #------------------------------------------------------------------------------ 

    def NoteToUpdate(self):
        dhnio.Dprint(4+self.dprintAdjust, 'backup_monitor.NoteToUpdate')
        self.updated = False


    def RemoveRebuilder(self, block_rebuilder):
        self.queueBlockRebuilders.remove(block_rebuilder)


    def RequestListFiles(self):
        self.requestedListFilesPacketIDs.clear()
        for idurl in contacts.getSupplierIDs():
            if contacts_status.isOnline(idurl):
                customerservice.RequestListFiles(idurl)
                self.requestedListFilesPacketIDs.add(idurl)


    def IncomingListFiles(self, supplierNum, packet, listFileText):
        supplierIdentity = packet.OwnerID
        self.requestedListFilesPacketIDs.discard(supplierIdentity)
        dhnio.Dprint(8+self.dprintAdjust, "backup_monitor.IncomingListFiles for supplier %d other requests: %s" % (supplierNum, self.requestedListFilesPacketIDs))

        if supplierNum >= self.mySupplierSet.supplierCount:
            dhnio.Dprint(2+self.dprintAdjust, 'backup_monitor.IncomingListFiles WARNING incorrect supplier number %d, number of suppliers is %d' % (supplierNum, self.mySupplierSet.supplierCount))
            return
        
        if self.eccMap is None:
            self.eccMap = eccmap.Current()

        # new code            
        # examples:
        # F20090709034221PM-0-Data from 0-1000
        # F20090709034221PM-0-Data from 0-1000 missing 1,3,
        for line in listFileText.splitlines():
            line = line.strip()
            # comment lines in Files reports start with blank,
            if line == '':
                continue
            # also don't consider the identity a backup,
            if line == supplierIdentity:
                continue
            # nor the backup_info.xml
            if line == settings.BackupInfoFileName():
                continue
            words = line.split(' ')
            # minimum is 3 words: "F20090709034221PM-0-Data", "from", "0-1000"
            if len(words) < 3:
                dhnio.Dprint(2+self.dprintAdjust, 'backup_monitor.IncomingListFiles WARNING incorrect line:[%s]' % line)
                continue
            try:
                backupID, lineSupplierNum, dataORparity = words[0].split('-')
                minBlockNum, maxBlockNum = words[2].split('-')
                lineSupplierNum = int(lineSupplierNum)
                maxBlockNum = int(maxBlockNum)
            except:
                dhnio.Dprint(2+self.dprintAdjust, 'backup_monitor.IncomingListFiles WARNING incorrect line:[%s]' % line)
                continue
            if lineSupplierNum != supplierNum:
                # this mean supplier have old files and we do not need it 
                # TODO what to do...  remove the files? Send "DeleteFile" packet?
                continue
            if backupID == '':
                dhnio.Dprint(2+self.dprintAdjust, 'backup_monitor.IncomingListFiles WARNING incorrect line:[%s]' % line)
                continue
            if dataORparity not in ['Data', 'Parity']:
                dhnio.Dprint(2+self.dprintAdjust, 'backup_monitor.IncomingListFiles WARNING incorrect line:[%s]' % line)
                continue
            missingBlocksSet = set()
            if len(words) ==  5:
                if words[3].strip() != 'missing':
                    dhnio.Dprint(2+self.dprintAdjust, 'backup_monitor.IncomingListFiles WARNING incorrect line:[%s]' % line)
                    continue
                missingBlocksSet = set(words[4].split(','))
            if not self.remoteFiles.has_key(backupID):
                self.remoteFiles[backupID] = {}
            # +1 because range(2) give us [0,1] but we want [0,1,2]
            for blockNum in range(maxBlockNum+1):
                if not self.remoteFiles[backupID].has_key(blockNum):
                    self.remoteFiles[backupID][blockNum] = {
                        'D': [0] * self.mySupplierSet.supplierCount,
                        'P': [0] * self.mySupplierSet.supplierCount,}
                # we set -1 if the file is missing and 1 if exist, so 0 mean "no info yet" ... smart!
                bit = -1 if str(blockNum) in missingBlocksSet else 1 
                if dataORparity == 'Data':
                    self.remoteFiles[backupID][blockNum]['D'][supplierNum] = bit
                elif dataORparity == 'Parity':
                    self.remoteFiles[backupID][blockNum]['P'][supplierNum] = bit
            # save max block number for this backup
            if not self.remoteMaxBlockNumbers.has_key(backupID):
                self.remoteMaxBlockNumbers[backupID] = -1 
            if maxBlockNum > self.remoteMaxBlockNumbers[backupID]:
                self.remoteMaxBlockNumbers[backupID] = maxBlockNum
            # mark this backup to be repainted
            self.updatedBackupIDs.add(backupID)
                
#        import pprint
#        pprint.pprint(self.remoteFiles)
                
        self.automat('incomming-list-files') 


    def RebuildReport(self, backupID, blockNum, remoteData, remoteParity):
        if not self.updated:
            return
        if not self.remoteFiles.has_key(backupID):
            self.remoteFiles[backupID] = {}
        if not self.remoteFiles[backupID].has_key(blockNum):
            self.remoteFiles[backupID][blockNum] = {
                'D': [0] * self.mySupplierSet.supplierCount,
                'P': [0] * self.mySupplierSet.supplierCount,}
        # save reconstructed block info into remote info structure, synchronize
        for supplierNum in range(self.mySupplierSet.supplierCount):
            self.remoteFiles[backupID][blockNum]['D'][supplierNum] = remoteData[supplierNum]
            self.remoteFiles[backupID][blockNum]['P'][supplierNum] = remoteParity[supplierNum]
        # if we know only 5 blocks stored on remote machine
        # but we got reconstructed 6th block - remember this  
        self.remoteMaxBlockNumbers[backupID] = max(
            self.remoteMaxBlockNumbers.get(backupID, -1),
            blockNum)
        self.updatedBackupIDs.add(backupID)
    

    def ScanMissingBlocks(self, backupID):
        missingBlocks = set()
        localMaxBlockNum = self.localMaxBlockNumbers.get(backupID, -1)
        remoteMaxBlockNum = self.remoteMaxBlockNumbers.get(backupID, -1)
        supplierActiveArray = self.mySupplierSet.GetActiveArray()
        dhnio.Dprint(6+self.dprintAdjust, "backup_monitor.ScanMissingBlocks supplierActiveArray=%s" % supplierActiveArray)

        if not self.remoteFiles.has_key(backupID):
            if not self.localFiles.has_key(backupID):
                # we have no local and no remote info for this backup
                # no chance to do some rebuilds...
                # TODO but how we get here ?! 
                dhnio.Dprint(4+self.dprintAdjust, 'backup_monitor.ScanMissingBlocks no local and no remote info for %s' % backupID)
            else:
                # we have no remote info, but some local files exists
                # so let's try to sent all of them
                # need to scan all block numbers 
                for blockNum in range(localMaxBlockNum):
                    # we check for Data and Parity packets
                    localData = self.GetLocalDataArray(backupID, blockNum)
                    localParity = self.GetLocalParityArray(backupID, blockNum)  
                    for supplierNum in range(len(supplierActiveArray)):
                        # if supplier is not alive we can not send to him
                        # so no need to scan for missing blocks 
                        if supplierActiveArray[supplierNum] != 1:
                            continue
                        if localData[supplierNum] == 1:
                            missingBlocks.add(blockNum)
                        if localParity[supplierNum] == 1:
                            missingBlocks.add(blockNum)
        else:
            # now we have some remote info
            # we take max block number from local and remote
            maxBlockNum = max(remoteMaxBlockNum, localMaxBlockNum)
            dhnio.Dprint(6+self.dprintAdjust, "backup_monitor.ScanMissingBlocks maxBlockNum=%d" % maxBlockNum)
            # and increase by one because range(3) give us [0, 1, 2], but we want [0, 1, 2, 3]
            for blockNum in range(maxBlockNum + 1):
                # if we have few remote files, but many locals - we want to send all missed 
                if not self.remoteFiles[backupID].has_key(blockNum):
                    missingBlocks.add(blockNum)
                    continue
                # take remote info for this block
                remoteData = self.GetRemoteDataArray(backupID, blockNum)
                remoteParity = self.GetRemoteParityArray(backupID, blockNum)  
                # now check every our supplier for every block
                for supplierNum in range(len(supplierActiveArray)):
                    # if supplier is not alive we can not send to him
                    # so no need to scan for missing blocks 
                    if supplierActiveArray[supplierNum] != 1:
                        continue
                    if remoteData[supplierNum] != 1:    # -1 means missing
                        missingBlocks.add(blockNum)     # 0 - no info yet
                    if remoteParity[supplierNum] != 1:  # 1 - file exist on remote supplier 
                        missingBlocks.add(blockNum)
                    

#        # old code
#        if not self.backupListFiles.has_key(backupID):
#            if self.localFiles.has_key(backupID):
#                # we have no remote info, but some local files exists
#                # so let's try to sent all of them
#                # need to scan all block numbers 
#                for blockNum in range(localMaxBlockNum):
#                    # we check for Data and Parity packets
#                    localData = self.GetLocalDataArray(backupID, blockNum)
#                    localParity = self.GetLocalParityArray(backupID, blockNum)  
#                    for supplierNum in range(len(supplierActiveArray)):
#                        # if supplier is not alive we can not send to him
#                        # so no need to scan for missing blocks 
#                        if supplierActiveArray[supplierNum] != 1:
#                            continue
#                        if localData[supplierNum] == 1:
#                            missingBlocks.add(blockNum)
#                        if localParity[supplierNum] == 1:
#                            missingBlocks.add(blockNum)
#            else:
#                # we have no local and no remote info for this backupID
#                # no chance to do some rebuilds...
#                # but how we get this situation ????!!!!
#                dhnio.Dprint(4+self.dprintAdjust, 'backup_monitor.ScanMissingBlocks no local and not remote info for %s' % backupID)
#
#        else:
#            # now we have some remote info
#            remoteListFiles = self.backupListFiles[backupID]
#            # we take max block number from local and remote
#            maxBlockNum = max(remoteListFiles.maxblockNum, localMaxBlockNum)
#            dhnio.Dprint(6+self.dprintAdjust, "backup_monitor.ScanMissingBlocks maxBlockNum=%d" % maxBlockNum)
#            # and increase by one because range(3) give us [0, 1, 2], but we want [0, 1, 2, 3]
#            for blockNum in range(maxBlockNum + 1):
#                for supplierNum in range(len(supplierActiveArray)):
#                    # if supplier is not alive we can not send to him
#                    # so no need to scan for missing blocks 
#                    if supplierActiveArray[supplierNum] != 1:
#                        continue
#                    # if we have no remote info about this supplier
#                    # but he is on line - we want to send to this man
#                    if supplierNum not in remoteListFiles.rawListFiles.keys():
#                        # but first need to make the data structure for him
#                        #supplierInfo = _SupplierBackupInfo(backupID, supplierNum, self.mySupplierSet.suppliers[supplierNum])
#                        #supplierInfo.ApplyMaxBlockNo(maxBlockNum)
#                        #self.backupListFiles[backupID].rawListFiles[supplierNum] = supplierInfo
#                        #remoteListFiles = self.backupListFiles[backupID]
#                        missingBlocks.add(int(blockNum))
#                        continue
#                    # finally check remote info for this supplier
#                    if str(blockNum) in remoteListFiles.rawListFiles[supplierNum].missingData:
#                        missingBlocks.add(int(blockNum))
#                        continue
#                    if str(blockNum) in remoteListFiles.rawListFiles[supplierNum].missingParity:
#                        missingBlocks.add(int(blockNum))
#                        continue

        dhnio.Dprint(6+self.dprintAdjust, "backup_monitor.ScanMissingBlocks %s" % missingBlocks)
        return list(missingBlocks)


    def ReadLocalFiles(self):
        self.localFiles.clear()
        self.localMaxBlockNumbers.clear()
        self.localBackupsSize.clear()
        counter = 0
        for filename in os.listdir(tmpfile.subdir('data-par')):
            if filename.startswith('newblock-'):
                continue
            try:
                backupID, blockNum, supplierNum, dataORparity  = filename.split('-')
                blockNum = int(blockNum)
                supplierNum = int(supplierNum)
            except:
                dhnio.Dprint(4, 'backup_monitor.ReadLocalFiles WARNING incorrect filename ' + filename)
                continue
            if dataORparity not in ['Data', 'Parity']:
                dhnio.Dprint(4, 'backup_monitor.ReadLocalFiles WARNING Data or Parity? ' + filename)
                continue
            if supplierNum >= self.mySupplierSet.supplierCount:
                dhnio.Dprint(4, 'backup_monitor.ReadLocalFiles WARNING supplier number %d > %d %s' % (supplierNum, self.mySupplierSet.supplierCount, filename))
                continue
            if not self.localFiles.has_key(backupID):
                self.localFiles[backupID] = {}
            if not self.localFiles[backupID].has_key(blockNum):
                self.localFiles[backupID][blockNum] = {
                    'D': [0] * self.mySupplierSet.supplierCount,
                    'P': [0] * self.mySupplierSet.supplierCount}
            self.localFiles[backupID][blockNum][dataORparity[0]][supplierNum] = 1
            if not self.localMaxBlockNumbers.has_key(backupID):
                self.localMaxBlockNumbers[backupID] = -1
            if self.localMaxBlockNumbers[backupID] < blockNum:
                self.localMaxBlockNumbers[backupID] = blockNum
            if not self.localBackupsSize.has_key(backupID):
                self.localBackupsSize[backupID] = 0
            self.localBackupsSize[backupID] += os.path.getsize(os.path.join(tmpfile.subdir('data-par'), filename))
            counter += 1
        dhnio.Dprint(6, 'backup_monitor.ReadLocalFiles  %d files indexed' % counter)


    def RepaintingProcess(self):
        reactor.callLater(2, self.RepaintingProcess)
        if len(self.updatedBackupIDs) == 0:
            return
        for backupID in self.updatedBackupIDs:
            if self.BackupStatusNotifyCallback != None:
                self.BackupStatusNotifyCallback(backupID)
        self.updatedBackupIDs.clear()


    def SetSupplierList(self, supplierList):
        dhnio.Dprint(8+self.dprintAdjust,"backup_monitor.SetSupplierList setting suppliers")
        # going from 2 to 4 suppliers (or whatever) invalidates all backups
        # all suppliers was changed because its number was changed
        # so we lost everything!
        if len(supplierList) != self.mySupplierSet.supplierCount:
            # erase all remove info
            self.remoteFiles = {}
            # also erase local info
            self.localFiles = {}
            # new ecc map will be taken later
            self.eccMap = None
            # remove all local files and all backups
            self.DeleteAllBackups()
            # restart backup_monitor immediately
            self.NoteToUpdate()
        # only single suppliers changed
        # need to erase info only for them 
        elif self.mySupplierSet.SuppliersChanged(supplierList):
            # take a list of suppliers positions that was changed
            changedSupplierNums = self.mySupplierSet.SuppliersChangedNumbers(supplierList)
            # notify io_throttle that we do not neeed already this suppliers
            for supplierNum in changedSupplierNums:
                io_throttle.DeleteSuppliers([self.mySupplierSet.suppliers[supplierNum]])
            # remove remote info for this guys
            for backupID in self.remoteFiles.keys():
                for blockNum in self.remoteFiles[backupID].keys():
                    for supplierNum in changedSupplierNums:
                        self.remoteFiles[backupID][blockNum]['D'][supplierNum] = 0
                        self.remoteFiles[backupID][blockNum]['P'][supplierNum] = 0
            # restart backup_monitor soon
            reactor.callLater(1, self.NoteToUpdate)
        # finally save the list of current suppliers 
        self.mySupplierSet.UpdateSuppliers(supplierList)

    #------------------------------------------------------------------------------ 
              

    def DeleteAllBackups(self):
        for backupId in set(self.localFiles.keys() + self.remoteFiles.keys()):
            self.DeleteBackup(backupId)


    # if the user deletes a backup, make sure we remove any work we're doing on it
    def DeleteBackup(self, backupID, removeLocalFilesToo=True):
        dhnio.Dprint(4+self.dprintAdjust, 'backup_monitor.DeleteBackup ' + backupID)
        # abort backup if it just started and is running at the moment
        backup_db.AbortRunningBackup(backupID)
        # also remove from list of running backups  
        if backupID in self.backupsInProcess:
            self.backupsInProcess.remove(backupID)
        # if we have several copies of same ID in working queue - remove them all
        while backupID in self.backupIDsQueue:
            self.backupIDsQueue.remove(backupID)
        # remote remote info for this backup 
        if self.remoteFiles.has_key(backupID):
            del self.remoteFiles[backupID]
        # if we requested for files for this backup - we do not need it anymore
        io_throttle.DeleteBackupRequests(backupID)
        # remove interests in transport_control
        transport_control.DeleteBackupInterest(backupID)
        # mark it as being deleted in the db
        backup_db.DeleteDirBackup(backupID)
        # finally remove local files for this backupID
        if removeLocalFilesToo:
            self.DeleteLocalBackup(backupID)


    def DeleteSupplierRestoreWork(self, supplierNum):
        return
#        for key in self.repairQueue:
#            self.repairQueue[key].availableData[supplierNum] = 0
#            self.repairQueue[key].availableParity[supplierNum] = 0
#            self.repairQueue[key].missingData[supplierNum] = 0
#            self.repairQueue[key].missingParity[supplierNum] = 0


    def DeleteAllSupplierData(self, supplierNum):
        io_throttle.DeleteSuppliers([self.mySupplierSet.suppliers[supplierNum]])


    def DeleteLocalBackup(self, backupID):
        dhnio.Dprint(8, 'backup_monitor.DeleteLocalBackup ' + backupID)
        num = 0
        sz = 0
        localDir = tmpfile.subdir('data-par')
        for filename in os.listdir(localDir):
            if filename.startswith(backupID):
                filepath = os.path.join(localDir, filename)
                try:
                    sz += os.path.getsize(filepath) 
                    os.remove(filepath)
                    num += 1
                    dhnio.Dprint(12, 'backup_monitor.DeleteLocalBackup ' + filepath)
                except:
                    dhnio.Dprint(12, 'backup_monitor.DeleteLocalBackup ERROR can not remove ' + filepath)
                    dhnio.DprintException()
        return num, sz

    #------------------------------------------------------------------------------ 

    def GetListFilesBackupIds(self, supplierNum, supplierId, listFileText):
        rawlist = listFileText.splitlines()
        resultlist = []
        for line in rawlist:
            # comment lines in Files reports start with blank,
            # also don't consider the identity a backup,
            # nor the backup_info.xml
            if len(line) > 0 and (line[0] == ' ' or line.strip() == supplierId or line == settings.BackupInfoFileName()):
                continue
            dashindex = line.find("-")
            backupId = ''
            if dashindex>0: 
                # if this is supplier 3 make sure we have a -3-
                if line.find("-" + str(supplierNum) + "-") > 0:   
                    # if there is a dash use only part before the dash
                    backupId=line[0:dashindex]                    
            if backupId != '' and backupId not in resultlist:
                resultlist.append(backupId)
        return misc.sorted_backup_ids(resultlist)


    # if we get a line "F20090709034221PM-0-Data from 0-1000"
    # or "F20090709034221PM-0-Data from 0-1000 missing 1,3,"
    # this will return 1000
    def GetLineMaxBlockNum(self, line):
        try:
            maxBlock = -1
            workLine = line
            if line.find(" missing ") > 0:
                workLine = line[0:line.find(" missing ")]
            lineMax = int(workLine[workLine.rfind("-")+1:])
            if lineMax > maxBlock:
                maxBlock = lineMax
            return maxBlock
        except:
            return -1


    def GetLineMissingBlocks(self, line, lineMax, backupMax):
        missingArray = []
        missingindex = line.find(" missing ") 
        if missingindex != -1:
            missingArray = line[missingindex+9:].split(",")
        if '' in missingArray:
            missingArray.remove('')
        if backupMax > lineMax:
            intMissingArray = range(lineMax+1,backupMax+1)
            for i in intMissingArray:
                missingArray.append(str(i))
        return missingArray


    def GetBackupStats(self, backupID):
        if not self.remoteFiles.has_key(backupID):
            return 0, 0, [(0, 0)] * self.mySupplierSet.supplierCount
        percentPerSupplier = 100.0 / self.mySupplierSet.supplierCount
        maxBlockNum = self.remoteMaxBlockNumbers.get(backupID, -1)
        fileNumbers = [0] * self.mySupplierSet.supplierCount
        totalNumberOfFiles = 0
        for blockNum in self.remoteFiles[backupID].keys():
            for supplierNum in range(len(fileNumbers)):
                if supplierNum < self.mySupplierSet.supplierCount:
                    if self.remoteFiles[backupID][blockNum]['D'][supplierNum] == 1:
                        fileNumbers[supplierNum] += 1
                        totalNumberOfFiles += 1
                    if self.remoteFiles[backupID][blockNum]['P'][supplierNum] == 1:
                        fileNumbers[supplierNum] += 1
                        totalNumberOfFiles += 1
        statsArray = []
        for supplierNum in range(self.mySupplierSet.supplierCount):
            if maxBlockNum > -1:
                # 0.5 because we count both Parity and Data.
                percent = percentPerSupplier * 0.5 * fileNumbers[supplierNum] / ( maxBlockNum + 1 )
            else:
                percent = 0.0
            statsArray.append(( percent, fileNumbers[supplierNum] ))
        del fileNumbers 
        return totalNumberOfFiles, maxBlockNum, statsArray


    def GetBackupLocalStats(self, backupID):
        if not self.localFiles.has_key(backupID):
            return 0, 0, 0, [(0, 0)] * self.mySupplierSet.supplierCount
        percentPerSupplier = 100.0 / self.mySupplierSet.supplierCount
        maxBlockNum = self.localMaxBlockNumbers.get(backupID, -1)
        totalNumberOfFiles = 0
        fileNumbers = [0] * self.mySupplierSet.supplierCount
        for blockNum in self.localFiles[backupID].keys():
            for supplierNum in range(len(fileNumbers)):
                if supplierNum < self.mySupplierSet.supplierCount:
                    if self.localFiles[backupID][blockNum]['D'][supplierNum] == 1:
                        fileNumbers[supplierNum] += 1
                        totalNumberOfFiles += 1
                    if self.localFiles[backupID][blockNum]['P'][supplierNum] == 1:
                        fileNumbers[supplierNum] += 1
                        totalNumberOfFiles += 1
        statsArray = []
        for supplierNum in range(self.mySupplierSet.supplierCount):
            if maxBlockNum > -1:
                # 0.5 because we count both Parity and Data.
                percent = percentPerSupplier * 0.5 * fileNumbers[supplierNum] / ( maxBlockNum + 1 )
            else:
                percent = 0.0
            statsArray.append(( percent, fileNumbers[supplierNum] ))
        del fileNumbers 
        return totalNumberOfFiles, self.localBackupsSize.get(backupID, 0), maxBlockNum, statsArray


    def GetBackupBlocksAndPercent(self, backupID):
        if not self.remoteFiles.has_key(backupID):
            return 0, 0
        # get max block number
        maxBlockNum = self.remoteMaxBlockNumbers.get(backupID, -1)
        if maxBlockNum == -1:
            return 0, 0
        # we count all remote files for this backup
        fileCounter = 0
        for blockNum in self.remoteFiles[backupID].keys():
            for supplierNum in range(self.mySupplierSet.supplierCount):
                if self.remoteFiles[backupID][blockNum]['D'][supplierNum] == 1:
                    fileCounter += 1
                if self.remoteFiles[backupID][blockNum]['P'][supplierNum] == 1:
                    fileCounter += 1
        # +1 since zero based and *0.5 because Data and Parity
        return maxBlockNum + 1, 100.0 * 0.5 * fileCounter / ((maxBlockNum + 1) * self.mySupplierSet.supplierCount)
    
    
    def GetBackupIds(self):
        return misc.sorted_backup_ids(self.remoteFiles.keys())
#        return misc.sorted_backup_ids(self.backupListFiles.keys())


#    def GetAllBackupsSpace(self):
#        totalBlocks = 0
#        for backupId in self.backupListFiles.keys():
#            # maxBlock is 0 based so count is +1
#            totalBlocks += (self.backupListFiles[backupId].maxblockNum + 1) 
#        return totalBlocks * settings.PacketSizeTarget() * self.mySupplierSet.supplierCount


#    def GetBackupSpace(self, backupId):
#        totalBlocks = 0
#        if self.backupListFiles.has_key(backupId):
#            # maxBlock is 0 based so count is +1
#            totalBlocks += (self.backupListFiles[backupId].maxblockNum + 1) 
#        return totalBlocks * settings.PacketSizeTarget() * self.mySupplierSet.supplierCount


    def GetLocalDataArray(self, backupID, blockNum):
        if not self.localFiles.has_key(backupID):
            return [0] * self.mySupplierSet.supplierCount
        if not self.localFiles[backupID].has_key(blockNum):
            return [0] * self.mySupplierSet.supplierCount
        return self.localFiles[backupID][blockNum]['D']


    def GetLocalParityArray(self, backupID, blockNum):
        if not self.localFiles.has_key(backupID):
            return [0] * self.mySupplierSet.supplierCount
        if not self.localFiles[backupID].has_key(blockNum):
            return [0] * self.mySupplierSet.supplierCount
        return self.localFiles[backupID][blockNum]['P']
        

    def GetRemoteDataArray(self, backupID, blockNum):
        if not self.remoteFiles.has_key(backupID):
            return [0] * self.mySupplierSet.supplierCount
        if not self.remoteFiles[backupID].has_key(blockNum):
            return [0] * self.mySupplierSet.supplierCount
        return self.remoteFiles[backupID][blockNum]['D']

        
    def GetRemoteParityArray(self, backupID, blockNum):
        if not self.remoteFiles.has_key(backupID):
            return [0] * self.mySupplierSet.supplierCount
        if not self.remoteFiles[backupID].has_key(blockNum):
            return [0] * self.mySupplierSet.supplierCount
        return self.remoteFiles[backupID][blockNum]['P']

    #------------------------------------------------------------------------------ 

    # if there is a backup in process, one supplier may list more files in the backup than another,
    # leading the backup_monitor to try to fix a backup in process.  We need to tell the backup_monitor
    # when a backup is in process and when it is finished
    def AddBackupInProcess(self, BackupName):
        self.backupsInProcess.append(BackupName)


    def RemoveBackupInProcess(self, BackupName):
        if BackupName in self.backupsInProcess:
            self.backupsInProcess.remove(BackupName)


    def IsBackupInProcess(self, BackupID):
        return BackupID in self.backupsInProcess

    
    def SetBackupStatusNotifyCallback(self, callBack):
        self.BackupStatusNotifyCallback = callBack


    def SetStatusCallBackForGuiBackup(self, callBack):
        self.StatusCallBackForGuiBackup = callBack


#------------------------------------------------------------------------------ 


if __name__ == "__main__":
    init()
    import pprint
    pprint.pprint(GetBackupIds())












#    def CleanupBackups(self):
#        #TODO - track if we've heard from enough suppliers to know a backup doesn't exist
#        backupsToKeep = int(settings.getGeneralBackupsToKeep())
#        dhnio.Dprint(12+self.dprintAdjust, "backup_monitor.CleanupBackups, keep " + str(backupsToKeep) + " backups")
#        foundBackups = 0 # how many backups for a directory we've found
#        didDelete = False
#        delay = 1
#        #potentially called many times after a request list files all
#        if time.time() - self.backupDBCheck > 60.0: 
#            # if it has been longer than x seconds since the last time we ran this
#            self.backupDBCheck = time.time()
#            backupDirectories = backup_db.GetBackupDirectories()
#            for backupDir in backupDirectories:
#                foundBackups = 0
#                backupIDsForDirectory = backup_db.GetDirBackupIds(backupDir)
#                if len(backupIDsForDirectory) > 0:
#                    backupIDsForDirectory.reverse()
#                    for backupId in backupIDsForDirectory:
#                        if backupId not in self.backupsInProcess:
#                            if self.backupListFiles.has_key(str(backupId)):
#                                foundBackups = foundBackups + 1
#                                if backupsToKeep > 0 and foundBackups > backupsToKeep:
#                                    dhnio.Dprint(2+self.dprintAdjust, "backup_monitor.CleanupBackups delete backup " + str(backupId) + " for directory " + str(backupDir) + " beyond the " + str(backupsToKeep) + " backups to keep")
#                                    self.DeleteBackup(backupId)
#                                    #customerservice.DeleteWholeBackup(backupId)
#                                    didDelete = True
#                            else: 
#                                # so we have something in our list of backups 
#                                # that should have happened, but no suppliers have info on it
#                                if len(self.rawListFiles) > self.eccMap.CorrectableErrors:
#                                    dhnio.Dprint(2+self.dprintAdjust, "backup_monitor.CleanupBackups too many suppliers don't have info on backup " + backupId + ", missing " + str(len(self.rawListFiles)) + " correctable " + str(self.eccMap.CorrectableErrors))
#                                    #   we temporary remove this feature
#                                    #   because something going wrong
#                                    #   backups are deleted after finishing
#                                    #backup_db.DeleteDirBackup(backupId)
#                                    #customerservice.DeleteWholeBackup(backupId) 
#                                    # may not be necessary if all suppliers don't have the backup
#                                    didDelete = True
#            if didDelete:
#                dhnio.Dprint(12+self.dprintAdjust, "backup_monitor.CleanupBackups scheduling another listfilesall at " + str(time.asctime(time.localtime(time.time()))))
#                reactor.callLater(30,customerservice.RequestListFilesAll)
