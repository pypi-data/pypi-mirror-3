#!/usr/bin/env python
# Store and forward offline IM's via DHT 

from time import time
from datetime import datetime
from socket import socket, AF_INET, SOCK_DGRAM
import logging

# DHT put/get/delete
from cspace.dht import proto, node, client
from cspace.dht.util import toId
from cspace.dht.client import DHTClient
from cspace.dht.rpc import RPCSocket
# Applet getPrivKey, getSeedNodes
from cspace.main import appletserver
# App and Service patching
from cspace.main import app, service
from cspaceapps.appletutil import CSpaceEnv, ApplicationConnection

# Various encodings
from cspace.util.hexcode import hexDecode, hexEncode
from cspace.util.wordcode import wordDecode, wordEncode
from nitro.bencode import encode as bencode, decode as bdecode

# Various operations/connections/streams
from nitro.async import AsyncOp
from nitro.tcp import tcpConnect
from nitro.linestream import TCPLineStream

# Signing, encrypting, decrypting
from ncrypt.rsa import RSAKey, RSAError, PADDING_PKCS1_OAEP
from ncrypt.digest import Digest, DigestType

# Offline message display
from PyQt4.QtCore import Qt

logger = logging.getLogger('cspace.ext.storefwd')


DEFAULT_EXTRA_TIMEOUT = 168*60*60    # 7 days
STALE_EXTRA_INTERVAL  = 60*60        # 1 hour



def _assert( cond, msg=None ) :
    if not cond :
        if msg is None : msg = 'invalid message data'
        raise proto.ProtocolError, msg


class Dummy (object): pass



# Monkey-patch the DHT for extra attributes
def DHTNode_init( self, *args, **kwargs ) :
    self._oldinit( *args, **kwargs )
    self._initExtraTimer()
    for x in NEWMESSAGES :
            self.requestTable[x] = getattr( self, 'do%s' % x )
            
def DHTNode_initExtraTimer( self ) :
    def onTimer() :
        self.store.removeStaleExtras()
    timeout = STALE_EXTRA_INTERVAL
    timerOp = self.reactor.addTimer( timeout, onTimer )
    self.otherOps.add( timerOp )

def DHTNode_doPutOffIM( self, msg, ctx ) :
    publicKeyData, envelope = msg
    newExtras = (envelope,)
    extras = self.store.getKeyExtra( publicKeyData, "offlineIM" )
    if extras is not None:
        extras += newExtras
    else:
        extras = newExtras
    # This does mean that messages will have their timeouts refreshed
    # every time the pkey receives a new offline message or removes one.
    self.store.setKeyExtra( publicKeyData, "offlineIM", extras,
                            DEFAULT_EXTRA_TIMEOUT )
    ctx.response( (0,) )

def DHTNode_doGetOffIM( self, msg, ctx ) :
    publicKeyData = msg[0]

    envelopes = self.store.getKeyExtra( publicKeyData, "offlineIM" )
    if envelopes is None:
        envelopes = []
    ctx.response( (len(envelopes),envelopes) )

def DHTNode_doDelOffIM( self, msg, ctx ) :
    publicKeyData, envelope, signature = msg
    
    # Check the delete signature
    # TODO: Add some call-specific data to ensure
    #       other similar functions aren't hijacked
    sigdata = bencode( (publicKeyData, envelope) )
    digestType = DigestType( "SHA1" )
    digest = Digest( digestType ).digest( sigdata )
    pubKey = RSAKey()
    pubKey.fromDER_PublicKey( publicKeyData )
    try:
        pubKey.verify( signature, digest, digestType )
    except RSAError:
        ctx.response( (-1,) )
        return
    
    extras = self.store.getKeyExtra( publicKeyData, "offlineIM" )
    try:
        index = list(extras).index(envelope)
    except ValueError:
        # Item not stored here.
        ctx.response( (-1,) )
        return

    extras = extras[:index] + extras[index+1:]

    self.store.setKeyExtra( publicKeyData, "offlineIM", tuple(extras),
                        DEFAULT_EXTRA_TIMEOUT )
    ctx.response( (0,) )

