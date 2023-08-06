import os, sys, StringIO
from types import StringType
from ncrypt.rsa import RSAKey, RSAError

from cspace.util.hexcode import hexEncode, hexDecode, HexDecodeError
from cspace.main.common import profileSettings, isValidUserName

class Contact( object ) :
    def __init__( self, publicKey, name ) :
        assert isValidUserName( name )
        self.publicKey = publicKey
        self.name = name
        self.publicKeyData = publicKey.toDER_PublicKey()

class Profile( object ) :
    def __init__( self, rsaKey, name, keyId, storeEntry ) :
        assert isValidUserName( name )
        self.rsaKey = rsaKey
        self.name = name
        self.keyId = keyId
        self.storeEntry = storeEntry
        self.contactNames = {}
        self.contactKeys = {}

    def addContact( self, contact ) :
#        if contact.name in self.contactNames:
#            print contact.name, 'already in contacts'
        assert contact.name not in self.contactNames
#        if contact.publicKeyData in self.contactKeys:
#            print contact.name, 'and public key too'
        assert contact.publicKeyData not in self.contactKeys
        self.contactKeys[contact.publicKeyData] = contact
        self.contactNames[contact.name] = contact

    def getContactByName( self, contactName ) :
        return self.contactNames.get( contactName )

    def getContactByPublicKey( self, publicKey ) :
        return self.contactKeys.get( publicKey.toDER_PublicKey() )

    def getContactNames( self ) :
        names = self.contactNames.keys()
        names.sort()
        return names

    def changeContactName( self, oldName, newName ) :
        assert isValidUserName( newName )
        c = self.contactNames.pop( oldName )
        c.name = newName
        self.contactNames[newName] = c

    def removeContact( self, contact ) :
        del self.contactNames[contact.name]
        del self.contactKeys[contact.publicKeyData]

def listProfiles() :
    ps = profileSettings()
    profiles = []
    for entry in ps.listEntries('') :
        userName = ps.getData( entry+'/Name' )
        keyId = ps.getData( entry+'/KeyID' )
        profiles.append( (userName,keyId,entry) )
    return profiles

def fromDER_PublicKeyFixed(src):
    from pyasn1.codec.der import decoder
    (priv, _) = decoder.decode(src)
    as_ints = tuple(int(x) for x in priv)
    k = RSAKey()
    k.loadPublicKey((as_ints[0], as_ints[1]))
    return k

#_ProfileObj = None
def loadProfile( entry, password ) :
    #global _ProfileObj
    #if _ProfileObj is not None:
        #return _ProfileObj
    ps = profileSettings()
    userName = ps.getData( entry+'/Name' )
    keyId = ps.getData( entry+'/KeyID' )
    encKey = ps.getData( entry+'/PrivateKey' )
    rsaKey = RSAKey()
    try :
        rsaKey.fromPEM_PrivateKey( encKey, password )
    except RSAError :
        return None
    profile = Profile( rsaKey, userName, keyId, entry )
    contactsData = ps.getData( entry+'/ContactList', '' )
    for line in contactsData.split('\n') :
        line = line.strip()
        if not line : continue
        name,hexKey = line.split(':')
        assert isValidUserName(name)
        #pubKey = RSAKey()
        hd = hexDecode(hexKey)
        #pubKey.fromDER_PublicKey( hd )
        try:        
            pubKey = fromDER_PublicKeyFixed( hd )
        except:
            return None
        #print 'profile.RSAKey', id(pubKey), name, hd.encode('hex')
        contact = Contact( pubKey, name )
        profile.addContact( contact )
    #_ProfileObj = profile
    return profile

def createProfile( rsaKey, password, userName, keyId ) :
    assert isValidUserName( userName )
    ps = profileSettings()
    baseEntry = userName
    entry = baseEntry
    suffix = 0
    while ps.getData(entry+'/PrivateKey') :
        suffix += 1
        entry = '%s-%d' % (baseEntry,suffix)
    encKey = rsaKey.toPEM_PrivateKey( password )
    ps.setData( entry+'/PrivateKey', encKey )
    ps.setData( entry+'/Name', userName )
    if keyId is not None :
        ps.setData( entry+'/KeyID', keyId )
    profile = Profile( rsaKey, userName, keyId, entry )
    return profile

def saveProfileContacts( profile ) :
    out = StringIO.StringIO()
    for name in profile.getContactNames() :
        c = profile.getContactByName( name )
        hexKey = hexEncode( c.publicKeyData )
        print>>out, '%s:%s' % (name,hexKey)
    ps = profileSettings()
    ps.setData( profile.storeEntry + '/ContactList', out.getvalue() )

def clearProfileContacts( profile ):
    ps = profileSettings()
    ps.setData( profile.storeEntry + '/ContactList', '' )
    
