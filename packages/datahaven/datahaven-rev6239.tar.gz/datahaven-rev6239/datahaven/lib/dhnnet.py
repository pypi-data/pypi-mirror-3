#!/usr/bin/python
#dhnnet.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#
#    simple network routines
#    do not want to import any dhn modules here

import os
import sys
import types
import socket
import urllib2

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in dhnnet.py')

from twisted.internet.defer import Deferred, fail
from twisted.web import client
from twisted.web.client import _parse
from twisted.web.client import getPage
from twisted.web.client import downloadPage
from twisted.web.client import HTTPClientFactory
from twisted.web.client import HTTPDownloader
from twisted.internet import ssl
from OpenSSL import SSL


_UserAgentString = "DataHaven.NET-http-agent"
_ProxySettings = {
    'host': '',
    'port': '',
    'ssl': 'False',
    'username':'',
    'password': ''
    }

#------------------------------------------------------------------------------

def init():
    pass

def detect_proxy_settings():
    d = {
        'host':'',
        'port':'',
        'username':'',
        'password':'',
        'ssl': 'False'}
    httpproxy = urllib2.getproxies().get('http', None)
    httpsproxy = urllib2.getproxies().get('https', None)

    if httpproxy is not None:
        try:
            scheme, host, port, path = _parse(httpproxy)
        except:
            return d
        d['ssl'] = 'False'
        d['host'] = host
        d['port'] = port

    if httpsproxy is not None:
        try:
            scheme, host, port, path = _parse(httpsproxy)
        except:
            return d
        d['ssl'] = 'True'
        d['host'] = host
        d['port'] = port

    return d

def set_proxy_settings(settings_dict):
    global _ProxySettings
    _ProxySettings = settings_dict

def get_proxy_settings():
    global _ProxySettings
    return _ProxySettings

def get_proxy_host():
    global _ProxySettings
    return _ProxySettings.get('host', '')

def get_proxy_port():
    global _ProxySettings
    try:
        return int(_ProxySettings.get('port', '8080'))
    except:
        return 8080

def get_proxy_username():
    global _ProxySettings
    return _ProxySettings.get('username', '')

def get_proxy_password():
    global _ProxySettings
    return _ProxySettings.get('password', '')

def get_proxy_ssl():
    global _ProxySettings
    return _ProxySettings.get('ssl', '')

def proxy_is_on():
    return get_proxy_host() != ''

#-------------------------------------------------------------------------------

class MyHTTPClientFactory(HTTPClientFactory):
    def page(self, page):
        if self.waiting:
            self.waiting = 0
            self.deferred.callback(page)

    def noPage(self, reason):
        if self.waiting:
            self.waiting = 0
            self.deferred.errback(reason)

    def clientConnectionFailed(self, _, reason):
        if self.waiting:
            self.waiting = 0
            self.deferred.errback(reason)


def getPageTwistedOld(url):
    global _UserAgentString
    scheme, host, port, path = _parse(url)
    factory = MyHTTPClientFactory(url, agent=_UserAgentString)
    reactor.connectTCP(host, port, factory)
    return factory.deferred

#------------------------------------------------------------------------------


def downloadPageTwisted(url, filename):
    global _UserAgentString
    return downloadPage(url, filename, agent=_UserAgentString)

#-------------------------------------------------------------------------------

#http://schwerkraft.elitedvb.net/plugins/scmcvs/cvsweb.php/enigma2-plugins/mediadownloader/src/HTTPProgressDownloader.py?rev=1.1;cvsroot=enigma2-plugins;only_with_tag=HEAD
class HTTPProgressDownloader(HTTPDownloader):
    """Download to a file and keep track of progress."""

    def __init__(self, url, fileOrName, writeProgress = None, *args, **kwargs):
        HTTPDownloader.__init__(self, url, fileOrName, supportPartial=0, *args, **kwargs)
        # Save callback(s) locally
        if writeProgress and type(writeProgress) is not list:
            writeProgress = [ writeProgress ]
        self.writeProgress = writeProgress

        # Initialize
        self.currentlength = 0
        self.totallength = None

    def gotHeaders(self, headers):
        HTTPDownloader.gotHeaders(self, headers)

        # If we have a callback and 'OK' from Server try to get length
        if self.writeProgress and self.status == '200':
            if headers.has_key('content-length'):
                self.totallength = int(headers['content-length'][0])
                for cb in self.writeProgress:
                    if cb:
                        cb(0, self.totallength)


    def pagePart(self, data):
        HTTPDownloader.pagePart(self, data)

        # If we have a callback and 'OK' from server increment pos
        if self.writeProgress and self.status == '200':
            self.currentlength += len(data)
            for cb in self.writeProgress:
                if cb:
                    cb(self.currentlength, self.totallength)




def downloadWithProgressTwisted(url, file, progress_func):
    global _UserAgentString
    scheme, host, port, path = _parse(url)
    factory = HTTPProgressDownloader(url, file, progress_func, agent=_UserAgentString)
    if scheme == 'https':
        contextFactory = ssl.ClientContextFactory()
        reactor.connectSSL(host, port, factory, contextFactory)
    else:
        reactor.connectTCP(host, port, factory)
    return factory.deferred

