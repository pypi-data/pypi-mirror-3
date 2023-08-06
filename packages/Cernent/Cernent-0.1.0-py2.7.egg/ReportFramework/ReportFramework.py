"""
.. module:: ReportFramework
   :platform: Unix
   :synopsis: This is the core of the reporting system.  It parses the .nessus file
            and does initial processing appending the results to the name space of the
            parsed object.

.. moduleauthor:: Chris White
"""
import os, sys, re, inspect, RFVulnProcs, RFTargetProcs, RFReportProcs
from lib.dotnessus_v2 import Report
from collections import OrderedDict
from config.config import pullConfAndInit

class ReportFramework():
    """The ReportFramework object contains the parsed file(s) that have been pre-processed.
    """
    def __init__(self, fileA, fileB=None):
        """Args:
            fileA (string): path to .nessus file
            
            fileB (string): path to 2nd .nessus file (optional)
        """
        self.parse(fileA, fileB)
        self.rpts = [self.rptA, self.rptB]
        self.process()
        
        
    def parse(self, fileA, fileB):
        """Parses fileA and fileB if it exists assigning them to rptA and rptB.
        rptA will always be the scan that took place earlier then rptB
        """
        self.rptA = Report()
        self.rptA.parse(fileA)
        
        if fileB:
            self.rptB = Report()
            self.rptB.parse(fileB)
            
            if self.rptA.scan_start > self.rptB.scan_start:
                self.rptA, self.rptB = self.rptB, rptA
        else:
            self.rptB = None
            
                    
    def process(self):
        """Steps through the parsed reports assigning various metrics to the rptA/B
        objects. If additional pre-processing is needed it should be added to the 
        appropriate RF module (Report level, Target level, Vuln level) Note the
        procs are run in the following order Vuln->Target->Report
        """
        def getProcs(module):
            return [x[1] for x in inspect.getmembers(module, predicate=inspect.isfunction) if x[0] != 'init']
        
        for rpt in self.rpts:
            if not rpt:
                continue
            # Loops through each target and each subsequent plugin (vulns) ticking counters etc
            RFReportProcs.init(rpt)
            for tgt in rpt.targets:
                RFTargetProcs.init(rpt, tgt)    
                for v in tgt.vulns:
                    RFVulnProcs.init(rpt, tgt, v)
                    for vMethod in getProcs(RFVulnProcs):
                        vMethod(rpt, tgt, v)
                
                for tMethod in getProcs(RFTargetProcs):
                    tMethod(rpt, tgt)
                    
            for rMethod in getProcs(RFReportProcs):
                rMethod(rpt)
                
                
    def printStatusMsg(self, msg, length=35, char='*'):
        print("\n%s\n%s\n%s\n" % (char * length, msg, char * length))
    
    
    def getStatusMsg(self, msg, length=35, char='*'):
        return "\n%s\n%s\n%s\n" % (char * length, msg, char * length)


    def msWrite(self, string, outPath):
        """Writes the string provided to it replacing line feeds with crlf for windows 
        notepad compatibility... we still live in a windows world unfortunately.
        """
        if outPath:
            out = open(outPath, 'w')
            out.write('%s\r\n' % string.replace('\n', '\r\n'))
            

def getExample(reportName):
    """Processes the example.nessus file specified in the cernent.conf file.
    
    Args:
        reportName (string): the name of the report module to process example.nessus
        
    Returns:
        result (string): the result of the report module
    """
    reportDict = loadReports()
    examplePath = pullConfAndInit()['examplePath']
    
    return reportDict[reportName].getResult(ReportFramework(examplePath))


def writeReport(inputFile, outputFile, reportName):
    reportDict = loadReports()
    
    return reportDict[reportName].writeResult(ReportFramework(inputFile), outputFile)
    

def writeSRReport(rf, outputFile, reportName):
    reportDict = loadReports()
    
    return reportDict[reportName].writeResult(rf, outputFile)


def loadReports():
    """This method loads the report modules in the reports directory.  It is largely
    inspired by `Crunchy's Plugin System <http://pytute.blogspot.com/2007/04/python-plugin-system.html>`_.

    The **reportDict**  global dictionary is populated with report module names as the keys and the imported
    module as the value.::

        {'execreport': <module 'execreport' from '/path/to/execreport.py'>}

    
    .. warning::

        The modules are blindly imported from the reports directory.
        There is currently no plans for a more secure method.
    """
    conf = pullConfAndInit()
    reportPath = conf['reportPath']
    reportDict = OrderedDict()

    # Enumerates the paths for each report module in reportPath
    reportFiles = [fname[:-3] for fname in os.listdir(reportPath) if fname.endswith(".py") if fname != '__init__.py']

    # Not sure this is needed anymore
    # Loops through reportFiles list adding each module to the path if it isn't
    # already in the path
    if not reportPath in sys.path:
        sys.path.append(reportPath)
    
    reportList = []
    # Quick list comprehension to import each file in the report files returning a list
    # of imported modules
    for fname in reportFiles:
        reportList.append(__import__(fname))

    # Creates a dictionary of report modules key'd by the module name
    for report in reportList:
        if not report.__name__ == '__init__':
            reportDict[report.__name__] = report
    
    return reportDict
    