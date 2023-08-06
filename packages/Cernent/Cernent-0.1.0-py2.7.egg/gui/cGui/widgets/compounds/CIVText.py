'''
Created on Apr 24, 2012

@author: Anarchee
'''
import Tkinter
from gui.cGui.widgets.CText import CText
#from gui.cGui.widgets.compounds.CEmailFrame import CEmailFrame

class CIVText(CText):
    '''
    Just an Extension of Tkinter's Entry object for Cernent/Cerno that contains an intial text value. This 
    widget is specialized for the email frame because it makes up of the Tkinter.StringVars used by the EmailItemWrapper class. 
    '''
    
    def __init__(self, master, text, emailFrame, **cnf):
        '''
        Creates a new CIVText instance. 
        
        Vars:
            
            master: The master widget this widget is attached to.
            
            text: The initial text. 
            
            emailFrame: The CEmailFrame this widget is associated with. 
            
        '''
        #CText.__init__(self, master, cnf)
        CText.__init__(self, master)
        self.defaultText = text
        self.currentVar = Tkinter.StringVar()
        self.insert("1.0", "...")
        self.emailFrame = emailFrame
        self.bind("<Button-1>", self.firstClick)
        self.bind("<FocusOut>", self.focusOut)

    def firstClick(self, event):
        '''
        '''
        if(self.get("1.0", Tkinter.END).rstrip() == self.defaultText and self['state'] == Tkinter.NORMAL):
            self.delete("1.0", Tkinter.END)
    
    def setTextVar(self, textVar):
        '''
        Sets the input textvar as the active textvar for the text of the textbox. 
        
        Agrs:
        
            textVar: the new current active textvar. 
        
        '''
        self.currentVar = textVar
        self.delete("1.0", Tkinter.END)
        self.insert("1.0", textVar.get())
    
    def focusOut(self, event):
        '''
        '''
        if(self.get("1.0", Tkinter.END).rstrip() == ""):
            self.insert("1.0", self.defaultText)   
        else:
            self.currentVar.set(self.get("1.0", Tkinter.END))
        self.emailFrame._saveEntry()