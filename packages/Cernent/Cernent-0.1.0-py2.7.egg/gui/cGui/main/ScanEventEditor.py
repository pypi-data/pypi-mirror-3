"""
.. module:: ScanEventEditor
   :platform: Unix
   :synopsis: This view allows a user to edit and manage ScanEvents. 

.. moduleauthor:: Brian Kraus


"""

from gui.cGui.widgets.CFrame import CFrame
from gui.cGui.widgets.CText import CText
from gui.cGui.widgets.CLabel import CLabel
from gui.cGui.widgets.CEntry import CEntry
from gui.cGui.widgets.CCheckButton import CCheckButton
from gui.cGui.widgets.COptionMenu import COptionMenu
from gui.cGui.widgets.CListBox import CListBox
from gui.cGui.widgets.CInitialValueEntry import CInitialValueEntry
from gui.cGui.config.GuiConfig import getBackgroundColor
from gui.cGui.widgets.Notebook import Notebook
from ScanEvent.ScanEvent import loadScanEvent
from ScanEvent.ScanEvent import saveScanEvent
from tkFileDialog import askopenfilename
from ScanEvent.ScanEvent import getPathToSaves
from Tkinter import Menu
from ScanEvent.ScanEvent import ScanEvent
from datetime import datetime
import Tkinter
from Tkinter import StringVar
from Tkinter import Scrollbar
from Tkinter import IntVar
import tkMessageBox

from gui.cGui.widgets.compounds.CEmailFrame import CEmailFrame

