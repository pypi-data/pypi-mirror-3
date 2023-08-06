#!/usr/bin/python
#firehire.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#  We contact datahaven.net for list of nodes we have hired
#   and we can also replace any node (fire & hire someone else at once)
#   by contacting datahaven.net and asking for replacement.
#
#  If at some point we are not getting good answers from a node
#  for too long we need to replace him and reconstruct the data
#  he was holding.  This is firehire and then scrubbing.
#
#  Probably if we try to contact someone for 48 hours and can not,
#  we want to give up on them.
#
#  GUI can firehire at any time.
#
#  Automatically fire if right after we ask a supplier for a BigPacket,
#    he turns around and asks us for it (like he does not have it).
#    Our regular code would not do this, but an evil modified version might
#       try to get away with not holding any data by just getting it from us
#       anytime we asked for it.  So we can not allow this cheat to work.
#
#  We ask for lists of files they have for us and keep these in  settings.FileListDir()/suppliernum
#  These should be updated at least every night.
#  If a supplier has not given us a list for several days he is a candidate for firing.
#
#  Transport_control should keep statistics on how fast different nodes are.
#  We could fire a slow node.
#
#  Restore can keep track of who did not answer in time to be part of raidread, and they can
#  be a candidate for firing.
#
#  The fire packet needs to use IDURL so that if there is a retransmission of the "fire" request
#    we just send new "list suppliers" again.
#
#  Task list
#  1) fire inactive suppliers (default is 48 hours)
#  2) fire suppliers with low rating (less than 25% by default)
#  3) test if supplier is "evil modifed"
#  4) test ListFiles peridoically
#  5) fire slow nodes



import os
import sys
import time


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in firehire.py')

from twisted.internet import task


import lib.dhnio as dhnio
import lib.misc as misc
import lib.settings as settings
import lib.contacts as contacts
import lib.transport_control as transport_control
import lib.nameurl as nameurl


import centralservice
import ratings
import backup_db
import events
import contacts_status


#-------------------------------------------------------------------------------

_StatusTask = None
_LogFile = None

#-------------------------------------------------------------------------------


def init():
    dhnio.Dprint(4, 'firehire.init')
    StatusLoopRestart()
    log('init')


def shutdown():
    dhnio.Dprint(4, 'firehire.shutdown')
    StatusLoopStop()
    logClose()


def log(s):
    global _LogFile
    if _LogFile is None:
        _LogFile = open(settings.FireHireLogFilename(), 'a')
    _LogFile.write('['+time.strftime('%d%m%y %H:%M:%S')+'] '+s.strip()+'\n')
    _LogFile.flush()
    os.fsync(_LogFile.fileno())


def logClose():
    global _LogFile
    if _LogFile is not None:
        _LogFile.close()
    _LogFile = None


def FireSupplier(idurl, reason='', info=''):
    dhnio.Dprint(4, 'firehire.FireSupplier %s reason=[%s] info=[%s]' % (idurl, reason, info))

#    # if we have any backups started - just do nothing
#    # because we do not want to change suppliers
#    # while we uploading any data to them.
#    if backup_db.HasRunningBackup():
#        return

    centralservice.SendReplaceSupplier(idurl)
    log('fire ' + nameurl.GetName(idurl) + ' ' + reason + ' ' + info)
    events.info('firehire',
                'request to fire supplier %s' % nameurl.GetName(idurl),
                'reason:%s\ninfo:%s\n' % (reason, info),)


def StatusLoop():
    dhnio.Dprint(6, 'firehire.StatusLoop')

    fire_index = 0
    for idurl in contacts.getSupplierIDs():
        # if supplier is alive - do not want to touch him at this time
        # just remember the last time we got a packet from him
#        if transport_control.ContactIsAlive(idurl):
        if contacts_status.isOnline(idurl):
            misc.writeSupplierData(idurl, 'lastpackettime',
                time.strftime('%d%m%y %H:%M:%S',
                    time.localtime(
                        transport_control.GetContactAliveTime(idurl))))
            continue

        if not ratings.exist_rating_dir(idurl):
            continue
        ratingTotal = ratings.read_total_rating_dict(idurl)
        if ratingTotal is None:
            continue
        ratingMonth = ratings.read_month_rating_dict(idurl)
        if ratingMonth is None:
            continue

        # collect data to make a decision
        try:
            totalHours = int(ratingTotal.get('all', '0'))
            totalHoursMonth = int(ratingMonth.get('all', '0'))
            aliveHoursMonth = int(ratingMonth.get('alive', '0'))
        except:
            totalHours = 0
            totalHoursMonth = 0
            aliveHoursMonth = 0
            dhnio.DprintException()
        connected = misc.readSupplierData(idurl, 'connected')
        try:
            connectedTime = time.mktime(time.strptime(connected, '%d%m%y %H:%M:%S'))
        except:
            connectedTime = 0
        try:
            lptLocal = time.mktime( time.strptime( misc.readSupplierData(idurl,
                                    'lastpackettime'), '%d%m%y %H:%M:%S'))
        except:
            lptLocal = 0

        # if we do not know how long we already connected with this guy - keep it
        if connected == '':
            continue

        # give time for new suppliers
        if connectedTime != 0 and time.time() - connectedTime <= 24 * 60 * 60:
            continue

        # wait to get more statistics
        if totalHours <= 48:
            continue

        # fire if not alive more than 48 hours:
        if lptLocal != 0 and time.time() - lptLocal > 60*60*48:
            fire_index += 1
            # do not want to send several packets at once
            reactor.callLater(fire_index*2, FireSupplier, idurl, 'inactive', str(time.time() - lptLocal)+' seconds')
            continue

        # fire if low rating
        if totalHoursMonth > 48 and aliveHoursMonth/totalHoursMonth < 0.10:
            fire_index += 1
            reactor.callLater(fire_index*2, FireSupplier, idurl, 'low-rating', '%d/%d' % (aliveHoursMonth, totalHoursMonth))
            continue


def StatusLoopRestart():
    dhnio.Dprint(6, 'firehire.StatusLoopRestart')
    global _StatusTask
    if _StatusTask is not None:
        StatusLoopStop()
    _StatusTask = task.LoopingCall(StatusLoop)
    _StatusTask.start(settings.DefaultAlivePacketTimeOut()*2)


def StatusLoopStop():
    global _StatusTask
    if _StatusTask is not None:
        if _StatusTask.running:
            _StatusTask.stop()
        del _StatusTask
        _StatusTask = None
        dhnio.Dprint(6, 'firehire.StatusLoopStop task finished')


