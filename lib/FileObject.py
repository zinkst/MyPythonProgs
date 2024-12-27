import os

class FileObject:
  absFileName = ""              # e.g  : /srcfiles/Videos/Favoriten/2024/202400_Sonstige/20020309_Video.mkv
  srcFileDirName = ""           # e.g. : /srcfiles/Videos
  srcRelativeDirName = ""       # e.g. : Favoriten
  fileBaseName = ""             # e.g. : 20020309_Video.mkv
  fileNameWithoutExtension = ""  # e.g. : 20020309_Video
  extension = ""                # e.g. : mkv
  srcRootDir = ""               # e.g. : /srcfiles/Videos
  srcDirRelativeToRootDir = ""  # e.g. : 2024/202400_Sonstige

  def __init__(self, absFileName, srcRootDir, srcRelativeDirName):
    self.absFileName = absFileName
    self.srcRootDir = srcRootDir
    self.srcRelativeDirName = srcRelativeDirName
    self.srcFileDirName = os.path.dirname(self.absFileName)
    self.fileBaseName = os.path.basename(self.absFileName)
    self.extension = os.path.splitext(self.fileBaseName)[1][1:]
    self.srcDirRelativeToRootDir = self.srcFileDirName[len(self.srcRootDir) + len(srcRelativeDirName) + 2:]
    self.fileNameWithoutExtension = os.path.splitext(self.fileBaseName)[0]

  def __str__(self):
    return f"""
  {"fileBaseName".ljust(25, ' ')} : {self.fileBaseName}
  {"dirName".ljust(25, ' ')} : {self.srcFileDirName}
  {"fileBaseName".ljust(25, ' ')} : {self.fileBaseName}
  {"extension".ljust(25, ' ')} : {self.extension}
  {"srcRootDir".ljust(25, ' ')} : {self.srcRootDir}
  {"srcDirRelativeToRootDir".ljust(25, ' ')} : {self.srcDirRelativeToRootDir}
  """