class ScanEventEditor(object):
    '''
    Defines an editor for ScanEvents.
    '''
    FOCUSOUT = "<FocusOut>"
    RETURN = "<Return>"
    PADX = 5
    PADY = 10
    INFINITY = "ALL"
    SAVE_INDEX = 1
    STATUS_BASE = "Status:  "

    def __init__(self, master, delegate):
        '''
        Creates a ScanEvent editor frame.
        
        Args:
            master (Frame):  The master frame that this view will add itself to.
            
            delegate (CGuiController):  The controlling delegate for this view.
        '''
        self.masterFrame = CFrame(master = master)
        self.masterFrame.rowconfigure(0, weight=0)
        self.masterFrame.rowconfigure(1, weight=1)
        self.masterFrame.columnconfigure(0, weight=1)
        self.delegate = delegate
        self.isLoading = False
        self._initComponents()
        self.curEvent = None
        self.clearChanged()
                
    def _initComponents(self):
        self._initStatusBar()
        self._initMenu()
        self.notebook = Notebook(self.masterFrame, 1000, 675)
        self._initSetupTab()
        self._initReportsTab()
        self._initEmailsTab()
        
    def _initStatusBar(self):
        self.status = CLabel(master = self.masterFrame, text = ScanEventEditor.STATUS_BASE)
        self.status.grid(row = 2, column = 0, sticky = "NW")
        
    def setStatusBarText(self, text):
        if not text:
            text = ""
        self.status.config(text = ScanEventEditor.STATUS_BASE + text)
        
    def _initMenu(self):
        self.root=self.delegate.getRootPane()
        self.root.protocol("WM_DELETE_WINDOW", self._closingHandler)
        self.menubar = Menu(self.root)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open", command=self.openScanEvent, accelerator='^o')
        self.root.bind("<Control-o>", self.openScanEvent)
        self.filemenu.add_command(label="Save", command=self.saveScanEvent, accelerator='^s')
        self.filemenu.add_command(label="New", command=self.newScanEvent, accelerator='^n')
        self.root.bind("<Control-n>", self.newScanEvent)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self._closingHandler)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        #Added menu to go back to the launchpad
        navMenu = Menu(self.menubar, tearoff=0)
        navMenu.add_command(label = "Return To Start", command = self._toLaunch)
        self.menubar.add_cascade(label = "Nav", menu=navMenu)
        
    def _closingHandler(self, event = None):
        '''
        When the window attempts to exit ('x' is pressed),
        this method determines if it should.  If any changes
        to the current scan event have been made then the user
        is asked if they want to exit or not, otherwise the
        gui will quit immediately.
        '''
        self.gatherData()
        if not self.hasChanged():
            self.delegate.close()
            return
        if self.curEvent.isComplete():
            message = "Are you sure you want to quit and lose all unsaved data?"
        else:
            message = "Are you sure you want to quit and lose all unsaved data?" \
            +"\nThis ScanEvent is not complete, " + \
            "thus it will not be run when it is scheduled:"
            for s in self.curEvent.getProblems():
                message = message + "\n" + s
        if tkMessageBox.askokcancel("Quit?", message):
            self.delegate.close()
        
    def _toLaunch(self):
        self.delegate.switchToLaunchpad(self)
        
    def newScanEvent(self, event = None):
        '''
        Attempts to configure the editor to a new scan event.
        If changes have been made, then the user is prompted to continue.
        If the user decides to cancel, nothing happens.  Otherwise 
        the editor is configured to a new scan event.
        
        Args:
            event:  Ignored.
        '''
        if self.hasChanged():
            if not tkMessageBox.askokcancel("New?", 
                            "Would you like to lose all unsaved fields and start over?"):
                return
        self.configureTo(ScanEvent())
        
    def openScanEvent(self, event = None):
        '''
        Attempts to open a scan event and configure the editor to it.
        The user is prompted to choose a file name.  If none is chosen
        then nothing happens.  Otherwise the editor is configured to a different
        scan event.
        
        Args:
            event: Ignored.
        '''
        name = self.getScanEventOpenName()
        if name:
            self.configureTo(loadScanEvent(name))
            
    def saveScanEvent(self, event = None):
        '''
        Attempts to save the current scan event.  If the current scanEvent
        doesn't have a name then it isn't saved.  Otherwise it is saved
        by name in the pre-defined /opt/cernent directory.
        
        Args:
            event: Ignored.
        '''
        self.gatherData()
        name = self.curEvent.getName()
        if name:
            saveScanEvent(self.curEvent, getPathToSaves() + name)
            self.clearChanged()
            self.delegate.setSubTitle(name)
            
    def getScanEventOpenName(self):
        '''
        Prompts the user to find a ScanEvent (.se) file.
        
        Returns:
            The absolute path to the selected ScanEvent, or None if the search was
            cancelled.
        '''
        return askopenfilename(initialdir=getPathToSaves(), filetypes=[".se {.se ?se ...?}"])
    
    def changeMade(self, event = None, other = None, otherOne = None):
        if self.isLoading:
            return
        '''
        This notifies the editor that one of the fields
        has changed.  The only parameter this
        method cares about is "self", so the remaining
        3 can be left blank.  If a call to this is made
        during a call to configureTo, it is ignored.
        
        Args:
            event: Ignored.
            other: Ignored.
            otherOne: Ignored.
        '''
        self.changed = True;
        self.enableSave(True)
        
    def hasChanged(self):
        '''
        Returns:
            Whether or not the currently editing scan event has changed since the last
            save.
        '''
        c = self.changed or self.targetHasChanged()
        return c
    
    def clearChanged(self):
        '''
        Resets the state so that the editor registers the currently editing
        scan event as having not changed.
        '''
        self.changed = False
        self.enableSave(False)
        
    def enableSave(self, isEnabled):
        '''
        Enables or disables the "Save" menu item per the given isEnabled boolean value.  If isEnabled
        is True, then the menu item is enabled.  This will also enable/disable the bound save command
        accordingly.
        
        Args:
            isEnabled (boolean):  Whether or not to disable the save menu command.
        '''
        if isEnabled:
            self.filemenu.entryconfig(ScanEventEditor.SAVE_INDEX, state = Tkinter.NORMAL)
            self.root.bind("<Control-s>", self.saveScanEvent)
        else:
            self.filemenu.entryconfig(ScanEventEditor.SAVE_INDEX, state = Tkinter.DISABLED)
            self.root.bind("<Control-s>", self._ignore)
            
    def _ignore(self, event = None):
        return "break"
    
    '''
    ************************* TARGET CONTROL
    '''
    
    def getTargetText(self):
        '''
        Returns:
            The String holding the contents of the targets input box.
        '''
        if self.targetText.size():
            return self.targetText.get(1.0, "end").strip()
        return ""
        
    def _targetChanged(self, event = None):
        if self.targetText.size():
            selected = self.getTargetText()
        else:
            selected = None
        if not selected == self.prevTarget:
            self.prevTarget = selected
            self.changeMade()
            if not self.curEvent.setTargets(selected):
                self.setStatusBarText("Invalid IP in Targets.")
                self.redTargets(True)
            else:
                self.redTargets(False)
                self.setStatusBarText(None)
                
    def redTargets(self, isRed):
        color = 'red'
        if not isRed:
            color = getBackgroundColor()
        self.targetText.config(highlightbackground=color)
    
    def targetHasChanged(self):
        '''
        Returns:
            If the contents of the target input box have changed.
        '''
        if self.targetText.size():
            selected = self.targetText.get(1.0, "end")
        else:
            selected = None
        if not selected is self.prevTarget:
            return True
        return False
    
    '''
    ****************************** SERVER CONTROL
    '''
    
    def setServerList(self, serverList):
        '''
        Sets the list of selectable items in the server listbox.
        
        Args:
            serverList ([String]):  The list of server names to select from.
        '''
        self.serverListBox.delete(0, "end")
        for server in serverList:
            self.serverListBox.insert("end", server)
            
    def _serverUpdated(self):
        selected = self.getSelectedServer()
        if not self.serverPrev == selected:
            self.serverPrev = selected
            self.changeMade()
        
    def _serverSelected(self, event = None):
        server = self.getSelectedServer()
        self.setStatusBarText("Connecting to server: " + server)
        if not self.delegate.isConnected(server):
            self._disableCurrentServer();
            self._clearPolicies();
            self.setStatusBarText("Unable to connect to server: " + server)
        else:
            self._enableCurrentServer();
            self.delegate._serverSelected()
            self._serverUpdated()
            self.setStatusBarText("Policies loaded from: " + server)
        
    def getSelectedServer(self):
        '''
        Returns:
            The server selected from the listbox, or None if no selection
            has been made.
        '''
        if self.serverListBox.curselection():
            selected = self.serverListBox.curselection()[0]
            return self.serverListBox.get(selected, selected)[0]
        return None
    
    def _disableCurrentServer(self):
        self._setCurrentItemColor('red','red')
    
    def _enableCurrentServer(self):
        self._setCurrentItemColor('black', 'gray')
    
    def _setCurrentItemColor(self, color, selColor):
        if self.serverListBox.curselection():
            curSelect = self.serverListBox.curselection()[0]
        else:
            return
        self.serverListBox.itemconfig(curSelect, background=color, selectbackground=selColor)
    
    '''
    ********************** POLICIES CONTROL
    '''
    
    def _policySelected(self, event = None):
        selected = self.getSelectedPolicy();
        if not selected == self.policyPrev:
            self.changeMade()
            self.policyPrev = selected
            
    def _clearPolicies(self):
        self.setPolicyList([])
            
    def setPolicyList(self, policyList):
        '''
        Sets the list of selectable policies in the policy listbox.
        
        Args:
            policyList ([String]):  The list of policies to select from.
        '''
        self.scanPolicyListBox.delete(0, "end")
        for policy in policyList:
            self.scanPolicyListBox.insert("end", policy)
        self.changeMade(None)
        
    def getSelectedPolicy(self):
        '''
        Returns:
            The selected policy from the listbox, or None if no selection is made.
        '''
        if self.scanPolicyListBox.curselection():
            selected = self.scanPolicyListBox.curselection()[0]
            return self.scanPolicyListBox.get(selected, selected)[0]
        return None
    
    '''
    ******************************** SCHEDULE CONTROL
    '''
    
    def getSchedule(self):
        '''
        Returns the schedule, which is a dict containing key-value pairs
        according to the apscheduler documentation.
        
        Returns:
            A dict containing the schedule per apscheduler docs.
        '''
        dwm = self.dwm.dwmSelection.get()
        if dwm == "Daily":
            return self._getScheduleDaily()
        elif dwm == "Weekly":
            return self._getScheduleWeekly()
        else:
            return self._getScheduleMonthly()
    
    def _getScheduleDaily(self):
        sched = {}
        sched['year'] = "*"
        sched['month'] = "*"
        sched['week'] = "*"
        sched['day'] = "*"
        sched['day_of_week'] = "*"
        self._setTime()
        sched['hour'] = self.reportFrame.time.whenVparsed.hour
        sched['minute'] = self.reportFrame.time.whenVparsed.minute
        sched['start_date'] = self.startDayV.get()
        sched['dwm'] = self.dwm.dwmSelection.get()
        return sched
    
    def _getScheduleWeekly(self):
        sched = self._getScheduleDaily()
        sched['day_of_week'] = self._getDaysOfWeek(True)
        return sched
    
    def _getDaysOfWeek(self, weekly):
        days = [self.reportFrame.days.mondV, self.reportFrame.days.tuesV, self.reportFrame.days.wedV,
                self.reportFrame.days.thurV, self.reportFrame.days.friV, self.reportFrame.days.satV,
                self.reportFrame.days.sunV]
        ds = []
        for i in range(0,7):
            if days[i].get():
                ds.append(str(i))
        if weekly:
            return ",".join(ds)
        ret = [x + " " + str(y) for x in self._getWeeks() for y in ds]
        return ",".join(ret)
        
    def _getWeeks(self):
        mods = ["st", "nd", "rd","th"]
        weeks = ["","","",""]
        if self.week.w1V.get():
            weeks[0] = "1"
        if self.week.w2V.get():
            weeks[1]="2"
        if self.week.w3V.get():
            weeks[2]="3"
        if self.week.w4V.get():
            weeks[3]="4"
        ws = []
        for i in range(0,4):
            if not weeks[i] == "":
                ws.append(weeks[i] + mods[i]) 
        return ws
    
    def _getScheduleMonthly(self):
        sched = self._getScheduleDaily()
        sched['day'] = self._getDaysOfWeek(False)
        return sched
        
    def _addWeek(self):
        self.week.grid(row=1, column=1, sticky="NW")
        
    def _removeWeek(self):
        self.week.grid_remove()
        
    def _addDays(self):
        self.reportFrame.days.grid(row=2, column = 0, columnspan=2, sticky="W")
        
    def _removeDays(self):
        self.reportFrame.days.grid_remove()
        
    def _dwmSelected(self, event):
        select = self.dwm.dwmSelection.get()
        if select == "Daily":
            self._removeWeek()
            self._removeDays()
        elif select == "Weekly":
            self._removeWeek()
            self._addDays()
        else:
            self._addDays()
            self._addWeek()
            
    '''
    ************************ START TIME/DATE CONTROL
    '''
            
    def _startDayChanged(self, event):
        strT = self.startDayV.get()
        try:
            day = datetime.strptime(strT, "%Y-%m-%d")
        except:
            self.setStatusBarText("Invalid format for Day: " + strT + " should be: %Y-%m-%d")
            self._startDayRed(True)
            return;
        self.setStatusBarText(None)
        self._startDayRed(False)
        self.startDayVparsed = day
        if not self.startDayPrev == strT:
            self.changeMade(None)
            self.startDayPrev = strT
            
    def _startDayRed(self, isRed):
        color = 'red'
        if not isRed:
            color = getBackgroundColor()
        self.startDay.config(highlightbackground=color)
        
    def _setTime(self, event = None):
        strT = self.reportFrame.time.whenV.get()
        try:
            time = datetime.strptime(strT, "%H:%M")
        except:
            self.setStatusBarText("Invalid format for Time string: " + strT + " should be in format: %H:%M")
            self._startTimeRed(True)
            return
        self.setStatusBarText(None)
        self.reportFrame.time.whenVparsed = time
        self._startTimeRed(False)
        
    def _startTimeRed(self, isRed):
        color = 'red'
        if not isRed:
            color = getBackgroundColor()
        self.reportFrame.time.when.config(highlightbackground=color)
        
    '''
    **************************** NOTIFICATIONS CONTROL
    '''
        
    def _startNotifPressed(self):
        if self.reportFrame.notif.startV.get():
            self.reportFrame.notif.startNotif['state'] = Tkinter.NORMAL
        else:
            self.reportFrame.notif.startNotif['state'] = Tkinter.DISABLED
            
    def _startNotifChanged(self, event = None, other=None, otherOne=None):
        if not self.curEvent.setStartNotif(self.reportFrame.notif.startNotifV.get()):
            self._startRed(True)
            self.setStatusBarText("Invalid email for start notification.")
        else:
            self._startRed(False)
            self.setStatusBarText(None)
            
    def _endNotifPressed(self):
        if self.reportFrame.notif.endV.get():
            self.reportFrame.notif.endNotif['state'] = Tkinter.NORMAL
        else:
            self.reportFrame.notif.endNotif['state'] = Tkinter.DISABLED
        
    def _endNotifChanged(self, event = None, other=None, otherOne=None):
        if not self.curEvent.setEndNotif(self.reportFrame.notif.endNotifV.get()):
            self._endRed(True)
            self.setStatusBarText("Invalid email for end notification.")
        else:
            self._endRed(False)
            self.setStatusBarText(None)
    
    def _startRed(self, isRed):
        color = 'red'
        if not isRed:
            color = getBackgroundColor()
        self.reportFrame.notif.startNotif.config(highlightbackground=color)
        
    def _endRed(self, isRed):
        color = 'red'
        if not isRed:
            color = getBackgroundColor()
        self.reportFrame.notif.endNotif.config(highlightbackground=color)
        
    '''
    *************************************** Setup Tab Widgets ***********************************************
    '''
        
    def _initSetupTab(self):
        self.setupFrame = CFrame(self.notebook.__call__())
        self._initSetupWidgets()
        self.notebook.add_screen(self.setupFrame, "Setup")
        size = 5
        for i in range(0, size):
            self.setupFrame.rowconfigure(i, weight = 1)
            self.setupFrame.columnconfigure(i, weight=1)
        
    def _initSetupWidgets(self):
        self._initScanName()
        self._initTargets()
        self._initServerList()
        self._initScanPolicyList()
        
    def _initScanName(self):
        self.scanName = CFrame(master = self.setupFrame)
        self.scanName.columnconfigure(0, weight=1)
        #label
        self.scanName.label = CLabel(text = "Scan Name", master = self.scanName)
        self.scanName.label.grid(row = 0, column = 0, sticky = "WN")
        #config
        self.nameV = StringVar()
        self.nameV.trace("w", self.changeMade)
        #entry
        self.scanName.entry = CEntry(master = self.scanName, textvariable=self.nameV)
        self.scanName.entry.grid(row = 1, column = 0, sticky = "WNE", pady = ScanEventEditor.PADY)
        self.scanName.grid(row = 0, column = 0, sticky = "NEWS",
                            pady=ScanEventEditor.PADY, padx=ScanEventEditor.PADX)
        
    def _initTargets(self):
        self.targetFrame = CFrame(master = self.setupFrame)
        self.targetFrame.rowconfigure(1, weight = 1)
        self.targetFrame.columnconfigure(0, weight = 1)
        #label
        self.targetLabel = CLabel(master = self.targetFrame, text="Targets")
        self.targetLabel.grid(row = 0, column = 0, sticky = "WN", pady=ScanEventEditor.PADY)
        #textbox
        self.targetText = CText(master = self.targetFrame, bd=2, relief='sunken')
        self.targetText.bind(ScanEventEditor.FOCUSOUT, self._targetChanged)
        self.targetText.grid(row = 1, column = 0, sticky = "WESN")
        #config
        self.prevTarget = self.getTargetText()
        #scrollbar
        scrollBar = Scrollbar(master = self.targetFrame)
        self.targetText.config(yscrollcommand=scrollBar.set)
        scrollBar.config(command=self.targetText.yview)
        scrollBar.grid(row = 1, column = 1, sticky = "NSW")
        self.targetFrame.grid(row = 1, column = 0, sticky = "NEWS", padx=ScanEventEditor.PADX)
                
    def _initServerList(self):
        '''Added exportselection=0 to allow multiple listbox selections'''
        self.serverFrame = CFrame(master = self.setupFrame)
        self.serverFrame.columnconfigure(0, weight = 1)
        self.serverFrame.rowconfigure(1, weight = 1)
        #label
        self.serverLabel = CLabel(master = self.serverFrame, text = "Nessus Server")
        self.serverLabel.grid(row = 0, column = 0, sticky = "WN", pady=ScanEventEditor.PADY)
        #listbox
        self.serverListBox = CListBox(master = self.serverFrame,
                                       selectmode = Tkinter.SINGLE, exportselection=0)
        self.serverListBox.grid(row = 1, column = 0, sticky = "WESN",)
        #config
        self.serverPrev = None
        self.serverListBox.bind("<ButtonRelease-1>", self._serverSelected)
        #scrollbars
        scrollBar = Scrollbar(master = self.serverFrame)
        self.serverListBox.config(yscrollcommand=scrollBar.set)
        scrollBar.config(command=self.serverListBox.yview)
        scrollBar.grid(row = 1, column = 1, sticky = "NSW")
        self.serverFrame.grid(row = 0, column = 1, sticky = "NSWE", padx=ScanEventEditor.PADX)
                
    def _initScanPolicyList(self):
        '''Added exportselection=0 to allow multiple listbox selections'''
        self.scanPolicyFrame = CFrame(master = self.setupFrame)
        self.scanPolicyFrame.columnconfigure(0, weight=1)
        self.scanPolicyFrame.rowconfigure(1, weight=1)
        self.scanPolicyLabel = CLabel(master = self.scanPolicyFrame, text = "Scan Policy")
        self.scanPolicyLabel.grid(row = 0, column = 0, sticky = "W", pady=ScanEventEditor.PADY)
        self.scanPolicyListBox = CListBox(master = self.scanPolicyFrame, selectmode = Tkinter.SINGLE, exportselection=0, width=30)
        self.scanPolicyListBox.grid(row = 1, column = 0, sticky = "WENS")
        self.policyPrev = None
        self.scanPolicyListBox.bind(ScanEventEditor.FOCUSOUT, self._policySelected)
        scrollBar = Scrollbar(master = self.scanPolicyFrame)
        self.scanPolicyListBox.config(yscrollcommand=scrollBar.set)
        scrollBar.config(command=self.scanPolicyListBox.yview)
        scrollBar.grid(row = 1, column = 1, sticky = "NSW")
        self.scanPolicyFrame.grid(row = 1, column = 1, sticky = "NEWS", padx=ScanEventEditor.PADX)
        
    '''
    **************************************** SCHEDULE TAB ********************************************
    '''
        
    def _initReportsTab(self):
        self.reportFrame = CFrame(self.notebook.__call__())
        self.reportFrame.columnconfigure(0, weight = 1)
        self.reportFrame.columnconfigure(1, weight = 1)
        self._initReportsWidgets()
        self.notebook.add_screen(self.reportFrame, "Scheduling")
        
        
    def _initReportsWidgets(self):
        self._initSchedDWM()
        self._initWeek()
        self._initSchedDays()
        self._dwmSelected(None)
        self._initStart()
        self._initNotifs()
        
    def _initSchedDWM(self):
        self.dwm = CFrame(master=self.reportFrame)
        self.schedLabel = CLabel(master = self.dwm, text="Schedule:")
        self.schedLabel.grid(row=0,column=0, sticky="SW")
        self.dwm.dwmSelection = StringVar(self.dwm)
        self.dwm.dwmSelection.set("Weekly")
        self.dwm.dwmSelection.trace("w", self.changeMade)
        self.dwm.dwmMenu = COptionMenu(self.dwm, self.dwm.dwmSelection, "Daily", "Weekly", "Monthly", command=self._dwmSelected)
        self.dwm.dwmMenu.grid(row=1, column=0, sticky="NW")
        self.dwm.grid(row=0,column=0, sticky="NW", pady = ScanEventEditor.PADY, padx = ScanEventEditor.PADX)

    def _initWeek(self):
        self.week = CFrame(master = self.dwm)
        self.week.label = CLabel(master = self.week, text="Week #: ")
        self.week.label.grid(row=0, column=0, sticky="NW", pady=ScanEventEditor.PADY)
        self.week.w1V = IntVar()
        self.week.w1V.trace("w", self.changeMade)
        self.week.w1 = CCheckButton(master = self.week, text="1", variable=self.week.w1V)
        self.week.w1.grid(row=0, column=1, sticky="NW")
        self.week.w2V = IntVar()
        self.week.w2V.trace("w", self.changeMade)
        self.week.w2 = CCheckButton(master = self.week, text="2", variable=self.week.w2V)
        self.week.w2.grid(row=0, column=2, sticky="NW")
        self.week.w3V = IntVar()
        self.week.w3V.trace("w", self.changeMade)
        self.week.w3 = CCheckButton(master = self.week, text="3", variable=self.week.w3V)
        self.week.w3.grid(row=1, column=1, sticky="NW")
        self.week.w4V = IntVar()
        self.week.w4V.trace("w", self.changeMade)
        self.week.w4 = CCheckButton(master = self.week, text="4", variable=self.week.w4V)
        self.week.w4.grid(row=1, column=2, sticky="NW")
        
    def _initSchedDays(self):
        self.reportFrame.days = CFrame(master = self.dwm)
        self.reportFrame.days.mondV = IntVar()
        self.reportFrame.days.mondV.trace("w", self.changeMade)
        self.reportFrame.days.monday = CCheckButton(master=self.reportFrame.days,
                                                 text="M",variable=self.reportFrame.days.mondV)
        self.reportFrame.days.monday.grid(row=0,column=0)
        self.reportFrame.days.tuesV = IntVar()
        self.reportFrame.days.tuesV.trace("w", self.changeMade)
        self.reportFrame.days.tuesday = CCheckButton(master=self.reportFrame.days,
                                                 text="T",variable=self.reportFrame.days.tuesV)
        self.reportFrame.days.tuesday.grid(row=0,column=1)
        self.reportFrame.days.wedV = IntVar()
        self.reportFrame.days.wedV.trace("w", self.changeMade)
        self.reportFrame.days.wednesday = CCheckButton(master=self.reportFrame.days,
                                                 text="W",variable=self.reportFrame.days.wedV)
        self.reportFrame.days.wednesday.grid(row=0,column=2)
        self.reportFrame.days.thurV = IntVar()
        self.reportFrame.days.thurV.trace("w", self.changeMade)
        self.reportFrame.days.thursday = CCheckButton(master=self.reportFrame.days,
                                                 text="TR",variable=self.reportFrame.days.thurV)
        self.reportFrame.days.thursday.grid(row=0,column=3)
        self.reportFrame.days.friV = IntVar()
        self.reportFrame.days.friV.trace("w", self.changeMade)
        self.reportFrame.days.friday = CCheckButton(master=self.reportFrame.days,
                                                 text="F",variable=self.reportFrame.days.friV)
        self.reportFrame.days.friday.grid(row=0,column=4)
        self.reportFrame.days.satV = IntVar()
        self.reportFrame.days.satV.trace("w", self.changeMade)
        self.reportFrame.days.saturday = CCheckButton(master=self.reportFrame.days,
                                                 text="Sat",variable=self.reportFrame.days.satV)
        self.reportFrame.days.saturday.grid(row=0,column=5)
        self.reportFrame.days.sunV = IntVar()
        self.reportFrame.days.sunV.trace("w", self.changeMade)
        self.reportFrame.days.sunday = CCheckButton(master=self.reportFrame.days,
                                                 text="Sun",variable=self.reportFrame.days.sunV)
        self.reportFrame.days.sunday.grid(row=0,column=6)
       
    def _initStart(self):
        self._initTimeSelector()
        self._initStartDay()
        
    def _initTimeSelector(self):
        self.reportFrame.time = CFrame(master = self.reportFrame)
        self.timeLabel = CLabel(master = self.reportFrame.time, text="Time: (24 hours)")
        self.timeLabel.grid(row=0, column = 0, sticky = "SW", pady=ScanEventEditor.PADY)
        self.reportFrame.time.whenV = StringVar()
        today = datetime.today()
        today = today.strftime("%H:%M")
        self.reportFrame.time.whenV.set(today)
        self.reportFrame.time.whenV.trace("w", self.changeMade)
        self.reportFrame.time.when = CEntry(self.reportFrame.time, text=today)
        self.reportFrame.time.when.bind(ScanEventEditor.FOCUSOUT, self._setTime)
        self.reportFrame.time.when.bind(ScanEventEditor.RETURN, self._setTime)
        self.reportFrame.time.when['textvariable'] = self.reportFrame.time.whenV
        self.reportFrame.time.when.grid(row=1,column=0, sticky= "NW")
        self.reportFrame.time.grid(row=1, column=0, sticky="NW", padx = ScanEventEditor.PADX)
        self._setTime(None)
        
    def _initStartDay(self):
        self.startD = CFrame(self.reportFrame)
        self.startDayL = CLabel(master = self.startD, text="Start Date:")
        self.startDayL.grid(row=0, column = 0, sticky = "NW", pady=ScanEventEditor.PADY)
        self.startDayV = StringVar()
        today = datetime.today().strftime("%Y-%m-%d")
        self.startDayV.set(today)
        self.startDayPrev = today
        self.startDay = CEntry(master=self.startD, text="", textvariable=self.startDayV)
        self.startDay.bind(ScanEventEditor.RETURN, self._startDayChanged)
        self.startDay.bind(ScanEventEditor.FOCUSOUT, self._startDayChanged)
        self.startDay.grid(row=1, column = 0, sticky = "NW")
        self.startD.grid(row=2, column=0, sticky ="NW", padx = ScanEventEditor.PADX)
        self._startDayChanged(None)
        
    def _initNotifs(self):
        self.reportFrame.notif = CFrame(master=self.reportFrame)
        self.reportFrame.notif.columnconfigure(1, weight=1)
        self.notifLabel= CLabel(master = self.reportFrame.notif, text="Notifications:")
        self.notifLabel.grid(row = 0, column = 0, columnspan=2, sticky = "SW")
        self.reportFrame.notif.startL = CLabel(master = self.reportFrame.notif, text="Start:", padx = 10)
        self.reportFrame.notif.startL.grid(row=1,column=0,columnspan=2, sticky="NW")
        self.reportFrame.notif.startV = IntVar()
        self.reportFrame.notif.startV.trace("w", self.changeMade)
        self.reportFrame.notif.startCheck = CCheckButton(master = self.reportFrame.notif, variable=self.reportFrame.notif.startV,
                                                         command=self._startNotifPressed)
        self.reportFrame.notif.startCheck.grid(row=2, column = 0, sticky = "NW")
        self.reportFrame.notif.startNotifV = StringVar()
        ex="administrator@example.com"
        self.reportFrame.notif.startNotifV.set(ex)
        self.reportFrame.notif.startNotifV.trace("w", self._startNotifChanged)
        self.reportFrame.notif.startNotif = CInitialValueEntry(master = self.reportFrame.notif, text="",
                                                               textvariable=self.reportFrame.notif.startNotifV,
                                                               state=Tkinter.DISABLED)
        self.reportFrame.notif.startNotif.grid(row=2, column = 1, sticky = "NWE")
        
        self.reportFrame.notif.finish = CLabel(master = self.reportFrame.notif, text="Finish:", padx = 10)
        self.reportFrame.notif.finish.grid(row=3, column=0, columnspan=2, sticky="NW")
        self.reportFrame.notif.endV = IntVar()
        self.reportFrame.notif.endV.trace("w", self.changeMade)
        self.reportFrame.notif.endCheck = CCheckButton(master = self.reportFrame.notif, variable=self.reportFrame.notif.endV,
                                                       command=self._endNotifPressed)
        self.reportFrame.notif.endCheck.grid(row=4, column=0, sticky="NW")
        self.reportFrame.notif.endNotifV = StringVar()
        self.reportFrame.notif.endNotifV.set(ex)
        self.reportFrame.notif.endNotifV.trace("w", self._endNotifChanged)
        self.reportFrame.notif.endNotif = CInitialValueEntry(master = self.reportFrame.notif, text="",
                                                             textvariable=self.reportFrame.notif.endNotifV,
                                                             state=Tkinter.DISABLED)
        self.reportFrame.notif.endNotif.grid(row=4, column=1, sticky="NWE")
        self.reportFrame.notif.grid(row=0, column = 1, sticky = "NWE",
                                     pady = ScanEventEditor.PADY, padx=ScanEventEditor.PADX)
            
    '''
    ******************************************** EMAILS TAB **********************************************
    '''
        
    def _initEmailsTab(self):
        self.emailFrame = CFrame(master = self.notebook.__call__())
        self.emailTab = CEmailFrame(self.emailFrame, self, self.delegate.getConfig())
        self.emailTab.grid()
        self.notebook.add_screen(self.emailFrame, "Emails")
        
        
    '''
    ******************************************* END TABS ***********************************************
    '''    
    
    '''
    ******************************** CONFIGURATION ************************
    '''
    
    def configureTo(self, scanEvent):
        self.isLoading = True
        '''
        This method takes an instance of a ScanEvent and configures all of the gui elements to reflect the values
        of the given ScanEvent.
        
        Args:
            scanEvent (ScanEvent):  The scan event to configure to.
        '''
        self.delegate.setSubTitle(scanEvent.getName())
        self.curEvent = scanEvent
        #Set the name if we are given one.
        name = self.curEvent.getName()
        self.nameV.set("")
        if name:
            self.nameV.set(name)
        #Set the targets if we are givnen it.
        targets = self.curEvent.getTargets()
        self.targetText.delete(1.0, "end")
        if targets:
            self.targetText.insert(1.0, targets)
        self._configureSched(scanEvent.getSchedule_GUI())
        self._configureScanner(scanEvent)
        self._configureNotifs()
        
        # dchee
        self._configureEmailTab(scanEvent.getEmailItems())
        self.isLoading = False
        self.clearChanged()
        
    def _configureNotifs(self):
        snotif = self.curEvent.getStartNotif()
        if snotif:
            self.reportFrame.notif.startV.set(True)
            self.reportFrame.notif.startNotifV.set(ScanEvent.DELIMITER_TARGETS.join(snotif))
        else:
            #Have to set to true, in order to change contents.
            self.reportFrame.notif.startV.set(True)
            self.reportFrame.notif.startNotifV.set("")
            #Then for reals set it to false.
            self.reportFrame.notif.startV.set(False)
        self._startNotifPressed()
        enotif = self.curEvent.getEndNotif()
        if enotif:
            self.reportFrame.notif.endV.set(True)
            self.reportFrame.notif.endNotifV.set(ScanEvent.DELIMITER_TARGETS.join(enotif))
        else:
            #Have to set to true, in order to change contents.
            self.reportFrame.notif.endV.set(True)
            self.reportFrame.notif.endNotifV.set("")
            #Then for reals set it to false.
            self.reportFrame.notif.endV.set(False)
        self._endNotifPressed()
        
    def _configureScanner(self, scanEvent):
        '''
        Configures the gui to select the right scanner and policy.
        Since the delegate sets the info for the scanners listbox, we just need to check
        if our selection is in that box.
        '''
        self.serverListBox.select_clear(0, "end")
        selectedScan = scanEvent.getScannerName()
        if not selectedScan:
            return
        scans = self.serverListBox.get(0, "end")
        size = len(scans)
        for i in range(0,size):
            if scans[i] == selectedScan:
                self.serverListBox.select_set(i,i)
                self._serverSelected(None)
                self._configurePolicy(scanEvent)
                
    def _configurePolicy(self, scanEvent):
        selectedPolicy = scanEvent.getPolicy()
        print "Selected policy: " + selectedPolicy
        if not selectedPolicy:
            return
        policies = self.scanPolicyListBox.get(0,"end")
        size = len(policies)
        if size:
            for i in range(0, size):
                if policies[i] == selectedPolicy:
                    self.scanPolicyListBox.select_set(i,i)
        else:
            self.setPolicyList([selectedPolicy])
            self.scanPolicyListBox.select_set(0, 0)
        
        
    def _configureSched(self, sched):
        if not sched:
            return
        if 'dwm' in sched and sched['dwm']:
            self.dwm.dwmSelection.set(sched['dwm'])
            self._dwmSelected(sched['dwm'])
        else:
            self.dwm.dwmSelection.set('Weekly')
            self._dwmSelected('Weekly')
            
        if 'start_date' in sched and sched['start_date']:
            self.startDayV.set(sched['start_date'])
        else:
            self.startDayV.set(datetime.today().strftime("%Y-%m-%d"))
            
        if 'hour' in sched and 'minute' in sched and sched['hour'] and sched['minute']:
            start = datetime.strptime(str(sched['hour']) + ":" + str(sched['minute']), "%H:%M")
            self.reportFrame.time.whenV.set(start.strftime("%H:%M"))
        else:
            self.reportFrame.time.whenV.set(datetime.today().strftime("%H:%M"))
        
        self._resetDays()
        self._resetWeeks()
        if 'day_of_week' in sched and sched['day_of_week']:
            string = sched['day_of_week']
            tokens = string.split(',')
            for s in tokens:
                if s.find(" ") != -1:
                    items = s.split(" ")
                    self._setWeekOn(items[0][0])
                    self._setDayOn(items[1][0])
                else:
                    self._setDayOn(s[0])
                    
    def _configureEmailTab(self, emailItems):
        if emailItems:
            self.emailTab.setEmailItems(emailItems)          
                
    def _resetDays(self):
        self.reportFrame.days.mondV.set(False)
        self.reportFrame.days.tuesV.set(False)
        self.reportFrame.days.wedV.set(False)
        self.reportFrame.days.thurV.set(False)
        self.reportFrame.days.friV.set(False)
        self.reportFrame.days.satV.set(False)
        self.reportFrame.days.sunV.set(False)
                
    def _setDayOn(self, day):
        if day == "0":
            self.reportFrame.days.mondV.set(True)
        if day == "1":
            self.reportFrame.days.tuesV.set(True)
        if day == "2":
            self.reportFrame.days.wedV.set(True)
        if day == "3":
            self.reportFrame.days.thurV.set(True)
        if day == "4":
            self.reportFrame.days.friV.set(True)
        if day == "5":
            self.reportFrame.days.satV.set(True)
        if day == "6":
            self.reportFrame.days.sunV.set(True)
            
    def _resetWeeks(self):
        self.week.w1V.set(False)
        self.week.w2V.set(False)
        self.week.w3V.set(False)
        self.week.w4V.set(False)
                    
    def _setWeekOn(self, week):
        if week == "1":
            self.week.w1V.set(True)
        if week == "2":
            self.week.w2V.set(True)
        if week == "3":
            self.week.w3V.set(True)
        if week == "4":
            self.week.w4V.set(True)
            
            
    '''
    ****************************** GATHERING ***************************
    '''
            
    def gatherData(self):
        '''
        This method takes all of the data from the Gui input elements 
        and sets the corresponding values
        in the current ScanEvent.
        '''
        '''
        Call some methods to check if any of the editable boxes have new data in it.
        '''
        self._targetChanged()
        self._serverUpdated()
        self._policySelected()
        self.curEvent.setName(self.nameV.get())
        self.curEvent.setTargets(self.getTargetText())
        policy = self.getSelectedPolicy()
        if policy:
            self.curEvent.setPolicy(policy)
        else:
            self.curEvent.setPolicy({})
        
        # Added by DCHEE
        self.curEvent.setEmailItems(self.emailTab.getEmailItems())
        
        self.curEvent.setSchedule(self.getSchedule())
        self.curEvent.setScannerName(self.getSelectedServer())
        self.curEvent.setPolicy(self.getSelectedPolicy())
        self._gatherNotifs()
        
    def _gatherNotifs(self):
        if self.reportFrame.notif.startV.get():
            self.curEvent.setStartNotif(
                self.reportFrame.notif.startNotifV.get())
        else:
            self.curEvent.setStartNotif(None)
            
        if self.reportFrame.notif.endV.get():
            self.curEvent.setEndNotif(
                self.reportFrame.notif.endNotifV.get())
        else:
            self.curEvent.setEndNotif(None)
    
    def add(self):
        '''
        Adds the ScanEventEditor view to the pre-defined master frame.
        '''
        self.delegate.setMenuBar(self.menubar)
        self.masterFrame.grid(row = 0, column = 0, columnspan = 1, sticky="NESW")
    
    def remove(self):
        '''
        Removes the ScanEventEditor view from the pre-defined master frame.
        '''
        self.masterFrame.grid_remove()
        self.delegate.clearMenuBar()
        self.menubar.grid_remove()
        