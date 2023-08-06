#!/usr/bin/python
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#userconfig.py
#
#
#to add a single item in user configuration:
#1. edit userconfig.py: UserConfig.default_xml_src
#   do not forget to add tag "label" and "info".
#   TODO: Vince need to check all spelling inside those tags.
#2. edit settings.py
#   you can add access functions like getECC() or getCentralNumSuppliers()
#3. edit guisettings.py if you wish user to be able to edit this item:
#   add key pair to dictionary CSettings.items
#   you can define your own Widget (for example: XMLTreeEMailSettingsNode or XMLTreeQ2QSettingsNode)
#   if you are using ComboBox Widget (xmltreenodes.XMLTreeComboboxNode)
#   you need to add his definition after line comment "#define combo boxes"
#4. finally, you need to read this value using lib.settings and do something...


import os
import codecs
import locale

from xml.dom import minidom, Node
from xml.dom.minidom import getDOMImplementation

#-------------------------------------------------------------------------------

def get_child(father,childname):
    for son in father.childNodes:
        if son.nodeName == childname:
            return son
    return None

def get_text(xmlnode):
    rc = u''
    for node in xmlnode.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data.strip()
    return rc.encode(locale.getpreferredencoding())

def set_text(xmlnode, txt):
    try:
        text = txt.decode(locale.getpreferredencoding())
    except:
        text = ''
    for node in xmlnode.childNodes:
        if node.nodeType == node.TEXT_NODE:
            node.data = u''
    j = 0
    while j < len(xmlnode.childNodes):
        node = xmlnode.childNodes[j]
        if node.nodeType == node.TEXT_NODE:
            node.data = text
            return
        j += 1
    node = xmlnode.ownerDocument.createTextNode(text)#.decode('latin_1'))
    xmlnode.appendChild(node)

def get_label(xmlnode):
    label = xmlnode.attributes.get('label', None)
    if label is not None:
        return label.value.encode(locale.getpreferredencoding())
    return None

def set_label(xmlnode, label):
    if label != '':
        xmlnode.setAttribute('label', label.decode(locale.getpreferredencoding()))

def get_info(xmlnode):
    label = xmlnode.attributes.get('info', None)
    if label is not None:
        v = label.value
        v = v.replace('\\n ', '\n')
        v = v.replace('\\n', '\n')
        return v.encode(locale.getpreferredencoding())
    return None

def set_info(xmlnode, info):
    if info != '':
        xmlnode.setAttribute('info', info.decode(locale.getpreferredencoding()))

#-------------------------------------------------------------------------------

