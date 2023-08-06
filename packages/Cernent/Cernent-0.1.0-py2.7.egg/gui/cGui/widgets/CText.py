'''
Created on Feb 27, 2012

@author: bkraus
'''

import Tkinter
from gui.cGui.config.GuiConfig import getBackgroundColor

class CText(Tkinter.Text):
    '''
    Just an extension of Tkinter's Text object for Cernent/Cerno
    '''
    
    def __init__(self, master, **cnf):
        Tkinter.Text.__init__(self, master, cnf)
        self.config(highlightbackground=getBackgroundColor())