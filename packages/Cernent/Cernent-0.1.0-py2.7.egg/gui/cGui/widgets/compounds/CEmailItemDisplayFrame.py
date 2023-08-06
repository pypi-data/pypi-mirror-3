'''
Created on Apr 24, 2012

@author: Anarchee
'''
from gui.cGui.widgets.CFrame import CFrame
from gui.cGui.widgets.CLabel import CLabel
from gui.cGui.widgets.CButton import CButton
from gui.cGui.widgets.CListBox import CListBox
from gui.cGui.widgets.CEntry import CEntry
from gui.cGui.widgets.CText import CText
from deliveryMethod.Mailer import Mailer
from ScanEvent.ScanEvent import EmailItem

from ReportFramework.ReportFramework import loadReports
from ReportFramework.ReportFramework import getExample

import Tkinter
import re

class CEmailItemDisplayFrame(CFrame):
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
        self.currentItem = []
        self.conf = conf
        self._setDefaultValues(conf)
        self._initializeEntryFrame()
        self._initializeReportFrame()
#        self._updateGUI()
        
    def _setDefaultValues(self, conf):
        self.defaultSubject = conf['subject']
        self.defaultMessage = conf['message']
        self.mailer = conf['mailer']
    
    def _initializeEntryFrame(self):
        fs = [("<FocusOut>", self._isEmailValid)]
        self._createCLabel("EDIT EMAIL ITEM", 0, 0, xPad= 10, yPad = 5)
        self.name = self._createEntry(1, 0, xPad = 10, yPad = 5, funcs = fs)
        self.emails = self._createEntry(2, 0, xPad = 10, yPad = 5, funcs = fs)
        self.subject = self._createEntry(3, 0, xPad = 10, yPad = 5, funcs = fs)
        self.text = self._createTextbox(4, 0, rowSpan = 4, xPad = 10, yPad = 5, funcs = fs)
        self.grid_columnconfigure(1,weight=1)
        
    def _initializeReportFrame(self):
        self._createCLabel("Available Reports", 0, 1, xPad = 10, yPad = 5)
        self.availableReports = self._createListbox(1, 1, rowSpan = 3, xPad = 10, yPad = 5)
        for key in loadReports().keys():
            self.availableReports[1].append(key)
            self.availableReports[0].insert(Tkinter.END, key)
            
        self._createButtonFrame(4, 1, rowSpan = 1, xPad = 5, yPad = 5, buttons = ["Include", "Preview"], cmd = [self._includeReports, self._previewReport])
            
        self._createCLabel("Included Reports", 5, 1, xPad = 10, yPad = 5)
        self.includedReports = self._createListbox(6, 1, rowSpan = 1, xPad = 10, yPad = 5)
        self._createButtonFrame(7, 1, rowSpan = 1, xPad = 5, yPad = 5, buttons = ["Test Email(s)"], cmd = [self._testEmailItem])
        
        
    def _createCLabel(self, inText, r, c, xPad = 5, yPad = 5):
        newLabel = CLabel(master = self, text = inText)
        newLabel.grid(row=r, column=c, sticky = "NEW", pady=yPad, padx=xPad)
        return newLabel
        
    def _createEntry(self, r, c, xPad = 5, yPad = 5, funcs = []):
        entryVar = Tkinter.StringVar()
        entry = CEntry(master = self, textvariable = entryVar)
        entry.grid(row=r, column=c, sticky = "NEWS", pady=yPad, padx=xPad)
        if funcs:
            for func in funcs:
                entry.bind(func[0], func[1])
        return entry, entryVar
        
    def _createTextbox(self, r, c, rowSpan, xPad = 5, yPad = 5, funcs = []):
        textbox = CText(master = self)
        textbox.grid(row = r, column = c, rowspan = rowSpan, sticky = "NEWS", pady=yPad, padx=xPad)
        if funcs:
            for func in funcs:
                textbox.bind(func[0], func[1])
        return textbox
        
    def _createListbox(self, r, c, rowSpan = 1, xPad = 5, yPad = 5, funcs = [], mode = 'extended'):
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
        
    def _newItem(self):
        pass
        
    def _includeReports(self):
        pass
    
    def _previewReport(self):
        window = Tkinter.Toplevel()
        window.title("Preview")
        frame = CFrame(master = window)
        label = CLabel(master = frame, text = self.availableReports[0].get('active'))
        label.grid(row = 0, column = 0, sticky = "NEWS", padx = 5, pady = 5)
        
        textFrame = CFrame(master = frame, width=100, height=24)
        scrollbar = Tkinter.Scrollbar(textFrame)
        scrollbar.pack(side='right', fill='y')
        text = CText(master = textFrame)
        text.pack(side='left', fill='y')
        scrollbar.config(command = text.yview)
        text.config(yscrollcommand=scrollbar.set)
          
        textFrame.grid(row = 1, column = 0, sticky = "NEWS", padx = 5, pady = 5)
        text.insert("1.0", getExample(self.availableReports[0].get('active')))
        frame.grid(row = 0, column = 0, sticky = "NEWS")
    
    def _removeIncludedReports(self):
        pass
    
    def _testEmailItem(self):
        if self.currentItem:
            emailItem  = EmailItem(self.currentItem)
            self.mailer.testEmailItem(emailItem)
        else:
            pass
            
    def _loadItem(self, item):
        pass
        #if self.currentItem:
        #    pass
        #else:
        #    pass
        
    def _saveEmailItem(self):
        self.currentItem[0] = self.name[1].get()
        self.currentItem[1] = self.emails[1].get()
        self.currentItem[2] = self.subject[1].get()
        self.currentItem[3] = self.text.get("1.0", Tkinter.END).strip()
        self.currentItem[4] = self.includedReports.get(0, Tkinter.END)
        
    def _checkForChange(self, dsfa):
        if(self.name[1].get() != self.currentItem[0]):
            print "1"
            #return True
        if(self.emails[1].get() != self.currentItem[1]):
            print "2"
            #return True
        if(self.subject[1].get() != self.currentItem[2]):
            print "3"
            #return True
        if(self.text.get("1.0", Tkinter.END).strip() != self.currentItem[3].strip()):
            print "4"
            #return True
        pass
        #return False
        
    def _updateGUI(self):
        if not self.currentItem[0]:
            self.currentItem[0] = "< New Item >"
        if not self.currentItem[1]:
            self.currentItem[1] = "< Input Addresses Here >"
        if not self.currentItem[2]:
            self.currentItem[2] = self.conf['subject']
        if not self.currentItem[3]:
            self.currentItem[3] = self.conf['message']
        self.name[1].set(self.currentItem[0])
        self.emails[1].set(self.currentItem[1])
        self.subject[1].set(self.currentItem[2])
        self.text.delete("1.0", Tkinter.END)
        self.text.insert("1.0", self.currentItem[3])
        self.includedReports[0].delete(0, Tkinter.END)
        for report in self.currentItem[4]:
            self.includedReports[0].insert(Tkinter.END, report)
            
        for report in self.includedReports[1]:
            self.includedReports[0].insert(Tkinter.END, report)
    
    def _isEmailValid(self, event):
        for addr in self.emails[1].get().split(","):
            if not re.match(r"[^@]+@[^@]+\.[^@]+", addr):
                print "The email is not valid"
                pass 
    
    def clearEntries(self):
        self.currentItem = None
        self.name[1].set('...')
        self.emails[1].set('...')
        self.subject[1].set('..')
        self.text.delete("1.0", Tkinter.END)
        self.text.insert("1.0", '...')
        self._disableEntries()
    
    def _disableEntries(self):
        '''
        '''
        self.name[0].configure(state="disabled")
        self.emails[0].configure(state="disabled")
        self.subject[0].configure(state="disabled")
        self.text.configure(state="disabled")
    
    def _enableEntries(self):
        '''
        '''
        self.name[0].configure(state="normal")
        self.emails[0].configure(state="normal")
        self.subject[0].configure(state="normal")
        self.text.configure(state="normal")
    
    def setItem(self, newItem):
        self._enableEntries()
        self._saveEmailItem()
        self.currentItem = newItem
        self._updateGUI()
    
    def getItem(self):
        self._saveEmailItem()
        return self.currentItem
    
