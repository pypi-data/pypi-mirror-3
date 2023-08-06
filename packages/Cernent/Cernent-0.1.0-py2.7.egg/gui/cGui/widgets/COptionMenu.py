'''
Created on Mar 13, 2012

@author: bkraus
'''

import Tkinter
from gui.cGui.config.GuiConfig import getBackgroundColor

class COptionMenu(Tkinter.OptionMenu):
    '''
    Just an extension of the Tkinter.OptionMenu class for Cernent purposes.
    '''
    
    def __init__(self, master, variable, value, *values, **kwargs):
        Tkinter.OptionMenu.__init__(self, master, variable, value, *values, **kwargs)
        self.config(highlightbackground=getBackgroundColor(), background=getBackgroundColor())