'''
Created on Mar 13, 2012

@author: bkraus
'''

import Tkinter
from gui.cGui.config.GuiConfig import getBackgroundColor

class CCheckButton(Tkinter.Checkbutton):
    '''
    Just a simple extension of Tkinter.Checkbutton for Cernent.
    '''
    def __init__(self, master, **cnf):
        Tkinter.Checkbutton.__init__(self, master, cnf)
        self.config(highlightbackground=getBackgroundColor(), background=getBackgroundColor())