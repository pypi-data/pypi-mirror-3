'''
Created on Feb 26, 2012

@author: bkraus
'''

import Tkinter
from gui.cGui.config.GuiConfig import getBackgroundColor

class CEntry(Tkinter.Entry):
    '''
    Just an Extension of Tkinter's Entry object for Cernent/Cerno
    '''
    
    def __init__(self, master, **cnf):
        Tkinter.Entry.__init__(self, master, cnf)
        self.config(highlightbackground=getBackgroundColor())