'''
.. module:: CEmailFrame
   :platform: Unix
   :synopsis: This module defines the CEmailFrame class 

.. moduleauthor:: Daniel Chee
'''
import Tkinter

from gui.cGui.widgets.CFrame import CFrame
from gui.cGui.widgets.CListBox import CListBox
from gui.cGui.widgets.CButton import CButton
from gui.cGui.widgets.CText import CText
from CIVEntry import CIVEntry
from CIVText import CIVText

from ReportFramework.ReportFramework import loadReports
from ReportFramework.ReportFramework import getExample

from ScanEvent.ScanEvent import fromString

from gui.cGui.widgets.CLabel import CLabel
from ScanEvent.ScanEvent import EmailItem

class CEmailFrame(CFrame):
    '''
    A Frame that allows the user of Cernent of add/edit/remove email items from the current scan event
    '''
    
    
    '''
    *************************************** INITIALIZATION ***********************************************
    '''
    def __init__(self, master, scanEventEditor, conf):
        '''
        Creates a new CEmailFrame.
        
        Args:
        
            master: The widget this frame will be attached to. 
            
            scanEventEditor: The event editor this frame is associated with. This is needed in 
                             order to track changes for dirty detection. 
        
        '''
        CFrame.__init__(self, master)
        self.items = []
        self.conf = conf
        self.scanEventEditor = scanEventEditor
        self.currentSelection = -1
        self.initialize()
    
    def initialize(self):
        '''
        This method initializes all of the widgets used by the email tab of the GUI
        '''
        self._createEmailItemListBox()
        self._viewEditEmailItem()
        self._addViewReports()
    
    def _createEmailItemListBox(self):
        '''
        This method initializes the first "1/3" of the email tab. This 
        includes the email item listbox as well as the add and remove buttons. 
        '''
        self.emailItemListBoxLabel = CLabel(master = self, text = "Email Items")
        self.emailItemListBoxLabel.config(bg="black", foreground="white", border=1, relief="raised")
        self.emailItemListBoxLabel.grid(row=0, column=0, sticky = "NEWS",pady=5, padx=10)
        
        self.emailItemListBox = CListBox(master = self)
        self.emailItemListBox.grid(row=1, column=0, rowspan = 5, sticky = "NEWS", pady=5, padx=10)
        self.emailItemListBox.bind("<ButtonRelease-1>", self._updateInformationEntryFrame)
        self.emailItemListBox.bind("<Return>", self._updateInformationEntryFrame)
        
        self.leftButtonFrame = CFrame(master = self)
        self.addButton = CButton(master = self.leftButtonFrame, text = "ADD", command=self._addEmailItem)
        self.addButton.grid(row = 0, column = 0, sticky="NEWS")
        self.removeButton = CButton(master = self.leftButtonFrame, text = "REMOVE", command=self._removeRecipient)
        self.removeButton.grid(row = 0, column = 1, sticky="NEWS")
        self.leftButtonFrame.grid(row=6, column=0, sticky = "NEWS",pady=5, padx=10)
        self.grid_columnconfigure(0,weight=1)
    
    def _viewEditEmailItem(self):
        '''
        This method initializes the part of the GUI where email items are viewed and edits
        are made. This includes everything except the email item listbox and the 
        reporting listboxes. 
        '''
        self.recipientLabel = CLabel(master = self, text = "EDIT EMAIL ITEM")
        self.recipientLabel.grid(row=0, column=1, sticky = "NEWS",pady=5, padx=10)
        
        self.nameEntry = CIVEntry(self, "< NAME >", self)
        self.nameEntry.grid(row=1, column=1, sticky = "NEWS",pady=5, padx=10)
        
        self.emailEntry = CIVEntry(self, "< RECIPIENT ADDRESSES >", self)
        self.emailEntry.grid(row=2, column=1, sticky = "NEWS", pady=5, padx=10)
        
        self.subjectEntry = CIVEntry(self, "< SUBJECT >", self)
        self.subjectEntry.grid(row=3, column=1, sticky = "NEWS", pady=5,padx=10)
        
        self.bodyEntry = CIVText(self, "< MESSAGE BODY >", self)
        self.bodyEntry.grid(row=5, column=1, rowspan = 1, sticky = "NEWS", padx=5, pady=10)
        
        self.grid_columnconfigure(1,weight=1)
        
        self._disableEntries()
    
    
    def _addViewReports(self):
        '''
        '''
        self.availableReportLabel = CLabel(master = self, text = "Available Reports")
        self.availableReportLabel.config(border=1, relief="raised")
        self.availableReportLabel.grid(row = 0, column = 2, sticky = "NEWS", pady = 5, padx = 5)
        self.availableReportListBox = CListBox(master = self)
        self.availableReportListBox.config(selectmode='extended')
        self.availableReportListBox.grid(row=1, column=2, rowspan = 3, sticky = "NEWS", pady=5, padx=5)
        self.availableReportButtonFrame = CFrame(master = self)
        self.includeReportsButton = CButton(master = self.availableReportButtonFrame, text = "Include", command = self._includeReports)
        self.includeReportsButton.grid(row = 0, column = 0, sticky = "NEWS")
        self.previewReportsButton = CButton(master = self.availableReportButtonFrame, text = "Preview", command = self._previewReport)
        self.previewReportsButton.grid(row = 0, column = 1, sticky = "NEWS")
        self.availableReportButtonFrame.grid(row = 4, column = 2, sticky = "NEWS", pady=5, padx=5)
        
        self.reportDict = loadReports()
        for key in self.reportDict.keys():
            self.availableReportListBox.insert(Tkinter.END, key)
        
        
        self.includedReportFrame = CFrame(master = self)
        self.includedReportLabel = CLabel(master = self.includedReportFrame, text = "Included Reports")
        self.includedReportLabel.config(border=1, relief="raised")
        self.includedReportLabel.grid(row = 0, column = 0, sticky = "NEWS", pady = 5, padx = 5)
        self.includedReportListBox = CListBox(master = self.includedReportFrame)
        self.includedReportListBox.config(selectmode='extended')
        self.includedReportListBox.bind("<FocusOut>", self._saveReports)
        self.includedReportListBox.grid(row=1, column=0, sticky = "NEWS", pady=5, padx=5)
        self.removeIncludedReportsButton = CButton(master = self.includedReportFrame, text = "Remove", command = self._removeIncludedReports)
        self.removeIncludedReportsButton.grid(row = 2, column = 0, sticky = "W")
        self.includedReportFrame.grid(row = 5, column = 2, sticky = "NEWS", pady = 5, padx = 5)
        
        self.testButtonFrame = CFrame(master = self)
        self.testEmailItemButton = CButton(master = self.testButtonFrame, text = "Test Email Item", command = self._testEmailItem)
        self.testEmailItemButton.grid(row = 0, column = 0, sticky = "NEWS")
        self.testButtonFrame.grid(row = 6, column = 2, sticky = "NEWS", pady = 5, padx = 5)
        
        
        
        
        
    '''
    *************************************** ACTION METHODS ***********************************************
    '''

    def _updateInformationEntryFrame(self, event):
        '''
        '''
        for selection in self.emailItemListBox.curselection():
            self.currentSelection = int(selection)
            item = self.items[int(selection)]
            self._enableEntries()
            self.nameEntry.configure(textvariable = item.getVar(EmailItem.NAME))
            self.emailEntry.configure(textvariable = item.getVar(EmailItem.TOADDRESSES))
            self.subjectEntry.configure(textvariable = item.getVar(EmailItem.SUBJECT))
            self.bodyEntry.setTextVar(item.getVar(EmailItem.BODY))
            self._updateIncludedReportsListBox(item.get(EmailItem.REPORTLIST))
            
            
    def _updateIncludedReportsListBox(self, reportList):
        '''
        '''
        self.includedReportListBox.delete(0, Tkinter.END)
        for report in reportList:
            self.includedReportListBox.insert(Tkinter.END, report)
    
    def _saveReports(self, trash):
        '''
        '''
        self._saveEntry()
    
    
    def _addEmailItem(self):
        '''
        '''
        self._enableEntries()
        newItem = EmailItemWrapper(["< NAME >", "< RECIPIENT ADDRESSES >", "< SUBJECT >", "< MESSAGE BODY >", []], self)
        self.nameEntry.setTextVar(newItem.getVar(EmailItem.NAME))
        self.emailEntry.setTextVar(newItem.getVar(EmailItem.TOADDRESSES))
        self.subjectEntry.setTextVar(newItem.getVar(EmailItem.SUBJECT))
        self.bodyEntry.setTextVar(newItem.getVar(EmailItem.BODY))
        self.items.append(newItem)
        self._updateEmailItemsListBox()
        self._updateIncludedReportsListBox(newItem.get(EmailItem.REPORTLIST))
        self.emailItemListBox.selection_set(Tkinter.END)
        self.currentSelection = (int)(self.emailItemListBox.curselection()[0])
        
        
    def _updateEmailItemsListBox(self):
        '''
        '''
        self.emailItemListBox.delete(0, Tkinter.END)
        for item in self.items:
            if(item.get(EmailItem.NAME) == "< NAME >"):
                self.emailItemListBox.insert(Tkinter.END, "New Entry")    
            else:
                self.emailItemListBox.insert(Tkinter.END, item.get(EmailItem.NAME))    
    
        
        
    def _removeRecipient(self):
        '''
        '''
        for selection in self.emailItemListBox.curselection():
            self.emailItemListBox.delete(selection)
            self.items.pop(int(selection))
        self.nameEntry.textvar.set("...")
        self.nameEntry.config(textvariable = self.nameEntry.textvar)
        self.emailEntry.textvar.set("...")
        self.emailEntry.config(textvariable = self.emailEntry.textvar)
        self.subjectEntry.textvar.set("...")
        self.subjectEntry.config(textvariable = self.subjectEntry.textvar)
        self.bodyEntry.delete("1.0", Tkinter.END)
        self.body = "..."
        self.bodyEntry.insert("1.0", self.body)
        self.disableEntries()
        
    def _saveEntry(self):
        '''
        '''
        if(self.currentSelection >= 0):
            item = self.items[self.currentSelection]
            if(item.update(self.includedReportListBox.get(0, Tkinter.END))):
                self.scanEventEditor.changeMade()
            self.emailItemListBox.delete(self.currentSelection)
            if(item.get(EmailItem.NAME) == "< NAME >"):
                self.emailItemListBox.insert(self.currentSelection, "New Entry")
            else:
                self.emailItemListBox.insert(self.currentSelection, item.get(EmailItem.NAME))
    
    def _disableEntries(self):
        '''
        '''
        self.nameEntry.configure(state="disabled")
        self.emailEntry.configure(state="disabled")
        self.subjectEntry.configure(state="disabled")
        self.bodyEntry.configure(state="disabled")
    
    def _enableEntries(self):
        '''
        '''
        self.nameEntry.configure(state="normal")
        self.emailEntry.configure(state="normal")
        self.subjectEntry.configure(state="normal")
        self.bodyEntry.configure(state="normal")
        
    def clearFrame(self):
        '''
        '''
        self.emailItemListBox.delete(0, Tkinter.END)
        self.name.set("...")
        self.email.set("...")
        self.subject.set("...")
        self.bodyEntry.delete("1.0", Tkinter.END)
        self.body = "..."
        self.bodyEntry.insert("1.0", self.body)
        for value in self.reportValues:
                value.set(0)
        
    def _removeIncludedReports(self):
        '''
        '''
        for item in self.includedReportListBox.curselection():
            self.includedReportListBox.delete(item)
        
    def _includeReports(self):
        '''
        '''
        for item in self.availableReportListBox.selection_get().split('\n'):
            include = True
            for x in self.includedReportListBox.get(0, Tkinter.END):
                if (item == x):
                    include = False
            if(include):
                self.includedReportListBox.insert(Tkinter.END, item)
                self.includedReportListBox.focus_set()
    
    def _previewReport(self):
        '''
        '''
        window = Tkinter.Toplevel()
        window.title("Preview")
        frame = CFrame(master = window)
        label = CLabel(master = frame, text = self.availableReportListBox.get('active'))
        label.grid(row = 0, column = 0, sticky = "NEWS", padx = 5, pady = 5)
        
        textFrame = CFrame(master = frame, width=100, height=24)
        scrollbar = Tkinter.Scrollbar(textFrame)
        scrollbar.pack(side='right', fill='y')
        text = CText(master = textFrame)
        text.pack(side='left', fill='y')
        scrollbar.config(command = text.yview)
        text.config(yscrollcommand=scrollbar.set)
          
        textFrame.grid(row = 1, column = 0, sticky = "NEWS", padx = 5, pady = 5)
        text.insert("1.0", getExample(self.availableReportListBox.get('active')))
        frame.grid(row = 0, column = 0, sticky = "NEWS")
        
        
    def _testEmailItem(self):
        self.mail = self.conf['mailer']
        pass
        
        
    def getEmailItems(self):
        '''
        Returns a list of email items that are contained in the currently-being-edited ScanEvent.
        
        returns: 
            a list of email items.
             
        '''
        itemlist = []
        for item in self.items:
            itemlist.append(EmailItem(item.getInfo()))
        return itemlist

    def setEmailItems(self, emailItemList):
        '''
        Updates the GUI to reflect the EmailItems contained in an already existing 
        ScanEvent. 
        
        Args:
            emailItemList: A list of the EmailItems contained in the current ScanEvent. 
        
        '''
        for item in emailItemList:
            self.items.append(EmailItemWrapper(item.getContents(), self))
        for item in self.items:
            self.emailItemListBox.insert(Tkinter.END, item.get(EmailItem.NAME))
        
        
        
