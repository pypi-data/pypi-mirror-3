import re

def init(rpt, tgt, vuln):
    ''''''
    
    
def commonOffenders(rpt, tgt, vuln):
    """
    commonOffenders: auxiliary method used during processing which collects metrics for common offenders.  
    Easy to create new categories based on the pn argument which is the vulnerability plugin name.
    To create new category totals be sure to create a new elif before the final else which calculates
    the remaining items that don't fit any of the descriptions provided.
    -- In general follow the report.x (e.g. report.microsoft) variable to see where and how
       it is referenced.
    """
    COMMONOFFENDERS = {'microsoft': '^MS|microsoft', 
                       'office': 'Office|Excel|Word|Works|PowerPoint', 
                       'adobe': 'Adobe|Acrobat|Reader|Flash|AIR|Shockwave', 
                       'mozilla': 'firefox|mozilla|thunderbird', 
                       'oracle': 'Sun|Oracle|Java', 
                       'apple': 'Apple|iTunes|Safari|Quicktime'}
    
    riskFactors = ['Critical', 'High', 'Medium', 'Low']
    
    rf = vuln.get('risk_factor')
    
    if rf and rf not in 'None':
        rfi = riskFactors.index(rf)
    else:
        return
            
    if 'offenders' not in rpt.stats:
        rpt.stats['offenders'] = {'other': [0,0,0,0]}
        for offender in COMMONOFFENDERS.keys():
            rpt.stats['offenders'][offender] = [0,0,0,0]
    
    for offender, regex in COMMONOFFENDERS.items():
        if offender in 'microsoft':
            if re.search(regex, vuln.plugin_name, re.IGNORECASE) and not re.search(COMMONOFFENDERS['office'], vuln.plugin_name, re.IGNORECASE):
                rpt.stats['offenders'][offender][rfi] += 1
                return
        elif re.search(regex, vuln.plugin_name, re.IGNORECASE):
            rpt.stats['offenders'][offender][rfi] += 1
            return
        
    rpt.stats['offenders']['other'][rfi] += 1
    

def riskFactor(rpt, tgt, vuln):
    
    rf = vuln.get('risk_factor')
    
    if not rf:
        return
                
    if rf == 'Critical':
        rpt.stats['critCount'] += 1
        tgt.stats['critCount'] += 1
        tgt.criticals.append(vuln.plugin_name)
        
    if rf == 'High':
        rpt.stats['highCount'] += 1
        tgt.stats['highCount'] += 1
        tgt.highs.append(vuln.plugin_name)
        
    if rf == 'Medium':
        rpt.stats['mediumCount'] += 1
        tgt.stats['mediumCount'] += 1
        tgt.mediums.append(vuln.plugin_name)
        
    if rf == 'Low':
        rpt.stats['lowCount'] += 1
        tgt.stats['lowCount'] += 1
        tgt.lows.append(vuln.plugin_name)
        
        
def exploitable(rpt, tgt, vuln):
    
    if vuln.get('exploit_available'):
        rpt.stats['pubExploitCount'] += 1
        tgt.stats['pubExploitCount'] += 1
        
    if vuln.get('exploit_framework_metasploit'):
        rpt.stats['metasploitCount'] += 1
        tgt.stats['metasploitCount'] += 1
        
def misc(rpt, tgt, vuln):
    
    if 'Reboot Required' in vuln.plugin_name:
        tgt.reboot = True
        rpt.reboots.append(tgt.get_name())
        
    if 'Log In Possible' in vuln.plugin_name:
        output = vuln.plugin_output.splitlines()
        for pn in output:
            if 'NULL' not in pn and 'Guest' not in pn:
                tgt.credentialed.append(pn)