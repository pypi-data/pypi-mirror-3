'''
Created on Feb 24, 2012

@author: bkraus
'''
import Tkinter

class testGui(Tkinter.Tk):
    
    def __init__(self, parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
        
    def initialize(self):
        self.makeButton()
        
    def makeButton(self):
        buttonFrame = Tkinter.Frame(self, background = "black")
        doButton = Tkinter.Button(buttonFrame, text="Click ME!", command=self.buttonClick)
        doButton.grid(row = 0, column = 0)
        buttonFrame.grid(row = 0, column = 0, columnspan = 1)
    
    def buttonClick(self):
        print "Heyo!"


def main():
    app = testGui(None)
    app.title("My little gui.")
    app.mainloop()

if __name__ == '__main__':
    main()
    