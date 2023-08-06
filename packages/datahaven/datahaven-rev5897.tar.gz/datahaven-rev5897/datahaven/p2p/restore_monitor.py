#!/usr/bin/python
#restore_monitor.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#
#manage currently restoring backups

import os
import sys
import time


import lib.dhnio as dhnio


import restore


_WorkingBackupIDs = {}
_WorkingBackupProgress = {}
OnRestorePacketFunc = None
OnRestoreDoneFunc = None

#------------------------------------------------------------------------------ 

def init():
    dhnio.Dprint(4, 'restore_monitor.init')

def packet_in_callback(backupID, packet):
    dhnio.Dprint(4, 'restore_monitor.packet_in_callback ' + backupID)
    global _WorkingBackupProgress
    global OnRestorePacketFunc
    
    SupplierNumber = packet.SupplierNumber()
    
    #want to count the data we restoring
    if SupplierNumber not in _WorkingBackupProgress[backupID].keys():
        _WorkingBackupProgress[backupID][SupplierNumber] = 0
    _WorkingBackupProgress[backupID][SupplierNumber] += len(packet.Payload)

    if OnRestorePacketFunc is not None:
        OnRestorePacketFunc(backupID, SupplierNumber, packet)

def restore_done(x):
    dhnio.Dprint(2, 'restore_monitor.restore_done ' + str(x))
    global _WorkingBackupIDs
    global _WorkingBackupProgress
    global OnRestoreDoneFunc
    
    backupID = x.split(' ')[0]
    _WorkingBackupIDs.pop(backupID, None)
    _WorkingBackupProgress.pop(backupID, None)
    
    if OnRestoreDoneFunc is not None:
        OnRestoreDoneFunc(backupID)

def restore_failed(x):
    dhnio.Dprint(2, 'restore_monitor.restore_failed ' + str(x))
    global _WorkingBackupIDs
    global _WorkingBackupProgress
    backupID = x.split(' ')[0]
    _WorkingBackupIDs.pop(backupID, None)
    _WorkingBackupProgress.pop(backupID, None)

def Start(backupID, outputFileName):
    dhnio.Dprint(6, 'restore_monitor.Start %s to %s' % (backupID, outputFileName))
    global _WorkingBackupIDs
    global _WorkingBackupProgress
    if backupID in _WorkingBackupIDs.keys():
        return None
    r = restore.restore(backupID, outputFileName)
    r.MyDeferred.addCallback(restore_done)
    r.MyDeferred.addErrback(restore_failed)
    r.SetPacketInCallback(packet_in_callback)
    _WorkingBackupIDs[backupID] = r
    _WorkingBackupProgress[backupID] = {}
    return r

def Abort(backupID):
    dhnio.Dprint(6, 'restore_monitor.Abort %s' % backupID)
    global _WorkingBackupIDs
    global _WorkingBackupProgress
    if not backupID in _WorkingBackupIDs.keys():
        return False
    r = _WorkingBackupIDs[backupID]
    r.Abort()
    return True

def GetWorkingIDs():
    global _WorkingBackupIDs
    return _WorkingBackupIDs.keys()

def IsWorking(backupID):
    global _WorkingBackupIDs
    return backupID in _WorkingBackupIDs.keys()

def GetProgress(backupID):
    global _WorkingBackupProgress
    return _WorkingBackupProgress.get(backupID, {})







