#!/usr/bin/python

#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#
#
# Strategy for automatic backups
#
# 1) Full backup to alternating set of nodes every 2 weeks.
#
# 2) Full monthly, then incremental weekly and daily
#
# 3) One time full and then incremental monthly, weekly
#
# 4) Break alphabetical list of files into N parts and do full
#    backup on one of those and incrementals on the rest.
#    So we no longer need part of the incremental history
#      every time, and after N times older stuff can toss.
#      so every day is part full and part incremental.  Cool.
#
#  Want user to be able to specify what he wants, or at least
#  select from a few reasonable choices.
#
#
# May just do (1) to start with.
#
# This code also wakes up every day and fires off localtester, remotetester
#   on some reasonable random stuff.
#
# This manages the whole thing, so after GUI, this has the highest level control functions.
#
# Some competitors let people choose what days to backup on.  Not sure this
#   is really so great though, once we have incremental.
#
# Some can handle partial file changes.  So if a 500 MB mail file only has
# a little bit appended, only the little bit is backed up.
#
# Some competitors can turn the computer off after a backup, but
# we need it to stay on for P2P stuff.
#
# need to record if zip, tar, dump, etc
#
# If we do regular full backups often, then we might not bother scrubbing older stuff.
# Could reduce the bandwidth needed (since scrubbing could use alot.l

import time, sys, os, sched             # sched lets you call os to schedule future commands

import dobackup
                                        #  Google or Python Coockbook page 133

class backupinfo:
    frequency=""
    fullinc=""
    bieccmap=""
    nextid=""
    nexttime=""

def backupmanager():
    dobackup.dobackup()                 # right now we just do one backup - not so clever at the moment

