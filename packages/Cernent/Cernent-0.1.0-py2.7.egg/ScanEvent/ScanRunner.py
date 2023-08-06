"""
.. module:: ScanEvent.ScanRunner
   :platform: Unix
   :synopsis: This module is what actually takes action. Once the scheduler determines 
            that a Scan Event needs to run it creates and launches the ScanRunner.  
            This sends the command to the Nessus server to have the targets scanned
            using the predefined settings in the Scan Event. It then checks in with
            the Nessus server to see when the scan has completed. Once completed the
            resulting .nessus file is downloaded to its archive directory.  The .nessus
            file is then parsed and processed through the report modules defined in the
            Email Items.  After the processing the resulting email(s) are sent out to
            defined recipients.

.. moduleauthor:: Chris White
"""

import logging, tempfile, os
from time import sleep
from ReportFramework import ReportFramework
from ReportFramework.ReportManager import ReportManager
from NessusCom.NessusCommunicator import NessusCommunicator


class ScanRunner():
    """This class handles the scan from start to finish, report parsing and
    processing, and report delivery.
    """ 

    # Time to wait between 'ScanFinished' checks
    TIME_TO_WAIT = 30
    
    def __init__(self, conf, scanEvent):
        self.logger = logging.getLogger('ScanEvent.ScanRunner')
        self.conf = conf
        self.scanEvent = scanEvent
        self.scannerParams = self.conf['scanners'][scanEvent.getScannerName()]
        self.nessusComm = NessusCommunicator(*self.scannerParams)
        self.mailer = self.conf['mailer']
        self.reportDict = ReportFramework.loadReports()
        
        self.reportMgr = ReportManager(self.scanEvent.getName(), 
                                       self.scanEvent.getScansToKeep(),
                                       self.conf['archivePath'])
    


    def _scanStartNotification(self):
        startNotification = self.scanEvent.getStartNotif()
        self.logger.debug('%s start notification recipients: %s' % (self.scanEvent.getName(), startNotification))
        if startNotification:
            self.logger.debug('%s start notification sent' % (self.scanEvent.getName()))
            self.conf['mailer'].sendGenMail(startNotification, '-= Scan Started =-', self.scanEvent.getName())
        
        
    def _scanStopNotification(self):
        stopNotification = self.scanEvent.getEndNotif()
        self.logger.debug('%s stop notification recipients: %s' % (self.scanEvent.getName(), stopNotification))
        if stopNotification:
            self.logger.debug('%s stop notification sent' % (self.scanEvent.getName()))
            self.conf['mailer'].sendGenMail(stopNotification, '-= Scan Finished =-', self.scanEvent.getName())
         
         
    def _getScanResults(self):
        """Checks the Nessus server every TIME_TO_WAIT until the scan has finished.
        Downloads and writes the resulting .nessus file to disk.
        """
        # Wait loop for scan to finish
        while not self.nessusComm.scanFinished(self.scanEvent.getUUID()):
            self.logger.debug('%s scan not finished.' % self.scanEvent.getName())
            sleep(self.TIME_TO_WAIT)
            
        # Downloads the results
        results = self.nessusComm.reportDownload(self.scanEvent.getUUID())
        self.logger.debug('Results received.')
        
        # Writes the results to disk and deletes it from memory
        self.reportMgr.writeReport(results)
        del results
        self.logger.debug('Results written to disk.')
        
    
    def _procNeccessaryReports(self):
        """Incomplete    
        Loops through ScanEvent.reportsToProcess and processes them
        Adding the file path of the customer report to the reportsToProcess Dictionary
        """
        fileA, fileB = self.reportMgr.getReportFiles()
        
        self.logger.debug('Pulling last two .nessus files.')
        self.logger.debug('FileA: %s' % fileA)
        self.logger.debug('FileB: %s' % fileB)
        self.rf = ReportFramework.ReportFramework(fileA, fileB)
        
        self.tempPath = tempfile.mkdtemp()
        self.logger.debug('Temporary Path: %s' % self.tempPath)
        
        self.finalReports = {}
        for emailItem in self.scanEvent.getEmailItems():
            emailItem.reportFiles = []
            for report in emailItem.getReportList():
                if report not in self.finalReports:
                    outputPath = '%s/%s-%s' % (self.tempPath, self.scanEvent.getName(), report)
                    
                    self.finalReports[report] = ReportFramework.writeSRReport(self.rf, 
                                                                              outputPath, 
                                                                              report)
                    
                    self.logger.debug('Report written: %s' % self.finalReports[report])
                
                emailItem.reportFiles.append(self.finalReports[report])
        
        
    def _sendEmailItems(self):
        """Loops through emailItems list sending out appropriate customer reports and message details
        to their respective recipients
        """
        ei = self.scanEvent.getEmailItems()
        
        for email in ei:
            self.logger.debug('Sending email: %s' % email.getName())
            self.mailer.sendMail(email)
            
            
    def _removeFinalReports(self):
        for file in self.finalReports.values():
            os.remove(file)
            self.logger.debug('Removing: %s' % file)
            
        os.rmdir(self.tempPath)
        self.logger.debug('Removing temp path: %s' % self.tempPath)
    
    
    def launch(self):
        
        uuid = self.nessusComm.performScan_By_PolicyName(self.scanEvent.getName(), 
                                                         self.scanEvent.getTargets(),
                                                         self.scanEvent.getPolicy())
        
        self._scanStartNotification()
        
        self.scanEvent.setUUID(uuid)
        
        self._getScanResults()
        
        self.nessusComm.logOff()
        
        self._scanStopNotification()
        
        self._procNeccessaryReports()
        
        self._sendEmailItems()
        
        self._removeFinalReports()
    
           