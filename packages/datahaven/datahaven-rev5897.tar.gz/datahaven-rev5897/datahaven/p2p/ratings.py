#!/usr/bin/python
#ratings.py
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
    sys.exit('Error initializing twisted.internet.reactor in ratings.py')

from twisted.internet import task


import lib.dhnio as dhnio
import lib.dhnmath as dhnmath
import lib.misc as misc
import lib.nameurl as nameurl
import lib.settings as settings
import lib.contacts as contacts
import lib.transport_control as transport_control


import contacts_status


#-------------------------------------------------------------------------------

_LoopCountRatingsTask = None

#-------------------------------------------------------------------------------


def init():
    dhnio.Dprint(4, 'ratings.init')
    start_count_ratings()

def shutdown():
    dhnio.Dprint(4, 'ratings.shutdown')
    stop_count_ratings()

def rating_dir(idurl):
    return os.path.join(settings.RatingsDir(), nameurl.UrlFilename(idurl))

def rating_month_file(idurl, monthstr=None):
    if monthstr is None:
        monthstr = time.strftime('%m%y')
    return os.path.join(rating_dir(idurl), monthstr)

def rating_total_file(idurl):
    return os.path.join(rating_dir(idurl), 'total')

def exist_rating_dir(idurl):
    return dhnio._dir_exist(rating_dir(idurl))

def make_rating_dir(idurl):
    dhnio._dir_make(rating_dir(idurl))

def read_month_rating_dict(idurl, monthstr=None):
    if monthstr is None:
        monthstr = time.strftime('%m%y')
    return dhnio._read_dict(rating_month_file(idurl, monthstr))

def write_month_rating_dict(idurl, rating_dict, monthstr=None):
    if monthstr is None:
        monthstr = time.strftime('%m%y')
    return dhnio._write_dict(rating_month_file(idurl, monthstr), rating_dict)

def read_total_rating_dict(idurl):
    return dhnio._read_dict(rating_total_file(idurl))

def write_total_rating_dict(idurl, rating_dict):
    return dhnio._write_dict(rating_total_file(idurl), rating_dict)

def make_blank_rating_dict():
    return {'all':'0', 'alive':'0'}

def increase_rating(idurl, alive_state):
    if not exist_rating_dir(idurl):
        make_rating_dir(idurl)

    month_rating = read_month_rating_dict(idurl)
    if month_rating is None:
        month_rating = make_blank_rating_dict()
    try:
        mallI = int(month_rating['all'])
        maliveI = int(month_rating['alive'])
    except:
        mallI = 0
        maliveI = 0
    mallI += 1
    if alive_state:
        maliveI += 1
    month_rating['all'] = str(mallI)
    month_rating['alive'] = str(maliveI)
    write_month_rating_dict(idurl, month_rating)

    total_rating = read_total_rating_dict(idurl)
    if total_rating is None:
        total_rating = make_blank_rating_dict()
    try:
        tallI = int(total_rating['all'])
        taliveI = int(total_rating['alive'])
    except:
        tallI = 0
        taliveI = 0
    tallI += 1
    if alive_state:
        taliveI += 1
    total_rating['all'] = str(tallI)
    total_rating['alive'] = str(taliveI)
    write_total_rating_dict(idurl, total_rating)
    return mallI, maliveI, tallI, taliveI

def read_all_monthly_ratings(idurl):
    if not exist_rating_dir(idurl):
        return None
    d = {}
    for monthstr in os.listdir(rating_dir(idurl)):
        if monthstr == 'total':
            continue
        month_rating = read_month_rating_dict(idurl, monthstr)
        if month_rating is None:
            continue
        d[monthstr] = month_rating
    return d

def rate_all_users():
    dhnio.Dprint(4, 'ratings.rate_all_users')
    monthStr = time.strftime('%B')
    for idurl in contacts.getContactsAndCorrespondents():
        #isalive = transport_control.ContactIsAlive(idurl)
        isalive = contacts_status.isOnline(idurl)
        mall, malive, tall, talive = increase_rating(idurl, isalive)
        month_percent = 100.0*float(malive)/float(mall)
        total_percent = 100.0*float(talive)/float(tall)
        dhnio.Dprint(4, '[%6.2f%%: %s/%s] in %s and [%6.2f%%: %s/%s] total - %s' % (
            month_percent,
            malive,
            mall,
            monthStr,
            total_percent,
            talive,
            tall,
            nameurl.GetName(idurl),))

def start_count_ratings():
    def _start():
        global _LoopCountRatingsTask
        _LoopCountRatingsTask = task.LoopingCall(rate_all_users)
        _LoopCountRatingsTask.start(settings.DefaultAlivePacketTimeOut())
    interval = dhnmath.interval_to_next_hour()
    #debug
    #interval = 10
    reactor.callLater(interval, _start)
    dhnio.Dprint(6, 'ratings.start_count_ratings will start after %s minutes' % str(interval/60.0))

def stop_count_ratings():
    global _LoopCountRatingsTask
    if _LoopCountRatingsTask:
        if _LoopCountRatingsTask.running:
            _LoopCountRatingsTask.stop()
        del _LoopCountRatingsTask
        _LoopCountRatingsTask = None
        dhnio.Dprint(6, 'ratings.stop_count_ratings task finished')

#-------------------------------------------------------------------------------


def main():
    pass

if __name__ == '__main__':
    main()
