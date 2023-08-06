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
import lib.diskspace as diskspace
from lib.automat import Automat


import backup_rebuilder
import fire_hire
import list_files_orator 
import automats

import backups
import customerservice
import io_throttle
import backup_db
import contacts_status

_BackupMonitor = None

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _BackupMonitor
    if _BackupMonitor is None:
        _BackupMonitor = BackupMonitor('backup_monitor', 'READY', 4)
    if event is not None:
        _BackupMonitor.automat(event, arg)
    return _BackupMonitor


class BackupMonitor(Automat):
    timers = {'timer-1sec':   (1,       ['RESTART']), 
              'timer-1hour':  (60*60,   ['READY']), }

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('MONITOR ' + newstate)

    def A(self, event, arg):
        #---READY---
        if self.state == 'READY':
            if event == 'restart' or event == 'timer-1hour':
                self.state = 'RESTART'
        #---RESTART---
        elif self.state == 'RESTART':
            if event == 'timer-1sec' and backup_rebuilder.A().state in [ 'STOPPED' , 'DONE' ]:
                list_files_orator.A('need-files')
                self.state = 'LIST_FILES'
        #---LIST_FILES---
        elif self.state == 'LIST_FILES':
            if event == 'list_files_orator.state' and arg is 'SAW_FILES':
                self.doPrepareListBackups()
                self.state = 'LIST_BACKUPS'
            elif event == 'list_files_orator.state' and arg is 'NO_FILES':
                self.state = 'READY'
            elif event == 'restart':
                self.state = 'RESTART'
        #---LIST_BACKUPS---
        elif self.state == 'LIST_BACKUPS':
            if event == 'list-backups-done':
                backup_rebuilder.A('start')
                self.state = 'REBUILDING'
            elif event == 'restart':
                self.state = 'RESTART'
        #---REBUILDING---
        elif self.state == 'REBUILDING':
            if event == 'backup_rebuilder.state' and arg is 'DONE':
                fire_hire.A('start')
                self.state = 'FIRE_HIRE'
            elif event == 'backup_rebuilder.state' and arg is 'STOPPED':
                self.state = 'READY'
            elif event == 'restart':
                backup_rebuilder.SetStoppedFlag()
                self.state = 'RESTART'
        #---FIRE_HIRE---
        elif self.state == 'FIRE_HIRE':
            if event == 'hire-new-supplier' or event == 'restart': # or ( event == 'fire-hire-finished' and self.isFailedSuppliers() ):
                self.state = 'RESTART'
            elif event == 'fire-hire-finished': # and not self.isFailedSuppliers():
                self.doCleanUpBackups()
                self.state = 'READY'

    def doPrepareListBackups(self):
        # take remote and local backups and get union from it 
        allBackupIDs = set(backups.local_files().keys() + backups.remote_files().keys())
        # take only backups from data base
        allBackupIDs.intersection_update(backup_db.GetBackupIds())
        # remove running backups
        allBackupIDs.difference_update(backups.backups_in_process())
        # sort it in reverse order - newer backups should be repaired first
        allBackupIDs = misc.sorted_backup_ids(list(allBackupIDs), True)
        # add backups to the queue
        backup_rebuilder.AddBackupsToWork(allBackupIDs)
        # update suppliers, clear stats for all 
        backups.suppliers_set().UpdateSuppliers(contacts.getSupplierIDs()) 
        dhnio.Dprint(6, 'backup_monitor.doPrepareListBackups %s' % str(allBackupIDs))
        self.automat('list-backups-done')

    def doCleanUpBackups(self):
        backupsToKeep = settings.getGeneralBackupsToKeep()
        if backupsToKeep < 1:
            backupsToKeep = 1
        for backupDir in backup_db.GetBackupDirectories():
            backupIDsForDirectory = backup_db.GetDirBackupIds(backupDir)
            while len(backupIDsForDirectory) > backupsToKeep:
                backupID = backupIDsForDirectory.pop(0)
                dhnio.Dprint(6, 'backup_monitor.doCleanUpBackups wish to remove %s of %s' % (backupID, backupDir))
                backup_db.AbortRunningBackup(backupID)
                backups.DeleteBackup(backupID)
                

def Restart():
    dhnio.Dprint(4, 'backup_monitor.Restart')
    A('restart')




        

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
#                        if backupId not in backups_in_process():
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