node.DHTNode._oldinit = node.DHTNode.__init__
node.DHTNode.__init__ = DHTNode_init
node.DHTNode._initExtraTimer = DHTNode_initExtraTimer

def validatePutOffIMRequest( msg ):
    _assert( len(msg) == 2 )
    # Public Key Data for Target
    _assert( type(msg[0]) is str )
    # Encrypted Envelope
    _assert( type(msg[1]) is str )
    return msg

def validatePutOffIMResponse( msg ):
    _assert( len(msg) == 1 )
    # Result
    _assert( type(msg[0]) is int)
    return msg

def validateGetOffIMRequest( msg ):
    _assert( type(msg) is list )
    _assert( len(msg) == 1 )
    publicKey = msg[0]
    _assert( type(publicKey) is str )
    return msg

def validateGetOffIMResponse( msg ):
    _assert( type(msg) is list )
    _assert( len(msg) == 2 )
    result, envelopes = msg
    _assert( type(result) is int )
    _assert( type(envelopes) is list )
    for env in envelopes:
        _assert( type(env) is str )
    return msg

def validateDelOffIMRequest( msg ):
    _assert( len(msg) == 3 )
    # Public Key Data for Target
    _assert( type(msg[0]) is str )
    # Encrypted Envelope
    _assert( type(msg[1]) is str )
    # Request signature
    _assert( type(msg[2]) is str )
    return msg

def validateDelOffIMResponse( msg ):
    _assert( len(msg) == 1 )
    # Result
    _assert( type(msg[0]) is int)
    _assert( msg[0] in (-1, 0) )
    return msg


# Register new messages
NEWMESSAGES = ('PutOffIM', 'GetOffIM', 'DelOffIM')
def _initTables():
    g = globals()
    for m in NEWMESSAGES:
        proto.requestValidators[m] = g[ 'validate' + m + 'Request' ]
        proto.responseValidators[m] = g[ 'validate' + m + 'Response' ]

        setattr( node.DHTNode, "do" + m, g[ 'DHTNode_do' + m ] )




_initTables()





# Monkey-patch the DataStore for generic extra attributes.
def DataStore_init( self, *args, **kwargs ):
    self._oldinit(*args, **kwargs)
    self.e = {}

def DataStore_setKeyExtra( self, publicKey, extraKey, value, timeout ):
    if not publicKey in self.e:
        self.e[publicKey] = {}
    extraData = self.e[publicKey]
    deadline = time() + timeout
    extraData[extraKey] = (value, deadline)
    
def DataStore_getKeyExtra( self, publicKey, extraKey ):
    if not publicKey in self.e:
        return None
    if not extraKey in self.e[publicKey]:
        return None
    return self.e[publicKey][extraKey][0]

def DataStore_removeStaleExtras( self ):
    t = time()
    for k,x in self.e.items() :
        for l,y in x.items():
            if y[-1] < t : del x[l]

node.DataStore._oldinit = node.DataStore.__init__
node.DataStore.__init__ = DataStore_init
node.DataStore.setKeyExtra = DataStore_setKeyExtra
node.DataStore.getKeyExtra = DataStore_getKeyExtra
node.DataStore.removeStaleExtras = DataStore_removeStaleExtras






# Monkey-patch the DHTClient for offline IM
def DHTClient_callGetOffIM( self, publicKeyData, nodeAddr,
        callback=None, **kwargs ) :
    return self.doCall( 'GetOffIM', (publicKeyData,), nodeAddr,
            callback, **kwargs )

def DHTClient_callPutOffIM( self, publicKeyData, envelope, nodeAddr,
        callback=None, **kwargs ) :
    args = ( publicKeyData, envelope )
    return self.doCall( 'PutOffIM', args, nodeAddr, callback,
            **kwargs )

def DHTClient_callDelOffIM( self, publicKeyData, envelope, signature, nodeAddr,
        callback=None, **kwargs ) :
    args = ( publicKeyData, envelope, signature )
    return self.doCall( 'DelOffIM', args, nodeAddr, callback,
            **kwargs )

