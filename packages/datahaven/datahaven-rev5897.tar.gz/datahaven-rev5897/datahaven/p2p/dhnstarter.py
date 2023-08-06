#!/usr/bin/python
#dhnstarter.py
#
#    Copyright DataHaven.Net Ltd. of Anguilla, 2006-2011
#    All rights reserved.
#

import os
import sys
import hashlib
import time
import subprocess

from distutils.dir_util import copy_tree
from twisted.python.win32 import cmdLineQuote

import EasyDialogs

#------------------------------------------------------------------------------

def sharedPath(filename, subdir='logs'):
    sharedDir = os.path.join(
                        #os.path.expanduser('~'),
                        #'Application Data',
                        os.environ['APPDATA'],
                        #'DataHavenNet',
                        'DataHaven.NET',
                        subdir)
    if filename is None:
        return os.path.abspath(sharedDir)
    return os.path.abspath(os.path.join(sharedDir, filename))

LogFilePath = sharedPath('dhnstarter.log', 'logs')
#UpdateLocationURL = 'https://downloads.datahaven.net/'
UpdateLocationURL = 'http://identity.datahaven.net/downloads/'
UpdateFolder = 'windows/'
FilesDigestsFilename = 'info.txt'
FilesDigestsLocalPath = sharedPath('info', 'metadata')
CurrentVersionDigestsFilename = 'version.txt'
CurrentVersionDigestsLocalPath = sharedPath('version', 'metadata')
StarterFilename = os.path.basename(sys.argv[0].lower()) #'dhnstarter.exe'
WGetFilename = 'wget.exe'
WGetLogFilename = sharedPath('wget.log', 'logs')
MainExecutableFilename = 'dhnmain.exe'
StarterFilename = 'dhnstarter.exe'


#ONLY LOWER CASE
ExcludesFiles = [
    'w9xpopen.exe',
    'MSVCR71.dll'.lower(),
    'python25.dll',
    WGetFilename,
    StarterFilename,
    CurrentVersionDigestsFilename,
    FilesDigestsFilename,
    ]


#------------------------------------------------------------------------------

def logwrite(txt, mode='a'):
    global LogFilePath
    fout = open(LogFilePath, mode)
    fout.write(txt)
    fout.close()

def read_file(filename, mode='rb'):
    try:
        file = open(filename, mode)
        data = file.read()
        file.close()
        return data
    except:
        return ''

def make_hash(data):
    return hashlib.md5(data).hexdigest()

def file_hash(filename):
    return make_hash(read_file(filename))

def run_wget(url, filename):
    cmd = '%s --no-check-certificate -o%s -O%s %s' % (WGetFilename, cmdLineQuote(WGetLogFilename), cmdLineQuote(filename), url)
    logwrite('%s\n' % cmd)
    return subprocess.call(cmd, shell=True)

def find_process_win32(applist):
    pidsL = []
    try:
        import win32com.client
        objWMI = win32com.client.GetObject("winmgmts:\\\\.\\root\\CIMV2")
        colProcs = objWMI.ExecQuery("SELECT * FROM Win32_Process")
        for Item in colProcs:
            pid = int(Item.ProcessId)
            if pid == os.getpid():
                continue
            search_str = Item.Caption.lower()
            if Item.CommandLine:
                search_str += Item.CommandLine.lower()
            for app in applist:
                if search_str.find(app) != -1:
                    pidsL.append(pid)
    except:
        logwrite('error in find_process_win32\n')
    return pidsL

def kill_process_win32(pid):
    try:
        from win32api import TerminateProcess, OpenProcess, CloseHandle
        PROCESS_TERMINATE = 1
        handle = OpenProcess(PROCESS_TERMINATE, False, pid)
        TerminateProcess(handle, -1)
        CloseHandle(handle)
    except:
        logwrite('error in kill_process_win32\n')

def stop_all(search_list):
    total_count = 0
    while True:
        count = 0
        appList = find_process_win32(search_list)
        for pid in appList:
            count +=1
            kill_process_win32(pid)
        if len(appList) == 0:
            break
        total_count += 1
        if total_count > 10:
            return 'error killing process '+str(appList)
        time.sleep(1)
    return 0

def launch(show):
    logwrite('launch %s show=%s\n' % (MainExecutableFilename, show))
    try:
        if show:
            subprocess.Popen([MainExecutableFilename, 'show'])
        else:
            subprocess.Popen([MainExecutableFilename,])
    except:
        return 'error starting dhnmain.exe'
    return 0

