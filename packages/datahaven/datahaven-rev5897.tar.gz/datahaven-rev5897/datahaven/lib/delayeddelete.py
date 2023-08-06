#!/usr/bin/python
#delayeddelete.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#


import os
import sys
import time


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in delayeddelete.py')


import dhnio
import tmpfile



class filetodelete:
    filename = ""     # name of file we are going to soon delete
    timetodelete = 0  # time after which we should delte this file
    def __init__ (self, filename, timetodelete):
        self.filename=filename
        self.timetodelete=timetodelete

deletequeue = []

def init():
    global deletequeue
    deletequeue=[]

def DeleteAfterTime(filename, delay):
##    dhnio.Dprint(14, "delayeddelete.DeleteAfterTime with %s" % filename)
    global deletequeue
    now = time.time()
    timetodelete = now + delay
    newjob = filetodelete(filename, timetodelete)
    deletequeue.append(newjob)
    CallIfNeeded()


def CheckQueue():
##    dhnio.Dprint(14, "delayeddelete.CheckQueue")
    global deletequeue
    now = time.time()
    removeditems=[]
    for item in deletequeue:
        if (item.timetodelete <= now and os.access(item.filename, os.W_OK)):
##            dhnio.Dprint(14, "delayeddelete.CheckQueue about to remove %s " % item.filename)
#            if (os.path.exists(item.filename)):
#                try:
#                    os.remove(item.filename)
#                except:
#                    dhnio.Dprint(14, "delayeddelete.CheckQueue wanted to remove file but it is busy ")
#            else:
#                dhnio.Dprint(1, "delayeddelete.CheckQueue ERROR wanted to remove file but not there %s " % item.filename)
            tmpfile.throw_out(item.filename)
            removeditems.append(item)
##        else:
##            dhnio.Dprint(14, "delayeddelete.CheckQueue not time yet for %s " % item.filename)

    if (len(removeditems)>0):
        for item in removeditems:
            deletequeue.remove(item)
    del removeditems
    CallIfNeeded()

def CallIfNeeded():
    global deletequeue
    if len(deletequeue)>0:
        reactor.callLater(3, CheckQueue)
##        dhnio.Dprint(14, "delayeddelete.CallIfNeeded callLater setup")
    else:
        dhnio.Dprint(14, "delayeddelete.CallIfNeeded queue is empty")



###  Run this with "tial dobackup"
##class ddeletetest(unittest.TestCase):
##    def test_delete(self):
##        now = time.time()
##        print "time is ", now
##        dhnio.WriteFile("/tmp/deletetest", "A bit of file data")
##        DeleteAfterTime("/tmp/deletetest", 10)
##