def DHTClient_lookupGetOffIM( self, publicKey, startNodes,
                              callback=None ) :
    obj = Dummy()
    def cancelGets() :
        for getOp in obj.getOps.keys() :
            getOp.cancel()
    def onGet( getOp, err, payload ) :
        del obj.getOps[getOp]
        if err >= 0 :
            result,envelopes = payload
            if result >= 0 :
                for env in envelopes:
                    if env not in obj.getResults:
                        obj.getResults.append( env )
        if not obj.getOps :
            op.notify( obj.getResults )
    def doGetOffIM( nodeAddr ) :
        getOp = self.callGetOffIM( publicKeyData, nodeAddr,
                lambda err,payload : onGet(getOp,err,payload) )
        obj.getOps[getOp] = 1
    def onResult( nodes ) :
        obj.getOps = {}
        obj.getResults = []
        for nodeAddr in nodes :
            doGetOffIM( nodeAddr )
        op.setCanceler( cancelGets )
        if not obj.getOps :
            op.notify( [] )
    publicKeyData = publicKey.toDER_PublicKey()
    lookupOp = self.lookup( toId(publicKeyData), startNodes,
            onResult )
    op = AsyncOp( callback, lookupOp.cancel )
    return op



def DHTClient_lookupPutOffIM( self, publicKey, envelope,
        startNodes, callback=None ) :
    obj = Dummy()
    def cancelPuts() :
        for putOp in obj.putOps.keys() :
            putOp.cancel()
    def doNotify() :
        op.notify( obj.successCount )
    def onPut( putOp, err, payload ) :
        del obj.putOps[putOp]
        if err >= 0 :
            result = payload[0]
            if result >= 0 :
                obj.successCount += 1
        if not obj.putOps :
            doNotify()
    def doPutOffIM( nodeAddr ) :
        putOp = self.callPutOffIM( publicKeyData, envelope,
                nodeAddr, lambda err,payload : onPut(putOp,err,payload) )
        obj.putOps[putOp] = 1
    def onResult( nodes ) :
        obj.nodes = nodes
        obj.successCount = 0
        obj.putOps = {}
        for nodeAddr in obj.nodes :
            doPutOffIM( nodeAddr )
        op.setCanceler( cancelPuts )
        if not obj.putOps :
            doNotify()
    publicKeyData = publicKey.toDER_PublicKey()
    lookupOp = self.lookup( toId(publicKeyData), startNodes,
            onResult )
    op = AsyncOp( callback, lookupOp.cancel )
    return op


def DHTClient_lookupDelOffIM( self, publicKey, envelope, signature,
        startNodes, callback=None ) :
    obj = Dummy()
    def cancelDels() :
        for delOp in obj.delOps.keys() :
            delOp.cancel()
    def doNotify() :
        op.notify( obj.successCount )
    def onDel( delOp, err, payload ) :
        del obj.delOps[delOp]
        if err >= 0 :
            result = payload
            if result >= 0 :
                obj.successCount += 1
        if not obj.delOps :
            doNotify()
    def doDelOffIM( nodeAddr ) :
        delOp = self.callDelOffIM( publicKeyData, envelope, signature,
                nodeAddr, lambda err,payload : onDel(delOp,err,payload) )
        obj.delOps[delOp] = 1
    def onResult( nodes ) :
        obj.nodes = nodes
        obj.successCount = 0
        obj.delOps = {}
        for nodeAddr in obj.nodes :
            doDelOffIM( nodeAddr )
        op.setCanceler( cancelDels )
        if not obj.delOps :
            doNotify()
    publicKeyData = publicKey.toDER_PublicKey()
    lookupOp = self.lookup( toId(publicKeyData), startNodes,
            onResult )
    op = AsyncOp( callback, lookupOp.cancel )
    return op


client.DHTClient.callPutOffIM = DHTClient_callPutOffIM
client.DHTClient.callGetOffIM = DHTClient_callGetOffIM
client.DHTClient.callDelOffIM = DHTClient_callDelOffIM
client.DHTClient.lookupGetOffIM = DHTClient_lookupGetOffIM
client.DHTClient.lookupPutOffIM = DHTClient_lookupPutOffIM
client.DHTClient.lookupDelOffIM = DHTClient_lookupDelOffIM







