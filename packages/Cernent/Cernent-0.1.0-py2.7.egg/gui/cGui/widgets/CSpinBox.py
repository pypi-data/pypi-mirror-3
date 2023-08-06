'''
Created on Mar 13, 2012

@author: bkraus
'''

from Tkinter import Spinbox
from gui.cGui.config.GuiConfig import getBackgroundColor

class CSpinBox(Spinbox):
    '''
    Extension of Tkinter.Spinbox
    '''
    
    def __init__(self, master, **cnf):
        Spinbox.__init__(self, master, cnf)
        self.config(highlightbackground=getBackgroundColor())