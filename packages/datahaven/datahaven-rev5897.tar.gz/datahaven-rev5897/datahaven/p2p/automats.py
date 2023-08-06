#!/usr/bin/env python
#automats.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#

import os
import sys

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in automat.py')
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet.task import LoopingCall


import lib.dhnio as dhnio
import lib.dhnnet as dhnnet
import lib.misc as misc
import lib.nameurl as nameurl
import lib.packetid as packetid
import lib.settings as settings
import lib.contacts as contacts
import lib.transport_control as transport_control
import lib.diskusage as diskusage
from lib.automat import Automat


import initializer
import p2p_connector

import dhninit
#import connectionmanager
import centralservice
import identitypropagate
import install
import webcontrol



#------------------------------------------------------------------------------

_GlobalState = 'AT_STARTUP'
_GlobalStateNotifyFunc = None

_AutomatsDict = {}

#_Initializer = None
_Installer = None
#_NetworkConnector = None
#_P2PConnector = None
_CentralConnector = None
_CentralRegistrator = None

#------------------------------------------------------------------------------

def set_global_state(st):
    global _GlobalState
    global _GlobalStateNotifyFunc
    oldstate = _GlobalState
    _GlobalState = st
    dhnio.Dprint(2, '{%s}->{%s} in automats.set_global_state' % (oldstate, _GlobalState))
    if _GlobalStateNotifyFunc is not None and oldstate != _GlobalState:
        try:
            _GlobalStateNotifyFunc(_GlobalState)
        except:
            dhnio.DprintException()


def get_global_state():
    global _GlobalState
    dhnio.Dprint(6, 'dhninit.get_global_state return [%s]' % _GlobalState)
    return _GlobalState

#------------------------------------------------------------------------------

#def A(id, event=None, arg=None):
#    a = all().get(id, None)
#    assert a is None
#    if event is not None:
#        a.automat(event, arg)
#    return a

#def initializer(event=None, arg=None):
#    global _Initializer
#    if _Initializer is None:
#        _Initializer = Initializer('initializer', 'AT_STARTUP', 4)
#    if event is not None:
#        _Initializer.automat(event, arg)
#    return _Initializer


def installer(event=None, arg=None):
    global _Installer
    if _Installer is None:
        _Installer = Installer('installer', 'READY', 4)
    if event is not None:
        _Installer.automat(event, arg)
    return _Installer


#def network_connector(event=None, arg=None):
#    global _NetworkConnector
#    if _NetworkConnector is None:
#        _NetworkConnector = NetworkConnector('network_connector', 'AT_STARTUP', 4)
#    if event is not None:
#        _NetworkConnector.automat(event, arg)
#    return _NetworkConnector


#def p2p_connector(event=None, arg=None):
#    global _P2PConnector
#    if _P2PConnector is None:
#        _P2PConnector = P2PConnector('p2p_connector', 'AT_STARTUP', 4)
#    if event is not None:
#        _P2PConnector.automat(event, arg)
#    return _P2PConnector


def central_connector(event=None, arg=None):
    global _CentralConnector
    if _CentralConnector is None:
        _CentralConnector = CentralConnector('central_connector', 'AT_STARTUP', 4)
    if event is not None:
        _CentralConnector.automat(event, arg)
    return _CentralConnector


def central_registrator(event=None, arg=None):
    global _CentralRegistrator
    if _CentralRegistrator is None:
        _CentralRegistrator = CentralRegistrator('central_registrator', 'AT_STARTUP', 4)
    if event is not None:
        _CentralRegistrator.automat(event, arg)
    return _CentralRegistrator

#------------------------------------------------------------------------------

