#!/usr/bin/python
#dhnmain.py
#
#
#    Copyright DataHaven.Net Ltd. of Anguilla, 2006-2011
#    All rights reserved.
#
#

import os
import sys
import time

#-------------------------------------------------------------------------------

def copyright():
    print 'Copyright DataHaven.Net Ltd. of Anguilla, 2006-2011.'
    print 'All rights reserved.'

def find_comments(output):
    if output is None or str(output).strip() == '':
        return ['empty output']
    if not isinstance(output, str):
        return [output.getErrorMessage()]
    import re
    return re.findall('\<\!--\[begin\] (.+?) \[end\]--\>', output, re.DOTALL)


def run(UI='', options=None, args=None, overDict=None):
    import lib.dhnio as dhnio
    dhnio.Dprint(6, 'dhnmain.run sys.path=%s' % str(sys.path))

    try:
        from dhnicon import USE_TRAY_ICON
        dhnio.Dprint(4, 'dhnmain.run USE_TRAY_ICON='+str(USE_TRAY_ICON))
        if USE_TRAY_ICON:
            from twisted.internet import wxreactor
            wxreactor.install()
    except:
        USE_TRAY_ICON = False
        dhnio.DprintException()

    if USE_TRAY_ICON:
        icon_filename = 'datahaven-windows.ico'
        if dhnio.Linux():
            icon_filename = 'datahaven-linux.png'
        import dhnicon
        icon_path = str(os.path.abspath(os.path.join(dhnio.getExecutableDir(), 'icons', icon_filename)))
        dhnio.Dprint(4, 'dhnmain.run call dhnicon.init(%s)' % icon_path)
        dhnicon.init(icon_path)
        def _tray_control_func(cmd):
            if cmd == 'exit':
                import dhninit
                dhninit.shutdown_exit()
        dhnicon.SetControlFunc(_tray_control_func)

    dhnio.Dprint(4, 'dhnmain.run want to import twisted.internet.reactor')
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing reactor in dhnmain.py\n')

    import lib.settings as settings
    if overDict:
        settings.override_dict(overDict)
    settings.init()
    if not options or options.debug is None:
        dhnio.SetDebug(settings.getDebugLevel())

    if dhnio.EnableLog and dhnio.LogFile is not None:
        dhnio.Dprint(2, 'dhnmain.run want to switch log files')
        if dhnio.Windows() and dhnio.isFrozen():
            dhnio.StdOutRedirectingStop()
        dhnio.CloseLogFile()
        dhnio.OpenLogFile(settings.MainLogFilename()+'-'+time.strftime('%y%m%d%H%M%S')+'.log')
        if dhnio.Windows() and dhnio.isFrozen():
            dhnio.StdOutRedirectingStart()

    dhnio.Dprint(2,"dhnmain.run UI=[%s]" % UI)

    if dhnio.Debug(10):
        dhnio.Dprint(0, '\n' + dhnio.osinfofull())

    dhnio.Dprint(4, 'dhnmain.run want to start automats')

    #import automats
    #automats.initializer('run', UI)

    import initializer
    initializer.A('run', UI)

    #reactor.addSystemEventTrigger('before', 'shutdown', lambda : initializer.A('reactor-stopped'))

    dhnio.Dprint(2, 'dhnmain.run calling reactor.run()')
    reactor.run()
    dhnio.Dprint(2, 'dhnmain.run reactor stopped')
    # this will call initializer() without reactor.callLater(0, ... )
    # we do not have any timers initializer() so do not worry
    initializer.A('reactor-stopped', use_reactor = False)

    dhnio.Dprint(2, 'dhnmain.run finished, EXIT')

    dhnio.CloseLogFile()

    if dhnio.Windows() and dhnio.isFrozen():
        dhnio.StdOutRedirectingStop()





def run_url_command(address, options=None, args=None, overDict=None):
    import lib.dhnio as dhnio
    import lib.settings as settings
    from twisted.web.client import getPage
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing twisted reactor in dhnmain.py\n')
    local_port = int(dhnio.ReadBinaryFile(settings.LocalPortFilename()))
    url = 'http://127.0.0.1:'+str(local_port)+'/'+address
    dhnio.Dprint(2, 'dhnmain.run_url_command url='+url)
    def _eb(x):
        print x.getErrorMessage()
        reactor.stop()
    d = getPage(url)
    d.addErrback(_eb)
    return d