'''
*************************************** CLASS DEFINITIONS ***********************************************
'''
             
class EmailItemWrapper(): 
    '''
    A wrapper class that encapsulates the contents of an email item in Tkinter.StringVars 
    for easy dirty detecion.     
    '''
    
    def __init__(self, contents, emailFrame):
        '''
        Creates an new EmailItemWrapper. 
        
        Args:
        
            contents: The contents (array) of the email item to be "wrapped".
            
            emailFrame: The CEmailFrame that this instance is associated with. 
            
        '''
        self.info = contents
        self.emailFrame = emailFrame
        self.name = Tkinter.StringVar()
        self.name.set(self.info[EmailItem.NAME])
        self.emails = Tkinter.StringVar()
        self.emails.set(self.info[EmailItem.TOADDRESSES])
        self.subject = Tkinter.StringVar()
        self.subject.set(self.info[EmailItem.SUBJECT])
        self.body = Tkinter.StringVar()
        self.body.set(self.info[EmailItem.BODY])
      
    def update(self, reports):
        '''
        This method updates the information contained in this wrapper to the values contained in the 
        String vars. Also updates the report list to the input report list. 
        
        Args:
        
            reports: The updated report list. 
        
        '''
        ans = False
        if(self.info[EmailItem.NAME] != self.name.get()):
            self.info[EmailItem.NAME] = self.name.get()
            ans = True
        if(self.info[EmailItem.TOADDRESSES] != self.emails.get()):
            self.info[EmailItem.TOADDRESSES] = self.emails.get()
            ans = True
        if(self.info[EmailItem.SUBJECT] != self.subject.get()):
            self.info[EmailItem.SUBJECT] = self.subject.get()
            ans = True
        if(self.info[EmailItem.BODY] != self.body.get()):
            self.info[EmailItem.BODY] = self.body.get()
            ans = True
        if(str(self.info[EmailItem.REPORTLIST]) != str(reports)):
            self.info[EmailItem.REPORTLIST] = reports
            ans = True 
        return ans
        
    def get(self, i):
        '''
        Returns the value assiciated with the given field. 
        
        returns:
            value of the string variable associated with the given field. 
        '''
        if(i == EmailItem.NAME):
            return self.info[EmailItem.NAME]
        elif(i == EmailItem.TOADDRESSES):
            return self.info[EmailItem.TOADDRESSES]
        elif(i == EmailItem.SUBJECT):
            return self.info[EmailItem.SUBJECT]
        elif(i == EmailItem.BODY):
            return self.info[EmailItem.BODY]
        elif(i == EmailItem.REPORTLIST):
            return self.info[EmailItem.REPORTLIST]
        else:
            pass
    
    def getVar(self, i):
        '''
        Returns the Tkinter.StringVar associated with the given entry field. 
        
        returns:
        
            var: the string variable associated with the given entry field. 
        
        '''                   
        if(i == EmailItem.NAME):
            return self.name
        elif(i == EmailItem.TOADDRESSES):
            return self.emails
        elif(i == EmailItem.SUBJECT):
            return self.subject
        elif(i == EmailItem.BODY):
            return self.body
        elif(i == EmailItem.REPORTLIST):
            pass
            #return self.reportList
        else:
            pass
        
    def getInfo(self):
        '''
        This method returns the information contained in an EmailItemWrapper instance, 
        which can be used to create an instance of an email item with containing that information.
        
        returns: 
        
            info: an array containing the information contained. 
            
        '''
        return self.info
            
    
    '''
    *************************************** MAIN METHOD (for testing purposes) ***********************************************
    '''
               
if __name__ == "__main__":
    test = Tkinter.Tk()
    test.title("Test")
    frame = CEmailFrame(test, None)
    frame.setEmailItems(fromString("['admin', 'admin1@foo.com, admin2@bar.com', 'reports', u'Here are the reports.\\n', ['Concise', 'JavaJRE']]^['exec', 'exec1@foo.com, exec2@bar.com', 'report', u'Here is the report\\n', ['Credentialed']]\n"), None, None)
    frame.grid(row = 0, column = 0)
    test.mainloop()


 
    
    