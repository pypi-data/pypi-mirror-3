'''
.. module:: CInitialValueText
   :platform: Unix
   :synopsis: This module defines the CInitialValueText class   

.. moduleauthor:: Daniel Chee
'''

import Tkinter
from gui.cGui.config.GuiConfig import getBackgroundColor

class CInitialValueText(Tkinter.Text):
    '''
    Just an Extension of Tkinter's Text object for Cernent/Cerno that is filled with initial text that is cleared
    away after the first click. 
    '''
    
    FIRST = True;
    
    def __init__(self, master, text):
        '''
        Creates a new CInitialValueText with the given initial text. 
        
        Args:
        
            text: The initial text. 
        '''
        
        Tkinter.Text.__init__(self, master)
        self.insert(Tkinter.END, text)
        self.bind("<Button-1>", self.firstClick)
        self.config(highlightbackground=getBackgroundColor())

    def firstClick(self, other):
        if(self.FIRST == True):
            self.delete('1.0', Tkinter.END)
            self.FIRST = False