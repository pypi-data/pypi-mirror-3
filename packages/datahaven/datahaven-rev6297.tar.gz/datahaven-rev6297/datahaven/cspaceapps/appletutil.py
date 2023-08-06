import sys, os
from nitro.async import AsyncOp
from nitro.tcp import tcpConnect, TCPStream
from nitro.linestream import TCPLineStream
from nitro.selectreactor import SelectReactor
from cspace.main.common import localSettings
from cspace.util.hexcode import hexDecode, hexEncode
from cspace.util.wordcode import wordDecode, wordEncode

class CSpaceEnv( object ) :
    def __init__( self ) :
        self.port = int( os.environ['CSPACE_PORT'] )
        self.user = os.environ['CSPACE_USER']
        self.event = os.environ['CSPACE_EVENT']
        self.isContactAction = (self.event == 'CONTACTACTION')
        self.isIncoming = (self.event == 'INCOMING')
        if self.isContactAction :
            self.contactName = os.environ['CSPACE_CONTACTNAME']
            self.actionDir = os.environ['CSPACE_ACTIONDIR']
            self.action = os.environ['CSPACE_ACTION']
            self.displayName = self.contactName
        elif self.isIncoming :
            self.service = os.environ['CSPACE_SERVICE']
            self.connectionId = os.environ['CSPACE_CONNECTIONID']
            self.contactName = os.environ['CSPACE_CONTACTNAME']
            self.incomingName = os.environ['CSPACE_INCOMINGNAME']
            if self.contactName :
                self.displayName = self.contactName
            else :
                self.displayName = '(Unknown %s)' % self.incomingName