def cmd_msg(opts, args, overDict):
    import lib.dhnio as dhnio
    if len(dhnio.find_process(['dhnmain.exe', 'dhnmain.py', 'dhnwc.py', 'dhn.py', ])) > 0:
        dhnio.Dprint(2, 'dhnmain.main DHN already running. EXIT.')
        return 1
    idurl = args[1]
    text = ' '.join(args[2:])
    dhnio.Dprint(2, 'dhnmain.cmd_msg to: ' + idurl)
    dhnio.Dprint(2, 'dhnmain.cmd_msg text:')
    dhnio.Dprint(0, text)
    import message
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing twisted reactor in dhnmain.py\n')

    def _send():
        dhnio.Dprint(2, 'dhnmain.cmd_msg._send')
        msgbody = message.MakeMessage(idurl, 'dhnmain short message', text)
        message.SendMessage(idurl, msgbody)
        message.SaveMessage(msgbody)

    dhnio.Dprint(2, 'dhnmain.cmd_msg want to import dhninit')
    import dhninit
    dhninit.initDoneFunc = _send

    UI = ''
    dhnio.Dprint(2, 'dhnmain.cmd_msg want to call dhninit.run("%s")' % UI)
    dhninit.run(UI, opts, args, overDict)
    dhnio.Dprint(2, 'dhnmain.cmd_msg will call reactor.run()')
    reactor.run()
    return 0

def cmd_register(opts, args, overDict):
    import lib.dhnio as dhnio
    if len(dhnio.find_process(['dhnmain.exe', 'dhnmain.py', 'dhnwc.py', 'dhn.py', ])) > 0:
        dhnio.Dprint(2, 'dhnmain.main DHN already running. EXIT.')
        return 1
    import lib.settings as settings
    import lib.tmpfile as tmpfile
    import install
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing twisted reactor in dhnmain.py\n')
    name = args[1]
    dhnio.Dprint(2, 'dhnmain.cmd_register ' + name)
    if overDict:
        settings.override_dict(overDict)
    settings.init()
    tmpfile.init(settings.getTempDir())
    def _progress(msg):
        dhnio.Dprint(2, 'INSTALL: %s' % msg)
    def _finish(x):
        dhnio.Dprint(2, 'INSTALL result is: %s' % str(x))
        reactor.callLater(1, reactor.stop)
    install.SetProgressNotifyCallback(_progress)
    res = install.RegisterNewUser(name)
    res.addCallback(_finish)
    reactor.run()

def cmd_recover(opts, args, overDict):
    import lib.dhnio as dhnio
    import lib.nameurl as nameurl
    import lib.settings as settings
    import install
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing twisted reactor in dhnmain.py\n')
    pk_filename = args[1]
    dhnio.Dprint(2, 'dhnmain.cmd_recover private key file name is ' + pk_filename)
    if overDict:
        settings.override_dict(overDict)
    settings.init()
    src = dhnio.ReadTextFile(pk_filename)
    if not src:
        dhnio.Dprint(2, 'dhnmain.cmd_recover ERROR wrong private key')
        return 1
    try:
        lines = src.split('\n')
        idurl = lines[0]
        txt = '\n'.join(lines[1:])
        fname = nameurl.UrlFilename(idurl)
        newurl = nameurl.FilenameUrl(fname)
        if idurl != newurl:
            idurl = ''
            txt = src
    except:
        idurl = ''
        txt = src

    if not idurl:
        dhnio.Dprint(2, 'dhnmain.cmd_recover ERROR wrong private key')
        return 1
    res = install.RecoverExistingUser(idurl, txt)
    res.addCallback(lambda x: reactor.stop())
    reactor.run()
    return 0

def cmd_backups(opts, args, overDict):
    import lib.dhnio as dhnio
    import lib.diskspace as diskspace
    import lib.settings as settings
    import lib.misc as misc
    import backup_db
    import backupshedule
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing twisted reactor in dhnmain.py\n')
    if overDict:
        settings.override_dict(overDict)
    settings.init()

    if args[1] == 'list':
        def _list_cb(src):
            for s in find_comments(src):
                print unicode(s)
            reactor.stop()
        run_url_command('backups', opts, args, overDict).addCallback(_list_cb)
        reactor.run()
        return 0

