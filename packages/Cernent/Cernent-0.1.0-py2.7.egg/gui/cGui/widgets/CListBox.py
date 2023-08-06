'''
Created on Feb 27, 2012

@author: bkraus
'''

import Tkinter
from gui.cGui.config.GuiConfig import getBackgroundColor

class CListBox(Tkinter.Listbox):
    '''
    An extension of Tkinter's ListBox for Cernent/Cerno
    '''
        
    def __init__(self, master, **cnf):
        Tkinter.Listbox.__init__(self, master, cnf)
        self.config(highlightbackground=getBackgroundColor())