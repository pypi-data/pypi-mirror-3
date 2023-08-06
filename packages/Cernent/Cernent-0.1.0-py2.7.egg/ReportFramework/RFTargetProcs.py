
def init(rpt, tgt):
    tgt.stats = {}
    tgt.reboot = False
    tgt.criticals, tgt.highs, tgt.mediums, tgt.lows = [],[],[],[]
    tgt.credentialed = []
    
    intVars = ['pubExploitCount', 'metasploitCount', 'lowCount', 'mediumCount', 'highCount', 'critCount']
    for var in intVars:
        tgt.stats[var] = 0
    
def default(rpt, tgt):
    rpt.host[tgt.get_name()] = tgt
    
    pers = [('critPer', 'critCount'),
            ('highPer', 'highCount'),
            ('mediumPer', 'mediumCount'),
            ('lowPer', 'lowCount')]

    for per, count in pers:
        rpt.stats[per].append(tgt.stats[count])
    
    tgt.criticals.sort()
    tgt.highs.sort()
    tgt.mediums.sort()
    tgt.lows.sort()
    tgt.criticalSet = set(tgt.criticals)
    tgt.highSet = set(tgt.highs)
    tgt.mediumSet = set(tgt.mediums)
    tgt.lowSet = set(tgt.lows)