##    elif args[1] == 'status':
##        backup_db.init()
##        total_space = 0
##        for backupDir in backup_db.GetBackupDirectories():
##            is_running = backup_db.IsBackupRunning(backupDir)
##            recentBackupID, totalBackupsSize, lastBackupStatus = backup_db.GetDirectoryInfo(backupDir)
##            backupSubdirectories = backup_db.GetDirectorySubfoldersInclude(backupDir)
##            try:
##                dirSizeFloat = float(dhnio.getDirectorySize(backupDir, backupSubdirectories))
##                totalBackupSizeFloat = float(totalBackupsSize)
##            except:
##                continue
##            dirSizeString = diskspace.MakeStringFromBytes(dirSizeFloat)
##            if dirSizeFloat == 0:
##                dirSizeString = 'empty'
##            total_space += totalBackupSizeFloat
##            dhnio.Dprint(0, '%s   %s %s %s' % (backupDir.ljust(30), recentBackupID, str(totalBackupsSize), dirSizeString))
##        dhnio.Dprint(0, 'total space: ' + str(total_space))
##        return 0

    elif args[1] == 'remove':
        url = 'backups?action=delete&backupdir='+misc.pack_url_param(os.path.abspath(args[2]))
        def _remove_cb(src):
            for s in find_comments(src):
                print unicode(s)
            reactor.stop()
        run_url_command(url, opts, args, overDict).addCallback(_remove_cb)
        reactor.run()
        return 0

    elif args[1] == 'add':
        if not os.path.isdir(os.path.abspath(args[2])):
            print 'Folder %s not exist' % args[2]
            return 1
        url = 'backups?action=dirselected&opendir='+misc.pack_url_param(os.path.abspath(args[2]))
        def _add_cb(src):
            for s in find_comments(src):
                print unicode(s)
            reactor.stop()
        run_url_command(url, opts, args, overDict).addCallback(_add_cb)
        reactor.run()
        return 0

    elif args[1] == 'shedule':
        if not os.path.isdir(os.path.abspath(args[2])):
            print 'Folder %s not exist' % args[2]
            return 1
        backupDir = os.path.abspath(args[2])
        shed = backupshedule.unpack(args[3])
        if shed is None:
            print backupshedule.format()
            return 1
        def _set_shedule_cb(src):
            for s in find_comments(src):
                print unicode(s)
            reactor.stop()
        url = 'backupshedule?action=save&backupdir=%s&type=%s&interval=%s&time=%s&details=%s' % (
            misc.pack_url_param(backupDir),
            shed['type'],
            shed['interval'],
            shed['time'],
            misc.pack_url_param(shed['details']),)
        run_url_command(url, opts, args, overDict).addCallback(_set_shedule_cb)
        reactor.run()
        return 0

    elif args[1] == 'start':
        if not os.path.isdir(os.path.abspath(args[2])):
            print 'Folder %s not exist' % args[2]
            return 1
        url = 'backups?action=start&backupdir='+misc.pack_url_param(os.path.abspath(args[2]))
        def _start_cb(src):
            for s in find_comments(src):
                print unicode(s)
            reactor.stop()
        run_url_command(url, opts, args, overDict).addCallback(_start_cb)
        reactor.run()
        return 0


##        if len(dhnio.find_process(['dhnmain.exe', 'dhnmain.py', 'dhnwc.py', 'dhn.py', ])) == 0:
##            dhnio.Dprint(2, 'dhnmain.main calling run("show")')
##            run('show', opts, args, overDict)
##            return 0
##        def _wait_suppliers_loop():
##            activeCount = 0
##            for i in range(0, settings.getCentralNumSuppliers()):
##                if transport_control.ContactIsAlive(contacts.getSupplierID(i)):
##                    activeCount += 1
##            need_suppliers = eccmap.Current().suppliers_number - eccmap.Current().CorrectableErrors
##            if activeCount >= need_suppliers:
##                reactor.callLater(0.5, _start, args[2])
##            else:
##                reactor.callLater(5, _wait_suppliers_loop)
##            dhnio.Dprint(2, 'dhnmain.cmd_backup._wait_suppliers_loop %s/%s' % (str(activeCount), str(need_suppliers)))
##        def _done(x):
##            dhnio.Dprint(2, 'dhnmain.cmd_backup._done ' + str(x))
##            reactor.stop()
##        def _failed(x):
##            dhnio.Dprint(2, 'dhnmain.cmd_backup._failed ' + str(x))
##            reactor.stop()
##        def _start(backupdir):
##            dhnio.Dprint(2, 'dhnmain.cmd_backup._start ' + backupdir)
##            #bid = "F"+time.strftime("%Y%m%d%I%M%S%p")
##            bid = misc.NewBackupID()
##            filename = "DataHaven-" + str(bid) + ".tar"
##            backup_monitor.AddBackupInProcess(bid)
##            recursive_subfolders = backup_db.GetDirectorySubfoldersInclude(backupdir)
##            dir_size = dhnio.getDirectorySize(backupdir, recursive_subfolders)
##            backup_db.AddDirBackup(backupdir, bid, 'in process', str(dir_size), str(time.time()), '')
##            result = dobackup.dobackup(bid, backupdir, filename, recursive_subfolders)
##            if result is not None:
##                result.addCallback(_done)
##                result.addErrback(_failed)
##            else:
##                reactor.callLater(0.5, _failed, bid)
##        import dhninit
##        dhninit.initDoneFunc = _wait_suppliers_loop
##        import backup_monitor
##        import dobackup
##        import lib.transport_control as transport_control
##        import lib.contacts as contacts
##        import lib.eccmap as eccmap
##        UI = ''
##        dhnio.Dprint(2, 'dhnmain.cmd_backup want to call dhninit.run("%s")' % UI)
##        dhninit.run(UI, opts, args, overDict)
##        dhnio.Dprint(2, 'dhnmain.cmd_backup will call reactor.run()')
##        reactor.run()
##        return 0

    else:
        dhnio.Dprint(2, 'dhnmain.cmd_backup ERROR wrong command line arguments')
        return 1

    return 1