def main():
    logwrite('main()\n')
    global ExcludesFiles
    #if we need to stop - we kill all running instances and exit
    if sys.argv.count('stop'):
        #we want to check if another instance is running
        return stop_all(['dhnstarter.',
                         'dhnmain.',
                         'dhnview.',
                         'dhn.', ])

    search_list = ['dhnstarter.exe',]
    # if we do not need to stop,
    # but still other instance is running
    # we do not want to work together. EXIT.
    if len(find_process_win32(search_list)) > 0:
        logwrite('another dhnstarter.exe found working')
        return 0

    show = False
    if sys.argv.count('show') or sys.argv.count('install'):
        show = True

    if not show:
        #if dhnmain.exe or dhnview.exe is running - stop it.
        search_list.extend(['dhnmain.',
                            'dhnview.',
                            'dhn.', ])
        res = stop_all(search_list)
        if res != 0:
            return res

    #read file "info"
    src = read_file(FilesDigestsLocalPath, 'r')
    if src == '':
        logwrite('file not found: %s\n' % FilesDigestsLocalPath)
        src = read_file(os.path.join(os.path.dirname(
            os.path.abspath(sys.executable)), FilesDigestsFilename))
        logwrite('take from current folder: %s \n' % FilesDigestsFilename)
    logwrite('info length: ' + str(len(src)) + '\n')

    cur_version = read_file(CurrentVersionDigestsLocalPath, 'r')
    if cur_version == '':
        logwrite('file not found: %s\n' % CurrentVersionDigestsLocalPath)
        cur_version = read_file(os.path.join(os.path.dirname(
            os.path.abspath(sys.executable)), CurrentVersionDigestsFilename))
        logwrite('take from current folder: %s \n' % CurrentVersionDigestsFilename)
    logwrite('current version is: %s\n' % cur_version)

    #if it is not exist, or it is empty - we want to download it from the server
    if src == '':
        url = UpdateLocationURL + FilesDigestsFilename
        logwrite('want to download %s\n' % url)

        if run_wget(url, FilesDigestsLocalPath):
            logwrite('wget error url=%s\n' % url)
            return 1

        if not os.path.isfile(FilesDigestsLocalPath):
            logwrite('file not found %s\n' % FilesDigestsLocalPath)
            return 1

        src = read_file(FilesDigestsLocalPath, 'r')
        if src == '':
            logwrite('error when reading from file %s\n' % FilesDigestsLocalPath)
            return 1

        new_version = make_hash(src)
        # current version was not changed but info file was empty
        # this mean dhn was installed previously
        # we do not want to check files now
        # will do during next start
        if new_version == cur_version:
            logwrite('version was not changed\n')

            # also try to remove info.txt and version.txt in the current folder
            # they can be here because included in the installation release
            # so they needed only during first start of the dhnstarter.exe
            # if we did not start with param "install" - we do not need them at all
            if sys.argv.count('install') == 0:
                try:
                    if os.path.exists('info.txt'):
                        os.remove('info.txt')
                    if os.path.exists('version.txt'):
                        os.remove('version.txt')
                except:
                    logwrite('can not remove info.txt or version.txt from current folder\n')
            return launch(show)

        try:
            fout = open(CurrentVersionDigestsLocalPath, 'w')
            fout.write(new_version)
            fout.close()
        except:
            logwrite('error writing to %s\n' % CurrentVersionDigestsLocalPath)

    #reading files hash values from info.txt
    current_info = {}
    for line in src.strip().split('\n'):
        words = line.split(' ')
        if len(words) < 2:
            continue
        fname = words[1].strip()
        #we do not want to check or download this files:
        if os.path.basename(fname.lower()) in ExcludesFiles:
            continue
        current_info[fname] = words[0].strip()

    logwrite('current info files ' + str(len(current_info)) +'\n')

    #read hash values for all files in the current folder
    local_info = {}
    logwrite('current path:  %s\n' % os.path.abspath('.'))
    # executable_filename = os.path.abspath(sys.argv[0])
    # fullpath = os.path.dirname(executable_filename)
    # fullpath = os.path.abspath('.')
    fullpath = sharedPath('', 'bin')
    logwrite('new path:      %s\n' % fullpath)
    for root, dirs, files in os.walk(fullpath):
        for fname in files:
            abspath = os.path.abspath(os.path.join(root, fname))
            relpath = abspath[len(fullpath)+1:]
            local_info[relpath] = file_hash(abspath)

    logwrite('local files %s\n' % str(len(local_info)) )

    #compare hash values
    download_list = []
    for fpath in current_info.keys():
        #if some file are missing - we want to download it
        if not local_info.has_key(fpath):
            logwrite('%s - missied\n' % fpath)
            download_list.append(fpath)
            continue
        #if some file hash is different - we want to download it and overwrite existing
        if local_info[fpath] != current_info[fpath]:
            logwrite('%s - hash is not the same\n' % fpath)
            download_list.append(fpath)
            continue

    logwrite('files to download: %s\n' % str(len(download_list)))

    download_list.sort()

    if len(download_list) > 0:
        try:
            dlg = None
            dlgshow = False

            if show:
                dlgshow = True

            # if len(download_list) > 1000:
            #     dlgshow = True

            if dlgshow:
                dlg = EasyDialogs.ProgressBar(
                    'Updating DataHaven.NET',
                    len(download_list),
                    '')

            #we want to download needed files
            for path in download_list:
                url = UpdateLocationURL + UpdateFolder + path
                url = url.replace('\\', '/')
                filename = os.path.join('.', path)
                dirname = os.path.dirname(filename)
