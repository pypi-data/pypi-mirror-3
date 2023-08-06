def getExtension():
    return '.txt'

def getName():
    return __file__.split('.')[0]

def getDescription():
    return 'Prints the alphanumeric sorted list of targets in the scan.'
    
def getResult(rf):
    rpt = rf.rpts[0]
    
    msg = rf.getStatusMsg("List of targets scanned")
    for target in sorted(rpt.targets, key=lambda t: t.name):
        msg += target.name + '\n'
        
    return msg

def writeResult(rf, outputPath):
    path = outputPath + getExtension()
    rf.msWrite(getResult(rf), path)
    
    return path