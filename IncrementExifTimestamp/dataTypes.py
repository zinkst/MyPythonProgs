from datetime import datetime

class RuntimeData:
  def __init__(self):  
    self.previousDateTime = datetime.fromtimestamp(0)
    self.dateTimeOrig = datetime.fromtimestamp(0)
  
  currentIncrement = 0
  activeSrcDirName = ""
  activeTgtDirName = ""
