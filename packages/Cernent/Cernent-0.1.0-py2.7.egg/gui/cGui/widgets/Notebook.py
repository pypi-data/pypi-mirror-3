'''
Created on Mar 12, 2012

@author: bkraus
'''

# file: notebook.py
# A simple notebook-like Tkinter widget.
# Copyright 2003, Iuri Wickert (iwickert yahoo.com) - Under the PSF license (same as python itself)
# Edited by Brian Kraus to add getParentFrame, and make the screen frame sizeable and
# also for it to use the grid management system.

import Tkinter
from Tkinter import IntVar
from Tkinter import Frame
from Tkinter import Radiobutton

class Notebook:
    
    
    # initialization. receives the master widget
    # reference and the notebook orientation
    def __init__(self, master, width=0, height=0):
        
        self.active_fr = None
        self.count = 0
        self.choice = IntVar(0)

        # creates notebook's frames structure
        self.rb_fr = Frame(master, borderwidth=2, relief=Tkinter.RIDGE)
        self.rb_fr.grid(row = 0, column = 0, columnspan=10, sticky="NWE")
        self.screen_fr = Frame(master, borderwidth=2, relief=Tkinter.RIDGE, width=width, height=height)
        self.screen_fr.grid(row=1, column = 0, columnspan=1, rowspan = 1, sticky = "WESN")
        self.screen_fr.rowconfigure(0, weight=1)
        self.screen_fr.columnconfigure(0, weight=1)

    # return a master frame reference for the external frames (screens)
    def __call__(self):
        '''
        Returns the main content panel to which all tabs will be added to
        so they can reference it on construction.
        
        Returns:
            The main content panel.
        '''
        return self.screen_fr

        
    # add a new frame (screen) to the (bottom/left of the) notebook
    def add_screen(self, fr, title):
        
        b = Radiobutton(self.rb_fr, text=title, indicatoron=0, \
            variable=self.choice, value=self.count, padx=10, \
            command=lambda: self.display(fr))
        b.grid(row = 0, column = self.count)
        # ensures the first frame will be
        # the first selected/enabled
        if not self.active_fr:
            self.display(fr)
        self.count += 1
        
        # returns a reference to the newly created
        # radiobutton (allowing its configuration/destruction)         
        return b

    # hides the former active frame and shows 
    # another one, keeping its reference
    def display(self, fr):
        if self.active_fr:
            self.active_fr.grid_forget()
        fr.grid(row = 0, column = 0, sticky="NESW")
        self.active_fr = fr