#-------------------------------------------------------------------------------


def downloadSSLWithProgressTwisted(url, file, progress_func, privateKeyFileName, certificateFileName):
    global _UserAgentString
    scheme, host, port, path = _parse(url)
    factory = HTTPProgressDownloader(url, file, progress_func, agent=_UserAgentString)
    if scheme != 'https':
        return None
    contextFactory = ssl.DefaultOpenSSLContextFactory(privateKeyFileName, certificateFileName)
    reactor.connectSSL(host, port, factory, contextFactory)
    return factory.deferred


#-------------------------------------------------------------------------------


class MyClientContextFactory(ssl.ClientContextFactory):
    def __init__(self, certificates_filenames):
        self.certificates_filenames = list(certificates_filenames)

    def verify(self, connection, x509, errnum, errdepth, ok):
        return ok

    def getContext(self):
        ctx = ssl.ClientContextFactory.getContext(self)
        for cert in self.certificates_filenames:
            try:
                ctx.load_verify_locations(cert)
            except:
                pass
        ctx.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT , self.verify)
        return ctx


def downloadSSL(url, fileOrName, progress_func, certificates_filenames):
    global _UserAgentString
    scheme, host, port, path = _parse(url)
    if scheme != 'https':
        return fail('expect only https protocol')
    if not isinstance(certificates_filenames, types.ListType):
        certificates_filenames = [certificates_filenames, ]
    cert_found = False
    for cert in certificates_filenames:
        if os.path.isfile(cert) and os.access(cert, os.R_OK):
            cert_found = True
            break
    if not cert_found:
        return fail('no one ssl certificate found')
    factory = HTTPDownloader(url, fileOrName, agent=_UserAgentString)
    contextFactory = MyClientContextFactory(certificates_filenames)
    reactor.connectSSL(host, port, factory, contextFactory)
    return factory.deferred

#------------------------------------------------------------------------------

class NoVerifyClientContextFactory:
    isClient = 1
    method = SSL.SSLv3_METHOD
    def getContext(self):
        def x(*args):
            return True
        ctx = SSL.Context(self.method)
        #print dir(ctx)
        ctx.set_verify(SSL.VERIFY_NONE,x)
        return ctx

def downloadSSL2(url, fileOrName, progress_func, certificates_filenames=[]):
    global _UserAgentString
    factory = HTTPDownloader(url, fileOrName, agent=_UserAgentString)

    if proxy_is_on():
        factory.path = url
        # TODO
        # need to check certificate too
        contextFactory = MyClientContextFactory(certificates_filenames)
        reactor.connectSSL(get_proxy_host(), get_proxy_port(), factory, contextFactory)

    else:
        scheme, host, port, path = _parse(url)
        if not isinstance(certificates_filenames, types.ListType):
            certificates_filenames = [certificates_filenames, ]
        cert_found = False
        for cert in certificates_filenames:
            if os.path.isfile(cert) and os.access(cert, os.R_OK):
                cert_found = True
                break
        if not cert_found:
            return fail('no one ssl certificate found')
        contextFactory = MyClientContextFactory(certificates_filenames)
        reactor.connectSSL(host, port, factory, contextFactory)

    return factory.deferred

#-------------------------------------------------------------------------------

class ProxyClientFactory(client.HTTPClientFactory):
    def setURL(self, url):
        client.HTTPClientFactory.setURL(self, url)
        self.path = url

def getPageTwisted(url):
    global _UserAgentString
    if proxy_is_on():
        factory = ProxyClientFactory(url, agent=_UserAgentString)
        reactor.connectTCP(get_proxy_host(), get_proxy_port(), factory)
        return factory.deferred
    else:
        return getPage(url, agent=_UserAgentString)

#------------------------------------------------------------------------------

def downloadHTTP(url, fileOrName):
    global _UserAgentString
    scheme, host, port, path = _parse(url)
    factory = HTTPDownloader(url, fileOrName, agent=_UserAgentString)
    if proxy_is_on():
        host = get_proxy_host()
        port = get_proxy_port()
        factory.path = url
    reactor.connectTCP(host, port, factory)
    return factory.deferred

#-------------------------------------------------------------------------------

def IpIsLocal(ip):
    if ip == '':
        return True
    if ip == '0.0.0.0':
        return True
    if ip.startswith('192.168.'):
        return True
    if ip.startswith('10.'):
        return True
    if ip.startswith('127.'):
        return True
    if ip.startswith('172.'):
        try:
            secondByte = int(ip.split('.')[1])
        except:
            raise Exception('wrong ip address ' + str(ip))
            return True
        if secondByte >= 16 and secondByte <= 31:
            return True
    return False

#-------------------------------------------------------------------------------

def getLocalIpError():
    import socket
    addr = socket.gethostbyname(socket.gethostname())
    if addr == "127.0.0.1" and os.name == 'posix':
        import commands
        output = commands.getoutput("/sbin/ifconfig")
        #TODO parseaddress not done yet
        addr = parseaddress(output)
    return addr