def cmd_restore(opts, args, overDict):
    import lib.dhnio as dhnio
    import lib.diskspace as diskspace
    import lib.settings as settings
    import lib.misc as misc
    import backup_db
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing twisted reactor in dhnmain.py\n')
    if overDict:
        settings.override_dict(overDict)
    settings.init()

    if args[1] == 'list':
        def _list_cb(src):
            for s in find_comments(src):
                print unicode(s)
            reactor.stop()
        run_url_command('restore', opts, args, overDict).addCallback(_list_cb)
        reactor.run()
        return 0
    elif args[1] == 'start':
        def _start_cb(src):
            for s in find_comments(src):
                print unicode(s)
            reactor.stop()
        url = 'restore?action=restore&backupid=%s' % args[2]
        run_url_command(url, opts, args, overDict).addCallback(_start_cb)
        reactor.run()
        return 0
    else:
        dhnio.Dprint(2, 'dhnmain.cmd_restore ERROR wrong command line arguments')
        return 2


def cmd_suppliers(opts, args, overDict):
    from twisted.internet import task
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing twisted reactor in dhnmain.py\n')
    import lib.dhnio as dhnio
    import lib.misc as misc
    import lib.nameurl as nameurl
    import lib.settings as settings
    import lib.contacts as contacts
    import lib.dhnpacket as dhnpacket
    import lib.packetid as packetid
    import lib.commands as commands
    import lib.transport_control as transport_control
    import centralservice
    import dhninit
    if overDict:
        settings.override_dict(overDict)
    settings.init()
    contacts.init()
    if args[1] == 'list':
        dhnio.Dprint(0,'[User name]            [ID URL]')
        for supid in contacts.getSupplierIDs():
            name = nameurl.GetName(supid)
            dhnio.Dprint(0, '%s   %s' % (name.ljust(20), supid))
        dhnio.Dprint(0, '')
        return 0
    elif args[1] == 'replace' or args[1] == 'change':
        def _acked(packet):
            dhnio.Dprint(4, 'dhnmain.cmd_supplier._acked')
            dhnio.Dprint(0, '[User name]            [ID URL]')
            for supid in contacts.getSupplierIDs():
                name = nameurl.GetName(supid)
                dhnio.Dprint(0, '%s   %s' % (name.ljust(20), supid))
            dhnio.Dprint(0, '')
            reactor.stop()
        def _check_suppliers():
            dhnio.Dprint(4, 'dhnmain.cmd_supplier._check_suppliers')
            dhnio.Dprint(0, '[User name]            [ID URL]')
            for supid in contacts.getSupplierIDs():
                name = nameurl.GetName(supid)
                dhnio.Dprint(0, '%s   %s' % (name.ljust(20), supid))
            dhnio.Dprint(0, '')
            reactor.stop()
        def _inbox(packet, proto, host):
            dhnio.Dprint(4, 'dhnmain.cmd_supplier._inbox ' + str(packet))
            if packet.Command == commands.ListContacts():
                reactor.callLater(1, _check_suppliers)
        def _send(num, newidurl=None):
            dhnio.Dprint(4, 'dhnmain.cmd_supplier._send num=' + str(num))
            transport_control.AddInboxCallback(_inbox)
            if newidurl is None:
                pid = centralservice.SendReplaceSupplier(num, True)
            else:
                pid = centralservice.SendChangeSupplier(num, newidurl, True)
            #transport_control.RegisterInterest(_acked, misc.getLocalID(), pid)
            if pid is None:
                reactor.stop()
        def _init_done():
            dhnio.Dprint(4, 'dhnmain.cmd_supplier._init_done')
            nameORidurl = args[2]
            if not nameORidurl.startswith('http://'):
                nameORidurl = misc.username2idurl(nameORidurl)
            num = contacts.numberForSupplier(nameORidurl)
            newidurl = None
            if args[1] == 'change':
                newidurl = args[3]
                if not newidurl.startswith('http://'):
                    newidurl = misc.username2idurl(newidurl)
            dhnio.Dprint(4, 'dhnmain.cmd_supplier._init_done %s num=%s' % (nameORidurl, str(num)))
            reactor.callLater(5, _send, num, newidurl)
        dhninit.initDoneFunc = _init_done
        dhninit.run('', opts, args, overDict)
        reactor.run()
    elif args[1] == 'status':
        def _status_cb(src):
            for s in find_comments(src):
                print unicode(s)
            reactor.stop()
        run_url_command('suppliers', opts, args, overDict).addCallback(_status_cb)
        reactor.run()
        return 0
    elif args[1] == 'call':
        def _print(src):
            for s in find_comments(src):
                print unicode(s)
            print '-----------------------------------'
        def _wait(src):
            run_url_command('suppliers', opts, args, overDict).addCallback(_print)
            reactor.callLater(10, _wait, '')
        run_url_command('suppliers?action=call', opts, args, overDict).addCallback(_wait)
        reactor.run()
        return 0
    else:
        dhnio.Dprint(2, 'dhnmain.cmd_suppliers ERROR wrong command line arguments')
        return 2
