#!/usr/bin/python
description = """This program searches a given Source Directory for files and performs 
a given operationThe reencoded files are stored under target directory
preserving the directory structure. 
it uses https://python3-exiv2.readthedocs.io/en/latest/tutorial.html as exif library
"""

from datetime import timedelta
from datetime import datetime
import os
import fnmatch
import shutil
import sys
import re
import string
import logging
import logging.config 
import json
import yaml
import pyexiv2

#import dataTypes
from dataTypes import RuntimeData

############################################################################
def findTGTFileName(activeSrcCompleteFileName,srcDirName,tgtDirName):
    logging.debug(" activeSrcCompleteFileName = " + activeSrcCompleteFileName)
    logging.debug(" srcDirName = " + srcDirName)
    logging.debug(" tgtDirName = " + tgtDirName)
    #fileName = os.path.basename(activeSrcCompleteFileName)
    srcRelativePathName=activeSrcCompleteFileName[len(srcDirName):]
    logging.debug(" srcRelativePathName = " + srcRelativePathName)
    tgtCompleteFileName = tgtDirName +srcRelativePathName
    logging.debug(" tgtCompleteFileName = " + tgtCompleteFileName)
    (tgtSubdirName,tail)=os.path.split(tgtCompleteFileName)
    logging.debug(" tgtSubdirName = " + tgtDirName)
    if not os.path.exists(tgtSubdirName):
        os.makedirs(tgtSubdirName, mode=0o775 )
    return tgtCompleteFileName
     
############################################################################
def initLogger():
    try: 
        rootLogger = logging.getLogger()
        logging.config.fileConfig("pyLoggerConfig.cfg")
    except:    
        logHandler = logging.StreamHandler(sys.stdout)
        #logging.basicConfig(stream=logHandler)
        rootLogger.addHandler(logHandler)
        rootLogger.setLevel(logging.DEBUG)
        rootLogger.setLevel(logging.INFO)
    return rootLogger

###################################################################################################

###########################################################################
def processFile(activeSrcCompleteFileName, tgtDirName, toolOptions):
    if toolOptions == "flat":
        fullTargetName = os.path.join(tgtDirName, os.path.basename(activeSrcCompleteFileName))
    elif toolOptions == "preserveDirStructure":
        fullTargetName=findTGTFileName(activeSrcCompleteFileName, runtimeData.activeSrcDirName, tgtDirName)
    else:   
      logging.error("unknown option %s" % toolOptions)
      exit
    
    if not os.path.exists(tgtDirName):
      try:
        os.mkdir(tgtDirName)
      except OSError:
         print ("Creation of the directory %s failed" % tgtDirName)
         exit(-1) 
    
    if not os.path.exists(fullTargetName):
      logging.info("shutil.copy2(\"%s\",\"%s\"" % (activeSrcCompleteFileName,tgtDirName ))
      shutil.copy2(activeSrcCompleteFileName,fullTargetName)
    
    # <tbd> remove late
    shutil.copy2(activeSrcCompleteFileName,fullTargetName)
     
    # if runtimeData.previousDateTime"] == "":
    #   runtimeData.previousDateTime"]=
    metadata = pyexiv2.ImageMetadata(fullTargetName)
    # avaliaböe Tags see https://exiv2.org/tags.html
    metadata.read() 
    
    # set DateTime Digitized to fileCreationDate
    fileCreationDate=datetime.fromtimestamp(os.path.getmtime(activeSrcCompleteFileName))
    logging.debug( "fileCreationDate: %s of Image: %s" % (fileCreationDate, fullTargetName) )
    metadata["Exif.Photo.DateTimeDigitized"]=fileCreationDate

    # set new Creation Date 
    runtimeData.dateTimeOrig = metadata['Exif.Image.DateTime'].value
    if runtimeData.previousDateTime == datetime.fromtimestamp(0):
      runtimeData.previousDateTime = runtimeData.dateTimeOrig
    if datetime.date(runtimeData.previousDateTime) == datetime.date(runtimeData.dateTimeOrig) :
      runtimeData.currentIncrement = runtimeData.currentIncrement + inputParams["incrementMinutes"]
    else:  
      runtimeData.currentIncrement = inputParams["dayoffsethours"]*60
    logging.debug( "dateTime: %s of Image: %s" % (runtimeData.dateTimeOrig, fullTargetName) ) 
    incrementedDateTime = runtimeData.dateTimeOrig + timedelta(minutes=runtimeData.currentIncrement)
    metadata['Exif.Image.DateTime'].value = incrementedDateTime
    metadata['Exif.Photo.DateTimeOriginal'].value = incrementedDateTime
    
    
    metadata.write()
    runtimeData.previousDateTime = incrementedDateTime
              
############################################################################
# main starts here
# global variables


rootLogger = initLogger()
# if sys.platform == "win32":
#   defaultEncoding="latin1"
# else:
#   defaultEncoding="UTF-8"

if len(sys.argv) == 1 :
    print(description)
    print((sys.argv[0] + "yaml config file"))
    configFileName = 'config.yaml'
else:
    configFileName=sys.argv[1]

with open(configFileName, 'r') as cfgfile:
    inputParams = yaml.load(cfgfile, Loader=yaml.FullLoader)

runtimeData=RuntimeData()
runtimeData.currentIncrement = inputParams["dayoffsethours"]*60

toolMode=inputParams["toolMode"]
if toolMode == "develop" :
  runtimeData.activeSrcDirName = os.path.join(os.getcwd(),inputParams[toolMode]["srcDirName"])
  runtimeData.activeTgtDirName = os.path.join(os.getcwd(),inputParams[toolMode]["tgtDirName"])
else:
  runtimeData.activeSrcDirName = inputParams[toolMode]["srcDirName"]
  runtimeData.activeTgtDirName = inputParams[toolMode]["tgtDirName"]

# tbd chekci fi this is desirecd
if os.path.exists(runtimeData.activeTgtDirName):
  shutil.rmtree(runtimeData.activeTgtDirName)

for Verz, VerzList, DateiListe in os.walk (runtimeData.activeSrcDirName):
    logging.debug(" VerzList = " + str(VerzList) )
    logging.debug(" DateiListe = " + str(DateiListe))
    for Datei in sorted(DateiListe):
        activeSrcCompleteFileName  = os.path.join(Verz,Datei)
        logging.debug(" acitveSrcCompleteFileName  = " + activeSrcCompleteFileName)
        if fnmatch.fnmatch(activeSrcCompleteFileName, inputParams["fileFilter"]):
            #tgtCompleteFileName = findTGTFileName(activeSrcCompleteFileName, runtimeData.activeSrcDirName"],runtimeData.activeTgtDirName"])
            processFile(activeSrcCompleteFileName, runtimeData.activeTgtDirName, inputParams["toolOptions"])
            
print(("successfully transfered %s " % runtimeData.activeSrcDirName))

