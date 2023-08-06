'''
.. module:: CInitialValueEntry
   :platform: Unix
   :synopsis: This module defines the CInitialValueEntry class   

.. moduleauthor:: Daniel Chee
'''

import Tkinter
from gui.cGui.config.GuiConfig import getBackgroundColor

class CInitialValueEntry(Tkinter.Entry):
    '''
    Just an Extension of Tkinter's Entry object for Cernent/Cerno that has initial text that 
    is cleared away after the first click. 
    '''
    
    FIRST = True;
    
    def __init__(self, master, text, **cnf):
        '''
        Creates a new CInitialValueEntry with the given initial text. 
        
        Args:
        
            text: The initial text.
        '''
        Tkinter.Entry.__init__(self, master, cnf)
        self.insert(0, text)
        self.bind("<Button-1>", self.firstClick)
        self.config(highlightbackground=getBackgroundColor())

    def firstClick(self, other):
        if(self.FIRST == True and self['state'] == Tkinter.NORMAL):
            self.delete(0, Tkinter.END)
            self.FIRST = False
    
    
    
    
    