##        def _status_loop():
##            dhnio.Dprint(0, '-------------------------------')
##            for supid in contacts.getSupplierIDs():
##                name = nameurl.GetName(supid)
##                s = ''
##                if transport_control.ContactIsAlive(supid):
##                    s = 'connected'
##                dhnio.Dprint(0, '%s   %s' % (name.ljust(20), s))
##            dhnio.Dprint(0, '')
##        def _init_cb():
##            dhnio.Dprint(4, 'dhnmain.cmd_supplier._init_cb')
##            for supid in contacts.getSupplierIDs():
##                LocalIdentity = misc.getLocalIdentity()
##                data = LocalIdentity.serialize()
##                packet = dhnpacket.dhnpacket(
##                    commands.Identity(),
##                    misc.getLocalID(),
##                    misc.getLocalID(),
##                    packetid.UniqueID(),
##                    data,
##                    supid,)
##                transport_control.outbox(packet, True)
##                del packet
##            t = task.LoopingCall(_status_loop)
##            t.start(10)
##        transport_control.init(_init_cb)
##        reactor.run()


def cmd_tc(opts, args, overDict):
    import lib.dhnio as dhnio
    import lib.settings as settings
    import lib.transport_control as transport_control
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing twisted reactor in dhnmain.py\n')
    if overDict:
        settings.override_dict(overDict)
    settings.init()
    if args[1] == 'init':
        dhnio.Dprint(2, 'dhnmain.cmd_tc will call transport_control.init()')
        transport_control.init()
        reactor.run()
    elif args[1] == 'ping':
        from twisted.internet import task
        import lib.misc as misc
        import lib.dhnpacket as dhnpacket
        import lib.packetid as packetid
        import lib.commands as commands
        import lib.contacts as contacts
        idurl = args[2]
        if not idurl.startswith('http://'):
            idurl = misc.username2idurl(idurl)
        interval = float(args[3])
        dhnio.Dprint(2, 'dhnmain.cmd_tc want to ping %s' % idurl)
        def _loop():
            dhnio.Dprint(6, 'dhnmain.cmd_tc._loop')
            LocalIdentity = misc.getLocalIdentity()
            data = LocalIdentity.serialize()
            packet = dhnpacket.dhnpacket(
                commands.Identity(),
                misc.getLocalID(),
                misc.getLocalID(),
                packetid.UniqueID(),
                data,
                idurl,)
            transport_control.outbox(packet, True)
            del packet
        def _init_cb():
            dhnio.Dprint(4, 'dhnmain.cmd_tc._init_cb')
            t = task.LoopingCall(_loop)
            t.start(interval)
        contacts.init()
        transport_control.init(_init_cb)
        reactor.run()
    else:
        dhnio.Dprint(2, 'dhnmain.cmd_tc ERROR wrong command line arguments')
        return 2
    return 0

