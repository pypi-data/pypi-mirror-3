"""
.. module:: Launchpad
   :platform: Unix
   :synopsis: The first view of the gui, allowing selection of what
              you want to do.

.. moduleauthor:: Brian Kraus


"""

from cernentd import daemonRunning 
from gui.cGui.widgets.CFrame import CFrame
from gui.cGui.widgets.CButton import CButton
from gui.cGui.widgets.CLabel import CLabel


class Launchpad(object):
    '''
    This is the first pane that the user sees when opening the gui,
    and allows them to select between editing
    ScanEvents or managing reports.
    '''
    D_ON_TEXT = "Daemon is: running"
    D_OFF_TEXT = "Daemon is: dead"
    START = "Start"
    STOP = "Stop"
    '''
    Preferred dimensions for the window showing this.
    '''
    WIDTH = 250
    HEIGHT = 175

    def _initScanEditButton(self):
        self.edit = CButton(master = self.masterFrame, text="Edit Scan Event",
                             command=self._scanEditPressed)
        self.edit.grid(row=0, column=0, sticky="NEW")
        
    def _scanEditPressed(self, event = None):
        self.delegate.switchToScanEventsEdit(self)
        
    def _initScanNewButton(self):
        self.new = CButton(master = self.masterFrame, text="New Scan Event",
                           command=self._scanNewPressed)
        self.new.grid(row=1, column=0, sticky="NEW")
        
    def _scanNewPressed(self, event = None):
        self.delegate.switchToScanEventsNew(self)
        
    def _initReportButton(self):
        self.report = CButton(master=self.masterFrame, text="Reports",
                              command=self._reportPressed)
        self.report.grid(row=2,column=0, sticky="NEW")
        
    def _reportPressed(self, event = None):
        self.delegate.switchToReports(self)

    def _initWidgets(self):
        self._initScanEditButton()
        self._initScanNewButton()
        self._initReportButton()
        self._initDaemonIndicator()
        
    def _initDaemonIndicator(self):
        self.dcon = CFrame(master = self.masterFrame)
        self.dcon.columnconfigure(0, weight=1)
        self.dcon.rowconfigure(0, weight=1)
        self.dcon.activeL = CLabel(master = self.dcon, text = Launchpad.D_OFF_TEXT)
        self.dcon.activeL.grid(row = 0, column = 0, sticky="SWE")
        self.dcon.grid(row=4, column = 0, sticky="SWE")
        self._setDaemonState()
        
    def _setDaemonState(self):
        isRunning = self._isDaemonRunning()
        if isRunning:
            self.dcon.activeL.config(text = Launchpad.D_ON_TEXT, foreground="green")
        else:
            self.dcon.activeL.config(text = Launchpad.D_OFF_TEXT, foreground="red")

    def _isDaemonRunning(self):
        return daemonRunning()

    def __init__(self, master, delegate, conf):
        '''
        Initialized the launchpad.
        
        Args:
            master (Frame):  The Frame for this view to add itself to.
            
            delegate (CGuiController): The controller to delegate this view.
            
            conf (dict):     The cernent configuration dict required for daemon
                             control.
        '''
        self.conf = conf
        self.delegate = delegate
        self.masterFrame = CFrame(master, width = delegate.WIDTH, height = delegate.HEIGHT, border=2)
        self.masterFrame.columnconfigure(0, weight=1)
        self.masterFrame.rowconfigure(3, weight=1)
        self._initWidgets()
        
    def add(self):
        '''
        Adds this view to the pre-configured master frame.
        '''
        self.masterFrame.grid(row = 0, column = 0, sticky="NESW")
        
    def remove(self):
        '''
        Removes this view from the pre-configured master frame.
        '''
        self.masterFrame.grid_remove()
        