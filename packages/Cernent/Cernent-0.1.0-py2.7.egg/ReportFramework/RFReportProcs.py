def init(rpt):
    rpt.stats = {}
    rpt.host = {}
    rpt.reboots = []
    
    rpt.stats['targetsCount'] = len(rpt.targets)
    
    pers = [('critPer', 'critCount'),
            ('highPer', 'highCount'),
            ('mediumPer', 'mediumCount'),
            ('lowPer', 'lowCount')]
    
    for per, count in pers:
        rpt.stats[per] = []
        
    intVars = ['pubExploitCount', 'metasploitCount', 'lowCount', 'mediumCount', 'highCount', 'critCount']
    
    for var in intVars:
        rpt.stats[var] = 0
    
def popStats(rpt):
    
    avgVars = [('avgCriticals', 'critPer'),
               ('avgHighs', 'highPer'),
               ('avgMediums', 'mediumPer'),
               ('avgLows', 'lowPer')]
            
    if rpt.stats['targetsCount']:
        for avg, per in avgVars:
            rpt.stats[avg] = sum(rpt.stats[per]) / rpt.stats['targetsCount']
    