def cmd_tcp(opts, args, overDict):
    import lib.dhnio as dhnio
    import lib.transport_tcp as transport_tcp
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing twisted reactor in dhnmain.py\n')
    if args[1] == 'receive':
        port = args[2]
        dhnio.Dprint(2, 'dhnmain.cmd_tcp receive on port ' + port)
        transport_tcp.receive(port)
        reactor.run()
    elif args[1] == 'send':
        host = args[2]
        port = args[3]
        filename = args[4]
        dhnio.Dprint(2, 'dhnmain.cmd_tcp send to %s:%s filename=[%s] ' % (host, port, filename))
        def _send(x):
            dhnio.Dprint(2, 'dhnmain.cmd_tcp result=[%s]' % str(x))
            reactor.stop()
        r = transport_tcp.send(filename, host, port)
        r.addBoth(_send)
        reactor.run()
    else:
        dhnio.Dprint(2, 'dhnmain.cmd_tcp ERROR wrong command line arguments')
        return 2
    return 0

def cmd_q2q(opts, args, overDict):
    import lib.dhnio as dhnio
    import lib.settings as settings
    import lib.transport_q2q as transport_q2q
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing twisted reactor in dhnmain.py\n')
    if overDict:
        settings.override_dict(overDict)
    settings.init()
    if args[1] == 'register':
        userhost = args[2]
        password = args[3]
        dhnio.Dprint(2, 'dhnmain.cmd_q2q register new user ' + userhost)
        def init_callback(x):
            dhnio.Dprint(4, 'dhnmain.cmd_q2q.init_callback: ' + str(x))
            transport_q2q.register(userhost, password).addBoth(lambda x: reactor.stop())
        transport_q2q.init(False).addBoth(init_callback)
        reactor.run()
    elif args[1] == 'receive':
        dhnio.Dprint(2, 'dhnmain.cmd_q2q receive')
        def init_callback(x):
            dhnio.Dprint(4, 'dhnmain.cmd_q2q.init_callback: ' + str(x))
            transport_q2q.receive()
        transport_q2q.init(False).addBoth(init_callback)
        reactor.run()
    elif args[1] == 'send':
        to_userhost = args[2]
        filename = args[3]
        timeout = None
        if len(args) > 4:
            timeout = int(args[4])
        dhnio.Dprint(2, 'dhnmain.cmd_q2q send to %s file %s' % (to_userhost, filename))
        def init_callback(x):
            dhnio.Dprint(4, 'dhnmain.cmd_q2q.init_callback: ' + str(x))
            if timeout:
                t = LoopingCall(transport_q2q.send, to_userhost, filename)
            else:
                transport_q2q.send(to_userhost, filename).addBoth(lambda x: reactor.stop())
        transport_q2q.init(False).addBoth(init_callback)
        reactor.run()
    elif args[1] == 'clear':
        transport_q2q.clear_local_db(settings.Q2QDir())
    else:
        dhnio.Dprint(2, 'dhnmain.cmd_tcp ERROR wrong command line arguments')
        return 2
    return 0

#------------------------------------------------------------------------------

def usage():
    return '''usage: datahaven [options] [command] [arguments]
Commands:
  show
  stop
  register <account name>
  recover <private-key-filename>
  backup list
  backup start <folder>
  backup add <folder>
  backup remove <folder>
  backup shedule <folder> <shedule in compact format>
  restore list
  restore start <backup ID> [location]
  restore delete <backup ID>
  suppliers list
  suppliers status
  suppliers call
  supplier replace <username or idurl>
  msg <idurl> <text>
  tc init
  tc ping <username or idurl> <interval>
  tcp send <host> <port> <filename>
  tcp receive <port>
  q2q register <username@q2q-server> <password>
  q2q receive
  q2q send <to_username@q2q-server> <filename> [timeout]
  q2q clear
  http receive
  http send
  help
'''


