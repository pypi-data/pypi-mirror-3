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
#2. edit settings.py
#   you can add access functions like getECC() or getCentralNumSuppliers()
#3. edit guisettings.py if you wish user to be able to edit this item:
#   add key pair to dictionary CSettings.items
#   you can define your own Widget (for example: XMLTreeEMailSettingsNode or XMLTreeQ2QSettingsNode)
#   if you are using ComboBox Widget (xmltreenodes.XMLTreeComboboxNode)
#   you need to add his definition after line comment "#define combo boxes"
#4. finally, you need to read this value using lib.settings and do something...


import os
import locale

from xml.dom import minidom
from xml.dom import Node
from xml.dom.minidom import getDOMImplementation

#-------------------------------------------------------------------------------

InfosDict = {
    'general':                      "General options.",
    'general-backups':              'How many backups of each directory to keep. ( 0 = unlimited )',
    'general-autorun':              "Starting the application during system startup.",
    'general-display-mode':         "Specifies how you want the window to display when you start the software.",
    'general-desktop-shortcut':     "Place shortcut on the Desktop?",
    'general-start-menu-shortcut':  "Add shortcut to the Start Menu?",
    'updates':                      "Software updates options.",
    'updates-mode':                 "You can choose one of the install modes. Software must be restarted after installation of the new version.",
    'updates-shedule':              "You can setup updating schedule here.",
    'central-settings':             "Central Server Settings. Here you can manage your settings stored on the DataHaven.NET Central Server (c).",
    'desired-suppliers':            "Number of remote suppliers which keeps your backups.",
    'needed-megabytes':             "How many megabytes you need to store your files?",
    'shared-megabytes':             "How many megabytes you ready to donate to other users?",
    'folder-backups':               "Place for your local backups files.",
    'folder-restore':               'Place where your restored files should be placed.',
    'folder-customers':             'Place for donated space, other users will keep their files here.',
    'emergency':                    "We can contact you if your account balance is running low, if your backups are not working, or if your machine appears to not be working.",
    'emergency-first':              "What is your preferred method for us to contact you if there are problems?",
    'emergency-second':             "What is the second best method to contact you?",
    'emergency-email':              "What email address should we contact you at? Email contact is free.",
    'emergency-phone':              "If you would like to be contacted by phone, what number can we reach you at? ($1 per call for our time and costs)",
    'emergency-fax':                "If you would like to be contacted by fax, what number can we reach you at? ($0.50 per fax for our time and costs)",
    'emergency-text':               "Other method we should contact you by? Cost will be based on our costs.",
    'transport':                    'You can use different protocols to transfer packets, called "transports". Here you can customize your transport settings.',
    'transport-tcp':                "transport_tcp uses the standard TCP protocol to transfer packets.",
    'transport-tcp-port':           "Enter the port number for the transport_tcp, which will be used to connect with you.",
    'transport-tcp-enable':         "transport_tcp uses the standard TCP protocol to transfer packets.<br>Do you want to use transport_tcp?",
    'transport-ssh':                "transport_ssh uses the technique of public and private key for the protection of transmitted packets.",
    'transport-ssh-port':           "Enter the port number for the transport_ssh, which will be used to connect with you.",
    'transport-ssh-enable':         "Enable transport_ssh?",
    'transport-cspace':             'CSpace provides a platform for secure, decentralized, user-to-user communication over the internet.<br>Go to <a href="http://cspace.in" target=_blank>http://cspace.in</a> for more details.',
    'transport-cspace-enable':      'CSpace provides a platform for secure, decentralized, user-to-user communication over the internet.<br>Go to <a href="http://cspace.in" target=_blank>http://cspace.in</a> for more details.<br>Do you want to use transport_cspace?',
    'transport-cspace-key-id':      'CSpace provides a platform for secure, decentralized, user-to-user communication over the internet.<br>Go to <a href="http://cspace.in" target=_blank>http://cspace.in</a> for more details.<br>Enter your CSpace user id here.',
    'upnp-enabled':                 'Do you want to use UPnP to configure port forwarding?',
    'gui':                          "Here You can setup user interfce options.",
    'gui-font-size':                'Specify the font size. Possible values: 6 - 56',
    'debug-level':                  "Higher values will produce more log messages.",
    'stream-enable':                "Go to http://127.0.0.1:[logs port number] to browse the program log.",
    }

#------------------------------------------------------------------------------ 