class Installer(Automat):
    MESSAGE_01 = {'message': 'incorrect user name', 'messageColor': 'red'}
    RECOVER_RESULTS = {
        'remote_identity_not_valid':  ('remote Identity is not valid', 'red'),
        'invalid_identity_source':    ('incorrect source of the Identity file', 'red'),
        'invalid_identity_url':       ('incorrect Identity file location', 'red'),
        'remote_identity_bad_format': ('incorrect format of the Identity file', 'red'),
        'incorrect_key':              ('Private Key is not valid', 'red'),
        'idurl_not_exist':            ('Identity URL address not exist or not reachable at this moment', 'blue'),
        'signing_error':              ('unable to sign the local Identity file', 'red'),
        'signature_not_match':        ('remote Identity and Private Key did not match', 'red'),
        'central_failed':             ('unable to connect to the Central server, try again later', 'blue'),
        'success':                    ('account restored!', 'green'), }

    def state_changed(self, oldstate, newstate):
        set_global_state('INSTALL ' + newstate)
        initializer('installer.state', newstate)

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'READY':
            if event == 'init':
                self.state = 'WHAT_TO_DO?'
        #---WHAT_TO_DO?---
        elif self.state == 'WHAT_TO_DO?':
            if event == 'register-selected':
                self.doUpdate(arg)
                self.state = 'ENTER_NAME'
            elif event == 'recover-selected':
                self.doUpdate(arg)
                self.state = 'LOAD_KEY'
        #---ENTER_NAME---
        elif self.state == 'ENTER_NAME':
            if event == 'back':
                self.doUpdate(arg)
                self.state = 'WHAT_TO_DO?'
            elif event == 'register-start' and self.isNameValid(arg):
                #central_registrator('start', arg)
                self.doRegisterStart(arg)
                self.doUpdate(arg)
                self.state = 'REGISTER'
            elif event == 'register-start' and not self.isNameValid(arg):
                self.doUpdate(arg, self.MESSAGE_01)
        #---LOAD_KEY---
        elif self.state == 'LOAD_KEY':
            if event == 'back':
                self.doUpdate(arg)
                self.state = 'WHAT_TO_DO?'
            elif event == 'load-barcode' or event == 'load-file' or event == 'clipboard-paste':
                self.doKeyRead(arg)
            elif event == 'recover-start':
                self.doRecoverStart(arg)
                self.doUpdate(arg)
                self.state = 'RECOVER'
        #---REGISTER---
        elif self.state == 'REGISTER':
            if event == 'register-result' and self.isRegisterSuccess(arg):
                self.state = 'CENTRAL'
            elif event == 'register-result' and not self.isRegisterSuccess(arg):
                self.state = 'ENTER_NAME'
        #---CENTRAL---
        elif self.state == 'CENTRAL':
            if event == 'central-ready' and self.isCentralValid(arg) and not self.isDirSelected(arg):
                self.doCentralSave(arg)
                self.doUpdate(arg)
                self.state = 'CONTACTS'
            elif event == 'central-ready' and self.isDirSelected(arg):
                self.doUpdate(arg)
            elif event == 'central-ready' and not self.isCentralValid(arg):
                self.doCentralMessage(arg)
        #---CONTACTS---
        elif self.state == 'CONTACTS':
            if event == 'contacts-ready' and self.isContactsValid(arg):
                self.doContactsSave(arg)
                self.doSaveLocalIdentity()
                self.doShowStartPage(arg)
                self.state = 'DONE'
            elif event == 'contacts-ready' and not self.isContactsValid(arg):
                self.doCentralMessage(arg)
        #---RECOVER---
        elif self.state == 'RECOVER':
            if event == 'recover-result' and self.isRecoverSuccess(arg):
                self.doRecoverSave(arg)
                self.doShowStartPage(arg)
                self.state = 'DONE'
            elif event == 'recover-result' and not self.isRecoverSuccess(arg):
                self.doRecoverResult(arg)
                self.state = 'LOAD_KEY'
        #---DONE---
        elif self.state == 'DONE':
            pass

    def isNameValid(self, arg):
        name = arg[1].args.get('login', [''])[0]
        if not misc.ValidUserName(name):
            return False
        return True

    def isRegisterSuccess(self, arg):
        return arg == 'success'

    def isDirSelected(self, arg):
        opendir = unicode(misc.unpack_url_param(webcontrol.arg(arg[1], 'opendir'), ''))
        return opendir != ''

    def isCentralValid(self, arg):
        request = arg[1]
        needed = webcontrol.arg(request, 'needed')
        donated = webcontrol.arg(request, 'donated')
        customersdir = unicode(misc.unpack_url_param(
            webcontrol.arg(request, 'customersdir'), settings.getCustomersFilesDir()))
        try:
            neededV = float(needed)
            donatedV = float(donated)
        except:
            return False
        if donatedV < settings.MinimumDonatedMb():
            return False
        if not os.path.isdir(customersdir):
            return False
        if not os.access(customersdir, os.W_OK):
            return False
        freeBytes, totalBytes = diskusage.GetDriveSpace(customersdir)
        if freeBytes <= donatedV * 1024 * 1024:
            return False
        return True

    def isContactsValid(self, arg):
        request = arg[1]
        email = webcontrol.arg(request, 'email').strip()
        phone = webcontrol.arg(request, 'phone').strip()
        fax = webcontrol.arg(request, 'fax').strip()
        text = webcontrol.arg(request, 'text')
        if email.strip() == '':
            return False
        if not misc.ValidEmail(email):
            return False
        if phone != '' and not misc.ValidPhone(phone):
            return False
        if fax != '' and not misc.ValidPhone(fax):
            return False
        if len(text) > 500:
            return False
        return True

    def isRecoverSuccess(self, arg):
        return arg == 'success'

    def doUpdate(self, arg, args={}):
        reactor.callLater(0, arg[0].finishRequest, arg[1], args)

    def doRegisterStart(self, arg):
        login = webcontrol.arg(arg[1], 'login')
        install.SetProgressNotifyCallback(webcontrol.InstallingProcessFunc)
        webcontrol.installing_process_str = ''
        install.RegisterNewUser(login).addCallbacks(
            lambda result: self.automat('register-result', result),
            lambda x: dhnio.DprintException())

    def doCentralMessage(self, arg):
        request = arg[1]
        needed = webcontrol.arg(request, 'needed')
        donated = webcontrol.arg(request, 'donated')
        customersdir = unicode(misc.unpack_url_param(
            webcontrol.arg(request, 'customersdir'), settings.getCustomersFilesDir()))
        try:
            neededV = float(needed)
            donatedV = float(donated)
        except:
            return self.doUpdate(arg, {'message': 'wrong value', 'messageColor':'red'})
        if donatedV < settings.MinimumDonatedMb():
            return self.doUpdate(arg, {'message': 'you should donate at least %d Mb' % settings.MinimumDonatedMb(), 'messageColor':'blue'})
        if not os.path.isdir(customersdir):
            return self.doUpdate(arg, {'message': 'directory %s not exist' % customersdir, 'messageColor':'red'})
        if not os.access(customersdir, os.W_OK):
            return self.doUpdate(arg, {'message': 'specified folder does not have write permissions', 'messageColor':'red'})
        freeBytes, totalBytes = diskusage.GetDriveSpace(customersdir)
        if freeBytes <= donatedV * 1024 * 1024:
            return self.doUpdate(arg, {'message': 'you do not have enough space on disk', 'messageColor':'blue'})
        return self.doUpdate(arg)

    def doCentralSave(self, arg):
        request = arg[1]
        needed = webcontrol.arg(request, 'needed')
        donated = webcontrol.arg(request, 'donated')
        customersdir = unicode(misc.unpack_url_param(
            webcontrol.arg(request, 'customersdir'), settings.getCustomersFilesDir()))
        settings.uconfig().set('central-settings.needed-megabytes', needed+'Mb')
        settings.uconfig().set('central-settings.shared-megabytes', donated+'Mb')
        settings.uconfig().set('folder.folder-customers', customersdir)
        settings.uconfig().update()

    def doContactsMessage(self, arg):
        request = arg[1]
        email = webcontrol.arg(request, 'email').strip()
        phone = webcontrol.arg(request, 'phone').strip()
        fax = webcontrol.arg(request, 'fax').strip()
        text = webcontrol.arg(request, 'text')
        if email.strip() == '':
            msg = 'Please enter your Email. We guarantee No spam. Email will not be published. Only to notify in case of critical errors while we are in the testing process.'
            return self.doUpdate(arg, {'message': msg, 'messageColor':'blue'})
        if not misc.ValidEmail(email):
            return self.doUpdate(arg, {'message': 'incorrect email address', 'messageColor':'red'})
        if phone != '' and not misc.ValidPhone(phone):
            return self.doUpdate(arg, {'message': 'incorrect phone number', 'messageColor':'red'})
        if fax != '' and not misc.ValidPhone(fax):
            return self.doUpdate(arg, {'message': 'incorrect fax number', 'messageColor':'red'})
        if len(text) > 500:
            return self.doUpdate(arg, {'message': 'the text is too long', 'messageColor':'red'})
        return self.doUpdate(arg)

    def doContactsSave(self, arg):
        request = arg[1]
        email = webcontrol.arg(request, 'email').strip()
        phone = webcontrol.arg(request, 'phone').strip()
        fax = webcontrol.arg(request, 'fax').strip()
        text = webcontrol.arg(request, 'text')
        settings.uconfig().set('emergency.emergency-email', email)
        settings.uconfig().set('emergency.emergency-phone', phone)
        settings.uconfig().set('emergency.emergency-fax', fax)
        settings.uconfig().set('emergency.emergency-text', text)
        settings.uconfig().update()

    def doSaveLocalIdentity(self):
        misc.saveLocalIdentity()

    def doKeyRead(self, arg):
        action = webcontrol.arg(arg[1], 'action')
        if action == 'load-barcode':
            self.doUpdate(arg, {'message': 'this feature is temporarily disabled', 'messageColor':'red'})
            return
        elif action == 'load-file':
            openfile = webcontrol.arg(arg[1], 'openfile')
            src = dhnio.ReadBinaryFile(openfile)
            if len(src) > 1024*10:
                return self.doUpdate(arg, {'message': 'file is too big for private key', 'messageColor': 'red'})
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
                dhnio.DprintException()
                idurl = ''
                txt = src
            self.doUpdate(arg, {'idurl': idurl, 'keysrc': txt})
            return
        elif action == 'clipboard-paste':
            src = misc.getClipboardText()
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
                dhnio.DprintException()
                idurl = ''
                txt = src
            self.doUpdate(arg, {'idurl': idurl, 'keysrc': txt})
            return
        else:
            dhnio.Dprint(2, 'automats.Installer.doKeyRead WARNING action='+action)

    def doRecoverStart(self, arg):
        idurl = webcontrol.arg(arg[1], 'idurl').strip()
        keysrc = webcontrol.arg(arg[1], 'keysrc').strip()
        install.SetProgressNotifyCallback(webcontrol.InstallingProcessFunc)
        install.RecoverExistingUser(idurl, keysrc).addCallbacks(
            lambda result: self.automat('recover-result', result),
            lambda x: dhnio.DprintException())

    def doRecoverResult(self, arg):
        install.ProgressMessage(self.RECOVER_RESULTS.get(arg, ['unknown result'])[0])

    def doRecoverSave(self, arg):
        settings.uconfig().set('central-settings.desired-suppliers', '0')
        settings.uconfig().set('central-settings.needed-megabytes', '0Mb')
        settings.uconfig().set('central-settings.shared-megabytes', '0Mb')
        settings.uconfig().update()

    def doShowStartPage(self, arg):
        reactor.callLater(0, webcontrol.DHNViewSendCommand, 'open /'+webcontrol._PAGE_STARTING)

