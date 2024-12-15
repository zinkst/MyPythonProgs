#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import string
import logging
import logging.config 
import os
import re
import time,datetime
from gi.repository import GExiv2
   

    
class FileObject:
 
  """
'ROOT-DIR': '/home/zinks/Stefan/myPrg/MyPythonPrgs/SearchAndCopyFileFromOriginalDir/testdata/'
'ORIGINALS-DIR': u'src/Alben'
'COPIES-TGT-DIR': u'test/car_new'
'COPIES-ORIG-DIR': u'test/car'
'ABS-COPIES-TGT-DIR': u'/home/zinks/Stefan/myPrg/MyPythonPrgs/SearchAndCopyFileFromOriginalDir/testdata/test/car_new'
'ABS-COPIES-ORIG-DIR': u'/home/zinks/Stefan/myPrg/MyPythonPrgs/SearchAndCopyFileFromOriginalDir/testdata/test/car'

fileBaseName = 01_Atlantic.mp3
absCopiesOrigDateiName = /home/zinks/Stefan/myPrg/MyPythonPrgs/SearchAndCopyFileFromOriginalDir/testdata/test/car/010MP3CAR/01_Keane_Under The Iron Sea/01_Atlantic.mp3
copiesPathRelativeToRootDir = test/car/010MP3CAR/01_Keane_Under The Iron Sea/01_Atlantic.mp3
copiesDirRelativeToRootDir = test/car/010MP3CAR/01_Keane_Under The Iron Sea
copiesTgtDirRelativeToRootDir=
copiesLinkDepthToBaseDir = 4
absDateiNameOnOriginal = /home/zinks/Stefan/myPrg/MyPythonPrgs/SearchAndCopyFileFromOriginalDir/testdata/src/Alben/Keane/Under The Iron Sea/01_Atlantic.mp3
dateiNameOnOriginalRelativeToRootDir = src/Alben/Keane/Under The Iron Sea/01_Atlantic.mp3
directoryNameOnOriginalRelativeToRootDir = src/Alben/Keane/Under The Iron Sea

    fileBaseName = 20100320100413FamilieZinkbeimPhotograph.jpg
    absCopiesOrigDateiName = /links/persdata/Stefan/myPrg/MyPythonPrgs/SearchAndCopyFileFromOriginalDir/testdata/Photo/src/1_bisherigeBestellungen/2010/20101107_FotobuchItalienUndSchweden/FotobuchBilder/20100320100413FamilieZinkbeimPhotograph.jpg
    copiesPathRelativeToRootDir = src/1_bisherigeBestellungen/2010/20101107_FotobuchItalienUndSchweden/FotobuchBilder/20100320100413FamilieZinkbeimPhotograph.jpg
    copiesDirRelativeToRootDir = src/1_bisherigeBestellungen/2010/20101107_FotobuchItalienUndSchweden/FotobuchBilder
    copiesTgtDirRelativeToRootDir = Entwickeln_Not_Found_Files_Dir/1_bisherigeBestellungen/2010/20101107_FotobuchItalienUndSchweden/FotobuchBilder
    copiesLinkDepthToBaseDir = 0
    absDateiNameOnOriginal = 
    dateiNameOnOriginalRelativeToRootDir = 
    directoryNameOnOriginalRelativeToRootDir = 
    foundOriginal = False
    fileId = 20100320100413FamilieZinkbeimPhotograph.jpg

  """
  ip = {}
  # keys :
  # ROOT-DIR ,ORIGINALS-DIR,ABS-COPIES-TGT-DIR,COPIES-TGT-DIR,COPIES-ORIG-DIR,ABS-ORIGINALS-DIR,ABS-COPIES-ORIG-DIR'}
  absCopiesOrigDateiName = u""
  fileBaseName    = u""
  fileId = u""
  absDateiNameOnOriginal = u""
  copiesPathRelativeToRootDir = u"" 
  copiesDirRelativeToRootDir = u""
  copiesTgtDirRelativeToRootDir=u""
  copiesLinkDepthToBaseDir = 0
  dateiNameOnOriginalRelativeToRootDir = u""
  directoryNameOnOriginalRelativeToRootDir = u""
  exifDateTimeString = None
  foundOriginal = False
  findMethod = "no"
   
  def printOut(self):
    output = "\r\nfileBaseName = " + self.fileBaseName + \
             "\r\nabsCopiesOrigDateiName = " + self.absCopiesOrigDateiName + \
             "\r\ncopiesPathRelativeToRootDir = " + self.copiesPathRelativeToRootDir + \
             "\r\ncopiesDirRelativeToRootDir = " + self.copiesDirRelativeToRootDir + \
             "\r\ncopiesTgtDirRelativeToRootDir = " + self.copiesTgtDirRelativeToRootDir + \
             "\r\ncopiesLinkDepthToBaseDir = " + str(self.copiesLinkDepthToBaseDir) + \
             "\r\nabsDateiNameOnOriginal = " + self.absDateiNameOnOriginal + \
             "\r\ndateiNameOnOriginalRelativeToRootDir = " + self.dateiNameOnOriginalRelativeToRootDir + \
             "\r\ndirectoryNameOnOriginalRelativeToRootDir = " + self.directoryNameOnOriginalRelativeToRootDir + \
             "\r\exifDateTimeString = " + str(self.exifDateTimeString) + \
             "\r\nfindMethod = " + self.findMethod + \
             "\r\nfoundOriginal = " + str(self.foundOriginal) + \
             "\r\nfileId = " + self.fileId + \
             "\r\n"
    return output
  

  def getDateTimeStringFromExif(absDateiName):
      retVal = None
      try:
          src_exif = GExiv2.Metadata(absDateiName)
          exifDateTime = src_exif['Exif.Photo.DateTimeOriginal']
          if exifDateTime is not None:
              # Python2
              #self.exifDateTimeString=exifDateTime.translate(None,': _')
              #Python 3
              trantab = str.maketrans({'_':'', ' ':'', ':':''})
              retVal = exifDateTime.translate(trantab)
      except KeyError:
          logging.debug("Image " + absDateiName + " does not have exiv date time")
      except:
          logging.debug("Fatal error " + absDateiName + " does not have exiv date time")
      return retVal 

  def initialize(self,inputParams,in_absCopiesOrigDateiName, originalFilesDict):
    self.ip = inputParams
    self.absCopiesOrigDateiName = in_absCopiesOrigDateiName
    self.fileBaseName = os.path.basename(self.absCopiesOrigDateiName)
    self.fileId = self.fileBaseName.rsplit('_',1)[0]
    found = False 
    self.exifDateTimeString = FileObject.getDateTimeStringFromExif(self.absCopiesOrigDateiName)
    found = self.findFileInDirsExact(originalFilesDict)
    # TODO handle mutiple hits
    logging.debug("Found Exact Match for: "+ self.fileBaseName)
    if found == False:
      found = self.findFileInDirsFuzzy(originalFilesDict)

    self.copiesPathRelativeToRootDir=self.absCopiesOrigDateiName[self.ip["ROOT-DIR_LENGTH"]:]          
    self.copiesDirRelativeToRootDir=os.path.dirname(self.copiesPathRelativeToRootDir)
    lengthCopiesOrigDir= len(self.ip['COPIES-ORIG-DIR'])
    self.copiesLinkDepthToBaseDir=self.copiesTgtDirRelativeToRootDir.count(os.sep) # +1
          
    if found == True:  
      self.dateiNameOnOriginalRelativeToRootDir=self.absDateiNameOnOriginal[self.ip["ROOT-DIR_LENGTH"]:]
      self.directoryNameOnOriginalRelativeToRootDir=os.path.dirname(self.dateiNameOnOriginalRelativeToRootDir)
      self.copiesTgtDirRelativeToRootDir=os.path.join(self.ip['COPIES-TGT-DIR'],self.copiesDirRelativeToRootDir[lengthCopiesOrigDir+1:] )
    else:
      self.copiesTgtDirRelativeToRootDir=os.path.join(self.ip['NOTFOUND_FILES_TGT_DIR'],self.copiesDirRelativeToRootDir[lengthCopiesOrigDir+1:] )
          
      

  def findFileInDirsExact(self,originalFilesDict):
      if self.fileBaseName in originalFilesDict:
          self.absDateiNameOnOriginal = originalFilesDict[self.fileBaseName]['absOrigFileName']
          self.foundOriginal = True
          self.findMethod="Exact"
      else:
            self.foundOriginal = False   
      return self.foundOriginal        
 

 
  def findFileInDirsFuzzy(self,originalFilesDict):
      for curOrigFileName in originalFilesDict:
          match = re.search(self.fileBaseName,curOrigFileName,re.IGNORECASE)
          if match != None:
            self.absDateiNameOnOriginal = originalFilesDict[curOrigFileName]['absOrigFileName']
            self.foundOriginal = True
            self.findMethod="CaseInsensitive"
            break
          else:
            curOrigFileId = curOrigFileName.rsplit('_',1)[0]  
            # special cases
            #20091108 11:18:38_TaufeVonValentin.jpg
            #20100215 092113_Fasching im Kindergarten.jpg
            # IMG_0891=IMG_2210
            translation_table = dict.fromkeys(map(ord, ': _'), None)
            curOrigFileIdNormalized = curOrigFileId.translate(translation_table)
            selfFileIdNormalized = self.fileId.translate(translation_table)
            match = re.match('\A(\d)+',selfFileIdNormalized,re.UNICODE)
            if match:
                selfFileIdNormalized = match.group(0)
            else:
                # orig Id does not correspond to a date
                origExifDateTimeString = originalFilesDict[curOrigFileName]['exifDateTimeString']
                logging.debug("exiv no id search for ) "+ str(self.fileBaseName) +" == " +curOrigFileName )
                if (self.exifDateTimeString == curOrigFileIdNormalized) and (selfFileIdNormalized != ""):
                   self.absDateiNameOnOriginal = originalFilesDict[curOrigFileName]['absOrigFileName']
                   self.findMethod="ExivDate NoID"
                   self.foundOriginal = True
                   break
            logging.debug("fuzzy method 1: "+ selfFileIdNormalized +" == " +curOrigFileIdNormalized )
            if match and (selfFileIdNormalized == curOrigFileIdNormalized) and (selfFileIdNormalized != ""):
              self.absDateiNameOnOriginal = originalFilesDict[curOrigFileName]['absOrigFileName']
              self.findMethod="Fuzzy 1"
              self.foundOriginal = True
              break
              #20100320100413FamilieZinkbeimPhotograph.jpg