#http://ubuntuforums.org/showthread.php?t=1215042
def getLocalIp(): # had this in p2p/stun.py
    import socket
    # 1: Use the gethostname method

    try:
        ipaddr = socket.gethostbyname(socket.gethostname())
        if not( ipaddr.startswith('127') ) :
            #print('Can use Method 1: ' + ipaddr)
            return ipaddr
    except:
        pass

    # 2: Use outside connection
    '''
    Source:
    http://commandline.org.uk/python/how-to-find-out-ip-address-in-python/
    '''

    ipaddr=''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('google.com', 0))
        ipaddr=s.getsockname()[0]
        #print('Can used Method 2: ' + ipaddr)
        return ipaddr
    except:
        pass


    # 3: Use OS specific command
    import subprocess , platform
    ipaddr=''
    os_str=platform.system().upper()

    if os_str=='LINUX' :

        # Linux:
        arg='ip route list'
        p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
        data = p.communicate()
        sdata = data[0].split()
        ipaddr = sdata[ sdata.index('src')+1 ]
        #netdev = sdata[ sdata.index('dev')+1 ]
        #print('Can used Method 3: ' + ipaddr)
        return ipaddr

    elif os_str=='WINDOWS' :

        # Windows:
        arg='route print 0.0.0.0'
        p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
        data = p.communicate()
        strdata=data[0].decode()
        sdata = strdata.split()

        while len(sdata)>0:
            if sdata.pop(0)=='Netmask' :
                if sdata[0]=='Gateway' and sdata[1]=='Interface' :
                    ipaddr=sdata[6]
                    break
        #print('Can used Method 4: ' + ipaddr)
        return ipaddr

    return '127.0.0.1' # uh oh, we're in trouble, but don't want to return none

#-------------------------------------------------------------------------------

def TestInternetConnection(remote_host='www.google.com'):
    try:
        (family, socktype, proto, garbage, address) = socket.getaddrinfo(remote_host, "http")[0]
    except Exception, e:
        return False

    s = socket.socket(family, socktype, proto)

    try:
        result = s.connect(address)
    except Exception, e:
        return False

    return result is None or result == 0


#------------------------------------------------------------------------------


def SendEmail(TO, FROM, HOST, PORT, LOGIN, PASSWORD, SUBJECT, BODY, FILES):
#    try:
        import smtplib
        from email import Encoders
        from email.MIMEText import MIMEText
        from email.MIMEBase import MIMEBase
        from email.MIMEMultipart import MIMEMultipart
        from email.Utils import formatdate

        msg = MIMEMultipart()
        msg["From"] = FROM
        msg["To"] = TO
        msg["Subject"] = SUBJECT
        msg["Date"]    = formatdate(localtime=True)
        msg.attach(MIMEText(BODY))

        # attach a file
        for filePath in FILES:
            if not os.path.isfile(filePath):
                continue
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(filePath,"rb").read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filePath))
            msg.attach(part)

        s = smtplib.SMTP(HOST, PORT)

        #s.set_debuglevel(True) # It's nice to see what's going on

        s.ehlo() # identify ourselves, prompting server for supported features

        if s.has_extn('STARTTLS'):
            s.starttls()
            s.ehlo() # re-identify ourse

        s.login(LOGIN, PASSWORD)  # optional

        failed = s.sendmail(FROM, TO, msg.as_string())

        s.close()

#    except:
#        dhnio.DprintException()


#-------------------------------------------------------------------------------


def test1():
    def done(x, filen):
        print 'done'
        print x
        print open(filen).read()
    def fail(x):
        print 'fail'
        print x.getErrorMessage()

    url = 'https://downloads.datahaven.net/info.txt'
    fn = '123'
    d = downloadSSL1(url, fn, None, 'dhn.cer')
    d.addCallback(done, fn)
    d.addErrback(fail)

def test2():
    def done(x):
        #print 'done!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        print x
    def fail(x):
        print 'fail'
        print x
        print x.getErrorMessage()
    url = 'http://identity.datahaven.net/veselin.xml'
    d = getPageTwisted(url)
    d.addCallback(done)
    d.addErrback(fail)

def test3():
    d = detect_proxy_settings()
    print d

def test4():
    def done(x, filen):
        print 'done'
        print x
        print open(filen).read()
    def fail(x):
        print 'fail'
        print x.getErrorMessage()

#    import settings
#    url = settings.UpdateLocationURL() + settings.CurrentVersionDigestsFilename()
    url = 'http://identity.datahaven.net/downloads/version.txt'
    fn = '123'
    d = downloadHTTP(url, fn)
    d.addCallback(done, fn)
    d.addErrback(fail)

def test5():
    SendEmail('to.datahaven@gmail.com',
              'dhnemail1@mail.offshore.ai',
              'smtp.gmail.com',
              587,
              'datahaven.net.mail@gmail.com',
              'datahaven.net.mail',
              'subj',
              'some body \n\n body',
              ['__init__.pyc'],)



if __name__ == '__main__':
    #init()
    test5()
    #reactor.run()