#------------------------------------------------------------------------------

class CentralConnector(Automat):
    timers = {'timer-1hour':  (60*60, ['CONNECTED']),
              'timer-10min':  (60*10, ['DISCONNECTED',]),
              'timer-1min':   (60,    ['IDENTITY', 'REQUEST_SETTINGS', 'SETTINGS', 'SUPPLIERS']),
              'timer-20sec':  (20,    ['IDENTITY',])}
    flagSettings = False

    def state_changed(self, oldstate, newstate):
        set_global_state('CENTRAL ' + newstate)
        p2p_connector.A('central_connector.state', newstate)

    def A(self, event, args):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'init':
                self.flagSettings = False
                self.doInitCentralService()
                self.doSendIdentity()
                self.state = 'IDENTITY'
        #---IDENTITY---
        elif self.state == 'IDENTITY':
            if event == 'identity-ack' and not self.isSettingsExist():
                self.doSendRequestSettings()
                self.state = 'REQUEST_SETTINGS'
            elif event == 'identity-ack' and self.isSettingsExist() and not self.flagSettings:
                self.doSendSettings()
                self.state = 'SETTINGS'
            elif event == 'identity-ack' and self.isSettingsExist() and self.flagSettings and not self.isSuppliersNeeded():
                self.state = 'CONNECTED'
            elif event == 'identity-ack' and self.isSettingsExist() and self.flagSettings and self.isSuppliersNeeded():
                self.doSendRequestSuppliers()
                self.state = 'SUPPLIERS'
            elif event == 'timer-20sec':
                self.doSendIdentity()
            elif event == 'timer-1min':
                self.state = 'DISCONNECTED'
        #---SETTINGS---
        elif self.state == 'SETTINGS':
            if event == 'settings-ack':
                self.flagSettings = True
                self.state = 'CONNECTED'