# Monkey-patch AppletConnection to spit out some DHT and key info
def AppletConnection_init( self, *args, **kwargs ):
    self._oldinit(*args, **kwargs)
    rt = self.requestTable
    rt['getprivkey'] = self._doGetPrivKey
    rt['getseednodes'] = self._doGetSeedNodes

def AppletConnection_doGetSeedNodes( self, words ):
    if len(words) != 0 :
        self._writeError( 'Malformed request' )
        return
    if not self.session.isOnline() :
        nodes = ["%s:%i" % node
                    for node in self.session.seedNodes]
    else:
        nodes = ["%s:%i" % node
                    for node in self.session.nodeTable.getNodes()]
    self._writeResult( nodes )

def AppletConnection_doGetPrivKey( self, words ):
    if len(words) != 0 :
        self._writeError( 'Malformed request' )
        return
    if not self.session.isOnline() :
        self._writeError( 'Not online' )
        return
    rsaKey = self.session.getProfile().rsaKey
    privKey = rsaKey.toDER_PrivateKey()
    self._writeResult( [hexEncode(privKey)] )

appletserver.AppletConnection._oldinit = appletserver.AppletConnection.__init__
appletserver.AppletConnection.__init__ = AppletConnection_init
appletserver.AppletConnection._doGetSeedNodes = AppletConnection_doGetSeedNodes
appletserver.AppletConnection._doGetPrivKey = AppletConnection_doGetPrivKey




def ApplicationConnection_init( self, *args, **kwargs ):
    self._oldinit(*args, **kwargs)
    rt = self.commands
    rt['getmyprivkey'] = "GetMyPrivKey"
    rt['getseednodes'] = "GetSeedNodes"
    self.seedNodes = []
    self.myPrivKey = None
    
def ApplicationConnection_req_GetMyPrivKey( self ):
    self.stream.writeData( 'GETPRIVKEY\r\n' )

def ApplicationConnection_resp_GetMyPrivKey( self, line ):
    privKeyData = hexDecode(line.strip())
    self.myPrivKey = privKeyData
    return ( privKeyData, )

def ApplicationConnection_req_GetSeedNodes( self ):
    self.stream.writeData( 'GETSEEDNODES\r\n' )

def ApplicationConnection_resp_GetSeedNodes( self, line ):
    self.seedNodes = []
    for nodeStr in line.strip().split():
        self.seedNodes.append(readAddr(wordDecode(nodeStr)))
    return ( self.seedNodes, )

def readAddr( arg ) :
    addr = arg.split( ':' )
    addr[1] = int(addr[1])
    addr = tuple(addr)
    return addr

ApplicationConnection._req_GetMyPrivKey = ApplicationConnection_req_GetMyPrivKey
ApplicationConnection._resp_GetMyPrivKey = ApplicationConnection_resp_GetMyPrivKey
ApplicationConnection._req_GetSeedNodes = ApplicationConnection_req_GetSeedNodes
ApplicationConnection._resp_GetSeedNodes = ApplicationConnection_resp_GetSeedNodes
ApplicationConnection._oldinit = ApplicationConnection.__init__
ApplicationConnection.__init__ = ApplicationConnection_init







