#!/usr/bin/python

#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#  For most of DHN code (outside ssh I think) we will only use ascii encoded string versions of keys.
#  Expect to make keys, signatures, and hashes all base64 strings soon.
#
#  Our local key is always onhand.
#
#  Todo:
#     Main thing is to be able to use public keys in contacts to verify dhnpackets
#     We never want to bother storing bad data, and need localtester to do localscrub
#
# Crypto info:
# http://www.amk.ca/python/writing/pycrypt/pycrypt.html

# run several times from interpreter and it does not like loading RSA key from previous run PREPRO


import os
import random
import base64
import hashlib
import time

from Crypto.PublicKey import RSA
from Crypto.Cipher import DES3,AES

import warnings
warnings.filterwarnings('ignore',category=DeprecationWarning)
from twisted.conch.ssh import keys
from twisted.spread import banana,jelly

import settings
import dhnio
import misc



# Global for this file
MyRsaKey = "" 
# This will be an object
LocalKey = None

#------------------------------------------------------------------------------ 

def isMyLocalKeyReady():
    global LocalKey
    return LocalKey is not None

def MyPublicKey():
    global MyRsaKey
    global LocalKey
    InitMyKey()
    Result = LocalKey.public().toString('openssh')
    return Result

def MyPrivateKey():
    global MyRsaKey
    global LocalKey
    InitMyKey()
    return LocalKey.toString('openssh')

def MyPublicKeyObject():
    global LocalKey
    InitMyKey()
    return LocalKey.public()

def MyPrivateKeyObject():
    global LocalKey
    InitMyKey()
    return LocalKey

def InitMyKey():
    dhnio.Dprint(18, 'dhncrypto.InitMyKey')
    global MyRsaKey
    global LocalKey
    if LocalKey is not None:
        return
    if MyRsaKey != "":
        return
    keyfilename = settings.KeyFileName()
    if os.path.exists(keyfilename):
        dhnio.Dprint(4, 'dhncrypto.InitMyKey load private key ')
        LocalKey = keys.Key.fromFile(keyfilename)
        MyRsaKey = LocalKey.keyObject
    else:
        dhnio.Dprint(4, 'dhncrypto.InitMyKey generate new private key')
        MyRsaKey = RSA.generate(2048, os.urandom)       #  want 2048 but might have had problem - had shorter when using banana for serialization
        LocalKey = keys.Key(MyRsaKey)
        keystring = LocalKey.toString('openssh')
        dhnio.WriteFile(keyfilename, keystring)

def Sign(input):
    #global MyRsaKey
    global LocalKey
    InitMyKey()
    # Makes a list but we just want a string
    Signature = LocalKey.keyObject.sign(input, '')
    # so we take first element in list - need str cause was long    
    result = str(Signature[0]) 
    return result

# key is public key in string format - as is dhncrypto standard, mostly
def VerifySignature(keystring, hashcode, signature):
    dhnio.Dprint(18, "dhncrypto.VerifySignature")
    keyobj = keys.Key.fromString(keystring).keyObject
    # needs to be a long in a list
    sig2 = long(signature),
    Result = bool(keyobj.verify(hashcode, sig2))
    return Result

def Verify(ConIdentity, hashcode, signature):
    dhnio.Dprint(18, "dhncrypto.Verify")
    key = ConIdentity.publickey
    Result = VerifySignature(key, hashcode, signature)
    return Result

def HashSHA(input):
    return hashlib.sha1(input).digest()
##    return(sha.new(input).digest())

def HashMD5(input):
    return hashlib.md5(input).digest()
##    return(md5.new(input).digest())

def Hash(input):
    return HashMD5(input)

#  Outside of this file we just use the string version of the public keys
def EncryptStringPK(publickeystring, input):
    keyobj = keys.Key.fromString(publickeystring)
    return EncryptBinaryPK(keyobj, input)

# This is just using local key
def EncryptLocalPK(input):
    global MyRsaKey
    global LocalKey
    InitMyKey()
    return EncryptBinaryPK(LocalKey, input)

# There is a bug in rsa.encrypt if there is a leading '\0' in the string.
# Only think we encrypt is produced by NewSessionKey() which takes care not to have leading zero.
# See   bug report in http://permalink.gmane.org/gmane.comp.python.cryptography.cvs/217
# So we add a 1 in front.
def EncryptBinaryPK(publickey, input):
    atuple = publickey.keyObject.encrypt("1"+input,"")
    #why "1"+input ???????? TODO
    #we just use strings here 
    return atuple[0]                     

# we only decript with our local private key so no argument for that
def DecryptLocalPK(input):
    global MyRsaKey
    global LocalKey
    InitMyKey()
    atuple=(input,)
    padresult=MyRsaKey.decrypt(atuple)
    result=padresult[1:]                   # remove the "1" added in EncryptBinaryPK
    dhnio.Dprint(14, "DecryptLocalPK input len=%d   output len=%d" % (len(input), len(result)))
    return(result)

def SessionKeyType():
    return "DES3"

def NewSessionKey():
    return chr(random.randint(1,255))+os.urandom(23)   # to work around bug in rsa.encrypt
##    return(os.urandom(24))          # really random string for making equivalent DES3 objects when needed

def EncryptWithSessionKey(rand24, input):
    SessionKey = DES3.new(rand24)
    data = misc.RoundupString(input,24)
    return SessionKey.encrypt(data)

def DecryptWithSessionKey(rand24, input):
    SessionKey = DES3.new(rand24)
    return SessionKey.decrypt(input)


def main():
    global LocalKey
    global MyRsaKey
    InitMyKey()

    samphash = HashMD5("test string")
    signature = Sign(samphash)
    print signature
    mk=MyPublicKey()
    if (VerifySignature(mk, samphash, signature)):
        print "verify signature is good"
    else:
        print "verify signature is bad"

def testsign():
    global MyRsaKey
    InitMyKey()
    sample = 'TestingDATA1123123\n3434\n.......,,,,,,,,dfasdf\\//'
    sample_hash = hashlib.md5(sample).digest()
##    sample_hash = md5.new(sample).digest()
    print len(sample_hash)
    sample_sign = MyRsaKey._sign(sample_hash, '')
    print sample_sign

if __name__ == '__main__':
##    main()
    testsign()


