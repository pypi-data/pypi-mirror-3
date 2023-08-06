#!/usr/bin/python
#backup_tar.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#  We want a pipe output or input so we don't need to store intermediate data.
#
#  The popen starts another process.  That process can block but we don't.
#  backup.py only takes data from this pipe when it is ready.

import os
import subprocess


import lib.nonblocking as nonblocking
import lib.dhnio as dhnio


# Returns file descriptor for process that makes tar archive
def backuptar(directorypath, recursive_subfolders=True):
    source_dir, archive_name = os.path.split(directorypath)
    subdirs = 'subdirs'
    if not recursive_subfolders:
        subdirs = 'nosubdirs'
    dhnio.Dprint(6, "backup_tar.backuptar source_dir=%s  archive_name=%s %s" % (source_dir, archive_name, subdirs))
    if dhnio.Windows():
        if dhnio.isFrozen():
            commandpath = 'dhnbackup.exe'
            cmdargs = [commandpath, subdirs, directorypath]
        else:
            commandpath = 'dhnbackup.py'
            cmdargs = ['python.exe', commandpath, subdirs, directorypath]
    else:
        commandpath = 'dhnbackup.py'
        cmdargs = ['python', commandpath, subdirs, directorypath]

    if not os.path.isfile(commandpath):
        dhnio.Dprint(1, 'backup_tar.backuptar ERROR %s not found' % commandpath)
        return None

    dhnio.Dprint(6, "backup_tar.backuptar cmdstr=" + str(cmdargs))
    try:
        if dhnio.Windows():
            import win32process
            p = nonblocking.Popen(
                cmdargs,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=False,
                creationflags = win32process.CREATE_NO_WINDOW,)
        else:
            p = nonblocking.Popen(
                cmdargs,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=False,)
    except:
        dhnio.Dprint(1, 'backup_tar.backuptar ERROR executing: ' + str(cmdargs) + str(dhnio.formatExceptionInfo()))
        return None

    return p

def test_tar2(backuppath, outputpath):
##        print "test_tar2 starting"
##        inputfile=backuptar(backuppath)
##        input=inputfile.read()
        inputpipe = backuptar(backuppath)
        input=inputpipe.stdout.read()
        dhnio.WriteFile(outputpath, input)
##        print "test_tar2 finished"

def test_tar3(backuppath, outputpath):
        print "test_tar3 starting"
##        inputfile=backuptar(backuppath)
##        inputfd=inputfile.fileno()
##        misc.makeNonBlocking(inputfd)
        inputpipe = backuptar(backuppath)
        inputpipe.make_nonblocking()
##        misc.makeNonBlocking(inputpipe.stdout.fileno())
        print "test_tar3 starting 2"
        outfile=open(outputpath,"wb")
        newchunk="x"
        ateof=0
        print "file open and len is ", len(newchunk)
        print "test_tar3 starting loop"
        while (True):
            try:
##                ready = select.select([inputfd],[],[]) # wait for input
##                print "test_tar3 finished select"
##                if (ateof == 0 and inputfd in ready[0]):
##                print 'misc.pipeReadyToRead(inputpipe))'
##                if  (misc.pipeReadyToRead(inputpipe)):
                if (inputpipe.state() == nonblocking.PIPE_CLOSED):
                    break
                if (inputpipe.state() == nonblocking.PIPE_READY2READ):
                    print "test_tar3 ready for read "
##                    newchunk = os.read(inputfd, 1000)
##                    newchunk = misc.pipeRead(inputpipe, 1000)
                    newchunk = inputpipe.recv(1000)
                    lnc=len(newchunk)
                    print "test_tar3 finished read  len = ", lnc
                    print "test_tar3 going to do if "
                    if lnc == 0:
                        print "test_tar3 got zero length read so ateof"
                        break
                    else:
                        print "test_tar3 doing write ", lnc
                        outfile.write(newchunk)
                        print "test_tar3 wrote ", lnc
            except:
                print "test_tar3 except"
                break
        # os.close(inputfd)

def testall():
        print "testall doing rm"
        if dhnio.Linux():
            os.system("/bin/rm /tmp/test*.bz2 ")
            inputdir = "/usr/share/man"
        else:
##            os.system("del /Q c:\\work\\projects\\p2p\\tmp\\*")
            inputdir = "c:\\work\\projects\\p2p\\usr\\share"

#        inputdir = "/home/vince/man"
        source_dir, archive_name = os.path.split(inputdir)

        if dhnio.Linux():
            print "testall making base file"
            os.system("cd %s; /bin/tar jcf %s %s" % (source_dir, "/tmp/test0.bz2", archive_name))      # after test with: tar tf /tmp/test0.bz2
            os.system("../dhnbackup.py %s > /tmp/test1.bz2" % inputdir )
            print "testall calling test2"
            test_tar2(inputdir, "/tmp/test2.bz2")
            print "doing diff for 2"
            os.system("diff /tmp/test1.bz2     /tmp/test2.bz2")
            test_tar3(inputdir, "/tmp/test3.bz2")
            print "doing diff for 3"
            os.system("diff /tmp/test1.bz2     /tmp/test3.bz2")
        else:
            #os.system("cd %s; /bin/tar jcf %s %s" % (source_dir, "/tmp/test1.bz2", archive_name))
            print "testall making base file"
            os.system("..\\dhnbackup.py %s > c:\\work\\projects\\p2p\\tmp\\test1.tar" % inputdir )
            print "testall calling test2"
            test_tar2(inputdir, "c:\\work\\projects\\p2p\\tmp\\test2.tar")
            print "testall calling test3"
            test_tar3(inputdir, "c:\\work\\projects\\p2p\\tmp\\test3.tar")

        for filenum in (0,1,2,3):
            if dhnio.Linux():
                filename= "/tmp/test%d.bz2" % filenum
                #filename= "/tmp/test%d.tar" % filenum
            else:
                filename= "c:\\work\\projects\\p2p\\tmp\\test%d.tar" % filenum
            size=os.path.getsize(filename)
            print  filename,  "  ", size


if __name__ == "__main__":
    testall()


