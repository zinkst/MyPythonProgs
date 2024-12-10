#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import string
import logging
import logging.config 
import os
import re
import time,datetime

import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2
   

    
class FileObject:
  ip = {}
  # keys :
  # ROOT-DIR ,ORIGINALS-DIR,ABS-FAVORITES-TGT-DIR,FAVORITES-TGT-DIR,FAVORITES-SRC-DIR,ABS-ORIGINALS-DIR,ABS-FAVORITES-SRC-DIR'}
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
             "\r\nexifDateTimeString = " + str(self.exifDateTimeString) + \
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
    # if found == False:
    #   found = self.findFileInDirsFuzzy(originalFilesDict)

    self.copiesPathRelativeToRootDir=self.absCopiesOrigDateiName[self.ip["SRC-ROOT-DIR_LENGTH"]+1:]          
    self.copiesDirRelativeToRootDir=os.path.dirname(self.copiesPathRelativeToRootDir)
    lengthCopiesOrigDir= len(self.ip['FAVORITES-SRC-DIR'])
    self.copiesLinkDepthToBaseDir=self.copiesDirRelativeToRootDir.count(os.sep)+inputParams["FAVORITES-TGT-DIR"].count(os.sep)-1
          
    if found == True:  
      self.dateiNameOnOriginalRelativeToRootDir=self.absDateiNameOnOriginal[self.ip["SRC-ROOT-DIR_LENGTH"]+1:]
      self.directoryNameOnOriginalRelativeToRootDir=os.path.dirname(self.dateiNameOnOriginalRelativeToRootDir)
      self.copiesTgtDirRelativeToRootDir=os.path.join(self.ip['FAVORITES-TGT-DIR'],self.copiesDirRelativeToRootDir[lengthCopiesOrigDir+1:] )
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
 

 
#   def findFileInDirsFuzzy(self,originalFilesDict):
#       for curOrigFileName in originalFilesDict:
#           match = re.search(self.fileBaseName,curOrigFileName,re.IGNORECASE)
#           if match != None:
#             self.absDateiNameOnOriginal = originalFilesDict[curOrigFileName]['absOrigFileName']
#             self.foundOriginal = True
#             self.findMethod="CaseInsensitive"
#             break
#           else:
#             curOrigFileId = curOrigFileName.rsplit('_',1)[0]  
#             # special cases
#             #20091108 11:18:38_TaufeVonValentin.jpg
#             #20100215 092113_Fasching im Kindergarten.jpg
#             # IMG_0891=IMG_2210
#             translation_table = dict.fromkeys(map(ord, ': _'), None)
#             curOrigFileIdNormalized = curOrigFileId.translate(translation_table)
#             selfFileIdNormalized = self.fileId.translate(translation_table)
#             match = re.match('\A(\d)+',selfFileIdNormalized,re.UNICODE)
#             if match:
#                 selfFileIdNormalized = match.group(0)
#             else:
#                 # orig Id does not correspond to a date
#                 origExifDateTimeString = originalFilesDict[curOrigFileName]['exifDateTimeString']
#                 logging.debug("exiv no id search for ) "+ str(self.fileBaseName) +" == " +curOrigFileName )
#                 if (self.exifDateTimeString == curOrigFileIdNormalized) and (selfFileIdNormalized != ""):
#                    self.absDateiNameOnOriginal = originalFilesDict[curOrigFileName]['absOrigFileName']
#                    self.findMethod="ExivDate NoID"
#                    self.foundOriginal = True
#                    break
#             logging.debug("fuzzy method 1: "+ selfFileIdNormalized +" == " +curOrigFileIdNormalized )
#             if match and (selfFileIdNormalized == curOrigFileIdNormalized) and (selfFileIdNormalized != ""):
#               self.absDateiNameOnOriginal = originalFilesDict[curOrigFileName]['absOrigFileName']
#               self.findMethod="Fuzzy 1"
#               self.foundOriginal = True
#               break
#               #20100320100413FamilieZinkbeimPhotograph.jpg
# #                   logging.debug("fuzzy method 2: "+ selfFileIdNormalized +" == " +curOrigFileIdNormalized )
# #                   if (selfFileIdNormalized == curOrigFileIdNormalized) and (selfFileIdNormalized != ""):
# #                       self.absDateiNameOnOriginal = originalFilesDict[curOrigFileName]
# #                       self.foundOriginal = True
# #                       self.findMethod="Fuzzy 2"
# #                       break
#             else:
#                #20050907_123010_RadtourWildbadKreuthStrandRottachEgern.jpg ==  20050907_20RadtourWildbadKreuthStrandRottachEgern.JPG  
#                #nur mit exiv date zu lösen benutze gexiv library
#                logging.debug("fuzzy method 3 (exiv) "+ str(self.exifDateTimeString) +" == " +curOrigFileIdNormalized )
#                if (self.exifDateTimeString == curOrigFileIdNormalized) and (selfFileIdNormalized != ""):
#                    self.absDateiNameOnOriginal = originalFilesDict[curOrigFileName]['absOrigFileName']
#                    self.findMethod="ExivDate"
#                    self.foundOriginal = True
#                    break
#       return self.foundOriginal        

 
 
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
      
 ################################################################################################      
#end class      
