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
                    #srcDirName=l2Node.firstChild.nodeValue.encode(defaultEncoding)
                    srcDirName=l2Node.firstChild.nodeValue
                if l2Node.nodeName == "tgtDirName":
                    """ Zugriff auf den Wert des tags """
                    #workDirName = l2Node.firstChild.nodeValue.encode(defaultEncoding)
                    tgtDirName = l2Node.firstChild.nodeValue
                    """ Zugriff auf ein Attribut des tags """
                    #workDirName = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "projectDirName":
                    projectDirName = l2Node.firstChild.nodeValue
                    
        elif l1Node.nodeName == "generic":
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "srcFileName":
                    #srcFilename = l2Node.getAttribute("value").encode(defaultEncoding)
                    srcFileName = l2Node.getAttribute("value")
                if l2Node.nodeName == "tgtFileName":
#                    linkPrefix = l2Node.getAttribute("value").encode(defaultEncoding)
                    tgtFileName = l2Node.getAttribute("value")
                if l2Node.nodeName == "debug":
                    inputParams["DEBUG"] = l2Node.firstChild.nodeValue
#    inputParams={}
             
    inputParams["srcDirName"]=srcDirName.encode(defaultEncoding)
    inputParams["tgtDirName"]=tgtDirName.encode(defaultEncoding)
    inputParams["srcFileName"]=srcFileName.encode(defaultEncoding)
    inputParams["tgtFileName"]=tgtFileName.encode(defaultEncoding)
    inputParams["projectDirName"]=projectDirName.encode(defaultEncoding)
    inputParams["DiaDirName"]="AllDiasScan"
    inputParams["FavDirName"]="FavoritenRelLinks"
    #logging.debug("srcDirName = %s" % inputParams["srcDirName"]) 
    #logging.debug("srcFileName = %s" % inputParams["srcFileName"]) 
    #logging.debug("tgtDirName = %s" % inputParams["tgtDirName"]) 
    #logging.debug("tgtFileName = %s" % inputParams["tgtFileName"]) 
    
    inputParams["srcName"]=os.path.join(inputParams["srcDirName"], inputParams["srcFileName"])
    inputParams["tgtName"]=os.path.join(inputParams["tgtDirName"], inputParams["tgtFileName"])
    
    #logging.info("srcName = %s" % inputParams["srcName"]) 
    #logging.info("tgtName = %s" % inputParams["tgtName"])
    logging.debug(inputParams) 
    return (inputParams)


############################################################################
def processCSVFile(inputParams):
    #logging.debug("addressLines[0] = %s " % str(addressLines[0]))
    try:
        csvReader = csv.reader(open(inputParams["srcName"]), delimiter=',', quotechar='"')
        outfile = codecs.open(inputParams["tgtName"], "wb", "utf8")
        for row in csvReader:
            #print row # row is a list containing all elements
            outline = ""
            for entry in row:
                if entry.isdigit():
                    if len(entry) ==1:
                         entry="0"+entry
                    outline = "1995"+row[0]+entry              
                    logging.debug ("outline=" + outline)  
                    outfile.write(outline + '\r\n')
                    listOfDiaKeys.append(outline)
    except IOError:
        logging.debug("error opening file %s " % inputParams["srcName"]) 
    finally:
     #   outfile.write('\n')
        outfile.close()
    return listOfDiaKeys

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
def findFileAndCreateLinkCommand(listOfDiaKeys,inputParams):
    listOfDiaAbsNames = []
    notFoundKeys = []
    for curDia in listOfDiaKeys:
        listOfDirs = []
        listOfDirs.append(os.path.join(inputParams["projectDirName"],inputParams["DiaDirName"]))
        diaCompleteFileName=findFileInDirsCaseInsensitive(listOfDirs, curDia)
        if diaCompleteFileName == "":
            logging.debug("not found")
            notFoundKeys.append(curDia)
        else:    
            logging.debug ("diaCompleteFileName = " + diaCompleteFileName)
            listOfDiaAbsNames.append(diaCompleteFileName) 
    listOfRelDiaNames = []
    for curDiaAbsName in listOfDiaAbsNames:
        curDiaPathRelativeToRootDir=curDiaAbsName[len(inputParams["projectDirName"]):]
        logging.debug("curDiaPathRelativeToRootDir = " + curDiaPathRelativeToRootDir)
        #listOfRelDiaNames.append(curDiaPathRelativeToRootDir)        
        logging.debug("calling   os.chdir("+inputParams["projectDirName"]+")" )
        os.chdir(inputParams["projectDirName"])
        tgtDir = os.path.join(inputParams["projectDirName"],inputParams["FavDirName"])
        if  not os.path.exists(tgtDir):
            logging.debug("calling   os.makedirs("+tgtDir+",'0775')")
            if inputParams["DEBUG"] != "true": 
                  os.makedirs(tgtDir )#,'0775')
        logging.debug("calling os.chdir("+tgtDir+")")
        os.chdir(tgtDir)
        #newRelLink=os.path.join( "..", curDiaPathRelativeToRootDir)
        newRelLink=".."+ curDiaPathRelativeToRootDir
        linkName=os.path.basename(curDiaPathRelativeToRootDir)
        logging.debug("checking os.symlink("+newRelLink+","+linkName+")")
        if  not os.path.exists(linkName):
            logging.debug("calling os.symlink("+newRelLink+","+linkName+")")
            if inputParams["DEBUG"] != "true":  
                os.symlink(newRelLink,linkName)
    writeNotFoundKeysToFile(notFoundKeys)

############################################################################
def writeNotFoundKeysToFile(notFoundKeys):
    try:
        #outfile = codecs.open(, "wb","latin1","xmlcharrefreplace")
        outFileName=os.path.join(inputParams["projectDirName"],"notFoundKeys.txt" )
        outfile = codecs.open(outFileName, "wb", "utf8")
        try:
          for curNotFoundKey in notFoundKeys:
            outLine=curNotFoundKey
            logging.info("outLine="+outLine)
            outfile.write(outLine + '\n')
        finally:
            outfile.close()
    except IOError:
        logging.info("error opening file %s" % outFileName) 
    return 1



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
  configFileName="ConvertDiaShowCSV.xml" 
else:
  configFileName=sys.argv[2]
#action=sys.argv[1]

inputParams={}

inputParms = readConfigFromXML(configFileName)

# select action

listOfDiaKeys = []
listOfDiaKeys = processCSVFile(inputParams)
logging.debug (listOfDiaKeys) 
findFileAndCreateLinkCommand(listOfDiaKeys, inputParams)
#if action == "1":
#  (listOfAbsoluteLinkNames,listOfRelativeLinkNames) = createFileListFromAbsoluteLinks(workDirName)
#  writeAbsoluteFilenamesList(workDirName, listOfAbsoluteLinkNames)
#  writeRelativeFilenamesList(workDirName, listOfRelativeLinkNames)
#elif action == "2":
#  processFavoritesList_CreateRelativeLinks(srcName)


