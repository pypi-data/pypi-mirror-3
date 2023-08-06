"""
.. module:: ReportManager
   :platform: Unix
   :synopsis: This module handles the writing and retrieval of .nessus files
           to archive. It insures that only the most recent .nessus files
           remain up to the scansToKeep value specified by the user during
           the Scan Event creation.

.. moduleauthor:: Chris White
"""

import os, datetime, logging, errno

class ReportManager():
    """ReportManager handles the file IO for .nessus files, enforcing the
    scansToKeep option. The folder structure uses the archivePath configured
    in the cernent.conf file plus the Scan Event name for the directory that
    holds the .nessus files.
    """
    def __init__(self, scanName, scansToKeep, base):
        self.logger = logging.getLogger('ReportFramework.ReportManager')
        self.reportDir = base + scanName + '/'
        self.makeDir(self.reportDir)
        self.scansToKeep = scansToKeep
        
        
    def makeDir(self, dir):
        """Creates the directory if it doesn't already exist checking for
        permission denied errors, all other errors are re-raised.
        """
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
            except IOError as e:
                if e.errno == errno.EACCES:
                    print("Permission Denied")
                    self.logger.warning('makeDir failed: Permission Denied')
                # Not a permission error.
                else:
                    raise e
                
            
    def writeReport(self, report): 
        """Writes the report to the correct directory using a timestamp format.
        (e.g. 2012-01-01_00:00:00.nessus)
        """
        reportFile = self.reportDir + datetime.datetime.today().strftime('%Y-%m-%d_%H%M%S') + '.nessus'
        
        f = open(reportFile, 'w')
        f.write(report)
        f.close()
        
        self.logger.debug('Nessus file written: %s' % reportFile)
        
        self.rmExcessReports()
        
        
    def rmExcessReports(self):
        """Removes the reports that go beyond the number of scansToKeep.
        This relies on the sorting order of the timestamp used when writing the report.
        """
        self.logger.debug("The number of scans to keep: %d" % self.scansToKeep)
        keepers = os.listdir(self.reportDir)[-self.scansToKeep:]
        for file in keepers:
            self.logger.debug('Keeping: %s' % (self.reportDir+file))
        if self.scansToKeep != -1:
            toDelete = os.listdir(self.reportDir)[:-self.scansToKeep]
            for file in toDelete:
                os.remove(self.reportDir+file)
                self.logger.debug('Old Nessus file removed %s' % self.reportDir+file)
            
            
    def getReportFiles(self):
        """Gets the most recent .nessus file paths
        """
        rpts = os.listdir(self.reportDir)
        
        if len(rpts) == 1:
            return self.reportDir + rpts[0], None
        else:
            return self.reportDir + rpts[0], self.reportDir + rpts[1]
        