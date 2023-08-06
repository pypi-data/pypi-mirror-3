#!/usr/bin/python
#dhnicon.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#
#

import os
import sys

USE_TRAY_ICON = True
LABEL = 'DataHaven.NET'
    
_IconObject = None
_ControlFunc = None

#------------------------------------------------------------------------------ 

def init(icon_filename):
    global _IconObject
    global USE_TRAY_ICON
    if not USE_TRAY_ICON:
        return

    import wx
    
    from twisted.internet import reactor


    def create_menu_item(menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item
    
    
    class MyTaskBarIcon(wx.TaskBarIcon):
        def __init__(self):
            #self.parent = parent
            super(MyTaskBarIcon, self).__init__()
            icon = wx.IconFromBitmap(wx.Bitmap(icon_filename))
            self.SetIcon(icon, LABEL)
            self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
            
        def CreatePopupMenu(self):
            menu = wx.Menu()
            create_menu_item(menu, 'show', self.on_show)
            create_menu_item(menu, 'hide', self.on_hide)
            menu.AppendSeparator()
            create_menu_item(menu, 'restart', self.on_restart)
            create_menu_item(menu, 'shutdown', self.on_exit)
            self.menu = menu
            return menu
        
        def on_left_down(self, event):
            control('show')
            
        def on_show(self, event):
            control('show')
            
        def on_hide(self, event):
            control('hide')
            
        def on_restart(self, event):
            control('restart')
            
        def on_exit(self, event):
            control('exit')
    
    
    class MyApp(wx.App):
        def __init__(self):
            wx.App.__init__(self, False)
            
        def OnInit(self):
            self.trayicon = MyTaskBarIcon()
            return True
        
        def OnExit(self):
            self.trayicon.Destroy() 
    
        
    _IconObject = MyApp() 

    reactor.registerWxApp(_IconObject)


def control(cmd):
    global _ControlFunc
    if _ControlFunc is not None:
        _ControlFunc(cmd)


def SetControlFunc(f):
    global _ControlFunc
    _ControlFunc = f

#------------------------------------------------------------------------------ 

if __name__ == "__main__":
    def test_control(cmd):
        print cmd
        if cmd == 'exit':
            reactor.stop()
        
    from twisted.internet import wxreactor
    wxreactor.install()
    from twisted.internet import reactor
    init(sys.argv[1])
    SetControlFunc(test_control)
    reactor.run()
    
    
    
