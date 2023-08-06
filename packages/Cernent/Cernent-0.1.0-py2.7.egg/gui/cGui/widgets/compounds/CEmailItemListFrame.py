'''
Created on Apr 27, 2012

@author: Anarchee
'''

from gui.cGui.widgets.CFrame import CFrame
from gui.cGui.widgets.CLabel import CLabel
from gui.cGui.widgets.CButton import CButton
from gui.cGui.widgets.CListBox import CListBox
from ScanEvent.ScanEvent import fromString
from ScanEvent.ScanEvent import EmailItem
from deliveryMethod.Mailer import Mailer
from CEmailItemDisplayFrame import CEmailItemDisplayFrame
import Tkinter


class CEmailItemListFrame(CFrame):
    '''
    A Frame that allows the user of Cernent of add/edit/remove email items from the current scan event
    '''
    
    
    '''
    *************************************** INITIALIZATION ***********************************************
    '''
    def __init__(self, master, conf):
        '''
        Creates a new CEmailFrame.
        
        Args:
        
            master: The widget this frame will be attached to. 
            
            scanEventEditor: The event editor this frame is associated with. This is needed in 
                             order to track changes for dirty detection. 
        
        '''
        CFrame.__init__(self, master)
        self._initialize(conf)
       
    def _initialize(self, conf):
        self.emailItemList = []
        self.currentSelection = -1
        self._createCLabel("Email Items", 0, 0, xPad = 5, yPad = 5)
        fs = [("<ButtonRelease-1>", self._listboxSelection)]
        self.listbox = self._createListbox(1, 0, rowSpan = 1, xPad = 5, yPad = 5, funcs = fs)
        self._createButtonFrame(2, 0, buttons = ["Add", "Remove"], cmd = [self._addEmailItem, self._removeEmailItem])
        self.displayFrame = CEmailItemDisplayFrame(self, conf)
        self.displayFrame.grid(row = 0, column = 1, rowspan = 7)
        self._updateGUI()
       
    def _createCLabel(self, inText, r, c, xPad = 5, yPad = 5):
        newLabel = CLabel(master = self, text = inText)
        newLabel.grid(row=r, column=c, sticky = "EWS", pady=yPad, padx=xPad)
        return newLabel   
    
    def _createListbox(self, r, c, rowSpan = 1, xPad = 5, yPad = 5, funcs = [], mode = 'normal'):
        listbox = CListBox(master = self)
        listbox.grid(row = r, column = c, rowspan = rowSpan, sticky = "NEWS", pady=yPad, padx=xPad)
        listbox.config(selectmode = mode)
        if funcs:
            for func in funcs:
                listbox.bind(func[0], func[1])
        return listbox, []
        
    def _createButtonFrame(self, r, c, rowSpan = 1, xPad = 5, yPad = 5, buttons = [], cmd = []):
        buttonFrame = CFrame(master = self)
        for i in range(len(buttons)):
            newButton = CButton(master = buttonFrame, text = buttons[i], command = cmd[i])
            newButton.grid(row = 0, column = i, sticky = "NEWS", pady=yPad, padx=xPad)
        buttonFrame.grid(row = r, column = c, rowspan = rowSpan, sticky = "NEWS", pady=yPad, padx=xPad)
        
    def _listboxSelection(self, event):
        if self.currentSelection >= 0:
            self.emailItemList[self.currentSelection] = self.displayFrame.getItem()
        self.currentSelection = int(self.listbox[0].curselection()[0])
        newItem = self.emailItemList[int(self.listbox[0].curselection()[0])]
        self.displayFrame.setItem(newItem)
        
    def _addEmailItem(self):
        self.currentSelection = len(self.emailItemList)
        self.listbox[0].insert(Tkinter.END, '< New Item >')
        self.emailItemList.append(['', '', '', '', []])
        self.displayFrame.setItem(self.emailItemList[0])
        
    def _removeEmailItem(self):
        for selection in self.listbox[0].curselection():
            self.listbox[0].delete(selection)
            self.emailItemList.pop(int(selection))
        self.displayFrame.clearEntries()
            
    def _updateGUI(self):
        if not self.emailItemList:
            self._addEmailItem()
        
    def setEmailItems(self, emailItemList):
        for item in emailItemList:
            self.emailItemList.append(item.getContents())
        for item in self.emailItemList:
            self.listbox[0].insert(Tkinter.END, item[0])
        self._updateGUI()

if __name__ == "__main__":
    test = Tkinter.Tk()
    test.title("Test")
    frame = CEmailItemListFrame(test, {'mailer': Mailer('cernentteam@gmail.com', 'cernentteam@gmail.com', 'smtp.gmail.com', '587', smtpUser='cernentteam', smtpPass='Coffee.Eat.Rope'), 'examplePath': '/opt/cernent/resources/example.nessus', 'archivePath': '/opt/cernent/archive/', 'administrators': 'dchee7@unm.edu', 'reportPath': '/opt/cernent/reports/', 'message': 'Hello,\n\nAttached are the vulnerability reports requested.\n\nRegards,\nIT Security Department\n', 'scanners': {'Main Scanner': ['127.0.0.1', 8834, 'bob', 'bob']}, 'subject': '-= Vulnerability Report =-'})
    #frame.setEmailItems(fromString("['admin', 'admin1@foo.com, admin2@bar.com', 'reports', u'Here are the reports.\\n', ['Concise', 'JavaJRE']]^['exec', 'exec1@foo.com, exec2@bar.com', 'report', u'Here is the report\\n', ['Credentialed']]\n"))
    frame.grid(row = 0, column = 0, sticky = "NEWS")
    test.mainloop()