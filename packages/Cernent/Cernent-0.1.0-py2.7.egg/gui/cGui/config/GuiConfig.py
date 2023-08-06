"""
.. module:: GuiConfig
   :platform: Unix
   :synopsis: Loads configuration info for the gui.

.. moduleauthor:: Brian Kraus


"""

class GuiConfigError(Exception):
    '''
    An exception signifying that the config file was incorrect.
    '''
    pass

class GuiConfig:
    '''
    The class that holds the loaded configuration info.
    '''
    LOADED = False;
    GuiPath = "/opt/cernent/etc/gui.cfg"
    Bg = None
    _NUM_ELEMS = 8
    Padx = None
    Pady = None
    foregroundColor = None
    labelBackground = None
    highlightBG = None
    highlightColor = None
    highlightThickness = 0
    
def getBackgroundColor():
    '''
    Returns:
        The default background color.
    '''
    if not GuiConfig.LOADED:
        _loadConfig()
    return GuiConfig.Bg

def getPadX():
    '''
    Returns:
        The default x padding.
    '''
    if not GuiConfig.LOADED:
        _loadConfig()
    return GuiConfig.Padx

def getPadY():
    '''
    Returns:
        The default y padding.
    '''
    if not GuiConfig.LOADED:
        _loadConfig()
    return GuiConfig.Pady
        
def _loadConfig():
    f = open(GuiConfig.GuiPath, "r")
    tokens = f.read().split('|')
    if len(tokens) != GuiConfig._NUM_ELEMS:
        raise GuiConfigError("Incorrent number of arguments: " + str(len(tokens)) + ", should be: " + str(GuiConfig._NUM_ELEMS))
    #First element is the background color.
    GuiConfig.Bg = tokens[0]
    #Second is x padding
    GuiConfig.Padx = int(tokens[1])
    #third is y padding
    GuiConfig.Pady = int(tokens[2])
    #4 is label background color
    GuiConfig.labelBackground = tokens[3]
    #5 is text color for labels.
    GuiConfig.foregroundColor = tokens[4]
    #highlight background color
    GuiConfig.highlighBG = tokens[5]
    #Highlight color
    GuiConfig.highlightColor = tokens[6]
    #Highlight thickness
    GuiConfig.highlightThickness = int(tokens[7])
    GuiConfig.LOADED = True
    f.close()
    
def getHighlightBG():
    '''
    Returns:
        The default highlight background color.
    '''
    return GuiConfig.highlightBG

def getHighlightColor():
    '''
    Returns:
        The default highlight color.
    '''
    return GuiConfig.highlightColor

def getHighlightThickness():
    '''
    Returns:
        The default highlight thickness.
    '''
    return GuiConfig.highlightThickness

def getForegroundColor():
    '''
    Returns:
        The default foreground color.
    '''
    if not GuiConfig.LOADED:
        _loadConfig()
    return GuiConfig.foregroundColor

def getLabelBackgroundColor():
    '''
    Returns:
        The default background color for CLabels.
    '''
    if not GuiConfig.LOADED:
        _loadConfig()
    return GuiConfig.labelBackground

if __name__ == '__main__':
    print getBackgroundColor()
    print getPadX()
    print getPadY()
    print getForegroundColor()
    print getLabelBackgroundColor()
    