#            elif event == 'settings-ack' and self.isSuppliersNeeded():
#                self.flagSettings = True
#                self.doSendRequestSuppliers()
#                self.state = 'SUPPLIERS'
            elif event in ['timer-1min', 'propagate']:
                self.doSendIdentity()
                self.state = 'IDENTITY'
            elif event == 'settings':
                self.doSendSettings()
        #---REQUEST_SETTINGS---
        elif self.state == 'REQUEST_SETTINGS':
            if event == 'request-settings-ack' and self.isSuppliersNeeded():
                self.flagSettings = True
                self.doSendRequestSuppliers()
                self.state = 'SUPPLIERS'
            elif event == 'request-settings-ack' and not self.isSuppliersNeeded():
                self.flagSettings = True
                self.state = 'CONNECTED'
            elif event in ['timer-1min', 'propagate']:
                self.doSendIdentity()
                self.state = 'IDENTITY'
        #---SUPPLIERS---
        elif self.state == 'SUPPLIERS':
            if event == 'list-suppliers':
                self.state = 'CONNECTED'
            elif event in ['timer-1min', 'propagate']:
                self.doSendIdentity()
                self.state = 'IDENTITY'
        #---CONNECTED---
        elif self.state == 'CONNECTED':
            if event in ['timer-1hour', 'propagate']:
                self.doSendIdentity()
                self.state = 'IDENTITY'
            elif event == 'settings':
                self.flagSettings = False
                self.doSendSettings()
                self.state = 'SETTINGS'
        #---DISCONNECTED---
        elif self.state == 'DISCONNECTED':
            if event in ['settings', 'propagate', 'timer-10min', 'identity-ack', 'list-suppliers', 'list-customers']:
                self.flagSettings = False
                self.doSendIdentity()
                self.state = 'IDENTITY'

    def isSettingsExist(self):
        return settings.getCentralNumSuppliers() > 0

    def isSuppliersNeeded(self):
        return settings.getCentralNumSuppliers() <= 0 or \
               contacts.numSuppliers() != settings.getCentralNumSuppliers()

    def _saveRequestedSettings(self, newpacket):
        sd = dhnio._unpack_dict(newpacket.Payload)
        settings.uconfig().set('central-settings.needed-megabytes', sd.get('n', str(settings.DefaultNeededMb())+'Mb'))
        settings.uconfig().set('central-settings.shared-megabytes', sd.get('d', str(settings.DefaultDonatedMb())+'Mb'))
        settings.uconfig().set('central-settings.desired-suppliers', sd.get('s', '2'))
        settings.uconfig().set('emergency.emergency-email', sd.get('e1', ''))
        settings.uconfig().set('emergency.emergency-phone', sd.get('e2', ''))
        settings.uconfig().set('emergency.emergency-fax', sd.get('e3', ''))
        settings.uconfig().set('emergency.emergency-text', sd.get('e4', '').replace('<br>', '\n'))
        settings.uconfig().update()
        reactor.callLater(0, self.automat, 'request-settings-ack', newpacket)

    def doInitCentralService(self):
        centralservice.init()

    def doSendIdentity(self):
        transport_control.RegisterInterest(
            lambda packet: self.automat('identity-ack', packet),
            settings.CentralID(),
            centralservice.SendIdentity(True))

    def doSendSettings(self):
        packetID = packetid.UniqueID()
        transport_control.RegisterInterest(
            lambda packet: self.automat('settings-ack', packet),
            settings.CentralID(),
            packetID)
        centralservice.SendSettings(True, packetID)

    def doSendRequestSettings(self):
        transport_control.RegisterInterest(
            lambda packet: self._saveRequestedSettings(packet),
            settings.CentralID(),
            centralservice.SendRequestSettings(True))

    def doSendRequestSuppliers(self):
        return centralservice.SendRequestSuppliers()

#    def doCheckLastReceipt(self, newpacket):
#        try:
#            status, last_receipt, = newpacket.Payload.split('\n', 2)
#            last_receipt = int(last_receipt)
#        except:
#            last_receipt = -1
#        missing_receipts = money.SearchMissingReceipts(last_receipt)
#        if len(missing_receipts) > 0:
#            reactor.callLater(0, SendRequestReceipt, missing_receipts)

#------------------------------------------------------------------------------

class CentralRegistrator(Automat):
    def A(self, event, arg):
        pass

#------------------------------------------------------------------------------