class OfflineIM( object ):
    
    (UNCONNECTED,
     CONNECTING,
     GETTINGPUBKEY,
     GETTINGPRIVKEY,
     GETTINGNODES,
     READY) = range(6)
    
    def __init__( self, pendingMessages, reactor, peerPubKey=None, app=None ):
        self.reactor = reactor
        self.pendingMessages = pendingMessages
        self.digestType = DigestType( 'SHA1' )
        
        if peerPubKey:
            self.peerPubKeyData = peerPubKey
            self.peerPubKey = RSAKey()
            self.peerPubKey.fromDER_PublicKey( hexDecode( peerPubKey ) )
        else:
            self.peerPubKey = None
            self.peerPubKeyData = None


        # TODO: Switch to SHA256 for production usage
        self.pubKey = None
        self.pubKeyData = None
        self.privKeyData = None
        self.privKey = None
        self.seedNodes = None
        self.app = app
        self.dhtClient = None           # For storing/retrieving messages
        self.stream = None              # AppletConnection stream
        self.nodeAddr = None
        self.state = self.UNCONNECTED
        self.sock = None
        self.rpcSocket = None
        
        # AsyncOp objects
        self.connectOp = None
        self.dhtop = None
        self.putop = None
        self.getop = None
        self.delop = None
        
    def _doCancel( self ) :
        if self.connectOp : self.connectOp.cancel()
        if self.stream : self.stream.close( deferred=True )
        
        # Shutdown rpc socket, dhtclient
        if self.app is None:
            self.rpcSocket.close()
        self.dhtClient = None
        self.seedNodes = None
        self.privKey = None
        self.pubKey = None

        # Notify self.dhtop
        if self.dhtop: self.dhtop.notify(-1)
        self.dhtop = None
        
        self.state = self.UNCONNECTED
        
    def shutdown( self ):
        self._doCancel()
        # Notify self.putop
        if self.putop: self.putop.notify(-1)
        self.putop = None
        
        # Notify self.getop
        if self.getop: self.getop.notify(-1)
        self.getop = None
        
        # Notify self.delop
        if self.delop: self.delop.notify(-1)
        self.delop = None
        
        
    ## AppletConnection / App
    def initialize( self ):
        app = self.app
        if app is not None and app.sm.current() == app.ONLINE:
            profile = app.session.getProfile()
            self.privKeyData = profile.rsaKey.toDER_PrivateKey()
            self.privKey = RSAKey()
            self.privKey.fromDER_PrivateKey(self.privKeyData)
            self.pubKeyData = profile.rsaKey.toDER_PublicKey()
            self.pubKey = RSAKey()
            self.pubKey.fromDER_PublicKey(self.pubKeyData)
            self.pubKeyData = hexEncode(self.pubKeyData)
            self.app = app
            if hasattr(app, 'ev'):
                self.dispatcher = app.ev
            else:
                self.dispatcher = app.dispatcher
            self.dhtClient = app.session.dhtClient
            #self.seedNodes = app.session.nodeTable.getNodes()
            self.seedNodes = app.seedNodes
            self.startDHTClient()
        else:
            self.env = CSpaceEnv()
            self.connectOp = tcpConnect( ('127.0.0.1',self.env.port), self.reactor, self._onConnect )
            self.state = self.CONNECTING
            self.dispatcher = None
            

    def _onConnect( self, conn ):
        self.stream = TCPLineStream( conn.getSock(), self.reactor )
        self.stream.setCloseCallback( self._onClose )
        self.stream.setErrorCallback( self._onError )
        self.stream.setInputCallback( self._onInput )
        self.stream.enableRead( True )
        self.connectOp = None
        if self.pubKey is None:
            self.getPublicKey()
        elif self.privKey is None:
            self.getPrivateKey()
        else:
            self.getSeedNodes()
        
    def getPublicKey( self ):
        self.stream.writeData( 'GETPUBKEY\r\n' )
        self.state = self.GETTINGPUBKEY
    
    def getPrivateKey( self ):
        self.stream.writeData( 'GETPRIVKEY\r\n')
        self.state = self.GETTINGPRIVKEY
    
    def getSeedNodes( self ):
        self.stream.writeData( 'GETSEEDNODES\r\n' )
        self.state = self.GETTINGNODES

    def _onClose( self ) :
        self._doCancel()

    def _onError( self, err, errMsg ) :
        self._onClose()
        
    def _toIP(self, ipstr):
        ipaddr, port = ipstr.split(":")
        return (ipaddr, int(port))
    
    def _onInput( self, line ) :
        if self.state == self.GETTINGPUBKEY :
            if not line.startswith('OK') :
                self.shutdown( )
                return
            self.pubKeyData = line.split()[1]
            self.pubKey = RSAKey()
            self.pubKey.fromDER_PublicKey( hexDecode( self.pubKeyData ) )
            self.getPrivateKey()
            
        elif self.state == self.GETTINGPRIVKEY :
            if not line.startswith('OK') :
                self.shutdown( )
                return
            self.privKeyData = line.split()[1]
            self.privKey = RSAKey()
            self.privKey.fromDER_PrivateKey( hexDecode( self.privKeyData ) )
            self.getSeedNodes()
            
        elif self.state == self.GETTINGNODES:
            if not line.startswith('OK') :
                self._doCancel()
                return
            nodes = line.strip().split(" ")[1:]
            self.seedNodes = [ self._toIP(wordDecode(node))
                               for node in nodes ]
            self.stream.close( deferred=True )
            self.stream = None
            self.startDHTClient()
            
        else :
            assert False
    
    
    ## DHT
    def startDHTClient( self, callback=None ):
        if self.dhtop is None:
            self.dhtop = AsyncOp(callback, self._doCancel)
        
        if None in (self.privKey, self.seedNodes):
            self.initialize()
            return
        
        if not self.dhtClient:
            self.sock = socket( AF_INET, SOCK_DGRAM )
            self.sock.bind( ('',0) )
            self.rpcSocket = RPCSocket( self.sock, self.reactor )
            self.dhtClient = DHTClient( self.rpcSocket )
        
        
        self.pubKeyDigest = Digest( self.digestType ).digest( self.pubKeyData )
        if self.peerPubKeyData:
            self.peerPubKeyDigest = Digest( self.digestType ).digest( self.peerPubKeyData )
        else:
            self.peerPubKeyDigest = None

        self.state = self.READY
        if self.dhtop is not None:
            self.dhtop.notify()

    def storeOfflineMessages( self, callback=None ):
        if callback or not self.putop:
            self.putop = AsyncOp( callback, self._doCancel )
        
        if not self.dhtClient:
            self.startDHTClient(self._doStore)
            return
        
        self._doStore()
        
    def _doStore( self, status=0 ):
        if status == -1:
            return
        
        if not len(self.pendingMessages):
            return
        
        global logger
        
        msg = self.pendingMessages.pop(0)
        
        # Sign the message.
        sigdata = bencode( (self.peerPubKeyDigest, self.pubKeyDigest,
                            int(time()), msg ) )
        digest = Digest( self.digestType ).digest( sigdata )
        signature = self.privKey.sign( digest, self.digestType )
        
        # Wrap it in an envelope for the peer
        envdata = bencode( (self.peerPubKeyDigest, self.pubKeyDigest,
                            int(time()), msg, signature ) )
        maxlen = self.peerPubKey.maxInputSize()
        logger.debug( "Envelope in %i chunks." % int(len(envdata) / maxlen) )
        logger.debug( "EnvData Length: %i" % len(envdata) )
        envelope = ""
        # NOTE: While for unlimited length messages, session keys would probably
        # be faster, we can reasonably assume the data here is pretty short (<1kB)
        for start in range(0, len(envdata), maxlen):
            partdata = envdata[start:start+maxlen]
            envelope += self.peerPubKey.encrypt(partdata)
        logger.debug( "Envelope Length: %i" % len(envelope) )
        
        self.dhtClient.lookupPutOffIM( self.peerPubKey, envelope,
                                       self.seedNodes, lambda s: self._onOfflineStored(s,msg) )
        
    
    def _onOfflineStored( self, successcount, msg=None ):
        if self.putop:
            self.putop.notify( successcount )
            if self.dispatcher:
                self.dispatcher.trigger('offlineim.put', msg)
        if len(self.pendingMessages):
            self._doStore( )
    
    
    def retrieveOfflineMessages( self, callback=None ):
        if callback or not self.getop:
            self.getop = AsyncOp( callback, self._doCancel )
        
        if not self.dhtClient:
            self.startDHTClient(self._doRetrieve)
            return
        
        self._doRetrieve()

    
    def _doRetrieve( self, status=0 ):
        if status == -1: return
        self.dhtClient.lookupGetOffIM( self.pubKey, self.seedNodes, self._onOfflineRetrieved )
        
    
    def _onOfflineRetrieved( self, envelopes ):
        # TODO: Move this to a background worker thread?
        global logger
        logger.info( "Retrieved %i offline messages." % len(envelopes) )
        for envelope in envelopes:            
            # Decrypt the content in blocks
            maxlen = self.privKey.maxInputSize() + self.privKey.paddingSize(PADDING_PKCS1_OAEP)
            logger.debug("Envelope in %i chunks." % int(len(envelope) / maxlen))
            logger.debug("Envelope Length: %i" % len(envelope))
            envdata = ""
            for start in range(0, len(envelope), maxlen):
                envpart = envelope[start:start+maxlen]
                try:
                    envdata += self.privKey.decrypt(envpart)
                except RSAError:
                    self.deleteOfflineMessage( envelope )
                    envdata = ""
                    break
            if len(envdata) == 0:
                continue
            
            logger.debug("EnvData Length: %i" % len(envdata))

            pubKeyDigest, peerPubKeyDigest, ts, msg, signature = bdecode(envdata)

            # Check the message peer pub key against our peer's pub key
            if self.peerPubKeyDigest not in ( None,peerPubKeyDigest ) :
                # Skip this message.  Different sender.
                logger.debug("Skipping message.  Different sender.")
                continue

            # Check the message pub key against our pub key
            if pubKeyDigest != self.pubKeyDigest:
                # Delete the message for being bad.
                logger.warn("Deleting message.  Bad recipient.")
                self.deleteOfflineMessage( envelope )
                continue
            
            # Check the signature, but only if we are inside the IM applet
            if self.peerPubKeyDigest:
                sigdata = bencode((pubKeyDigest, peerPubKeyDigest, ts, msg))
                digest = Digest( self.digestType ).digest( sigdata )
                try :
                    self.peerPubKey.verify( signature, digest, self.digestType )
                except RSAError :
                    # Delete the message for having a fake signature.
                    logger.warn("Deleting message.  Bad signature.")
                    self.deleteOfflineMessage( envelope )
                    continue
            
            # Pass it on
            if self.dispatcher:
                self.dispatcher.trigger('offlineim.get', ts, msg, peerPubKeyDigest)

            self.getop.notify(ts, msg, peerPubKeyDigest)
            
            if self.peerPubKeyDigest:
                # Liberate the message record from the DHT
                logger.info("Deleting message.  Successfully received.")
                self.deleteOfflineMessage( envelope )

    def deleteOfflineMessage( self, envelope ):
        sigdata = bencode( (hexDecode(self.pubKeyData), envelope) )
        digest = Digest( self.digestType ).digest( sigdata )
        signature = self.privKey.sign( digest, self.digestType )
        
        self.dhtClient.lookupDelOffIM( self.pubKey, envelope, signature,
                                       self.seedNodes, lambda s : self._onOfflineDeleted(s, envelope) )
    
    def _onOfflineDeleted( self, successcount, envelope=None ):
        # Not much to do here.
        global logger
        if self.dispatcher and successcount > 0:
            self.dispatcher.trigger('offlineim.del', envelope)
        logger.debug( "Success count: %i" % successcount )
