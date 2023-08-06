#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

"""
.. module:: cernentd
   :platform: Unix
   :synopsis: Cernent daemon which handles scheduling, scan launching, and maintenance tasks.

.. moduleauthor:: Chris White
"""

import os, signal, datetime, platform, ctypes, logging, fcntl, sys, time
from subprocess import Popen, PIPE
from apscheduler.scheduler import Scheduler
from NessusCom.NessusCommunicator import NessusCommunicator
from NessusCom.NessusCommunicator import canReachNessusServer
from ScanEvent.ScanRunner import ScanRunner
from ScanEvent.ScanEvent import getScanEventList
from ScanEvent.ScanEvent import MarkerFileIO
from socket import gethostname
from lib.Daemon import Daemon
from config.config import pullConfAndInit


# Location of the pidfile
PIDPATH = '/tmp/cernent.pid'


class Cernentd(Daemon):
    """Subclasses `Daemon <http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/ >`_ to daemonize
    the scan scheduler which uses `APScheduler <http://packages.python.org/APScheduler/ >`_.
    
    The scheduler launches the scans at the predetermined times.  It also manages maintenance tasks like checking
    for low disk space, ensuring the Nessus servers are accessible, checking the Plugin Set version number to inform
    the admin of stale plugins. Lastly it monitors the marker.marker file for modifications to the Scan Events,
    unloading, loading, and reloading as necessary.
    
    
    Args:
        conf (dict): Dictionary containing various configuration items defined in the cernent.conf file
        
        daemon (bool): Boolean that decides whether or not to daemonize, default is True.  If set to false the scheduler
        runs in the launching terminal.
    """
    def __init__(self, conf, daemon=True):
        logging.basicConfig(filename='/opt/cernent/cernent.log', 
                            format='%(asctime)s %(levelname)s:%(name)s -> %(message)s',
                            level=logging.DEBUG)
        self.logger = logging.getLogger('cernentd')
        self.conf = conf
        self.sched = Scheduler()
        # List used to keep track of which scans are currently running to avoid the unloading of Scan Events from the
        # Scheduler while it is still running.
        self.runningScans = []
        # Checks the daemon bool, if it is to daemonize it calls the Daemon's constructor, otherwise it directly
        # launches the run method.
        if daemon:
            Daemon.__init__(self, PIDPATH)
        else:
            self.run()
    
    
    def run(self):
        """The run method is used by Daemon as the launch point once daemonized.  
        It is run directly when not daemonized.
        """
        self._initScheduler()
        self.sched.start()
        # APScheduler spawns a thread when the scheduler is started, if the calling class finishes execution the
        # scheduler is closed, this while loop keeps the daemon running and subsequently the scheduler.
        while True:
            time.sleep(10)
 
            
            
            
    #Check if connecting but notify if fails,
    #conf['mailer']  while give us the mailer, with this we 
    #can send a message.
    def checkScannerConnectivities(self):
        downScanners = []
        for scanner in self.conf['scanners'].values():
            s = NessusCommunicator(*scanner)       
            isAvail = canReachNessusServer(s.hostName, s.port, s.userName, s.password)
            if not isAvail:
                downScanners.append(s)
        if len(downScanners) > 0:
            _handleDownScanners(downScanners)
        
    def _handleDownScanners(self, downScanners):
        pass                                        ############TODO MAIL OUT DESCRIPTION OF DOWN SCANNERS
                                                    ############TO APPROPRIATE PARTIES
                                                    
                                                    
                                                    
                                                    
    def _checkPluginSetStatus(self):
        """Checks the plugin timestamp for each configured scanner to ensure the scanners are
        taking in regular updates.  Since Cernent is meant to significantly reduce the amount
        of time spent with the scanner the likelihood of out-of-date plugin sets is increased.
        
        If a plugin set has not been updated for two days and email will be sent to the
        administrators.
        """
        problems = []
        for scannerName, scannerParams in self.conf['scanners'].items():
            s = NessusCommunicator(*scannerParams)
            
            updateLag = datetime.timedelta(days=2)
            
            now = datetime.datetime.today()
            try:
                plugin_dt = datetime.datetime.strptime(s.getPluginSet(), '%Y%m%d%H%M')
            except(AttributeError):
                self.logger.critical('%s is experiencing communication issues.' % scannerName)
                return
            
            self.logger.info('%s plugin date: %s' % (scannerName, plugin_dt))
            
            if (now - plugin_dt) > updateLag:
                self.logger.warning('%s plugins out of date: %s' % (scannerName, plugin_dt))
                problems.append((scannerName, plugin_dt))
                
            s.logOff()
            
        if problems:
            msg ='The following scanners are reporting a plugin set 2 or more days old:\n\n'
            for scanner, plugin_dt in problems:
                msg += '%s reports its plugin set is %d days old: %s\n\n' % (scanner, 
                                                                             (now - plugin_dt).days, 
                                                                             plugin_dt)
                
            self.conf['mailer'].sendGenMail(toAddr=self.conf['administrators'], 
                                            subject='-= Plugin Set(s) Out-of-Date =-', 
                                            body=msg)
    
    
    def _launchScanEvent(self, conf, se):
        """Launches the scan events to it's respective Nessus scanner. Adds the ScanEvent to the runningScans
        before launching, and removes it once finished.
        
        Args:
            nessusComm (NessusCommunicator): The Nessus server to perform the scan.
        
            mail (Mailer): The mailer object to send the email once the scan is finished.
            
            se (ScanEvent): The scan event to be launched
        """
        self.runningScans.append(se.name)
        self.logger.info('%s Launched' % se.name)
        s = ScanRunner(conf, se)
        s.launch()
        self.runningScans.remove(se.name)
    
    
    def _checkForScanEventChanges(self):
        """Checks the marker file for Scan Event changes and reloads the Scan Event if there were
        any changes.
        """
        if MarkerFileIO.getSENames():
            reload = []
            markedSEs = MarkerFileIO.getSEObjects()
            unloaded = self._unloadScanEvents()
            for se in markedSEs:
                if se.getName() in unloaded:
                    self.logger.debug('Reloading %s.' % se.getName())
                    reload.append(se)
            self._scheduleScanEvents(reload)
            
    
    def _unloadScanEvents(self):
        """Unloads Scan Events that have been marked as changed in the marker.marker file
        
        Will only unload the Scan Event if it is not currently running. This ensures the one launched
        Scan Event at a time.
        
        Returns:
            unloaded (list): The list of Scan Events that were successfully unloaded.
        """
        unloaded = []
        jobs = self.sched.get_jobs()
        changed = MarkerFileIO.getSENames()
        self.logger.debug('MarkerFileIO.getSENames(): %s' % changed)
        
        jobNames = [job.name for job in jobs]
        
        for seName in changed:
            if seName not in jobNames:
                self.logger.debug('New scan event detected: %s' % seName)
                unloaded.append(seName)
                MarkerFileIO.removeSE(seName)
                changed.remove(seName)    
        
        for job in jobs:
            if job.name in changed:
                self.logger.debug('Scan event %s has changed.' % job.name)
                if job.name not in self.runningScans:
                    self.logger.debug('Unloading %s.' % job.name)
                    MarkerFileIO.removeSE(job.name)
                    self.sched.unschedule_job(job)
                    unloaded.append(job.name)
                else:
                    self.logger.debug('Scan event %s is currently running. Waiting to reload.' % job.name)
                
        return unloaded
            
            
    def _scheduleScanEvents(self, ses):
        """Adds the Scan Events to the scheduler as a cron job, telling it to begin execution
        at _launchScanEvent, specifying the arguments needed for _launchScanEvent, the Scan Event
        Name and a flattened dictionary containing the Scan Event's schedule.
        
        Args:
            ses (list):  Scan Events to schedule.
        """
        for se in ses:
            try:
                self.sched.add_cron_job(self._launchScanEvent, 
                                        args=[self.conf, se],
                                        name=se.getName(),
                                        **se.getSchedule())
            except Exception as e:
                self.logger.debug('Problem loading Scan Event %s:' % se.getName())
                
                self.conf['mailer'].sendGenMail(toAddr=self.conf['administrators'],
                                                subject='-= Scan Event Load Error =-', 
                                                body='%s:\n%s' % (se.getName, e))
    
    
    def _initScheduler(self):
        """Initializes the scheduler with maintenance tasks and Scan Events. Also sets the the thread pool
        to 50 from its default of 20
        """
        MarkerFileIO.clearFile()
        ses = getScanEventList()
    
        self.sched._threadpool.max_threads = 50
        self.sched.add_cron_job(self._checkForScanEventChanges, minute='*/1', second='30')
        self.sched.add_cron_job(self._checkForLowDiskSpace, hour='8', minute='1')
        self.sched.add_cron_job(self._checkPluginSetStatus, hour='8', minute='2')
        
        #complain at Brian_D if doesn't work 
        #self.sched.add_cron_job(self.checkScannerConnectivities, hour='*/1')
        
        self._scheduleScanEvents(ses)
    
    
    def _checkForLowDiskSpace(self):
        """Administrative task checking the disk space of the report path's partition which stores 
        the .nessus files. If the partition falls below 10% free space an email is sent to the 
        administrators.
        """
        #http://stackoverflow.com/questions/51658/cross-platform-space-remaining-on-volume-using-python
        #minor modifications
        def get_free_space(folder):
            if platform.system() == 'Windows':
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), 
                                                           None, None, 
                                                           ctypes.pointer(free_bytes))
                return free_bytes.value
            else:
                s = os.statvfs(folder)
                return s.f_bfree * s.f_frsize
            
        #Not cross platform safe
        def get_total_disk_space(folder):
            s = os.statvfs(folder)
            return s.f_frsize * s.f_blocks
        
        #Not cross platform safe
        def get_disk_used_percentage(folder):
            return get_free_space(folder) / float(get_total_disk_space(folder)) * 100

        p = get_disk_used_percentage(self.conf['archivePath'])
        
        self.logger.info("Current free disk space (%.2f%%)" % p)
        
        if p < 10:
            self.logger.warning("Disk space running low (%.2f%%)" % p)
            self.conf['mailer'].sendGenMail(toAddr=self.conf['administrators'], 
                                            subject='-= Cernent Low Disk Space =-', 
                                            body="%s's disk space is running low (%.2f%%)" % (gethostname(), p))
            
            
def runBash(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    out = p.stdout.read().strip()
    return out

def forkIt():
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)

    runBash('python ' + dir_path + '/cernentd.py start')
    
    
def noDaemon():
    daemon = Cernentd(pullConfAndInit(), daemon=False)
    daemon.logger.info('Starting non-Daemon')
    daemon.start()
    
    
def startDaemon(gui=False):
    if gui:
        forkIt()
    daemon = Cernentd(pullConfAndInit())
    daemon.logger.info('Starting Daemon')
    daemon.start()
    
        
def stopDaemon():
    daemon = Cernentd(None)
    daemon.logger.info('Stopping Daemon')
    daemon.stop()
    
     
def restartDaemon():
    daemon = Cernentd(pullConfAndInit())
    daemon.logger.info('Restarting Daemon')
    daemon.restart()
    
    
def daemonRunning():
    daemon = Cernentd(None)
    return daemon.running()
           

def main():
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            startDaemon()
        elif 'stop' == sys.argv[1]:
            stopDaemon()
        elif 'restart' == sys.argv[1]:
            restartDaemon()
        elif 'nodaemon' == sys.argv[1]:
            noDaemon()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt):
        print("")
        exit()
