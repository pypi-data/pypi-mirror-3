"""
.. module:: InitMode
   :platform: Unix
   :synopsis: This module needs documentation...

.. moduleauthor:: Chris White
"""
import datetime, readline
from collections import OrderedDict
from ScanEvent import ScanEvent

def printStatusMsg(msg, length=25, char='-'):
    print("\n%s\n%s\n%s\n" % (char * length, msg, char * length))
    
def getUserIn(msg):
    var = raw_input(msg + ": ")
    if var == "":
        print("No input given, try again.")
        return getUserIn(msg)
    return var

def getUserInWithDef(msg, default):
    var = raw_input("%s [%s]: " % (msg, default))
    if var == "":
        return default
    return var

def getIndexedList(ls, start):
    msg = ''
    for i in range(len(ls)) + start:
        index = '[%d]' % i + start
        msg += '%-4s %s\n' % (index, ls[i])
        
    return msg

def getIndexedUserInput(ls, prompt, index=False):
    
    print(getIndexedList(ls))
    if index:
        return getUserInWithDef(prompt, '0')
    else:
        return ls[int(getUserInWithDef(prompt, '0'))]
    
def getMultipleIndexedUserInputList(ls, prompt, index=False):
    selection = []
    print(getIndexedList(ls))
    try:
        if index:
            return [x for x in getUserInWithDef(prompt, '0').replace(' ', '').split(',')]
        else:
            return [ls[int(x)] for x in getUserInWithDef(prompt, '0').replace(' ', '').split(',')]
    except(IndexError):
        print("Please choose from the available options.")
        return getMultipleIndexedUserInputList(ls, prompt, index)
    
#http://stackoverflow.com/questions/2533120/show-default-value-for-editing-on-python-input-possible
def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return raw_input(prompt)
    finally:
        readline.set_startup_hook()


def askYesNo(prompt):
    yes = ("yes", "y")
    no = ("no", "n")
    ans = getUserIn(prompt + ' [y/n]').lower()
    if ans in yes:
        return True
    elif ans in no:
        return False
    else:
        print("Invalid Input, try again.")
        return askYesNo(prompt)
    
def getScanName(template):
    printStatusMsg('Scan Event Prefix')
    print("Please specify the Scan Event name prefix.  Each scan event will have")
    print("a numerical suffix (e.g. MyScanEvent: MyScanEvent1, MyScanEvent2...etc)\n")
    input = getUserIn("Scan Event name(s)")
    
    if not template.setName(input):
        print('Invalid Input, try again.')
        getScanName(template)
    
    

def getNessusScanner(conf, template):
    printStatusMsg('Nessus Scanners')
    input = getIndexedUserInput(conf['scanners'].keys(), 'Nessus Scanner')

    if not template.setScannerName(input):
        print('Invalid Input, try again.')
        getNessusScanner(conf, template)
        
        
def getPolicy(scanners, template):
    scannerName = template.getScannerName()
    scanner = scanners[scannerName]
    printStatusMsg('%s Policies' % scannerName)
    try:
        policies = scanner.getPolicyDict()
        policyName = getIndexedUserInput(sorted(policies.keys()), 'Policy')
        
        if not template.setPolicy(policyName):
            print('Invalid Input, try again.')
            getPolicy(scanners, template)
    except(AttributeError):
        print("%s was not reachable or is misconfigured." % scannerName)
        exit()
        

def getFrequency(template):
    
    def getTime():
        printStatusMsg('Time', 15)
        print('First specify the start time for the scan events. Then specify the minute gap between')
        print('subsequent scan events in this initialization mode.')
        print('e.g. Start Time=11:00 & Gap=60:')
        print('    ScanEvent1 @ 11:00, ScanEvent2 @ 12:00, ScanEvent3 @ 13:00,... etc\n')
        time = getUserInWithDef('24hr Start Time', '08:00')
        try:
            datetime.datetime.strptime(time, '%H:%M')
            return time
        except(ValueError):
            print('Invalid time, try again.')
            return getTime()
    
    def getWeeks():
        printStatusMsg('Weeks', 15)
        ls = ['1st', '2nd', '3rd', '4th']
        return getMultipleIndexedUserInputList(ls, 'Weeks')
    
    def getWeekdays():
        printStatusMsg('Weekdays', 15)
        ls = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return getMultipleIndexedUserInputList(ls, 'Weekdays', True)
        
    printStatusMsg('Schedule')
    ls = ['Daily', 'Weekly', 'Monthly', 'Custom']
    
    dwm = getIndexedUserInput(ls, 'Frequency')
    
    if dwm == 'Custom':
        frequency = getCustomCron()
    else:
        frequency = {'week': '*', 'hour': '*', 
                     'day_of_week': '*', 'month': '*', 
                     'year': '*', 'start_date': datetime.datetime.today().strftime('%Y-%m-%d'), 
                     'minute': '*', 'dwm': dwm}

        weeks = weekdays = None
        
        
        if dwm == 'Monthly':
            weeks = getWeeks()
        
        if dwm == 'Monthly' or dwm == 'Weekly':
            weekdays = getWeekdays()
            
        if dwm == 'Monthly':
            dofw = []
            for week in weeks:
                for weekday in weekdays:
                    dofw.append('%s %s' % (week, weekday))
            frequency['day_of_week'] = ','.join(dofw)
        elif dwm == 'Weekly':
            frequency['day_of_week'] = ','.join(weekdays)
        else:
            frequency['day_of_week'] = '*'
            
        frequency['hour'], frequency['minute'] = getTime().split(':')
        
    if not template.setSchedule(frequency):
        print('Invalid Input, try again.')
        getFrequency(template)
        