class UserConfig:
    default_xml_src = ur"""<settings>
 <general label="general" info="General options.">
  <general-backups label="backup count" info="How many backups of each directory to keep. 0 means unlimited.">
   2
  </general-backups>
  <general-autorun label="autorun" info="Starting the application during system startup">
   True
  </general-autorun>
  <general-display-mode label="display mode" info="Specifies how you want the window to display when you start the software.">
   iconify window
  </general-display-mode>
  <general-desktop-shortcut label="desktop shortcut" info="Place shortcut on the Desktop">
   True
  </general-desktop-shortcut>
  <general-start-menu-shortcut label="start menu shortcut" info="Add shortcut to the Start Menu">
   True
  </general-start-menu-shortcut>
 </general>
 <updates label="updates" info="Software updates options.">
  <updates-mode label="mode" info="You can choose one of the install modes. Software must be restarted after installation of the new version.">
   install automatically
  </updates-mode>
  <updates-shedule label="shedule" info="You can setup updating shedule here.">
4
12:00:00
6

  </updates-shedule>
 </updates>
 <central-settings label="central server" info="Central Server Settings. Here you can manage your settings stored on the DataHaven.NET Central Server (c).">
  <desired-suppliers label="number of suppliers" info="Number of suppliers:">
   2
  </desired-suppliers>
  <needed-megabytes label="needed space" info="Needed space:">
   100Mb
  </needed-megabytes>
  <shared-megabytes label="donated space" info="Donated space:">
   2Gb
  </shared-megabytes>
 </central-settings>
 <folder label="folders">
  <folder-customers label="Directory for donated space">
  
  </folder-customers>
  <folder-restore label="restore">
  
  </folder-restore>
  <folder-messages label="messages">
  
  </folder-messages>
  <folder-receipts label="receipts">
  
  </folder-receipts>
  <folder-temp label="temp">
  
  </folder-temp>
 </folder>
 <emergency label="emergency" info="We can contact you if your account balance is running low, if your backups are not working, or if your machine appears to not be working.">
  <emergency-first label="primary" info="What is your preferred method for us to contact you if there are problems?">
   email
  </emergency-first>
  <emergency-second label="secondary" info="What is the second best method to contact you?">
   phone
  </emergency-second>
  <emergency-email label="email" info="What email address should we contact you at? Email contact is free.">

  </emergency-email>
  <emergency-phone label="phone" info="If you would like to be contacted by phone, what number can we reach you at? ($1 per call for our time and costs)">

  </emergency-phone>
  <emergency-fax label="fax" info="If you would like to be contacted by fax, what number can we reach you at? ($0.50 per fax for our time and costs)">

  </emergency-fax>
  <emergency-text label="other" info="Other method we should contact you by? Cost will be based on our costs.">

  </emergency-text>
 </emergency>
 <network>
  <network-proxy>
   <network-proxy-enable>
    False
   </network-proxy-enable>
   <network-proxy-host>

   </network-proxy-host>
   <network-proxy-port>

   </network-proxy-port>
   <network-proxy-username>

   </network-proxy-username>
   <network-proxy-password>

   </network-proxy-password>
   <network-proxy-ssl>
    False
   </network-proxy-ssl>
  </network-proxy>
 </network>
 <transport label="transports" info='You can use different protocols to transfer packets, called "transports". Here you can customize your transport settings. On the page "Identity", in the "contacts", you can set the priority of protocols.'>
  <transport-tcp label="tcp" info="transport_tcp uses the standard TCP protocol to transfer packets.">
   <transport-tcp-port label="server port" info="Enter the port number for the transport_tcp, which will be used to connect with you.">
    7771
   </transport-tcp-port>
   <transport-tcp-enable label="enabled" info="Enable transport_tcp?.">
    True
   </transport-tcp-enable>
  </transport-tcp>
  <transport-ssh label="ssh" info="transport_ssh uses the technique of public and private key for the protection of transmitted packets.">
   <transport-ssh-port label="server port" info="Enter the port number for the transport_ssh, which will be used to connect with you.">
    5022
   </transport-ssh-port>
   <transport-ssh-enable label="enabled" info="Enable transport_ssh?.">
    False
   </transport-ssh-enable>
  </transport-ssh>
  <transport-q2q label="q2q" info='Q2Q is a protocol designed to allow secure TCP networking behind heavily networked masqueraded and firewalled computers. In order to use transport_q2q, you must be registered on any of the Q2Q servers. Use the button "Register Now" for quick setup on the server by default: q2q.datahaven.net'>
   <transport-q2q-host label="server address" info="transport_q2q server address.">

   </transport-q2q-host>
   <transport-q2q-username label="username" info="Username on the Q2Q server.">

   </transport-q2q-username>
   <transport-q2q-password label="password" info="Password on the Q2Q server.">

   </transport-q2q-password>
   <transport-q2q-enable label="enabled" info="Enable transport_q2q?.">
    True
   </transport-q2q-enable>
  </transport-q2q>
  <transport-email label="email" info='Here you can manage your e-mail settings. You need to set it up if you want to use transport_email. Use it if it is impossible to connect via other transports. Click "Start Wizard" for quick configuration your mailbox.'>
   <transport-email-address label="address" info="Your e-mail address.">

   </transport-email-address>
   <transport-email-pop-host label="pop server hostname" info="Host name of POP server for incomming mail. For example: 'pop.gmail.com'.">

   </transport-email-pop-host>
   <transport-email-pop-port label="pop server port" info="Port number to connect to POP server.">

   </transport-email-pop-port>
   <transport-email-pop-username label="pop username" info="Username on POP server.">

   </transport-email-pop-username>
   <transport-email-pop-password label="pop password" info="Password on POP server.">

   </transport-email-pop-password>
   <transport-email-pop-ssl label="pop security" info='Select "Yes" if your POP server requires a secure connection.'>
    False
   </transport-email-pop-ssl>
   <transport-email-smtp-host label="smtp server hostname" info="Host name of SMTP server for outgoing mail. For example: 'smtp.gmail.com'.">

   </transport-email-smtp-host>
   <transport-email-smtp-port label="smtp server port" info="Port number to connect to SMTP server.">

   </transport-email-smtp-port>
   <transport-email-smtp-username label="smtp username" info="Your username on SMTP server.">

   </transport-email-smtp-username>
   <transport-email-smtp-password label="smtp password" info="Your password on SMTP server.">

   </transport-email-smtp-password>
   <transport-email-smtp-need-login label="smtp authorization" info='Select "Yes" if your SMTP server requires authentication.'>
    False
   </transport-email-smtp-need-login>
   <transport-email-smtp-ssl label="smtp security" info="Do you think your SMTP server requires a secure connection?">
    False
   </transport-email-smtp-ssl>
   <transport-email-enable label="enabled" info="Enable transport_email?.">
    False
   </transport-email-enable>
  </transport-email>
  <transport-http label="http" info='Transport_http allows you to maintain a connection with others in the case when your own internet connection is limited. On the remote computer of another user will be running the server to which you can connect the same way as the usual site on the Internet. Periodically, will be connected to the server and check whether there are packages for you. This is a pretty slow way to transfer data but if your internet provider forbids incoming connections it helps you be in touch.'>
   <transport-http-server-port label="server port" info='Specify a port for your HTTP server. Other users will try to connect with you on this port to receive packets from you.'>
    9786
   </transport-http-server-port>
   <transport-http-ping-timeout label="ping timeout" info="How often does the transport_http will connect to other users to receive packets addressed to you? Specify the interval in seconds.">
    5
   </transport-http-ping-timeout>
   <transport-http-enable label="enabled" info='Enable transport_http?. If you agree your computer will periodically connect to other computers to check whether there are any packets for you.'>
    True
   </transport-http-enable>
   <transport-http-server-enable label="server enabled" info="Would you like to run http server on your machine? Then, other users with limited Internet connection will be able to exchange packets with you.">
    True
   </transport-http-server-enable>
  </transport-http>
  <transport-skype label="skype" info='You can use the Skype to exchange packets. The settings Skype need to allow access to the process "dhnmain".'>
   <transport-skype-enable label="enabled" info="Enable transport_skype?.">
    False
   </transport-skype-enable>
  </transport-skype>
  <transport-cspace label="cspace" info='CSpace provides a platform for secure, decentralized, user-to-user communication over the internet.'>
   <transport-cspace-enable label="enabled">
    True
   </transport-cspace-enable>
   <transport-cspace-key-id label="key-id">
   
   </transport-cspace-key-id>
  </transport-cspace>
 </transport>
 <gui label="user interface" info="Here You can setup user interfce options.">
  <gui-font-size label="font size" info='Specify the font size. Possible values: 6 - 56'>
   12
  </gui-font-size>
 </gui>
 <logs label="Logs">
  <debug-level label="Debug level" info="Higher values will produce more log messages.">
   4
  </debug-level>
  <stream-enable label="enable logs" info="Go to http://127.0.0.1:[logs port number] to watch log messages.">
   False
  </stream-enable>
  <stream-port label="logs port number">
   9999
  </stream-port>
  <traffic-enable label="enable packets traffic" info="Go to http://127.0.0.1:[traffic port number] to see packets traffic.">
   False
  </traffic-enable>
  <traffic-port label="traffic port number">
   9997
  </traffic-port>
 </logs>
 <other label="DEBUG" info="OTHER TOOLS (DEBUG)">
  <DoBackupMonitor>
  Y
  </DoBackupMonitor>
  <ShowBarcode>
  N
  </ShowBarcode>
  <FireInactiveSupplierIntervalHours>
  30
  </FireInactiveSupplierIntervalHours>
  <Dozer>
  0
  </Dozer>
  <BandwidthLimit>
  
  </BandwidthLimit>
  <upnp-enabled>
   True
  </upnp-enabled>
  <upnp-at-startup>
   False
  </upnp-at-startup>
  <eccmapCurrentName>
  
  </eccmapCurrentName>
  <emailSendTimeout>
  
  </emailSendTimeout>
  <emailReceiveTimeout>
  
  </emailReceiveTimeout>
 </other>
</settings>"""

    xmlsrc = ''
    data = {}
    labels = {}
    infos = {}
    default_data = {}
    default_order = []

    def __init__(self, filename):
        self.filename = filename
        if os.path.isfile(self.filename):
            self._read()
        else:
            self._create()

        doc1 = self._parse(self.default_xml_src)
        self._load(
            self.default_data,
            doc1.documentElement,
            order=self.default_order, )

        doc2 = self._parse(self.xmlsrc)
        self._load(
            self.data,
            doc2.documentElement)

        self._validate(True)


    def _parse(self, src):
        try:
            s = src.encode('utf-8')
            return minidom.parseString(s)
        except:
            return minidom.parseString(self.default_xml_src.encode('utf-8'))

    def _read(self):
        fin = open(self.filename, 'r')
        src = fin.read()
        fin.close()
