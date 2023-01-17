#!/usr/bin/python
description = """This program searches a given Source Directory for files and performs 
a given operationThe reencoded files are stored under target directory
preserving the directory structure. 
it offers various options to compute the Image timestamp an uses https://python3-exiv2.readthedocs.io/en/latest/tutorial.html as exif library
"""

from datetime import timedelta
from datetime import datetime
from mimetypes import init
import os
import fnmatch
import shutil
import sys
import re
import string
import logging
import logging.config 
import json
from tabnanny import filename_only
import yaml
import pyexiv2
import shlex
import subprocess

from dataTypes import RuntimeData

############################################################################
def findTGTFileName(activeSrcCompleteFileName,srcDirName,tgtDirName):
    # logging.debug("activeSrcCompleteFileName = " + activeSrcCompleteFileName)
    # logging.debug("srcDirName = " + srcDirName)
    # logging.debug("tgtDirName = " + tgtDirName)
    
    if inputParams["toolOptions"] == "flat":
      tgtCompleteFileName = os.path.join(tgtDirName, os.path.basename(activeSrcCompleteFileName))
    elif inputParams["toolOptions"] == "preserveDirStructure":
      srcRelativePathName=activeSrcCompleteFileName[len(srcDirName):]
      logging.debug(" srcRelativePathName = " + srcRelativePathName)
      tgtCompleteFileName = tgtDirName +srcRelativePathName
      logging.debug(" tgtCompleteFileName = " + tgtCompleteFileName)
      (tgtSubdirName,tail)=os.path.split(tgtCompleteFileName)
      logging.debug(" tgtSubdirName = " + tgtDirName)
      if not os.path.exists(tgtSubdirName):
        os.makedirs(tgtSubdirName, mode=0o775 )
    else:   
      logging.error("unknown option %s" % inputParams["toolOptions"])
      exit(-1)
    
    if not os.path.exists(tgtDirName):
      try:
        os.mkdir(tgtDirName)
      except OSError:
         print ("Creation of the directory %s failed" % tgtDirName)
         exit(-1) 
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
def setTimestampFromDJIExportFilename(activeSrcCompleteFileName, activeTgtCompleteFileName, toolOptions):
    shutil.copy2(activeSrcCompleteFileName,activeTgtCompleteFileName)
    logging.info("Processing %s" %(os.path.basename(activeTgtCompleteFileName))) 
    metadata = pyexiv2.ImageMetadata(activeTgtCompleteFileName)
    # avaliable Tags see https://exiv2.org/tags.html
    metadata.read() 
    # /testdata/src/0731/dji_export_1659184032750.jpg
    filename_only=os.path.basename(activeTgtCompleteFileName)
    epochTimestamp=int(re.search(r"^dji_export_([0-9]*).jpg", filename_only).group(1))
    fileTimestamp = datetime.fromtimestamp(epochTimestamp/1000.0)
    metadata["Exif.Photo.DateTimeDigitized"]=fileTimestamp
    metadata['Exif.Photo.DateTimeOriginal']=fileTimestamp
    metadata['Exif.Image.DateTime']=fileTimestamp
    metadata.write()

###################################################################################################
def setTimestampFromWhatsAppFilename(activeSrcCompleteFileName, activeTgtCompleteFileName, toolOptions):
    shutil.copy2(activeSrcCompleteFileName,activeTgtCompleteFileName)
    logging.info("Processing %s" %(os.path.basename(activeTgtCompleteFileName))) 
    metadata = pyexiv2.ImageMetadata(activeTgtCompleteFileName)
    # avaliable Tags see https://exiv2.org/tags.html
    metadata.read() 
    # WhatsApp Image 2022-12-15 at 19.28.35.jpeg
    filename_only=os.path.basename(activeTgtCompleteFileName)
    rex1 = re.compile(r"^WhatsApp Image ([0-9-]*) at ([0-9.]*).jpeg")
    reMatch = rex1.match(filename_only)
    fileTSstr=reMatch.group(1) + " at " + reMatch.group(2) 
    fileTimestamp = datetime.strptime(fileTSstr, "%Y-%m-%d at %H.%M.%S")
    logging.debug( "fileTimestamp: %s" % (fileTimestamp) ) 
    #fileTimestamp = datetime.fromtimestamp(epochTimestamp/1000.0)
    metadata["Exif.Photo.DateTimeDigitized"]=fileTimestamp
    metadata['Exif.Photo.DateTimeOriginal']=fileTimestamp
    metadata['Exif.Image.Make']="WhatsApp"
    metadata['Exif.Image.Model']="Import"
    metadata
    metadata.write()
    os.utime(activeTgtCompleteFileName, (fileTimestamp.timestamp(),fileTimestamp.timestamp()))
    
   
