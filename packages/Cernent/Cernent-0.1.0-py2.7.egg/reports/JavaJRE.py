import re

def getExtension():
    return '.txt'

def getName():
    return __file__.split('.')[0]

def getDescription():
    return 'This reports the distribution of Java JRE versions.'
    
def getResult(rf):
    rpt = rf.rpts[0]
    
    javas = {'hsc':{}, 'mg':{}, 'other':{}, 'all':{}}
    
    for target in rpt.targets:
        for vuln in target.vulns:
            if vuln.plugin_id == '33545':
                key = 'other'
                if re.search('hsc', target.name, re.IGNORECASE):
                    key = 'hsc'
                if re.search('mg', target.name, re.IGNORECASE):
                    key = 'mg'
                    
                for line in vuln.plugin_output.splitlines():
                    if re.search('version', line, re.IGNORECASE):
                        version = line.split()[2]
                        if javas[key].has_key(version):
                            javas[key][version] += 1
                        else:
                            javas[key][version] = 1
                        if javas['all'].has_key(version):
                            javas['all'][version] += 1
                        else:
                            javas['all'][version] = 1
         
    msg = ''   
    for key in sorted(javas.keys()):
        msg += rf.getStatusMsg(key)
        for ver in sorted(javas[key].keys()):
            count = ''
            msg += ver + ':'
            count = '|' * javas[key][ver]
            msg += count + ' (%d)\n' % javas[key][ver]
            
    return msg

def writeResult(rf, outputPath):
    path = outputPath + getExtension()
    rf.msWrite(getResult(rf), path)
    
    return path