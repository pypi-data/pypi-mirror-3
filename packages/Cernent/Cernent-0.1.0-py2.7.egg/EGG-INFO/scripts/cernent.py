#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

"""
.. module:: cernent
   :platform: Unix
   :synopsis: Main modules used to control the daemon, launch the gui, among other CLI functions.

.. moduleauthor:: Chris White
"""

import argparse, logging
from gui.cGui.controller.CGuiController import CGuiController
from NessusCom.NessusCommunicator import NessusCommunicator
from ReportFramework.ReportFramework import loadReports
from ScanEvent.InitMode import initMode
from config.config import pullConfAndInit, checkAuxPaths, createAuxilliary
    
def _processArgs():
    """Uses `argparse <http://docs.python.org/dev/library/argparse.html>`_ to create the command line arguments and subsequent variables/values.
    
    It also loops through the **reportDict** and displays their respective help descriptions sorted by report name.

    Returns:
        list.  parsed options.
    """
    parser = argparse.ArgumentParser(description='Cernent', prog='cernent')

    parser.add_argument('-i', '--initmode', action='store_true', help='Scan Event batch mode.')
    parser.add_argument('-s', '--setup', action='store_true', help='Setup directory structure and supporting files.')
    
    #List of CLI options in use to avoid user supplied report collisions
    collisions = ['i', 'initmode']
    
    try:
        #Loops through report modules adding them to the argparse object
        reportDict = loadReports()
        for reportName, report in reportDict.items():
            if reportName not in collisions:
                parser.add_argument('--%s' % reportName, action='store_true', help=report.getDescription())
    except(KeyError):
        pass
        
    return parser.parse_args()
            

def _createNessusComms(scanners):
    """Instantiates the NessusCommunicator objects for each of the scanners defined in the configuration file
    
    Args:
       scanners (dict):  Dictionary of scanner names to scanner parameters.
       
    Returns:
        dict. NessusCommunicators.
    """
    ncs = {}
    
    for key, value in scanners.iteritems():
        ncs[key] = NessusCommunicator(*value)
        
    return ncs


def main():
    """Pulls user arguments, configurations, and controls execution.
    """
    options = _processArgs()
    
    if options.setup:
        createAuxilliary()
        exit()

    checkAuxPaths()
    conf = pullConfAndInit()

    if options.initmode:
        initMode(conf, _createNessusComms(conf['scanners']), [], [])
        exit()
            
    app = CGuiController(_createNessusComms(conf['scanners']), conf)
    app.show()
    

'''
Runs main as long as script is executed at the command line, looks for and catches
Ctrl-C keyboard interrupts in case the python interpreter or O/S doesn't by default.
'''    
if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt):
        print("")
        exit()