##        print '_read before', type(src)
        self.xmlsrc = src.decode(locale.getpreferredencoding())
##        print '_read after', type(self.xmlsrc)

    def _write(self):
##        print '_write before', type(self.xmlsrc)
        src = self.xmlsrc.encode(locale.getpreferredencoding())
##        print '_write after', type(src)
        try:
            fout = open(self.filename, 'w')
            fout.write(src)
            fout.flush()
            os.fsync(fout.fileno())
            fout.close()
        except:
            pass

    def _create(self):
        self.xmlsrc = self.default_xml_src
        self._write()

    # check existing user-config and our template, add nodes if they are missing
    def _validate(self, remove=False):
        changed = False
        for key in self.default_data.keys():
            if not self.data.has_key(key):
                self.data[key] = self.default_data[key]
                changed = True
        if remove:
            for key in self.data.keys():
                if not self.default_data.has_key(key):
                    del self.data[key]
                    changed = True
        if changed:
            self.xmlsrc = self._make_xml()[0]
            self._write()

    def _load(self, data, node, path='', order=None):
        d = get_text(node)
        if path != '':
            data[path] = d
        if order is not None:
            order.append(path)

        if not self.labels.has_key(path):
            l = get_label(node)
            if l is not None:
                self.labels[path] = l
            else:
                self.labels[path] = node.tagName
        else:
            set_label(node, self.labels[path])

        if not self.infos.has_key(path):
            i = get_info(node)
            if i is not None:
                self.infos[path] = i
        else:
            set_info(node, self.infos[path])

        for subnode in node.childNodes:
            if subnode.nodeType == Node.ELEMENT_NODE:
                name = str(subnode.tagName)
                if path != '':
                    name = path+'.'+name
                self._load(data, subnode, name, order)

    def _from_data(self, parent, doc):
        for path in self.default_order:
            if path.strip() == '':
                continue
            value = self.data.get(path, '')
            label = self.labels.get(path, '')
            info = self.infos.get(path, '')
            leafs = path.split('.')
            prevleaf = parent
            leafnode = None
            for leaf in leafs:
                leafnode = get_child(prevleaf, leaf)
                if leafnode is None:
                    leafnode = doc.createElement(leaf)
                    prevleaf.appendChild(leafnode)
                prevleaf = leafnode
            set_label(leafnode, label)
            set_info(leafnode, info)
            set_text(leafnode, value)

    def _make_xml(self):
        impl = getDOMImplementation()
        doc = impl.createDocument(None, 'settings', None)
        rootnode = doc.documentElement
        self._from_data(rootnode, doc)
        xmlsrc = doc.toprettyxml("  ","\n")
        return xmlsrc, rootnode

    def update(self, node=None):
        if node is None:
            self.xmlsrc = self.Serialize()
        else:
            self.UnserializeObject(node)
        self._write()

    def Serialize(self):
        doc1 = self._parse(self.xmlsrc)
        self.default_order = []
        self._load(
            self.default_data,
            doc1.documentElement,
            order=self.default_order, )
        return self._make_xml()[0]

    def SerializeObject(self):
        doc1 = self._parse(self.xmlsrc)
        self.default_order = []
        self._load(
            self.default_data,
            doc1.documentElement,
            order=self.default_order, )
        return self._make_xml()[1]

    def Unserialize(self, src):
        doc = self._parse(src)
        node = doc.documentElement
        self.data.clear()
        self._load(self.data, node)
        self.xmlsrc = doc.toprettyxml("  ","\n") # doubles if put spaces here

    def UnserializeObject(self, xml_object):
        self.data.clear()
        self._load(self.data, xml_object)
        self.xmlsrc = xml_object.toprettyxml("  ","\n") # doubles if put spaces here

    # use this when user needs to "reset to factory defaults"
    def reset(self):
        self.xmlsrc = self.default_xml_src

    def get(self, key, request=None):
        if not request:
            return self.data.get(key, None)
        elif request=='all':
            return (self.data.get(key, None),
                    self.labels.get(key, None),
                    self.infos.get(key, None),
                    self.default_data.get(key, None),)
        elif request=='data':
            return self.data.get(key, None)
        elif request=='label':
            return self.labels.get(key, None)
        elif request=='info':
            return self.infos.get(key, None)
        elif request=='default':
            return self.default_data.get(key, None)
        return self.data.has_key(key)

    def has(self, key):
        return self.data.has_key(key)

    def set(self, key, value, request=None):
        if request=='data':
            self.data[key] = value
        elif request=='label':
            self.labels[key] = value
        elif request=='info':
            self.infos[key] = value
        else:
            self.data[key] = value

    def get_childs(self, key, request=None):
        d = {}
        if request=='data':
            for k,v in self.data.items():
                if k.startswith(str(key)+'.'): d[k] = v
        elif request=='label':
            for k,v in self.labels.items():
                if k.startswith(str(key)+'.'): d[k] = v
        elif request=='info':
            for k,v in self.labels.items():
                if k.startswith(str(key)+'.'): d[k] = v
        elif request=='default':
            for k,v in self.default_data.items():
                if k.startswith(str(key)+'.'): d[k] = v
        else:
            for k,v in self.data.items():
                if k.startswith(str(key)+'.'): d[k] = v
        return d

    def set_childs(self, key, childs_dict):
        if not self.data.has_key(key):
            return
        for k,v in childs_dict.items():
            _key = k
            if not k.startswith(key+'.'):
                _key = key+'.'+k
            self.data[_key] = v

    def make_child_name(self, key, namebase):
        i = 0
        while True:
            name = unicode(key+'.'+namebase+str(i))
            if not self.data.has_key(name):
                return name
            i += 1

#-------------------------------------------------------------------------------

def main():
    import settings
    uc = UserConfig(settings.UserConfigFilename())
    uc.update()
    import pprint
    pprint.pprint(uc.data)

##    for path in uc.default_order:
##        if path.strip() == '':
##            continue
##        leafs = path.split('.')
##        print path, len(leafs)


if __name__ == "__main__":
    main()



