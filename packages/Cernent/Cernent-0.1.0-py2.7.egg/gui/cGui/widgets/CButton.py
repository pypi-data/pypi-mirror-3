'''
Created on Feb 27, 2012

@author: bkraus
'''

import Tkinter
from gui.cGui.config.GuiConfig import getBackgroundColor

class CButton(Tkinter.Button):
    '''
    Just an extention of Tkinter's Button object for Cernent/Cerno
    '''
    
    
    def __init__(self, master, **cfg):
        Tkinter.Button.__init__(self, master, cfg)
        self.config(highlightbackground=getBackgroundColor())