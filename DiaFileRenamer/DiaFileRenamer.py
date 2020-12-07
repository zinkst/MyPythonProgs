#!/usr/bin/python
# -*- coding: utf-8 -*-
description = """This program handles hadles directories with absolutelinks to 
favorite Photos, or files with lists to favorites Photos 

ManagePhotoFavorites.py <option> [<xml_configfile>]

where option is one of : 

1: as input a directory containing absolute links to Favorite Photos and create a file  
   containing a list with relative links to those Photos and a file containing absolute links
   
2: as input take a file with a list of relative links and create those links in <workDirName>/linksrel   

3: (not implemented, can be done with a cp option) copy files contained in linksrel to folder files as new files ...

"""

import os
import shutil
import glob
import sys
import re
import string
import logging
import logging.config 
#from xml import dom
from xml.dom import minidom
from xml.dom import Node
import codecs
import csv



############################################################################
    
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

############################################################################
def readConfigFromXML(configFileName):
    try:
        xmldoc = minidom.parse(configFileName)
    except IOError:
        print "config file " + configFileName + " not found"
        sys.exit(1)
        
    #print xmldoc.toxml().encode("utf-8")
    logging.debug(xmldoc.toxml(defaultEncoding))
    configNode = xmldoc.firstChild
    for l1Node in configNode.childNodes:
        if l1Node.nodeName == sys.platform:
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "srcDirName":
                    """ Zugriff auf den Wert des tags """
                    #srcDirName = l2Node.getAttribute("value").encode(defaultEncoding)
                    inputParams["srcDirName"]=l2Node.firstChild.nodeValue.encode(defaultEncoding)
                if l2Node.nodeName == "tgtDirName":
                    """ Zugriff auf ein Attribut des tags """
                    inputParams["tgtDirName"] = l2Node.getAttribute("value").encode(defaultEncoding)
         
        elif l1Node.nodeName == "generic":
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "filePattern":
                    inputParams["filePattern"] = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "simulate":
                    inputParams["SIMULATE"] = l2Node.firstChild.nodeValue
    logging.debug(inputParams) 
    return (inputParams)

############################################################################
def processTgtDir(tgtDirName,filePattern):
    for dir, dirList, fileList in os.walk (tgtDirName):
  #      logging.debug(" dirList = " + str(dirList) )
  #      logging.debug(" fileList = " + str(fileList))
        for file in fileList:
            match = re.search(filePattern,file,re.IGNORECASE)
            if match != None:
                completeFileName = os.path.join(dir,file)
                listOfNewScanDiaFileNames.append(completeFileName)
    return listOfNewScanDiaFileNames        


############################################################################
def findFileInDirsCaseInsensitive(absDirNames,filePattern):
    tgtCompleteFileName = u""
    found= -1
    for dirName in absDirNames:
      #dirName = os.path.join(self.ip["ROOT-DIR"],relDirName)
      for dir, dirList, fileList in os.walk (dirName):
  #      logging.debug(" dirList = " + str(dirList) )
  #      logging.debug(" fileList = " + str(fileList))
        for file in fileList:
          match = re.search(filePattern,file,re.IGNORECASE)
          if match != None:
            tgtCompleteFileName = os.path.join(dir,file)
            found = 1
            break
          else:
            found = -1   
        if found == 1:
          break  
    return tgtCompleteFileName        

############################################################################
def findFileAndCreateRenameCommand(listOfNewScanDiaFileNames,inputParams):
    listOfSrcDirs = []
    listOfSrcDirs.append(inputParms["srcDirName"])
    renameDict = {}
    notFoundKeys = []
    for curNewScan in listOfNewScanDiaFileNames:
        (curBaseName,ext) = os.path.splitext(os.path.basename(curNewScan))
        foundTarget=findFileInDirsCaseInsensitive(listOfSrcDirs, curBaseName)
        if foundTarget == "":
            logging.debug("not found")
        else:    
            logging.debug ("foundTarget = " + foundTarget)
            (curNewPath,curNewFileName)=os.path.split(curNewScan)
            newFileName=os.path.join(curNewPath,os.path.basename(foundTarget))
            renameDict[curNewScan]=newFileName 
    for key, value in renameDict.iteritems():
        logging.debug("calling os.rename("+key+","+value+")")
        if inputParams["SIMULATE"] != "true":  
            os.rename(key, value)
    
    

############################################################################
# main starts here

rootLogger = initLogger()

if sys.platform == "win32":
  #defaultEncoding="latin1"
  defaultEncoding="UTF-8"
else:
  defaultEncoding="UTF-8"


if len(sys.argv) < 1 :
  print description
  print sys.argv[0] + "<xml_configfile>"
elif len(sys.argv) == 1:
  configFileName="DiaFileRenamer.xml" 
else:
  configFileName=sys.argv[2]
#action=sys.argv[1]

inputParams={}

inputParms = readConfigFromXML(configFileName)

# select action

listOfNewScanDiaFileNames = []
listOfNewScanDiaFileNames = processTgtDir(inputParams["tgtDirName"],inputParms["filePattern"])
logging.debug (listOfNewScanDiaFileNames) 
findFileAndCreateRenameCommand(listOfNewScanDiaFileNames, inputParams)
#if action == "1":
#  (listOfAbsoluteLinkNames,listOfRelativeLinkNames) = createFileListFromAbsoluteLinks(workDirName)
#  writeAbsoluteFilenamesList(workDirName, listOfAbsoluteLinkNames)
#  writeRelativeFilenamesList(workDirName, listOfRelativeLinkNames)
#elif action == "2":
#  processFavoritesList_CreateRelativeLinks(srcName)