##                if os.path.exists(filename):
##                    try:
##                        os.remove(filename)
##                    except:
##                        pass
                if not os.path.isdir(dirname):
                    try:
                        os.makedirs(dirname)
                    except:
                        pass

                if dlg:
                    dlg.label( '%s' % (path) )

                filenameWget = filename+'.wget'
                if os.path.isfile(filenameWget):
                    try:
                        os.remove(filenameWget)
                    except:
                        logwrite('wget warning can not remove filename=%s\n' % filenameWget)

                if run_wget(url, filenameWget):
                    logwrite('wget error url=%s filename=%s\n' % (url, filenameWget))

                else:
                    h = file_hash(filenameWget)
                    if h == current_info[path]:
                        try:
                            if os.path.isfile(filename):
                                os.remove(filename)
                                logwrite('REMOVED: %s\n' % path)
                        except:
                            logwrite('can not remove %s\n' % (filename))
                        try:
                            os.rename(filenameWget, filename)
                            logwrite('UPDATED: %s\n' % path)
                        except:
                            logwrite('can not rename %s->%s\n' % (filenameWget, filename))
                    else:
                        logwrite('incorrect file %s :  hash values is not equal\n' % path)

                if dlg:
                    dlg.inc()

            if dlg:
                del dlg
                dlg = None

        except KeyboardInterrupt:
            return 'canceled'

    #finally - start dhnmain.exe and exit
#    os.spawnl(os.P_NOWAIT, MainExecutableFilename, 'show')
    return launch(show)


if __name__ == "__main__":
    if hasattr(sys, 'frozen'):
        executable_filename = os.path.abspath(sys.executable)
    else:
        executable_filename = os.path.abspath(sys.argv[0])
    sharedStarterFilename = sharedPath(StarterFilename, 'bin')
    binDirExist = os.path.isdir(sharedPath(None, 'bin'))

    if not os.path.isdir(sharedPath('', 'bin')):
        os.makedirs(sharedPath('', 'bin'))

    if not os.path.isdir(sharedPath('', 'logs')):
        os.makedirs(sharedPath('', 'logs'))

    if not os.path.isdir(sharedPath('', 'metadata')):
        os.makedirs(sharedPath('', 'metadata'))

    logwrite('started %s. sys.argv:%s \n' % (time.asctime(), str(sys.argv)), 'w')

    logwrite('is bin folder exist? : %s\n' % str(binDirExist))
    logwrite('executable filename is %s\n' % executable_filename)
    logwrite('shared location is     %s\n' % sharedStarterFilename)

    if (not binDirExist) or executable_filename != sharedStarterFilename:
        #if dhn is running - stop it.
        res = stop_all([    'dhnstarter.',
                            'dhnmain.',
                            'dhnview.',
                            'dhn.', ])
        if res != 0:
            logwrite('can not stop dhn: %s\n' % res)
            sys.exit(res)

        logwrite('copy files to %s\n' % sharedPath('', 'bin'))
        copy_tree( os.path.dirname(executable_filename),
                   sharedPath('', 'bin'))

        logwrite('cd to bin\n')
        os.chdir(sharedPath('', 'bin'))

        try:
            os.remove(FilesDigestsLocalPath)
        except:
            logwrite('can not remove %s\n' % FilesDigestsLocalPath)

        exepath = sharedStarterFilename
        cmdargs = [StarterFilename,]
        if sys.argv.count('show') or sys.argv.count('install'):
            cmdargs.append('show')
        logwrite('launch %s cmdargs=%s' % (exepath, str(cmdargs)))
        os.spawnv(os.P_DETACH, exepath, cmdargs)
        sys.exit(0)

    else:
        os.chdir(sharedPath('', 'bin'))

    retcode = main()

    if retcode == 1:
        launch(sys.argv.count('show') or sys.argv.count('install'))

    elif retcode != 0:
        logwrite('retcode='+retcode+'\n')






