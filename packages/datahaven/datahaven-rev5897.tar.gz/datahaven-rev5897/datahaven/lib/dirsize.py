#!/usr/bin/python
#dirsize.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#


from twisted.internet import threads

import dhnio
import diskspace

_Jobs = {}
_Dirs = {}

def ask(dirpath, callback=None, arg=None):
    global _Jobs
    global _Dirs
    dhnio.Dprint(6, 'dirsize.ask %s, type=%s' % (dirpath, str(type(dirpath))))
    if _Jobs.has_key(dirpath):
        return 'counting size'
    d = threads.deferToThread(dhnio.getDirectorySize, dirpath)
    d.addCallback(done, dirpath)
    _Jobs[dirpath] = (d, callback, arg)
    _Dirs[dirpath] = 'counting size'
    return 'counting size'
    
def done(size, dirpath):
    global _Dirs
    global _Jobs
    dhnio.Dprint(6, 'dirsize.done %s %s %s' % (str(size), dirpath.decode(), str(type(dirpath))))
    _Dirs[dirpath] = str(size)
    try:
        (d, cb, arg) = _Jobs.pop(dirpath, (None, None, None))
        if cb:
            cb(dirpath, size, arg)
    except:
        dhnio.DprintException()
    
def get(dirpath, default=''):
    global _Dirs
    return _Dirs.get(dirpath, default)
    
def isjob(dirpath):
    global _Jobs
    return _Jobs.has_key(dirpath)

def getLabel(dirpath):
    global _Dirs
    s = _Dirs.get(dirpath, '')
    if s != 'counting size':
        try:
            return diskspace.MakeStringFromBytes(int(s))
        except:
            return str(s)
    return str(s)
    
def getInBytes(dirpath):
    return diskspace.GetBytesFromString(get(dirpath))     
        
    