#                   logging.debug("fuzzy method 2: "+ selfFileIdNormalized +" == " +curOrigFileIdNormalized )
#                   if (selfFileIdNormalized == curOrigFileIdNormalized) and (selfFileIdNormalized != ""):
#                       self.absDateiNameOnOriginal = originalFilesDict[curOrigFileName]
#                       self.foundOriginal = True
#                       self.findMethod="Fuzzy 2"
#                       break
            else:
               #20050907_123010_RadtourWildbadKreuthStrandRottachEgern.jpg ==  20050907_20RadtourWildbadKreuthStrandRottachEgern.JPG  
               #nur mit exiv date zu lösen benutze gexiv library
               logging.debug("fuzzy method 3 (exiv) "+ str(self.exifDateTimeString) +" == " +curOrigFileIdNormalized )
               if (self.exifDateTimeString == curOrigFileIdNormalized) and (selfFileIdNormalized != ""):
                   self.absDateiNameOnOriginal = originalFilesDict[curOrigFileName]['absOrigFileName']
                   self.findMethod="ExivDate"
                   self.foundOriginal = True
                   break
      return self.foundOriginal        

 
 
  def comparePicturesByExifDate(self,curOrigFullFileName):
     try:
         src_exif = GExiv2.Metadata(self.absCopiesOrigDateiName)
         src_ExifDate = src_exif.get_date_time().strftime('%Y%m%d%H%M%S')
         #logging.DEBUG("src-exifTimeStamp for " + self.fileBaseName + " is " + src_ExifDate)
         tgt_exif = GExiv2.Metadata(curOrigFullFileName)
         tgt_ExifDate = tgt_exif.get_date_time().strftime('%Y%m%d%H%M%S')
         #logging.DEBUG("tgt-exifTimeStamp for " + os.path.basename(curOrigFullFileName) + " is " +tgt_ExifDate) )
         if src_ExifDate == tgt_ExifDate:
             return True
         else:
             return False
     except:
        logging.debug("Image does not have exiv date time")
        return False
      
 
 ############################################################### 
  def oldfindFileInDirsExact(self,dirNames):
    for relDirName in dirNames:
      dirName = os.path.join(self.ip["ROOT-DIR"],relDirName)
      logging.debug(" dirName = " + dirName )
      for dir, dirList, fileList in os.walk (dirName):
  #      logging.debug(" dirList = " + str(dirList) )
  #      logging.debug(" fileList = " + str(fileList))
        for file in fileList:
          if file == self.fileBaseName:
            self.absDateiNameOnOriginal = os.path.join(dir,file)
            self.foundOriginal = True
            break
          else:
            self.foundOriginal = False   
        if self.foundOriginal == True:
          break  
    return self.foundOriginal        

  def oldfindFileInDirsFuzzy(self,dirNames):
    for relDirName in dirNames:
      dirName = os.path.join(self.ip["ROOT-DIR"],relDirName)
      logging.debug(" dirName = " + dirName )
      for dir, dirList, fileList in os.walk (dirName):
  #      logging.debug(" dirList = " + str(dirList) )
  #      logging.debug(" fileList = " + str(fileList))
        for curOrigFile in fileList:
          match = re.search(self.fileBaseName,curOrigFile,re.IGNORECASE)
          if match != None:
            self.absDateiNameOnOriginal = os.path.join(dir,curOrigFile)
            self.foundOriginal = True
            break
          else:
            curOrigFileId = curOrigFile.rsplit('_',1)[0]  
            # special cases
            #20091108 11:18:38_TaufeVonValentin.jpg
            #20100215 092113_Fasching im Kindergarten.jpg
            #20100320100413FamilieZinkbeimPhotograph.jpg
            translation_table = dict.fromkeys(map(ord, ': _'), None)
            curOrigFileIdNormalized = curOrigFileId.translate(translation_table)
            selfFileIdNormalized = self.fileId.translate(translation_table)
            if selfFileIdNormalized == curOrigFileIdNormalized:
              self.absDateiNameOnOriginal = os.path.join(dir,curOrigFile)
              self.foundOriginal = True
              break
          self.foundOriginal = False   
        if self.foundOriginal == True:
          break  
    return self.foundOriginal        


################################################################################################      
#end class      
