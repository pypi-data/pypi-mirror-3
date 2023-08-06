def sanitize(timeString):
    if '-' in timeString:
        splitter = '-'
    elif ':' in timeString:
        splitter = ':'
    else:
        return timeString
    (mins,secs) = timeString.split(splitter)
    return (mins+'.'+secs)
def GetCoachData(filePath):
    try:
        with open(filePath) as fileData:
            return fileData.readline().strip().split(',')
    except IOError as ioErr:
        print('File Error: '+ str(ioErr))
        return(None)
class AthleteList(list):
    def __init__(self,athleteName,athleteDob=None,athleteTimes=[]):
        list.__init__([])
        self.name = athleteName
        self.extend(athleteTimes)
        self.dob = athleteDob
    def top3(self):
        return (sorted(set([sanitize(t) for t in self]))[0:3])
