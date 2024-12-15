#!/usr/bin/python
# -*- coding: utf-8 -*-
description = """This program searches a given Source Directory for files and performs 
a given operation (encode from asciii to utf8). The reencoded files are stored under target directory
preserving the directory structure. 
"""

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


############################################################################
def findTGTFileName(srcCompleteFileName,srcDirName,tgtDirName):
    logging.debug(" srcCompleteFileName = " + srcCompleteFileName)
    logging.debug(" srcDirName = " + srcDirName)
    logging.debug(" tgtDirName = " + tgtDirName)
    #fileName = os.path.basename(srcCompleteFileName)
    srcRelativePathName=srcCompleteFileName[len(srcDirName):]
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

############################################################################
def processFile(srcCompleteFileName, tgtDirName, toolName, toolOptions):
    if toolOptions == "flat":
        fullTargetName = os.path.join(tgtDirName, os.path.basename(srcCompleteFileName))
    elif toolOptions == "preserveDirStructure":
        fullTargetName=findTGTFileName(srcCompleteFileName, inputParams['srcDirName'], tgtDirName)
    else:   
      logging.error("unknown option %s" % toolOptions)
      exit
      
    if not os.path.exists(fullTargetName):
      if toolName == "copy":
        logging.info("shutil.copy2(\"%s\",\"%s\"" % (srcCompleteFileName,tgtDirName ))
        shutil.copy2(srcCompleteFileName,fullTargetName)
      elif toolName == "symlink":
        logging.info("os.symlink( %s ,%s )" % (srcCompleteFileName,tgtDirName ))
        os.symlink(srcCompleteFileName, fullTargetName)
      else:   
        logging.error("unknown command %s" % toolName)
    else:
        logging.info("File.exists(%s )" % (fullTargetName ))
              
############################################################################
# main starts here
# global variables


rootLogger = initLogger()
if sys.platform == "win32":
  defaultEncoding="latin1"
else:
  defaultEncoding="UTF-8"

if len(sys.argv) == 1 :
    print(description)
    print((sys.argv[0] + "<xml_configfile>"))
    configFileName = 'ConvertDirectoryTreeConfig.yaml'
else:
    configFileName=sys.argv[1]

with open(configFileName, 'r',encoding='utf-8') as cfgfile:
    inputParams = yaml.load(cfgfile)


for Verz, VerzList, DateiListe in os.walk (inputParams["srcDirName"]):
    logging.debug(" VerzList = " + str(VerzList) )
    logging.debug(" DateiListe = " + str(DateiListe))
    for Datei in sorted(DateiListe):
        srcCompleteFileName  = os.path.join(Verz,Datei)
        logging.debug(" srcCompleteFileName  = " + srcCompleteFileName)
        if fnmatch.fnmatch(srcCompleteFileName, inputParams["fileFilter"]):
            #tgtCompleteFileName = findTGTFileName(srcCompleteFileName, inputParams["srcDirName"],inputParams["tgtDirName"])
            processFile(srcCompleteFileName, inputParams["tgtDirName"], inputParams["toolName"],inputParams["toolOptions"])
            
print(("successfully transfered %s " % inputParams["srcDirName"]))

