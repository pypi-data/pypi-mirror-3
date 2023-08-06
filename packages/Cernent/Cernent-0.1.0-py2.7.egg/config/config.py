"""
.. module:: config
   :platform: Unix
   :synopsis: Parses the cernent.conf and initializes the configuration items

.. moduleauthor:: Chris White


"""

import ConfigParser, os, shutil, glob
from deliveryMethod.Mailer import Mailer
from pwd import getpwnam

#Configuration file location
CONFLOCATION = '/opt/cernent/etc/cernent.conf'

base = '/opt/cernent'
aux = [base, base + '/etc/cernent.conf', base + '/etc/gui.cfg', base + '/resources/example.nessus',
       base + '/resources/example.nessus', base + '/ScanEvents', base + '/reports', base + '/archive']


YES = ['Yes', 'yes', 'YES', 'Y', 'y']

def _getUserIn(msg):
    var = raw_input(msg + ": ")
    if var == "":
        print("No input given, try again.")
        return getUserIn(msg)
    return var


def _getUserInWithDef(msg, default):
    var = raw_input("%s (%s): " % (msg, default))
    if var == "":
        return default
    return var

    
def _checkConfPath():
    """Checks to make sure the /opt/cernent/etc/cernent.conf file exists"""
    if not os.path.exists(CONFLOCATION):
        print("The configuration file, %s, is not present.  Please run cernent.py -s to setup auxiliary files." % CONFLOCATION)
        exit()
        
def checkAuxPaths():
    """Checks to make sure the /opt/cernent/ path and subsequent auxilliary files exists.  
    If not prompts user to run the -s --setup from cernent"""
    foundAny = False
    missingAux = False
    
    for path in aux:
        if not os.path.exists(path):
            print('Necessary auxiliary file/folder is missing: %s...' % path)
            missingAux = True
        else:
            foundAny = True
            
    if missingAux:
        if foundAny:
            print('\nIt appears you have one or more of the required auxiliary file(s)/folder(s).')
            print('If you have done any configuration please save those files before re/running')
            print('cernent -s to resetup your auxiliary files and folders as those changes will')
            print('be lost.\n')
        print('As listed above, required auxiliary files and/or folders are missing.  Please')
        print('run cernent with a -s for setup.')
        exit()
        
    

        
def pullConfAndInit(init=True):
    """Uses `ConfigParser <http://docs.python.org/library/configparser.html>`_ to parse the Cernent configuration file.
    
    It places the configuration items into a dictionary called **conf** keyed by the same configuration key inserting the config as the value.

    Where it makes sense initialization and/or instantiation takes place here as well.
    
    Returns:
        dict. configuration.
    """
    #_checkConfPath()
    
    config = ConfigParser.ConfigParser()
    config.read(CONFLOCATION)
    
    #Configuration dictionary
    conf = {'scanners': {}}
    
    #Loops through each section in the config file, pulling their respective configurations
    for section in config.sections():
        if 'defaults' in section:
            #Path used to store .nessus files from Nessus
            conf['archivePath'] = config.get(section, 'archivePath')
            #Path used to load report modules
            conf['reportPath'] = config.get(section, 'reportPath')
            #Path to example.nessus file for example output
            conf['examplePath'] = config.get(section, 'examplePath')
            #Comma separated list of Cernent administrator's email addresses
            conf['administrators'] = config.get(section, 'administrators')
            
        if "email" in section:
            #The default subject to use
            conf['subject'] = config.get(section, 'subject')
            
            #The default message to use, pulled from a resource file
            f = open(config.get(section, 'message'))
            conf['message'] = f.read()
            f.close()
            
        if "mailer" in section:
            #The smtp server to use when sending email.
            fromAddress = config.get(section, 'fromAddress')
            alertFromAddress = config.get(section, 'alertFromAddress')
            smtp_server = config.get(section, 'smtp_server')
            port = config.get(section, 'port') 
            username = config.get(section, 'username')
            password = config.get(section, 'password')
            
            if init:
                conf['mailer'] = Mailer(fromAddress, alertFromAddress, smtp_server, port, username, password)
            
        if "scanner" in section:
            #The configuration sections that contain scanner in the name will be put into a dictionary
            #keyed by the scanner name with a list of paramemters as the value
            conf['scanners'][config.get(section, 'name')] = [config.get(section, "hostname"), int(config.get(section, "port")),
                                                     config.get(section, "username"), config.get(section, 'password')]        
    return conf


def createAuxilliary():
    
    if os.geteuid() != 0:
        print("Permission Denied: Please run with root/sudo privileges.")
        exit()
        
    ans = _getUserInWithDef('If auxiliary files already exist they may be overwritten by this\nfunction. Continue?', 'No')
    
    if ans in YES:
        
        print('\nCernent user is the account used to make scan event and configuration changes.')
        cernentUser = _getUserInWithDef('Cernent user', os.getlogin())
        
        userStat = getpwnam(cernentUser)
        
        installDir = '/'.join(__file__.split('/')[:-2])
        auxDir = base
        #auxDir = '/tmp/cernent'
        srcDst = [('/archive/', '/archive/'), ('/etc/*', '/etc/'), ('/reports/*.py', '/reports/'),
                  ('/resources/*', '/resources/'), ('/ScanEvents/*', '/ScanEvents/')]
        
        for src, dst in srcDst:
            try:
                os.makedirs(auxDir + dst)
            except(OSError):
                pass
            for file in glob.glob(installDir + src):
                if '__init__.py' not in file:
                    shutil.copy(file, auxDir + dst)
                  
        for root, dirs, files in os.walk(auxDir):  
            for momo in dirs:  
                print os.path.join(root, momo)
                os.chown(os.path.join(root, momo), userStat.pw_uid, userStat.pw_gid)
                os.chmod(os.path.join(root, momo), 0700)
            for momo in files:
                os.chown(os.path.join(root, momo), userStat.pw_uid, userStat.pw_gid)
                os.chmod(os.path.join(root, momo), 0600)
                
        os.chown(auxDir, userStat.pw_uid, userStat.pw_gid)
        os.chmod(auxDir, 0700)
                
        