def getGap():
    gap = int(getUserInWithDef('Gap in minutes', '60'))
    if isinstance(gap, int) and gap > 0:
        return gap
        
            
def tabFormat(string, tabWidth, columns):
    fstring = ''
    for line in string.splitlines():
        sline = line.split(' ', columns)
        for s in sline:
            fstring += '%-*s' % (tabWidth, s)
        fstring += '\n'
    return fstring
        
#Taken from the cron style job in the APScheduler documentation
#http://packages.python.org/APScheduler/cronschedule.html
def getCustomCron():
    printStatusMsg("Available Fields")
    print(tabFormat('''Field Description
year 4-digit year number
month month number (1-12)
day day of the month (1-31)
week ISO week number (1-53)
day_of_week number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
hour hour (0-23)
minute minute (0-59)
second second (0-59)''', 15, 1)),
        
    printStatusMsg("Expression Types")
    print('''Expression\tField\tDescription
*\t\tany\tFire on every value
*/a\t\tany\tFire every a values, starting from the minimum
a-b\t\tany\tFire on any value within the a-b range (a must be smaller than b)
a-b/c\t\tany\tFire every c values within the a-b range
xth y\t\tday\tFire on the x -th occurrence of weekday y within the month
last x\t\tday\tFire on the last occurrence of weekday x within the month
last\t\tday\tFire on the last day within the month
x,y,z\t\tany\tFire on any matching expression; can combine any number of any of the above expressions''')
    
    printStatusMsg('Cron')
    frequency = OrderedDict([('year', ''), ('month', ''), 
                 ('day', ''), ('week', ''), 
                 ('day_of_week', ''), ('hour', ''), 
                 ('minute', ''), ('second', '')])
    
    for key in frequency.keys():
        frequency[key] = getUserInWithDef(key, '*')
        
    frequency['dwm': 'Custom']
    
    return frequency

def getStartStopNotify(conf):
    printStatusMsg('Start Stop Notify')
    print('Provide the email address(es) you would like to receive email notification')
    print('for the start and stop of the scan. Enter None to disable notifications.')
    print('(e.g. admin1@example.com, admin2@example.com)\n')
    
    start = getUserInWithDef('Scan start notification email(s)', conf['administrators'])
    print('')
    stop = getUserInWithDef('Scan stop notification email(s)', start)
    
    return start, stop

def getScansToKeep(template):
    printStatusMsg('Scans to Keep')
    print('Specify the number of scans to keep between 0 and 10 or Inf for no limit.\n')
    scansToKeep = getUserInWithDef('Scans to keep', '2')
    if template.setScansToKeep(scansToKeep):
        print('\nInvalid input, try again.')
        return getScansToKeep(template)
    
def getEmailItems(conf, template):
    printStatusMsg('Email Item(s)')
    emailItems = []
    cont = True
    while cont:
        name = getUserInWithDef('Email name', 'EmailItem')
        
        #Test code, need to be able to set recipients after the fact
        recipients = 'temporary@example.com'
        
        subject = rlinput('\nSubject: ', conf['subject'])
        
        message = rlinput('\nMessage Body:\n\n', conf['message'])
        
        reports = getUserInWithDef('\nReports', conf['reports'])
        
        # Hey Chris, this is very close an email Item can be created by inserting a list the contents.
        # EmailItem([name, recipients, subject, message, reports])
        # where reports is a list of strings.
        
        # or another example EmailItem(['admin', [admin1@foo.com, admin2@bar.com], 'subject', u'Here are the reports.\\n', ['Concise', 'JavaJRE']]^['exec', 'exec1@foo.com, exec2@bar.com', 'report', u'Here is the report\\n', ['Credentialed']])
        
        #emailItems.append(EmailItem(name, recipients, subject, message, reports))
        
        cont = askYesNo('\nCreate another email item?')
            
    template.setEmailItems(emailItems)
            
    
def initMode(conf, scanners, emailList, targetList):
    
    intro = '''This is the Cernent initialization mode.  You will be asked 
to specify the constants that will be applied to each ScanEvent.  
Your email/target list will then be used to create subsequent Scan Events 
with sequence numbers added as necessary.  You'll be given the option to 
accept, reject or edit a scan event before it is created. The prompts along 
the way will describe any behaviors that may not be obvious during 
initialization mode.\n'''
    
    print(intro)
    
    template = ScanEvent()
    
    getScanName(template)
    #template.setName(getScanName())
    
    getNessusScanner(conf, template)
    #template.setScannerName(getNessusScanner(conf))
    
    getPolicy(scanners, template)
    #template.setPolicy(getPolicy(template.getScannerName(), scanners[template.getScannerName()]))
    
    getFrequency(template)
    #template.setSchedule(getFrequency())
    
    gap = getGap()
    #gap = getUserInWithDef('Gap in minutes', '60')
    
    
    #start, stop = getStartStopNotify(conf)
    #template.setStartNotify(start)
    #template.setStopNotify(stop)
    
    getScansToKeep(template)
    #template.setScansToKeep(getScansToKeep())
    
    getEmailItems(conf, template)
    
    
    

        