def help():
    return '''usage: datahaven [options] [command] [arguments]

Commands:
  show                  execute the programm and show the main window

  stop                  stop all datahaven instances if found

  register <account name>
                        generate a new private key and register new account

  recover <private-key-filename>
                        recover existing account with your private key file


  backup list           show list of your backup folders

  backup start <folder> start a new backup of the given folder

  backup add <folder>   add backup folder, but not start new backup

  backup remove <folder>
                        remove all backups of the folder

  backup shedule <folder> <shedule in compact format>
                        set a shedule for a folder to
                        start backups automaticaly


  restore list          show backups ready to be restored

  restore <backup ID> [location]
                        restore a given backup


  suppliers list        show list of your suppliers

  suppliers status      show current status of your suppliers

  suppliers call        send a packets to checks out who is alive
                        press ^C to exit

  supplier replace <username or idurl>
                        replace a single supplier with new one


  msg <idurl> <text>    send a short message to another user and exit


  tc init               call "transport_control.init()"

  tc ping <username or idurl> <interval>
                        call "transport_control.init()"
                        and start sending packet Identity
                        to given user periodically


  tcp send <host> <port> <filename>
                        call "transport_tcp.send()"
                        send a file using transport_tcp

  tcp receive <port>    call "transport_tcp.receive()"
                        transport_tcp will start listening specific port


  q2q register <username@q2q-server> <password>
                        call "transport_q2q.register()"
                        register new q2q user
                        and write username and password to local config

  q2q receive           call "transport_q2q.receive()"
                        start receiving files using transport_q2q
                        you need to be registered first

  q2q send <to_username@q2q-server> <filename> [timeout]
                        call "transport_q2q.send()"
                        send a file to specific user
                        you need to be registered first

  q2q clear             call "transport_q2q.clear()"
                        remove your username and password from local config


  http receive          call "transport_http.receive()"

  http send             call "transport_http.send()"

'''