class UserConfig:
    default_xml_src = ur"""<settings>
 <general label="general">
  <general-backups label="backup count">
   2
  </general-backups>
  <general-local-backups-enable label="local backups">
   True
  </general-local-backups-enable>
  <general-wait-suppliers-enable label="wait suppliers">
   True 
  </general-wait-suppliers-enable>
  <general-autorun label="autorun">
   True
  </general-autorun>
  <general-display-mode label="display mode">
   iconify window
  </general-display-mode>
  <general-desktop-shortcut label="desktop shortcut">
   True
  </general-desktop-shortcut>
  <general-start-menu-shortcut label="start menu shortcut">
   True
  </general-start-menu-shortcut>
 </general>
 <updates label="updates">
  <updates-mode label="mode">
   install automatically
  </updates-mode>
  <updates-shedule label="schedule">
4
12:00:00
6

  </updates-shedule>
 </updates>
 <central-settings label="central server">
  <desired-suppliers label="number of suppliers">
   4
  </desired-suppliers>
  <needed-megabytes label="needed space">
   4GB
  </needed-megabytes>
  <shared-megabytes label="donated space">
   8GB
  </shared-megabytes>
 </central-settings>
 <folder label="folders">
  <folder-customers label="donated space">
  
  </folder-customers>
  <folder-backups label="local backups">
  
  </folder-backups>
  <folder-restore label="restored files">
  
  </folder-restore>
  <folder-messages label="messages">
  
  </folder-messages>
  <folder-receipts label="receipts">
  
  </folder-receipts>
  <folder-temp label="temporary files">
  
  </folder-temp>
 </folder>
 <emergency label="emergency">
  <emergency-first label="primary">
   email
  </emergency-first>
  <emergency-second label="secondary">
   phone
  </emergency-second>
  <emergency-email label="email">

  </emergency-email>
  <emergency-phone label="phone">

  </emergency-phone>
  <emergency-fax label="fax">

  </emergency-fax>
  <emergency-text label="other">

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
 <transport label="transports">
  <transport-tcp label="transport_tcp">
   <transport-tcp-port label="TCP port">
    7771
   </transport-tcp-port>
   <transport-tcp-enable label="transport_tcp enable">
    True
   </transport-tcp-enable>
  </transport-tcp>
  <transport-ssh label="ssh">
   <transport-ssh-port label="SSH port">
    5022
   </transport-ssh-port>
   <transport-ssh-enable label="transport_ssh enable">
    False
   </transport-ssh-enable>
  </transport-ssh>
  <transport-q2q label="q2q">
   <transport-q2q-host label="q2q server address">

   </transport-q2q-host>
   <transport-q2q-username label="q2q username">

   </transport-q2q-username>
   <transport-q2q-password label="q2q password">

   </transport-q2q-password>
   <transport-q2q-enable label="q2q enabled">
    True
   </transport-q2q-enable>
  </transport-q2q>
  <transport-email label="email">
   <transport-email-address label="address">

   </transport-email-address>
   <transport-email-pop-host label="pop server hostname">

   </transport-email-pop-host>
   <transport-email-pop-port label="pop server port">

   </transport-email-pop-port>
   <transport-email-pop-username label="pop username">

   </transport-email-pop-username>
   <transport-email-pop-password label="pop password">

   </transport-email-pop-password>
   <transport-email-pop-ssl label="pop security">
    False
   </transport-email-pop-ssl>
   <transport-email-smtp-host label="smtp server hostname">

   </transport-email-smtp-host>
   <transport-email-smtp-port label="smtp server port">

   </transport-email-smtp-port>
   <transport-email-smtp-username label="smtp username">

   </transport-email-smtp-username>
   <transport-email-smtp-password label="smtp password">

   </transport-email-smtp-password>
   <transport-email-smtp-need-login label="smtp authorization">
    False
   </transport-email-smtp-need-login>
   <transport-email-smtp-ssl label="smtp security">
    False
   </transport-email-smtp-ssl>
   <transport-email-enable label="enabled">
    False
   </transport-email-enable>
  </transport-email>
  <transport-http label="http">
   <transport-http-server-port label="server port">
    9786
   </transport-http-server-port>
   <transport-http-ping-timeout label="ping timeout">
    5
   </transport-http-ping-timeout>
   <transport-http-enable label="enabled">
    True
   </transport-http-enable>
   <transport-http-server-enable label="server enabled">
    True
   </transport-http-server-enable>
  </transport-http>
  <transport-skype label="skype">
   <transport-skype-enable label="enabled">
    False
   </transport-skype-enable>
  </transport-skype>
  <transport-cspace label="transport_cspace">
   <transport-cspace-enable label="transport_cspace enable">
    True
   </transport-cspace-enable>
   <transport-cspace-key-id label="CSpace user id">
   
   </transport-cspace-key-id>
  </transport-cspace>
 </transport>
 <gui label="user interface">
  <gui-font-size label="font size">
   12
  </gui-font-size>
 </gui>
 <logs label="logs">
  <debug-level label="debug level">
   4
  </debug-level>
  <stream-enable label="enable logs">
   False
  </stream-enable>
  <stream-port label="logs port number">
   9999
  </stream-port>
  <traffic-enable label="enable packets traffic">
   False
  </traffic-enable>
  <traffic-port label="traffic port number">
   9997
  </traffic-port>
 </logs>
 <other label="other">
  <BandwidthLimit>
  
  </BandwidthLimit>
  <upnp-enabled label="UPnP enable">
   True
  </upnp-enabled>
  <upnp-at-startup label="check UPnP at startup">
   False
  </upnp-at-startup>
 </other>
</settings>"""

#  <memdebug-enable label="memdebug enable">
#   False
#  </memdebug-enable>
#  <memdebug-port label="memdebug port number">
#   9995
#  </memdebug-port>

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
        # else:
            # set_info(node, self.infos[path])

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
            # set_info(leafnode, info)
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
        self.xmlsrc = doc.toprettyxml("  ", "\n") # doubles if put spaces here

    def UnserializeObject(self, xml_object):
        self.data.clear()
        self._load(self.data, xml_object)
        self.xmlsrc = xml_object.toprettyxml("  ", "\n") # doubles if put spaces here

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

    def print_all(self):
        for path in self.default_order:
            if path.strip() == '':
                continue
            value = self.data.get(path, '')
            label = self.labels.get(path, '')
            print path.ljust(40),
            print label.ljust(20),
            print value

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

#def get_info(xmlnode):
#    label = xmlnode.attributes.get('info', None)
#    if label is not None:
#        v = label.value
#        v = v.replace('\\n ', '\n')
#        v = v.replace('\\n', '\n')
#        return v.encode(locale.getpreferredencoding())
#    return None

#def set_info(xmlnode, info):
#    if info != '':
#        xmlnode.setAttribute('info', info.decode(locale.getpreferredencoding()))

def get_info(xmlnode):
    global InfosDict
    return InfosDict.get(xmlnode.tagName, '')

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



