'''
Created on Mar 4, 2012

@author: Anarchee
'''

import Tkinter
from gui.cGui.config.GuiConfig import getBackgroundColor

class CFrame(Tkinter.Frame):
    '''
    Just an extension of Tkinter's Frame object for Cernent/Cerno
    '''
    def __init__(self, master, **cnf):
        Tkinter.Frame.__init__(self, master, cnf)
        self.config(bg = getBackgroundColor())
        