#







# Monkey-patch the console application
def CSpaceService_init(self, *args, **kwargs):
    self._oldinit(*args, **kwargs)
    self.offlineIM = OfflineIM([], self.reactor, app=self)
    self.sm.appendCallback( lambda : self.offlineIM.retrieveOfflineMessages(
                                        self._onOfflineRetrieved) ,
                           self.CONNECTING, self.ONLINE)
    self.sm.appendCallback(self.offlineIM.shutdown,
                           self.ONLINE, self.DISCONNECTING)
    self.digestType = DigestType( "SHA1" )

def CSpaceService_onOfflineRetrieved(self, ts, msg=None, peerPubKeyDigest=None):
    if ts == -1: return
    contacts = self.session.getProfile().contactNames
    for name,contact in contacts.items():
        if not hasattr(contact, 'publicKeyDigest'):
            contact.publicKeyDigest = Digest( self.digestType ).digest(hexEncode(contact.publicKeyData))
        if contact.publicKeyDigest == peerPubKeyDigest:
            self.action(name, 'TextChat')
            return
        

service.CSpaceService._oldinit = service.CSpaceService.__init__
service.CSpaceService.__init__ = CSpaceService_init
service.CSpaceService._onOfflineRetrieved = CSpaceService_onOfflineRetrieved

