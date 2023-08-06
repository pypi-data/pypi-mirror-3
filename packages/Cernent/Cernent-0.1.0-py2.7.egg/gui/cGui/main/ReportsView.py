"""
.. module:: ReportsView
   :platform: Unix
   :synopsis: The ad-hoc reporting view 

.. moduleauthor:: Brian Kraus


"""

from gui.cGui.widgets.CLabel import CLabel
from gui.cGui.widgets.CListBox import CListBox
from gui.cGui.widgets.CText import CText
from Tkinter import Scrollbar
from gui.cGui.widgets.CFrame import CFrame
import Tkinter
from Tkinter import Menu
from ReportFramework.ReportFramework import loadReports, getExample, writeReport
from tkFileDialog import asksaveasfilename

class ReportsView(object):
    '''
    The ReportsView is the ad-hoc reporting view.
    '''
    
    '''
    Default padding
    '''
    PADX = 5
    PADY = 5
    SAVE_INDEX = 1

    def __init__(self, master, delegate):
        '''
        Initialized the ReportsView.
        
        Args:
            master (Frame):  The frame in which this view will add itself to.
            
            delegate (CGuiController):  The controlling delegate to this view.
        '''
        self.nessusFile = None
        self.delegate = delegate
        self._initWidgets(master)        
        
    def _initWidgets(self, master):
        self.mainFrame = CFrame(master)
        self.mainFrame.columnconfigure(0, weigh = 1)
        self.mainFrame.columnconfigure(2, weigh = 1)
        self.mainFrame.rowconfigure(0, weigh = 1)
        self.mainFrame.rowconfigure(2, weigh = 1)
        self._initMenu()
        self._initReports()
        self._initDescription()
        self._initPadding()
        self._initOutput()
        
    def _initMenu(self):
        self.root=self.delegate.getRootPane()
        self.root.protocol("WM_DELETE_WINDOW", self.delegate.close)
        self.menubar = Menu(self.root)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label = "Change Report", command = self._changeReport)
        self.filemenu.add_command(label = "Save", command = self._savePressed)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.delegate.close)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        #Added menu to go back to the launchpad
        navMenu = Menu(self.menubar, tearoff=0)
        navMenu.add_command(label = "Return To Start", command = self._toLaunch)
        self.menubar.add_cascade(label = "Nav", menu=navMenu)
        
    def _toLaunch(self):
        self.delegate.switchToLaunchpad(self)
        
    def _changeReport(self):
        nfile = self.delegate.getNessusFile()
        if nfile:
            self.setNessusFile(nfile)
        
    def _initReports(self):
        self.reports = CFrame(master = self.mainFrame)
        self.reports.rowconfigure(1, weight = 1)
        self.reports.columnconfigure(0, weight = 1)
        self.reports.reportL = CLabel(master = self.reports, text = "Available reports:")
        self.reports.reportL.grid(row = 0, column = 0, sticky = "NSW")
        self.reports.reportsList = CListBox(master = self.reports, selectmode = Tkinter.SINGLE, exportselection=0)
        self.reports.reportsList.bind("<ButtonRelease-1>", self._reportSelected)
        self.reports.reportsList.grid(row = 1, column = 0, sticky = "NEWS")
        scrollBar = Scrollbar(master = self.reports)
        self.reports.reportsList.config(yscrollcommand=scrollBar.set)
        scrollBar.config(command=self.reports.reportsList.yview)
        scrollBar.grid(row = 1, column = 1, sticky = "NSW")
        self.reports.grid(row = 0, column = 0, sticky = "NEWS")
        self._reportSelected()
        
    def getSelectedReport(self):
        '''
        Returns the report that is currently selected in the listbox, or None
        if nothing is selected.
        
        Returns:
            The selected report (String) name.
        '''
        if self.reports.reportsList.curselection():
            selected = self.reports.reportsList.curselection()[0]
            return self.reports.reportsList.get(selected, selected)[0]
        return None
        
    def _reportSelected(self, event = None):
        report = self.getSelectedReport()
        if not report:
            self._enableSave(False)
            return
        self.setDescription(self.reportDict[report].getDescription())
        self.setOutputText(getExample(self.getSelectedReport()))
        self._enableSave(True)
        
    def _enableSave(self, isEnabled):
        '''
        Enables or disables the "Save" menu item per the given isEnabled boolean value.  If isEnabled
        is True, then the menu item is enabled.  This will also enable/disable the bound save command
        accordingly.
        
        Args:
            isEnabled (boolean):  Whether or not to disable the save menu command.
        '''
        if isEnabled:
            self.filemenu.entryconfig(ReportsView.SAVE_INDEX, state = Tkinter.NORMAL)
            self.root.bind("<Control-s>", self._savePressed)
        else:
            self.filemenu.entryconfig(ReportsView.SAVE_INDEX, state = Tkinter.DISABLED)
            self.root.bind("<Control-s>", self._ignore)
            
    def _ignore(self, event = None):
        return "break"
        
    def setReports(self, reps):
        '''
        Sets the selectable reports.
        
        Args:
            reps ([String]):  The list of reports that can be selected.
        '''
        self.reports.reportsList.delete(0, Tkinter.END)
        for report in reps:
            self.reports.reportsList.insert(Tkinter.END, report)
            
    def _initDescription(self):
        self.desc = CFrame(master = self.mainFrame)
        self.desc.rowconfigure(1, weight = 1)
        self.desc.columnconfigure(0, weight = 1)
        self.desc.label = CLabel(master = self.desc, text = "Report Description:")
        self.desc.label.grid(row = 0, column = 0, sticky= "NWS")
        self.desc.text = CText(master = self.desc, state = Tkinter.DISABLED)
        self.desc.text.grid(row = 1, column = 0, sticky = "NEWS")
        scrollBar = Scrollbar(master = self.desc)
        self.desc.text.config(yscrollcommand=scrollBar.set)
        scrollBar.config(command=self.desc.text.yview)
        scrollBar.grid(row = 1, column = 1, sticky = "NSW")
        self.desc.grid(row = 2, column = 0, sticky = "NEWS")
        
    def setDescription(self, text):
        '''
        Sets the content of the description box in the view.
        
        Args:
            text (String):  The description.
        '''
        self.desc.text.config(state = Tkinter.NORMAL)
        self.desc.text.delete(1.0, Tkinter.END)
        self.desc.text.insert(Tkinter.END, text)
        self.desc.text.config(state = Tkinter.DISABLED)
        
    def add(self):
        '''
        Adds this view to the pre-set master frame.
        '''
        self.mainFrame.grid(row = 0, column = 0, sticky = "NEWS")
        self.delegate.setMenuBar(self.menubar)
        
    def remove(self):
        '''
        Removes this view from the pre-set master frame.
        '''
        self.mainFrame.grid_remove()
        self.delegate.clearMenuBar()
        
    def setNessusFile(self, nFile):
        '''
        Takes the path to a .nessus file to set up in this gui.
        
        Args:
            nFile (String): The absolute path to a .nessus file to use
                            in creating this ad-hoc report.
        '''
        self.reportDict = loadReports()
        self.delegate.setSubTitle(nFile)
        self.setReports(self.reportDict.keys())
        self.setDescription("")
        self.setOutputText("")
        
    def _initPadding(self):
        f = CFrame(master = self.mainFrame)
        f.grid(row = 0, column = 1, padx = ReportsView.PADX)
        f2 = CFrame(master = self.mainFrame)
        f2.grid(row = 1, column = 0, pady = ReportsView.PADY)
        
    def _initOutput(self):
        self.out = CFrame(master = self.mainFrame)
        self.out.columnconfigure(0, weight = 1)
        self.out.rowconfigure(1, weight = 1)
        self.out.label = CLabel(master = self.out, text = "Example Output:")
        self.out.label.grid(row = 0, column = 0, sticky = "SWE")
        self.out.text = CText(master = self.out, state = Tkinter.DISABLED)
        self.out.text.grid(row = 1, column = 0, sticky = "NEWS")
        scrollBar = Scrollbar(master = self.out)
        self.out.text.config(yscrollcommand=scrollBar.set)
        scrollBar.config(command=self.out.text.yview)
        scrollBar.grid(row = 1, column = 1, sticky = "NSW")
        self.out.grid(row = 0, column = 2, rowspan = 3, sticky = "NEWS")
        
    def setOutputText(self, text):
        '''
        Sets the content of the example output box.
        
        Args:
            text (String):  The example output.
        '''
        self.out.text.config(state = Tkinter.NORMAL)
        self.out.text.delete(1.0, Tkinter.END)
        self.out.text.insert(Tkinter.END, text)
        self.out.text.config(state = Tkinter.DISABLED)
        
    def _savePressed(self, event = None):
        report = self.getSelectedReport()
        if not report:
            return
        saveLoc = self._getOutputName()
        if not saveLoc:
            return
        writeReport(self.nessusFile, saveLoc, report)
    
    def _getOutputName(self):
        return asksaveasfilename()
        