def parser():
    from optparse import OptionParser, OptionGroup
    parser = OptionParser(usage=usage())
    group = OptionGroup(parser, "Log")
    group.add_option('-d', '--debug',
                        dest='debug',
                        type='int',
                        help='set debug level',)
    group.add_option('-q', '--quite',
                        dest='quite',
                        action='store_true',
                        help='quite mode, do not print any messages to stdout',)
    group.add_option('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        help='verbose mode, print more messages',)
    group.add_option('-n', '--no-logs',
                        dest='no_logs',
                        action='store_true',
                        help='do not use logs',)
    group.add_option('-o', '--output',
                        dest='output',
                        type='string',
                        help='print log messages to the file',)
    group.add_option('-t', '--tempdir',
                        dest='tempdir',
                        type='string',
                        help='set location for temporary files (default is /tmp/dhn)',)
    group.add_option('--twisted',
                        dest='twisted',
                        action='store_true',
                        help='show twisted log messages too',)
    parser.add_option_group(group)


    group = OptionGroup(parser, "Network")
    group.add_option('--tcp-port',
                        dest='tcp_port',
                        type='int',
                        help='set tcp port number for incoming connections',)
    group.add_option('--no-upnp',
                        dest='no_upnp',
                        action='store_true',
                        help='do not use UPnP',)
    group.add_option('--no-q2q',
                        dest='no_q2q',
                        action='store_true',
                        help='do not use transport_q2q',)
    group.add_option('--no-cspace',
                        dest='no_cspace',
                        action='store_true',
                        help='do not use transport_cspace',)
    parser.add_option_group(group)

    return parser


def override_options(opts, args):
    overDict = {}
    if opts.tcp_port:
        overDict['transport.transport-tcp.transport-tcp-port'] = str(opts.tcp_port)
    if opts.no_upnp:
        overDict['other.upnp-enabled'] = 'False'
    if opts.no_q2q:
        overDict['transport.transport-q2q.transport-q2q-enable'] = 'False'
    if opts.no_cspace:
        overDict['transport.transport-cspace.transport-cspace-enable'] = 'False'
    if opts.tempdir:
        overDict['folder.folder-temp'] = opts.tempdir
    if opts.debug or str(opts.debug)=='0':
        overDict['logs.debug-level'] = str(opts.debug)
    return overDict


def main():
    try:
        import lib.dhnio as dhnio
    except:
        dirpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        sys.path.insert(0, os.path.abspath('datahaven'))
        sys.path.insert(0, os.path.abspath(os.path.join(dirpath, '..')))
        sys.path.insert(0, os.path.abspath(os.path.join(dirpath, '..', '..')))
        try:
            import lib.dhnio as dhnio
        except:
            return 1

    dhnio.LifeBegins()

    dhnio.InstallLocale()

    (opts, args) = parser().parse_args()

    if opts.no_logs:
        dhnio.DisableLogs()

    logpath = ''
    if dhnio.Windows():
        #logpath = os.path.join(os.path.expanduser('~'), 'Application Data', 'DataHavenNet', 'logs', 'dhnmainstart.log')
        #logpath = os.path.join(os.path.expanduser('~'), 'Application Data', 'DataHaven.NET', 'logs', 'dhnmainstart.log')
        logpath = os.path.join(os.environ['APPDATA'], 'DataHaven.NET', 'logs', 'dhnmainstart.log')
#        if dhnio.isFrozen():
#            if not opts.verbose and not opts.quite:
#                opts.quite = True

    if dhnio.Linux():
        logpath = os.path.join(os.path.expanduser('~'), 'datahavennet', 'logs', 'dhnmainstart.log')

    if opts.output:
        logpath = opts.output

    if opts.debug or str(opts.debug) == '0':
        dhnio.SetDebug(opts.debug)

    if opts.quite and not opts.verbose:
        dhnio.DisableOutput()
    else:
        if logpath != '':
            dhnio.OpenLogFile(logpath)
            dhnio.Dprint(2, 'dhnmain.main log file opened ' + logpath)
            if dhnio.Windows() and dhnio.isFrozen():
                dhnio.StdOutRedirectingStart()
                dhnio.Dprint(2, 'dhnmain.main redirecting started')

    if opts.verbose:
        copyright()

    dhnio.Dprint(2, 'dhnmain.main started ' + time.asctime())

    overDict = override_options(opts, args)

    cmd = ''
    if len(args) > 0:
        cmd = args[0].lower()


    if cmd == '':
        if len(dhnio.find_process(['dhnmain.', 'dhn.', ])) > 0:
            dhnio.Dprint(0, 'dhnmain.main DHN already running. EXIT.')
            return 0
        dhnio.Dprint(4, 'dhnmain.main calling run()')
        run('', opts, args, overDict)
        return 0


    elif cmd == 'show':
        appList = dhnio.find_process(['dhnview.' ])
        if len(appList):
            dhnio.Dprint(0, 'dhnmain.main found another dhnview instance running at the moment. EXIT.')
            return 0

        appList = dhnio.find_process(['dhnmain.', 'dhn.', ])
        if len(appList) == 0:
            dhnio.Dprint(0, 'dhnmain.main calling run("show")')
            run('show', opts, args, overDict)
            return 0

        dhnio.Dprint(0, 'dhnmain.main calling webcontrol.show()')
        import webcontrol
        webcontrol.show()

        return 0


    elif cmd == 'stop':
        total_count = 0
        while True:
            count = 0
            appList = dhnio.find_process(['dhnmain.', 'dhn.', 'dhnview.', ])
            for pid in appList:
                count += 1
                dhnio.Dprint(0, 'dhnmain.main want to stop pid %d' % pid)
                dhnio.kill_process(pid)
            if len(appList) == 0:
                dhnio.Dprint(0, 'dhnmain.main no more DataHaven.NET processes found')
                return 0
            total_count += 1
            if total_count > 10:
                dhnio.Dprint(0, 'dhnmain.main some DataHaven.NET processes found, but can not stop them')
                return 1
            time.sleep(1)
        return 1


    elif cmd == 'backup' or cmd == 'backups':
        return cmd_backups(opts, args, overDict)


    elif cmd == 'restore':
        return cmd_restore(opts, args, overDict)


    elif cmd == 'suppliers' or cmd == 'supplier':
        return cmd_suppliers(opts, args, overDict)


    elif cmd == 'msg':
        return cmd_msg(opts, args, overDict)


    elif cmd == 'register':
        return cmd_register(opts, args, overDict)


    elif cmd == 'recover':
        return cmd_recover(opts, args, overDict)


    elif cmd == 'tc':
        return cmd_tc(opts, args, overDict)


    elif cmd == 'tcp':
        return cmd_tcp(opts, args, overDict)


    elif cmd == 'q2q':
        return cmd_q2q(opts, args, overDict)


    elif cmd == 'help':
        print help()
        return 0

    else:
        dhnio.Dprint(1, 'dhnmain.main ERROR wrong command')
        return 1


#-------------------------------------------------------------------------------

if __name__ == "__main__":
    ret = main()
    if ret == 2:
        print usage()
    sys.exit(ret)