if __name__ == "__main__":
    test = Tkinter.Tk()
    test.title("Test")
    #frame = CEmailItemDisplayFrame(test, [], {'mailer': Mailer('cernentteam@gmail.com', 'cernentteam@gmail.com', 'smtp.gmail.com', '587', smtpUser='cernentteam', smtpPass='Coffee.Eat.Rope'), 'examplePath': '/opt/cernent/resources/example.nessus', 'archivePath': '/opt/cernent/archive/', 'administrators': 'dchee7@unm.edu', 'reportPath': '/opt/cernent/reports/', 'message': 'Hello,\n\nAttached are the vulnerability reports requested.\n\nRegards,\nIT Security Department\n', 'scanners': {'Main Scanner': ['127.0.0.1', 8834, 'bob', 'bob']}, 'subject': '-= Vulnerability Report =-'})
    frame = CEmailItemDisplayFrame(test, ['admin', 'admin1@foo.com, admin2@bar.com', 'reports', u'Here are the reports.\\n', ['Concise', 'JavaJRE']], {'mailer': Mailer('cernentteam@gmail.com', 'cernentteam@gmail.com', 'smtp.gmail.com', '587', smtpUser='cernentteam', smtpPass='Coffee.Eat.Rope'), 'examplePath': '/opt/cernent/resources/example.nessus', 'archivePath': '/opt/cernent/archive/', 'administrators': 'dchee7@unm.edu', 'reportPath': '/opt/cernent/reports/', 'message': 'Hello,\n\nAttached are the vulnerability reports requested.\n\nRegards,\nIT Security Department\n', 'scanners': {'Main Scanner': ['127.0.0.1', 8834, 'bob', 'bob']}, 'subject': '-= Vulnerability Report =-'})
    #frame.setEmailItems(fromString([['admin', 'admin1@foo.com, admin2@bar.com', 'reports', u'Here are the reports.\\n', ['Concise', 'JavaJRE']]^['exec', 'exec1@foo.com, exec2@bar.com', 'report', u'Here is the report\\n', ['Credentialed']]]), None, None)
    frame.grid(row = 0, column = 0)
    test.mainloop()