# Monkey-patch the GUI application
def MainWindow_init(self, *args, **kwargs):
    self._oldinit(*args, **kwargs)
    self.offlineIM = OfflineIM([], self.reactor, app=self)
    self.sm.appendCallback(lambda : self.offlineIM.retrieveOfflineMessages(
                                        self._onOfflineRetrieved) ,
                           self.CONNECTING, self.ONLINE)
    self.sm.appendCallback(self.offlineIM.shutdown,
                           self.ONLINE, self.DISCONNECTING)
    self.digestType = DigestType( "SHA1" )


def MainWindow_onOfflineRetrieved(self, ts, msg=None, peerPubKeyDigest=None):
    if ts == -1: return
    contacts = self.session.getProfile().contactNames
    for name,contact in contacts.items():
        if not hasattr(contact, 'publicKeyDigest'):
            contact.publicKeyDigest = Digest( self.digestType ).digest(hexEncode(contact.publicKeyData))
        if contact.publicKeyDigest == peerPubKeyDigest:
            self.actionManager.execDefaultAction(name)
            return
        
app.MainWindow._oldinit = app.MainWindow.__init__
app.MainWindow.__init__ = MainWindow_init
app.MainWindow._onOfflineRetrieved = MainWindow_onOfflineRetrieved



# Monkey-Patch the IM applet
def IMWindow_init( self, *args, **kwargs ):
    self._oldinit( *args, **kwargs )
    self.offlineIM = OfflineIM(self.pendingMessages,
                               self.reactor,
                               self.peerPubKey)
    self.offlineIM.retrieveOfflineMessages(self._onOfflineRetrieved)
    
