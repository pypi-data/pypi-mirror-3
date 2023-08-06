#!/usr/bin/python
#weblog.py

import sys
import urllib
import base64
from time import strftime

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in weblog.py')

from twisted.web import server, resource

myweblistener = None
default_level = 6
default_reload_timeout = 600
default_lines = 999999
maxlines = default_lines
loglist = ['', 'Web Log',]

header_html = '''<html><head>
<meta http-equiv="refresh" content="%(reload)s">
<title>dhn-web-log</title></head>
<body bgcolor="#FFFFFF" text="#000000" link="#0000FF" vlink="#0000FF">
<form action="" method="get">
<input size="4" name="level" value="%(level)s" />
<input size="4" name="reload" value="%(reload)s" />
<input size="10" name="lines" value="%(lines)s" />
<input type="submit" value="update" />
</form>
<a href="?reload=0.2&level=%(level)s&lines=%(lines)s">[1/5 sec.]</a>|
<a href="?reload=0.5&level=%(level)s&lines=%(lines)s">[1/2 sec.]</a>|
<a href="?reload=1&level=%(level)s&lines=%(lines)s">[1 sec.]</a>|
<a href="?reload=5&level=%(level)s&lines=%(lines)s">[5 sec.]</a>|
<a href="?reload=10&level=%(level)s&lines=%(lines)s">[10 sec.]</a>|
<a href="?reload=30&level=%(level)s&lines=%(lines)s">[30 sec.]</a>|
<a href="?reload=600&level=%(level)s&lines=%(lines)s">[600 sec.]</a>
<br>
<a href="?level=2&reload=%(reload)s&lines=%(lines)s">[debug2]</a>|
<a href="?level=4&reload=%(reload)s&lines=%(lines)s">[debug4]</a>|
<a href="?level=6&reload=%(reload)s&lines=%(lines)s">[debug6]</a>|
<a href="?level=8&reload=%(reload)s&lines=%(lines)s">[debug8]</a>|
<a href="?level=10&reload=%(reload)s&lines=%(lines)s">[debug10]</a>|
<a href="?level=12&reload=%(reload)s&lines=%(lines)s">[debug12]</a>|
<a href="?level=18&reload=%(reload)s&lines=%(lines)s">[debug18]</a>
<a href="?level=99&reload=%(reload)s&lines=%(lines)s">[debug99]</a>
<pre>
'''


def log(level, s):
    global loglist
    global maxlines
    global myweblistener
    if not myweblistener:
        return
    while len(loglist) > maxlines:
        loglist.pop(0)
    loglist.append([level, strftime('%H:%M:%S'), s])

class LogPage(resource.Resource):
    def __init__(self,parent):
        self.parent = parent
        resource.Resource.__init__(self)

    def render(self, request):
        global loglist
        global maxlines
        DlevelS = request.args.get('level', [''])[0]
        try:
            DlevelV = int(DlevelS)
        except:
            DlevelV = default_level

        reloadS = request.args.get('reload', [''])[0]
        try:
            reloadV = float(reloadS)
        except:
            reloadV = default_reload_timeout

        linesS = request.args.get('lines', [''])[0]
        try:
            maxlines = int(linesS)
        except:
            maxlines = default_lines

        d = {'level': str(DlevelV), 'reload': str(reloadV), 'lines': str(maxlines)}
        out = header_html % d
        for i in range(len(loglist)-1, 0, -1):
            t = loglist[i]
            level = t[0]
            timestr = t[1]
            s = t[2]
            if level > DlevelV:
                continue
            color = ''
##            if level == 1:
##                color = ''
##            if level > 6:
##                color = 'darkgray'
##            if level > 12:
##                color = 'gray'
            if s.find('BOGUS') > 0:
                color = 'purple'
            if s.find('WARNING') > 0:
                color = 'blue'
            if s.find('ERROR') > 0:
                color = 'red'
            if s.find('NETERROR') > 0:
                color = 'lightgray'
            if s.find('Exception:') > 0:
                color = 'red'
            a = '%s\n'
            if color != '':
                a = ('<font color=white style="BACKGROUND-COLOR:%s">' % color) + '%s</font>\n'

            try:
                out += a % str(s)
            except:
                try:
                    out += a % str(urllib.quote(s))
                except:
                    out += a % str(base64.encodestring(s))

##            try:
##                out += a % ('['+timestr+']'+string.rjust('', level)+s.encode('latin_1', 'ignore'))+'\n'
##            except:
##                try:
##                    out += a % ('['+timestr+']'+string.rjust('', level)+str(s))+'\n'
##                except:
##                    out += a % ('['+timestr+']'+string.rjust('', level)+str('encoding error'))+'\n'

#            try:
##                out += a % (''+timestr+''+' '*level+s.encode('latin_1', 'ignore'))+'\n'
#                out += a % (''+timestr+''+' '*level+str(s))+'\n'
#            except:
#                try:
#                    out += a % (''+timestr+''+' '*level+repr(s))+'\n'
#                except:
#                    out += a % (''+timestr+''+' '*level+str('encoding error'))+'\n'



        return out+'</pre></body></html>'

class RootResource(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        logpage = LogPage(self)
        self.putChild('', logpage)

def init(port = 9999):
    global myweblistener
    if myweblistener:
        return
    root = RootResource()
    site = server.Site(root)
    try:
        myweblistener = reactor.listenTCP(port, site)
    except:
        pass

def shutdown():
    global myweblistener
    if myweblistener:
        myweblistener.stopListening()
        del myweblistener
        myweblistener = None

#------------------------------------------------------------------------------

if __name__ == "__main__":
    init(int(sys.argv[1]))
    reactor.run()








