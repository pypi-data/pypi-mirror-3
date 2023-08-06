"""
.. module::MarkerFileIO
   :platform: Unix
   :synopsis: The MarkerFileIO module is a wrapper around a file named marker.marker
   				that exists inside the ScanEventDirectory.  Its purpose is to hold
   				the names of all scan events that need to be loaded into the 
   				daemon.  An example of this would be if a scan event was created
   				or edited since the daemon was last initialized, then the daemon
   				would check the marker file, see these two SE files, and load them.

.. moduleauthor:: Brian_D
"""


import os
import ScanEvent

def clearFile():
	'''
		This method deletes all entries in the marker file.
	'''
	markerDirectory = ScanEvent.getPathToSaves()
	if not os.path.exists(markerDirectory + "marker.marker"):
		#print "Tried to clear marker file that doesn't exist.  Creating new empty marker file."
		mF = open(markerDirectory + "marker.marker", "w")
		mF.close()
	else:
		#print "Wiping Scan event marker file clean"
		os.remove(markerDirectory + "marker.marker")
		mF = open(markerDirectory + "marker.marker", "w")
        mF.close()
        
def getMarkerFileDirectory():
    return ScanEvent.getPathToSaves()
        
def getSENames():
	'''
		This method returns a list of strings reporting all Scan Event
		names that are marked in the marker.marker file.
	'''
	markerDirectory = ScanEvent.getPathToSaves()
 	#We first make sure it exists, create it if it doesn't and return empty list
 	if not os.path.exists(markerDirectory + 'marker.marker'):
 		print "Tried to open non-existent marker file at:" + markerDirectory
 		mF = open(markerDirectory + "marker.marker", "w")
 		mF.close()
 		return []
 	mF = open(markerDirectory + "marker.marker", "r")
 	names = [x.strip() for x in mF.readlines()]
 	mF.close()
 	return names
 
 
 
def removeSE(ScanName):
	'''
		Removes the specified scan event name from the list.  This method may
		be called when a scan event is loaded from the daemon that was previously
		marked and no longer should be.
	'''
	markerDirectory = ScanEvent.getPathToSaves()
	names = getSENames()
	names = filter (lambda a: a != ScanName, names)
	os.remove(markerDirectory + "marker.marker")
	mF = open(markerDirectory + "marker.marker", "a")
	for n in names:
		mF.write(n + '\n')
		
	
def addSE(ScanName):
	'''
		Puts a scan name in the marker file.  Putting a scan name in the 
		marker file means that it was edited or saved since the daemon
		has been running, and that it should be loaded into the daemon
		whenever the daemon checks the marker file.
	'''
	markerDirectory = ScanEvent.getPathToSaves()
	removeSE(ScanName)
	if not os.path.exists(markerDirectory + 'marker.marker'):
		print "adding scan event entry to marker that does not yet exist"
		print "creating marker now"
	mf = open(markerDirectory + 'marker.marker', "a")
	mf.write(ScanName + '\n')
	mf.close()
		
		
def getSEObjects():
    '''
		The method gets all the scan names that are marked, creates 
		instances of them, and returns them all in a list.  This 
		method would be called by the daemon when it wishes to load
		all marked scan event files.
    '''
    markerDirectory = ScanEvent.getPathToSaves()
    names = getSENames()
    SEs = []
    dir = ScanEvent.getPathToSaves()
	
	
    for name in names:
        try:
            path = dir + name + '.se'
            se = ScanEvent.loadScanEvent(path)
            SEs.append(se)  
        except IOError:
            print 'Tried to load: %s which is does not exist in the ScanEvent directory.' % path
	return SEs
	
	