class ApplicationConnection( object ) :
    (UNCONNECTED,
     COMMANDING,
     CONNECTING,
     ACCEPTING,
     LISTENING,
     CONNECTED) = range(6)
    
    def __init__( self, env=None, reactor=None, openCallback=None, errCallback=None ):
        if env is None:
            env = CSpaceEnv()
        self.env = env
        if reactor is None:
            reactor = SelectReactor()
        self.reactor = reactor
        self.openCallback = openCallback
        self.connectOp = tcpConnect( ('127.0.0.1',self.env.port),
                                     self.reactor,
                                     self._openStream )
        self.openOp = AsyncOp(openCallback, self.close)
        self.errCB = errCallback
        self.state = self.UNCONNECTED
        self.error = ""

        self.results = []
        self.myPubKey = None
        self.incomingPubKey = None
        self.remoteUser = None
        self.remoteKey = None
        self.contactNames = []
        self.contactPubKeys = {}
        
        
        self.commands = {
            'echo': "Echo",
            'getcontacts': "GetContacts",
            'getpubkey': "GetContactPubKey",
            'getmypubkey': "GetMyPubKey",
            'getcontactpubkeys': "GetContactPubKeys",
            'connect': "Connect",
            'connectpubkey': "ConnectPubKey",
            'accept': "Accept",
            'getincomingpubkey': "GetIncomingPubKey",
            'registerlistener': "RegisterListener",
            'sendlistener': "SendListener"
        }

    def close( self ):
        if self.connectOp : self.connectOp.cancel()
        if self.stream and not self.stream.hasShutdown():
            self.stream.close( deferred=True )

    def _doCancel( self ):
        self.close()
        if self.errCB: self.errCB(self.error)

    def _setError( self, errMsg ):
        self.error = errMsg
        
    def _openStream(self, connector):
        self.connectOp = None
        if connector.getError() != 0 :
            self._setError( 'Unable to connect to CSpace.' )
            return

        self.sock = connector.getSock()
        self.stream = TCPLineStream( self.sock, self.reactor )
        self.stream.setCloseCallback( self._onClose )
        self.stream.setErrorCallback( self._onError )
        self.stream.setInputCallback( self._onInput )
        self.stream.enableRead( True )
        
        if self.openOp:
            self.openOp.notify(0)
            self.openOp = None
            
    def _onClose(self):
        self.close()
        
    def _onError(self, error, errMsg):
        self._setError(errMsg)
        self.close()
        
    def chainCommands(self, chain, cmdErrorCallback=None):
        self.cmdErrCB = cmdErrorCallback
        self.chain = chain
        self.cmd, self.args, self.cbChain = self.chain.pop(0)
        if len(self.chain):
            cbSuccess = self._nextChain
        else:
            cbSuccess = self._finishedChain
        self.command(self.cmd, self.args, cbSuccess, self.cmdErrCB)
    
    def _nextChain(self, result):
        self.results.append( (self.cmd, self.args, result) )
        if self.cbChain:
            self.cbChain(result)
        self.cmd, self.args, self.cbChain = self.chain.pop(0)
        if len(self.chain):
            cbSuccess = self._nextChain
        else:
            cbSuccess = self._finishedChain
        self.command(self.cmd, self.args, cbSuccess, self.cmdErrCB)
    
    def _finishedChain(self, result):
        self.results.append( (self.cmd, self.args, result) )
        if self.cbChain:
            self.cbChain(result)
        

    def command( self, cmd, args, callback=None, errcallback=None ):
        cmd = cmd.lower()
        if cmd not in self.commands:
            errcallback("Bad command: %s" % cmd)
        
        reqAction = getattr(self, "_req_" + self.commands[cmd])
        self.respAction = getattr(self, "_resp_" + self.commands[cmd])
        self.respCB = callback
        self.errCB = errcallback
        self.state = self.COMMANDING
        
        reqAction(*args)
                  
    def _onInput( self, line ):
        if self.state in (self.COMMANDING,
                          self.CONNECTING,
                          self.ACCEPTING):
            
            if self.state in (self.CONNECTING, self.ACCEPTING):
                self.response += line
                if not self.response.endswith("\n"):
                    return
                line = self.response
            
            if not line.startswith("OK") and line.endswith("\n"):
                self.close()
                if line.startswith("ERROR "):
                    line = line[6:]
                if self.errCB:
                    self.errCB("%s" % line)
                return

            line = line[3:-2]
            result = self.respAction( line )
            respCB = self.respCB
            self.respAction = None
            self.respCB = None
            if None not in (result, respCB):
                respCB(*result)

    
    def _req_Echo( self, text ):
        self.stream.writeData( 'ECHO %s\r\n' % wordEncode(text) )
        
    def _resp_Echo( self, line ):
        return ( wordDecode(line), )
    
    def _req_GetContacts( self ):
        self.stream.writeData( 'GETCONTACTS\r\n' )
        
    def _resp_GetContacts( self, line ):
        self.contactNames = line.split()
        return ( self.contactNames, )
    
    def _req_GetContactPubKey( self, cname=None ):
        if cname is None:
            cname = self.env.contactName
        self._cname = cname
        self.stream.writeData( 'GETPUBKEY %s\r\n' % cname )
    
    def _resp_GetContactPubKey( self, line ):
        pubKeyData = self.contactPubKeys[self._cname] = hexDecode(line.strip())
        del self._cname
        return ( pubKeyData, )
    
    def _req_GetMyPubKey( self ):
        self.stream.writeData( 'GETPUBKEY\r\n' )

    def _resp_GetMyPubKey( self, line ):
        pubKeyData = hexDecode(line.strip())
        self.myPubKey = pubKeyData
        return ( pubKeyData, )

    def _req_GetContactPubKeys( self ):
        self.stream.writeData( 'GETCONTACTPUBKEYS\r\n' )
    
    def _resp_GetContactPubKeys( self, line ):
        words = line.split(" ")
        contacts = {}
        for cnum in range(0, len(words), 2):
            cname = wordDecode(words[cnum])
            ckey = hexDecode(words[cnum+1])
            contacts[cname] = ckey
        self.contactPubKeys = contacts
        self.contactNames = self.contactPubKeys.keys()
        self.contactNames.sort()
        return ( dict(contacts), )
    
    def _req_GetIncomingPubKey( self, connectionId=None ):
        if not connectionId:
            connectionId = self.env.connectionId
        self.connectionId = connectionId
        self.stream.writeData( 'GETINCOMINGPUBKEY %s\r\n' % connectionId )
    
    def _resp_GetIncomingPubKey( self, line ):
        self.incomingPubKey = hexDecode(line.strip())
        return ( self.incomingPubKey, )

    def _req_Accept( self, connectionId=None ):
        if connectionId is None:
            connectionId = self.env.connectionId
        self.connectionId = connectionId
        self.response = ""
        self.state = self.ACCEPTING
        self.stream.writeData( "ACCEPT %s\r\n" % connectionId )        

    def _resp_Accept( self, line ):
        self.stream.shutdown()
        self.state = self.CONNECTED
        return ( self.sock, )
    
    def _req_Connect( self, remoteUser=None, remoteService=None ):
        if remoteUser is None:
            remoteUser = self.env.contactName
        if remoteService is None:
            remoteService = self.env.actionDir
        self.remoteUser = remoteUser
        self.remoteService = remoteService
        self.response = ""
        self.state = self.CONNECTING
        self.stream.writeData( 'CONNECT %s %s\r\n' % (remoteUser,remoteService) )
    
    def _resp_Connect( self, rline ):
        self.stream.shutdown()
        self.state = self.CONNECTED
        return ( self.sock, )
    
    
    def _req_ConnectPubKey( self, remoteKey, remoteService=None ):
        if remoteService is None:
            remoteService = self.env.actionDir
        self.remoteService = remoteService
        self.remoteKey = remoteKey
        self.response = ""
        self.state = self.CONNECTING
        self.stream.writeData( 'CONNECTPUBKEY %s %s\r\n' % (remoteKey,remoteService) )

    def _resp_Connect( self, rline ):
        self.stream.shutdown()
        self.state = self.CONNECTED
        return ( self.sock, )
    
    # TODO: RegisterListener, SendListener

        