###########################################################################
def incrementTimestampFromFixedValue(activeSrcCompleteFileName, activeTgtCompleteFileName, toolOptions):
    shutil.copy2(activeSrcCompleteFileName,activeTgtCompleteFileName)
    logging.info("Processing %s" %(os.path.basename(activeTgtCompleteFileName))) 
    metadata = pyexiv2.ImageMetadata(activeTgtCompleteFileName)
    # avaliable Tags see https://exiv2.org/tags.html
    metadata.read() 
    initialTimestamp=datetime(2022, 8, 6, 9, 20,0)
    if  runtimeData.previousDateTime == datetime(1970, 1, 1, 1, 0):
      runtimeData.previousDateTime=initialTimestamp
      runtimeData.currentIncrement=0  
    else:
      runtimeData.currentIncrement = inputParams["incrementMinutes"]
    incrementedDateTime = runtimeData.previousDateTime + timedelta(minutes=runtimeData.currentIncrement)
    metadata["Exif.Photo.DateTimeDigitized"]=incrementedDateTime
    metadata['Exif.Photo.DateTimeOriginal']=incrementedDateTime
    metadata['Exif.Image.DateTime']=incrementedDateTime
    metadata.write()
    os.utime(activeTgtCompleteFileName, (incrementedDateTime.timestamp(),incrementedDateTime.timestamp()))
    runtimeData.previousDateTime=incrementedDateTime
    
###########################################################################
def incrementTimestampFromMtime(activeSrcCompleteFileName, activeTgtCompleteFileName, toolOptions):
    shutil.copy2(activeSrcCompleteFileName,activeTgtCompleteFileName)
    logging.info("Processing %s" %(os.path.basename(activeTgtCompleteFileName))) 
    metadata = pyexiv2.ImageMetadata(activeTgtCompleteFileName)
    # avaliable Tags see https://exiv2.org/tags.html
    metadata.read() 
    
    # set DateTime Digitized to fileCreationDate
    fileCreationDate=datetime.fromtimestamp(os.path.getmtime(activeSrcCompleteFileName))
    # try:
    #   metadata["Exif.Photo.DateTimeDigitized"].raw_value
    # except KeyError: 
    #   logging.debug( "fileCreationDate: %s of Image: %s" % (fileCreationDate, activeTgtCompleteFileName) )
    #   metadata["Exif.Photo.DateTimeDigitized"]=fileCreationDate
    metadata["Exif.Photo.DateTimeDigitized"]=fileCreationDate
    # copy comment to Image Title
    try:
      metadata["Xmp.dc.title"].raw_value
    except KeyError: 
      comment=metadata["Exif.Photo.UserComment"].value
      if comment != "":
        metadata["Xmp.dc.title"] = {'x-default': comment }
    
    # set new Creation Date 
    try: 
      runtimeData.dateTimeOrig = metadata['Exif.Image.DateTime'].value
    except KeyError: 
      logging.warning("could not get Photo.DateTime for %s" % (activeTgtCompleteFileName))
      try:
        runtimeData.dateTimeOrig = metadata['Exif.Photo.DateTimeOriginal'].value
      except KeyError: 
        logging.warning("could not get Photo.DateTimeOriginal for %s" % (activeTgtCompleteFileName))
        runtimeData.dateTimeOrig = fileCreationDate
    if runtimeData.previousDateTime == datetime.fromtimestamp(0):
      runtimeData.previousDateTime = runtimeData.dateTimeOrig
    if datetime.date(runtimeData.previousDateTime) == datetime.date(runtimeData.dateTimeOrig) :
      runtimeData.currentIncrement = runtimeData.currentIncrement + inputParams["incrementMinutes"]
    else:  
      runtimeData.currentIncrement = inputParams["dayoffsethours"]*60
    logging.debug( "dateTime: %s of Image: %s" % (runtimeData.dateTimeOrig, activeTgtCompleteFileName) ) 
    incrementedDateTime = runtimeData.dateTimeOrig + timedelta(minutes=runtimeData.currentIncrement)
    try:
      metadata['Exif.Image.DateTime'].value = incrementedDateTime
    except KeyError: 
      logging.warning("could not set Photo.DateTime for %s" % (activeTgtCompleteFileName))
    metadata['Exif.Photo.DateTimeOriginal'].value = incrementedDateTime
    # The following doesn't work with pyeviv2 => need to use exiftool to set 
    # metadata['Exif.GPSInfo.GPSTimeStamp'].value = incrementedDateTime
    metadata.write()
    
    # setGPSTimeStamp(activeTgtCompleteFileName)

    os.utime(activeTgtCompleteFileName, (fileCreationDate.timestamp(), incrementedDateTime.timestamp()))
    runtimeData.previousDateTime = incrementedDateTime

