'''
Created on Feb 26, 2012

@author: bkraus
'''

import Tkinter
from gui.cGui.config.GuiConfig import getLabelBackgroundColor
from gui.cGui.config.GuiConfig import getForegroundColor

class CLabel(Tkinter.Label):
    '''
    Just an Extension of Tkinter's Label object for Cernent/Cerno
    '''
    def __init__(self, master ,**cnf):
        Tkinter.Label.__init__(self, master, cnf)
        self.config(bg = getLabelBackgroundColor(), foreground=getForegroundColor(),
                     border=1, relief="raised")