class CSpaceConnector( object ) :
    def __init__( self, sock, remoteUser, remoteService, reactor, callback ) :
        self.stream = TCPStream( sock, reactor )
        self.stream.setCloseCallback( self._onClose )
        self.stream.setErrorCallback( self._onError )
        self.stream.setInputCallback( self._onInput )
        self.stream.initiateRead( 1 )
        self.stream.writeData( 'CONNECT %s %s\r\n' % (remoteUser,remoteService) )
        self.response = ''
        self.op = AsyncOp( callback, self.stream.close )

    def getOp( self ) : return self.op

    def _onClose( self ) :
        self.stream.close()
        self.op.notify( -1, None )

    def _onError( self, err, errMsg ) :
        self._onClose()

    def _onInput( self, data ) :
        self.response += data
        if self.response.endswith('\n') :
            if not self.response.startswith('OK') :
                self._onClose()
                return
            self.stream.shutdown()
            sock = self.stream.getSock()
            self.op.notify( 0, sock )

class CSpaceAcceptor( object ) :
    def __init__( self, sock, connectionId, reactor, callback ) :
        self.stream = TCPStream( sock, reactor )
        self.stream.setCloseCallback( self._onClose )
        self.stream.setErrorCallback( self._onError )
        self.stream.setInputCallback( self._onInput )
        self.stream.initiateRead( 1 )
        self.stream.writeData( 'ACCEPT %s\r\n' % connectionId )
        self.response = ''
        self.op = AsyncOp( callback, self.stream.close )

    def getOp( self ) : return self.op

    def _onClose( self ) :
        self.stream.close()
        self.op.notify( -1, None )

    def _onError( self, err, errMsg ) :
        self._onClose()

    def _onInput( self, data ) :
        self.response += data
        if self.response.endswith('\n') :
            if not self.response.startswith('OK') :
                self._onClose()
                return
            self.stream.shutdown()
            sock = self.stream.getSock()
            self.op.notify( 0, sock )

def cspaceConnect( cspaceAddr, remoteUser, remoteService, reactor, callback ) :
    def onTCPConnect( connector ) :
        if connector.getError() != 0 :
            op.notify( -1, None )
            return
        connectOp = CSpaceConnector( connector.getSock(), remoteUser,
                remoteService, reactor, op.notify ).getOp()
        op.setCanceler( connectOp.cancel )
    tcpOp = tcpConnect( cspaceAddr, reactor, onTCPConnect )
    op = AsyncOp( callback, tcpOp.cancel )
    return op

def cspaceAccept( cspaceAddr, connectionId, reactor, callback ) :
    def onTCPConnect( connector ) :
        if connector.getError() != 0 :
            op.notify( -1, None )
            return
        acceptOp = CSpaceAcceptor( connector.getSock(), connectionId,
                reactor, op.notify ).getOp()
        op.setCanceler( acceptOp.cancel )
    tcpOp = tcpConnect( cspaceAddr, reactor, onTCPConnect )
    op = AsyncOp( callback, tcpOp.cancel )
    return op

class LogFile( object ) :
    def __init__( self, fileName ) :
        configDir = localSettings().getConfigDir()
        logFile = os.path.join( configDir, fileName )
        try :
            if os.path.getsize(logFile) >= 1024*1024 :
                os.remove( logFile )
        except OSError :
            pass
        self.f = file( logFile, 'a' )

    def write( self, s ) :
        self.f.write( s )
        self.f.flush()

    def flush( self ) :
        pass

def initializeLogFile( fileName ) :
    logFile = LogFile( fileName )
    sys.stdout = logFile
    sys.stderr = logFile