############################################################################
def setGPSTimeStamp(activeTgtCompleteFileName):
    cmd=shlex.split("exiftool -P -m -overwrite_original \"-GPSTimeStamp<DateTimeOriginal\" \"-GPSDateStamp<DateTimeOriginal\"")
    cmd.append(activeTgtCompleteFileName) 
    result = subprocess.run(cmd,stdout=subprocess.PIPE,universal_newlines=True)
    if result.returncode !=0:
      logging.warning("Could not write GPSDateStamp for %s error %s" % (activeTgtCompleteFileName, result.stdout) )

###########################################################################
def processFile(activeSrcCompleteFileName, activeTgtCompleteFileName, toolOptions):
    setTimestampFromWhatsAppFilename(activeSrcCompleteFileName, activeTgtCompleteFileName, toolOptions)
    #incrementTimestampFromFixedValue(activeSrcCompleteFileName, activeTgtCompleteFileName, toolOptions)
    #incrementTimestampFromMtime(activeSrcCompleteFileName, activeTgtCompleteFileName, toolOptions)
    #setTimestampFromDJIExportFilename(activeSrcCompleteFileName, activeTgtCompleteFileName, toolOptions)

############################################################################
# main starts here
# global variables


rootLogger = initLogger()

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
else:
  runtimeData.activeSrcDirName = inputParams[toolMode]["srcDirName"]
runtimeData.activeTgtDirName = inputParams["tgtDirName"]

# TODO check if this is desired
if os.path.exists(runtimeData.activeTgtDirName):
  shutil.rmtree(runtimeData.activeTgtDirName)

for Verz, VerzList, DateiListe in os.walk (runtimeData.activeSrcDirName):
    logging.debug(" VerzList = " + str(VerzList) )
    logging.debug(" DateiListe = " + str(DateiListe))
    for Datei in sorted(DateiListe):
        activeSrcCompleteFileName  = os.path.join(Verz,Datei)
        logging.debug(" acitveSrcCompleteFileName  = " + activeSrcCompleteFileName)
        if fnmatch.fnmatch(activeSrcCompleteFileName, inputParams["fileFilter"]):
            activeTgtCompleteFileName = findTGTFileName(activeSrcCompleteFileName, runtimeData.activeSrcDirName,runtimeData.activeTgtDirName)
            processFile(activeSrcCompleteFileName, activeTgtCompleteFileName, inputParams["toolOptions"])
            
logging.info(("successfully transfered %s " % runtimeData.activeSrcDirName))

