def getExtension():
    return '.txt'

def getName():
    return __file__.split('.')[0]

def getDescription():
    return 'Reports whether or not a host was scanned using credentials or not. Printing the credentials used for the scan if appropriate'

def getResult(rf):
    rpt = rf.rpts[0]
    
    creds = []
    uncreds = []
    
    msg = ''
    
    for target in rpt.targets:
        if target.credentialed:
            creds.append(target)
        else:
            uncreds.append(target)
    
    msg += rf.getStatusMsg("Credentialed Scan")
    
    for target in creds:
        msg += target.name + '\n'
        for cred in target.credentialed:
            msg +="\t%s\n" % cred
        
    msg += rf.getStatusMsg("Uncredentialed Scan")
    for target in uncreds:
        msg += target.name + '\n'
        
    return msg

def writeResult(rf, outputPath):
    path = outputPath + getExtension()
    rf.msWrite(getResult(rf), path)
    
    return path