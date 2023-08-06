
"""
.. module:: NessusCommunicator
   :platform: Unix
   :synopsis: Module for XMLRPC communication with the NessusServer.
              There exists one NessusCommunicator object per connection.

.. moduleauthor:: Brian_D
"""

import lib.NessusXMLRPC as NessusXMLRPC
import logging, socket


logger = logging.getLogger('NessusCommunicator')


class NessusCommunicator:
    """
       The NessusCommunicator class is a wrapper around a XMLRPC connection to a single Nessus scanner
       with a single username and password.  It is important to note that this class makes us of 
       already existing code, the NessusXMLRPC.py module that may be found on google code.
    """
    def __init__(self, HostName, Port, UserName, Password):
        """
            Constructor creates a new NessusCommunicator object which encapsulates the functionality
            of a user signing in.  Upon object creation, there is immediate sign in (binding to server).
            
            Args: HostName may be the DNS or IP address of the Nessus Scanner as string
                  Port is the port that scanner is listening on as integer
                  UserName is the account name for who's signing in to the nessus server as string
                  Password is the corresponding password for the account name as string
                  
        """
        self.hostName = HostName
        self.port = Port
        self.userName = UserName
        self.password = Password  
        self.hasBinded = False
        self.__bindToNessusServer()  
     
        
    def __bindToNessusServer(self):
        """
            Initiates the internal Nessus Scanner object and logs on to it.
            This should be the first method call after object instantiation as
            it logs on the server, retrieves, and parses needed information.
        """
        try:
            self.scanner = NessusXMLRPC.Scanner(self.hostName, self.port, self.userName, self.password)
            self.hasBinded = True
        except(socket.gaierror):
            #print 'socket.gaierror'
            self.scanner = None
            pass
        except(socket.error):
            #print 'socket.error'
            self.scanner = None
            pass
        except:
            #print 'general exception'
            self.scanner = None
            pass    
                
                
    def getHasBinded(self):
        """
        Returns true if binding (signing in) with the Nessus Server was successful.
        If returns true, then there exists a internal scanner object.
        """
        return self.hasBinded
    

    def getPolicyDict(self):
        """
        This method polls the nessus scanner and returns a dictionary 
        where every policy by its string policy name is mapped to  
        the corresponding string policyID.
        """
        self.policyList  = self.scanner.policyList()
        self.policyDict  = {}
        for policy in self.policyList:
            self.policyDict[policy['policyName']] = policy['policyID']
        return self.policyDict

    def getPolicyList(self):
        """
        This method polls the nessus scanner and returns a list
        enumerating all policies available on scanner by name.
        """
        self.policyList = self.scanner.policyList()
        self.simplePolicyList = []
        for policy in self.policyList:
            self.simplePolicyList.append(policy['policyName'])
        return self.simplePolicyList
    
    
    def getScanList(self):
        """
        This method polls the nessus scanner and returns a list
        of all currently running scans occuring on the nesses
        scanner.
        """
        result = self.scanner.scanList()['scanList']
        if type(result) == type({}):
            logger.debug(str([result['scan']]))
            return [result['scan']]
        else:
            logger.debug('Failed to detect dict')
            logger.debug(str(result))
            return result
            
    def isConnected(self):
         """
         Returns whether the connection to the Nessus Server
         is still alive.
         """
         #we test by grabbing a scan list which should be extremely light weight 
         #for a server anyways.  If the connection is not live, then an exception
         #will be thrown, so if it runs at all then the connection is live.
         try:
             result = self.scanner.scanList()['scanList']
             return True
         except:
             return False

    
        
    def logOff(self, seq=None):
        """
        Cleanly kills the connection to the Nessus Scanner.
        """
        return self.scanner.logout(seq);
    
    
    
    def _resetConnection(self):
        ''' 
        Used for when we want to be ensured that the Nessus Server is up to date.  
        We logout and immediately log back in
        '''
        self.scanner.logout()
        self.scanner.login(self.userName, self.password)    
    
    
    def performScan_By_PolicyID(self, ScanName, Target_IP, Policy_ID, seq=None):
        """
        Tells the Nessus scanner to perform scan on the Target_IP using the Policy
        which corresponds to the Policy_ID
        Args:
            ScanName the readable name of the scan
            Target_IP which IP the server will scan
            Policy_ID the ID of the policy for which to scan
        Performs scan with argument of Policy_ID.
        """
        return self.scanner.scanNew(ScanName, Target_IP, Policy_ID, seq)['uuid']
    
    
    def performScan_By_PolicyName(self, ScanName, Target_IP, Policy_Name, seq=None):
        """
        Tells the Nessus scanner to perform scan on the Target_IP using the Policy
        which is referenced by its name.
        Args:
            Target_IP where the scan will take place
            Policy_Name the human readable name of the policy to use
        Performs scan with argument of Policy_ID.
        """
        correspondingID = self.getPolicyDict()[Policy_Name]
        return self.performScan_By_PolicyID(ScanName, Target_IP, correspondingID, seq)
        
         
    def reportList(self, seq=None):
        """
        Returns a list of all reports within the Nessus Scanner.
        """
        return self.scanner.reportList(seq)
    
    
    def reportReadableName_2_UUID_Map(self):
        """
        Returns a map of human-readable report names and their corresponding
        UUID name which is actually used for the downloading the report. 
        """
        readableNameToUUID_Dict = {}
        for report in rList:
            readableNameToUUID_Dict[report['readableName']] = report['name']
        return readableNameToUUID_Dict    
            
        
    def reportDownload(self, report, version=None):
        """
            Args:
                Report is the 'name' of a report.  In the returned dictionary
                of reportList there's 'readableName' which is seen in the Nessus client
                and there's 'name' which is the UUID that should be used here to 
                identify the report that will be returned in XML format.
        """
        #self._resetConnection()
        results = self.scanner.reportDownload(report, version)
        if len(results) < 200:
            return None
        else:
            return results
        

    def scanFinished(self, uuid):
        """
        Checks if the scan, labeled by its uuid, is finished
        """
        sl = self.getScanList()
        if not sl:
            return True
        for scan in sl:
            if scan['uuid'] == uuid:
                if scan['status'] == 'completed':
                    return True
                else:
                    return False
        return True
        
        
    def getPluginSet(self):
        return self.scanner.plugin_set


def canReachNessusServer(HostName, Port, UserName, Password):
    """
    This static method is used to make sure that a connection can be made
    with the nessus server specifed by the parameters.
    Args:
        HostName: The nessus server IP or DNS location
        Port: The port the nessus XMLRPC connection is on
        UserName: The user name for who's trying to sign onto the Nessus Server
        Password: The corresponding password for the user.
    """
    testConnectObj = NessusCommunicator(HostName, Port, UserName, Password)
    status = testConnectObj.getHasBinded()   
    if status:
        testConnectObj.logOff()
    del testConnectObj
    return status  