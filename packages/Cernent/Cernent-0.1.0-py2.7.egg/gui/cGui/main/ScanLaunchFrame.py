'''
Created on Feb 26, 2012

***
DEMO CODE - DO NOT USE / JUDGE
***


@author: bkraus
'''

import Tkinter
from gui.cGui.widgets.CEntry import CEntry
from gui.cGui.widgets.CLabel import CLabel
from gui.cGui.widgets.CText import CText
from gui.cGui.widgets.CListBox import CListBox
from gui.cGui.widgets.CButton import CButton
from gui.cGui.widgets.CFrame import CFrame
from gui.cGui.config.GuiConfig import getBackgroundColor
from gui.cGui.config.GuiConfig import getPadX
from gui.cGui.config.GuiConfig import getPadY

class ScanLaunchFrame(object):
    '''
    This is the main gui panel for Modifying ScanEvents.
    '''
    WIDTH = 1000
    HEIGHT = 700
    BG = getBackgroundColor()
    PadX = getPadX()
    PadY = getPadY()
    
    
    def __init__(self, master, delegate):
        self.delegate = delegate
        self.frame = CFrame(master, width = ScanLaunchFrame.WIDTH, height = ScanLaunchFrame.HEIGHT)
        self.initializeWidgets()
        
    def initScanNameLabel(self):
        self.scanName = CLabel(text = "Scan Name", master = self.frame, bg=ScanLaunchFrame.BG)
        self.scanName.grid(row = 0, column = 0, columnspan = 2, sticky = "W", padx=ScanLaunchFrame.PadX, pady=ScanLaunchFrame.PadY)
        
    def initScanNameEntry(self):
        self.scanNameEntry = CEntry(master = self.frame, width=40, highlightbackground=ScanLaunchFrame.BG)
        self.scanNameEntry.grid(row = 1, column = 0, columnspan = 5, sticky = "W", padx=ScanLaunchFrame.PadX)
        
    def initTargetLabel(self):
        self.targetLabel = CLabel(master = self.frame, text="Targets", bg=ScanLaunchFrame.BG)
        self.targetLabel.grid(row = 2, column = 0, columnspan = 1, sticky = "W", padx=ScanLaunchFrame.PadX, pady=ScanLaunchFrame.PadY)
        
    def initTargetText(self):
        self.targetText = CText(master = self.frame, bd=2, relief='sunken', highlightcolor='#5095C8', highlightbackground=ScanLaunchFrame.BG, highlightthickness=3)
        self.targetText.grid(row = 3, column = 0, columnspan = 5, rowspan = 20, sticky = "W", padx=ScanLaunchFrame.PadX, pady=ScanLaunchFrame.PadY)
        
    def initServerLabel(self):
        self.serverLabel = CLabel(master = self.frame, text = "Nessus Server", bg=ScanLaunchFrame.BG)
        self.serverLabel.grid(row = 0, column = 6, columnspan = 2, sticky = "W", padx=ScanLaunchFrame.PadX)
        
    def initServerListBox(self):
        '''Added exportselection=0 to allow multiple listbox selections'''
        self.serverListBox = CListBox(master = self.frame, selectmode = Tkinter.SINGLE, exportselection=0, width=30)
        self.serverListBox.grid(row = 1, column = 6, columnspan = 5, rowspan = 7, sticky = "W", padx=ScanLaunchFrame.PadX)
        self.serverListBox.bind("<ButtonRelease-1>", self._serverSelected)
        
    def _serverSelected(self, event):
        self.delegate._serverSelected()
        
    def initScanPolicyLabel(self):
        self.scanPolicyLabel = CLabel(master = self.frame, text = "Scan Policy", bg=ScanLaunchFrame.BG)
        self.scanPolicyLabel.grid(row = 8, column = 6, columnspan = 2, sticky = "W", padx=ScanLaunchFrame.PadX, pady=ScanLaunchFrame.PadY)
        
    def initScanPolicyListBox(self):
        '''Added exportselection=0 to allow multiple listbox selections'''
        self.scanPolicyListBox = CListBox(master = self.frame, selectmode = Tkinter.SINGLE, exportselection=0, width=30)
        self.scanPolicyListBox.grid(row = 8, column = 6, columnspan = 5, rowspan = 25, sticky = "W", padx=ScanLaunchFrame.PadX)
        self.scanPolicyListBox.bind("<ButtonRelease-1>", self._policySelected)
        
    def _policySelected(self, event):
        self.delegate._policySelected()
                
    def scanButtonPressed(self):
        self.delegate.runScan()
    
    def initScanButton(self):
        self.scanButton = CButton(master = self.frame, text = "Scan Now", command = self.scanButtonPressed, anchor='center', highlightbackground=ScanLaunchFrame.BG)
        self.scanButton.grid(row = 35, column = 6, columnspan = 3, sticky = "E", pady=ScanLaunchFrame.PadY)
        
    def initializeWidgets(self):
        self.initScanNameLabel()
        self.initScanNameEntry()
        self.initTargetLabel()
        self.initTargetText()
        self.initServerLabel()
        self.initServerListBox()
        self.initScanPolicyLabel()
        self.initScanPolicyListBox()
        self.initScanButton()
        
    def setScanName(self, text = ""):
        self.scanNameEntry.config(text = text)
        
    def setServerList(self, serverList):
        self.serverListBox.delete(0, "end")
        for server in serverList:
            self.serverListBox.insert("end", server)
            
    def setPolicyList(self, policyList):
        self.scanPolicyListBox.delete(0, "end")
        for policy in policyList:
            self.scanPolicyListBox.insert("end", policy)
            
    def getSelectedPolicy(self):
        if self.scanPolicyListBox.curselection():
            selected = self.scanPolicyListBox.curselection()[0]
            return self.scanPolicyListBox.get(selected, selected)[0]
        return None
        
    
    def getSelectedServer(self):
        if self.serverListBox.curselection():
            selected = self.serverListBox.curselection()[0]
            return self.serverListBox.get(selected, selected)[0]
        return None
    
    def getScanName(self):
        return self.scanNameEntry.get()
    
    def getTargets(self):
        return self.targetText.get(1.0, "end")
    
    def add(self):
        self.frame.grid(row = 0, column = 0)
        