def IMWindow_shutdown( self ):
    if self.offlineIM is not None:
        self.offlineIM.shutdown()
    self._oldshutdown()
    
def IMWindow_onOfflineStored( self, successcount):
    if successcount > 0:
        self.ui.statusLabel.setText( 'Offline Message Sent' )
        return
    self.ui.statusLabel.setText( 'Failed to send Offline Message.' )
    
def IMWindow_onOfflineRetrieved( self, tstamp, msg='', peerPubKey=None ):
    if tstamp == -1:
        # TODO: Status error message?
        return
    if self.isHidden() : self.show()
    self._offlineMessage( msg, self.peerName, tstamp )
    
def IMWindow_offlineMessage( self, msg, fromUser, tstamp ):
    msg = unicode( msg, 'utf8', 'replace' )
    msg = unicode( Qt.escape(msg) )
    msg = msg.replace( '\r\n', '<br/>' )
    msg = msg.replace( '\n', '<br/>' )
    msg = msg.replace( '\t', '    ' )
    msg = msg.replace( '  ', ' &nbsp;' )
    color = (fromUser == self.peerName) and '#FF821C' or 'black'
    tstext = str(datetime.fromtimestamp(int(tstamp)))
    self.ui.chatLogView.append( u'<font face="Verdana" size="-1" color="%s"><i>[%s]</i>&nbsp;<b>%s: </b></font>%s' % (color,tstext,fromUser,msg) )
    self.flash()


def IMWindow_onConnClose( self, conn ):
    if conn in self.connecting :
        self.connecting.remove( conn )
        if self.pendingMessages :
            self.offlineIM.storeOfflineMessages(self._onOfflineStored)
        self.ui.statusLabel.setText( 'Offline Messaging (Connection Failed)' )
    else :
        assert conn in self.connected
        self.connected.remove( conn )
        self.ui.statusLabel.setText( '' )
    if (not self.connecting) and (not self.connected) and self.isHidden() :
        self.shutdown()

def initIM(IMWindow):
    IMWindow._oldinit = IMWindow.__init__
    IMWindow._oldshutdown = IMWindow.shutdown
    IMWindow._oldonConnClose = IMWindow._onConnClose
    
    IMWindow.__init__ = IMWindow_init
    IMWindow.shutdown = IMWindow_shutdown
    IMWindow._onOfflineStored = IMWindow_onOfflineStored
    IMWindow._onConnClose = IMWindow_onConnClose
    IMWindow._onOfflineRetrieved = IMWindow_onOfflineRetrieved
    IMWindow._offlineMessage = IMWindow_offlineMessage

