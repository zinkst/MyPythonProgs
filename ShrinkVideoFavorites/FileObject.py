#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import ffmpeg  # dnf install python3-ffmpeg-python.noarch


class FileObject:
  absFileName = ""              # e.g  : /srcfiles/Videos/2024/202400_Sonstige/20020309_Video.mkv
  dirName = ""                  # e.g. : /srcfiles/Videos/2024/202400_Sonstige/
  fileBaseName = ""             # e.g. : 20020309_Video.mkv
  extension = ""                # e.g. : mkv
  srcRootDir = ""               # e.g. : /srcfiles/Videos
  srcDirRelativeToRootDir = ""  # e.g. : Videos/2024/202400_Sonstige/

  def __init__(self, absFileName, srcRootDir):
    self.absFileName = absFileName
    self.dirName = os.path.dirname(self.absFileName)
    self.fileBaseName = os.path.basename(self.absFileName)
    self.extension = os.path.splitext(self.fileBaseName)[1][1:]
    self.srcRootDir = srcRootDir
    self.srcDirRelativeToRootDir = self.dirName[len(self.srcRootDir) + 1:]

  def __str__(self):
    return f"""
  absFileName             : {self.absFileName}
  dirName                 : {self.dirName}
  fileBaseName            : {self.fileBaseName}
  extension               : {self.extension}
  srcRootDir              : {self.srcRootDir}
  srcDirRelativeToRootDir : {self.srcDirRelativeToRootDir}
  """

  def ProbeVideoFile(self):
    videoMetadata = ffmpeg.probe(self.absFileName)
    print (videoMetadata['streams'])
