"""
.. module:: CGuiController
   :platform: Unix
   :synopsis: The main controller for the cernent gui. 

.. moduleauthor:: Brian Kraus


"""

import os, platform
#from gui.cGui.main.ScanLaunchFrame import ScanLaunchFrame
from gui.cGui.main.Launchpad import Launchpad
from gui.cGui.widgets.CFrame import CFrame
import Tkinter
from tkFileDialog import askopenfilename
from ScanEvent.ScanEvent import getPathToSaves
from gui.cGui.main.ScanEventEditor import ScanEventEditor
from ScanEvent.ScanEvent import ScanEvent
from ScanEvent.ScanEvent import loadScanEvent
from gui.cGui.main.ReportsView import ReportsView
from Tkinter import Menu

class CGuiController(object):
    '''
    Creates the controller for the Cernent/Cerno gui.
    This controller also creates all neccessary components of the gui and manages them.
    '''
    WIDTH = 1000
    HEIGHT = 750
    TITLE = "Cernent"
    
    def __init__(self, scanners, conf):
        '''
        Initialized the controller for the main cernent gui.
        
        Args:
            scanners (dict): The set of scanners per the cernent config file
                             mapped to their respective nessus communicator.
            conf (dict):     Miscellaneous configuration of cernent.
        '''
        self.conf = conf
        self.scanners = scanners
        self._initWindow()
        self._initBaseFrame()
        self._initComponents()
        self.clearMenuBar()
        self.switchToLaunchpad()
        #The scanEvent currently being edited.
        
    def getConfig(self):
        '''
        Returns the configuration dict for cernent.
        '''
        return self.conf
        
    def _initWindow(self):
        self.window = Tkinter.Tk()
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.grid_propagate(True)
        self.window.title(CGuiController.TITLE)
        
    def _initBaseFrame(self):
        self.baseFrame = CFrame(master = self.window)
        self.baseFrame.columnconfigure(0, weight=1)
        self.baseFrame.rowconfigure(0, weight=1)
        self.baseFrame.grid_propagate(True)
        self.baseFrame.grid(row = 0, column = 0, sticky = "NESW")
        
    def _initComponents(self):    
        self.launch = Launchpad(self.baseFrame, self, self.conf)
        self.scanEdit = ScanEventEditor(self.baseFrame, self)
        self.scanEdit.setServerList(self.scanners.keys())
        self.reportManage = ReportsView(self.baseFrame, self)
        self._initBlankMenu()
        
    def _initBlankMenu(self):
        self.blankMenu= Menu(master = self.window)
    
    def isConnected(self, serverName):
        '''
        Returns:
            If the server has a connected communicator.
        '''
        return self.scanners[serverName].isConnected()
    
    def show(self):
        '''
        Calls the mainloop for the gui, making it visible and active.
        '''
        '''Fix for Mac window manager not bringing the new window to the foreground on launch'''
        if 'Darwin' in platform.system():
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        self.window.mainloop()
        
    def hide(self):
        '''
        Closes the gui window and destroys all widgets.
        '''
        self.window.quit()
        
    def close(self):
        '''
        Informs the controller that the gui should be closed.
        '''
        self.window.quit()
        
    def getRootPane(self):
        '''
        Returns the Tk Instance that is this gui's window.
        This is used as the root pane for purposed of menus and such.
        
        Returns:
            An instance of Tk that is this gui's main window.
        '''
        return self.window
        
    def _serverSelected(self):
        '''
        Notifies this controller that a server has been selected
        '''
        self.selectedServer = self.scanEdit.getSelectedServer()
        if not self.selectedServer:
            return
        #self.setStatusBarText("Loading policy list from server: " + self.selectedServer)
        self.policies = self._getPolicyDictFromS_Name(self.selectedServer)
        self.scanEdit.setPolicyList(sorted(self.policies.keys()))
        #self.setStatusBarText("Completed loading policy list")
        
    def _getPolicyDictFromS_Name(self, sname):
        return self.scanners[sname].getPolicyDict()
        
    def switchToScanEventsEdit(self, sender):
        '''
        Switches the items in the gui to the scan event editor.
        This method will prompt the user to select a file holding
        the scan event they want to open.
        
        Args:
            sender:  The current occupant of the gui's main frame,
                     which shall be removed from the gui to make
                     room for the scan event editor.  If "None"
                     then the scan event editor will be added immediately.
        '''
        #Ask which scan event (.se file) you want to load.
        fileName = self.getScanEventFileName()
        if fileName:
            self.switchToScanEdit(loadScanEvent(fileName), fileName, sender)
            
    def switchToLaunchpad(self, sender = None):
        '''
        Switches the gui to display the Launchpad.
        
        Args:
            sender:  The current occupant of the gui's main frame,
                     which shall be removed before adding in the 
                     Launchpad.  If "None", then the Launchpad
                     will be added immediately.
        '''
        if sender:
            sender.remove()
        self._setSizeToLaunch()
        self.launch.add()
            
    def getScanEventFileName(self):
        '''
        Opens a dialogue box for the user to select a Scan Event (.se file)
        and returns it.
        
        Returns:
            The selected file's absolute path, or None if the selection was cancelled.
        '''
        return askopenfilename(initialdir=getPathToSaves(), filetypes=[".se {.se ?se ...?}"])
            
    def switchToScanEventsNew(self, sender):
        '''
        Switched the gui to display the ScanEvent editor.
        This method sets the editor to a new instance of ScanEvent,
        and will have no configurations set.
        
        Args:
            sender:  The current occupant of the gui's main frame,
                     to be removed so the scan event editor can take
                     its place.
        '''
        self.switchToScanEdit(ScanEvent(), None, sender)
        
    def switchToScanEdit(self, scanEvent, location, sender):
        '''
        Performs the act of removing the current occupand of the gui's main frame
        and switching in the ScanEventEditor.
        
        Args:
            scanEvent (ScanEvent):  An instance of ScanEvent for which the ScanEventEditor
                                    should configure itself to.  Cannot be None.
            
            location (String):      The path as to where scanEvent came from.  This can
                                    be None, implying that scanEvent is new and has no
                                    home.
                                    
            sender:                 The current occupant of the gui's main frame, to be
                                    removed so the ScanEventEditor can be placed.
        '''
        self.scanEdit.configureTo(scanEvent)
        self._setSizeToReg()
        sender.remove()
        self.scanEdit.add()
        
    def switchToReports(self, sender):
        '''
        Switched the gui to display the ad-hoc reporting window.
        This method asks the user for which .nessus file to use
        in the reports frame.  If the user cancels the file selection
        no switch will take place and the gui will not change.
        
        Args:
            sender:  The current occupant of the gui's main frame,
                     that will be removed.
        '''
        nessusFile = self.getNessusFile()
        if nessusFile:
            self._setSizeToReg()
            self.reportManage.setNessusFile(nessusFile)
            sender.remove()
            self.reportManage.add()
            
    def getNessusFile(self):
        '''
        Opens a dialogue box and asks the user to select a .nessus file.
        
        Returns:
            The absolute path to the selected file, or None if the selection
            was cancelled.
        '''
        return askopenfilename(title="Search for a .nessus file",
                               filetypes=[".nessus {.nessus ?nessus ...?}"])
            
    def setSubTitle(self, text):
        '''
        Sets the subtext for the title of the window.
        
        Args:
            text (String): The text to be the subtext, or None if there
                           is no subtext.
        '''
        if not text:
            self.window.title(CGuiController.TITLE)
        else:
            self.window.title(CGuiController.TITLE + " - " + text)
        self.window.update_idletasks()
            
    def setMenuBar(self, tmenu):
        '''
        Sets the menu bar of the window to the given menu.
        
        Args:
            tmenu (Tkinter.Menu):  The menu to be displayed.
                                   Can be None, but if you
                                   wish to clear the menu bar
                                   call clearMenuBar instead.
        '''
        self.window.config(menu = tmenu)
        
    def clearMenuBar(self):
        '''
        Clears the window's menu bar.
        '''
        self.window.config(menu = self.blankMenu)
        
    def _setSizeToLaunch(self):
        self._resizeWindow(Launchpad.WIDTH, Launchpad.HEIGHT)
        
    def _setSizeToReg(self):
        self._resizeWindow(CGuiController.WIDTH, CGuiController.HEIGHT)
        
    def _resizeWindow(self, width, height):
        self.window.columnconfigure(0,minsize=width)
        self.window.rowconfigure(0,minsize=height)
        self.window.minsize(width, height)
        self.window.geometry(str(width) + "x" + str(height))
        self.window.update_idletasks()
        self._centerScreen(width, height)
        
    def _centerScreen(self, width, height):
        w = self.window.winfo_screenwidth()
        h = self.window.winfo_screenheight()
        rootsize = (width, height)
        x = w/2 - rootsize[0]/2
        y = h/2 - rootsize[1]/2
        self.window.geometry("%dx%d+%d+%d" % (rootsize + (x, y)))
        
if __name__ == '__main__':
    '''
    Runs the gui with fake and invalid arguments. (just to see it)
    '''
    app = CGuiController({'item 1':'1','item 2':'2','item 3':'3',
                          'item 4':'4','item 5':'5','item 6':'6',
                          'item 7':'7','item 8':'8','item 9':'9',
                          'item 10':'10','item 11':'11','item 12':'12',
                          'item 13':'13'}, None)
    app.show()
        
        
        