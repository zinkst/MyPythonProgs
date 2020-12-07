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
                  
        elif l1Node.nodeName == "generic":
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "srcFileName":
                    #srcFilename = l2Node.getAttribute("value").encode(defaultEncoding)
                    srcFileName = l2Node.getAttribute("value")
                if l2Node.nodeName == "tgtFileName":
#                    linkPrefix = l2Node.getAttribute("value").encode(defaultEncoding)
                    tgtFileName = l2Node.getAttribute("value")
                                 
#    inputParams={}
             
    inputParams["srcDirName"]=srcDirName.encode(defaultEncoding)
    inputParams["tgtDirName"]=tgtDirName.encode(defaultEncoding)
    inputParams["srcFileName"]=srcFileName.encode(defaultEncoding)
    inputParams["tgtFileName"]=tgtFileName.encode(defaultEncoding)
    
    logging.debug("srcDirName = %s" % inputParams["srcDirName"]) 
    logging.debug("srcFileName = %s" % inputParams["srcFileName"]) 
    logging.debug("tgtDirName = %s" % inputParams["tgtDirName"]) 
    logging.debug("tgtFileName = %s" % inputParams["tgtFileName"]) 
    
    inputParams["srcName"]=os.path.join(inputParams["srcDirName"], inputParams["srcFileName"])
    inputParams["tgtName"]=os.path.join(inputParams["tgtDirName"], inputParams["tgtFileName"])
    
    logging.info("srcName = %s" % inputParams["srcName"]) 
    logging.info("tgtName = %s" % inputParams["tgtName"]) 
    return (inputParams)


############################################################################
def processFile(inputParams):
    #logging.debug("addressLines[0] = %s " % str(addressLines[0]))
    try:
        fsock = codecs.open(inputParams["srcName"], "rb", "utf8")
        outfile = codecs.open(inputParams["tgtName"], "wb", "utf8")
        try:
            nextLine=fsock.readline()
            nextLine=nextLine.rstrip('\r\n')
            logging.debug("curLine="+nextLine)
            while nextLine:
                ## put your line handling code here ###
                arrowIndex = nextLine.find('->')
                outline = nextLine[arrowIndex+2:]  
                
                outline = 'ln -sf "' + outline +'"'
                logging.debug("outline="+outline)
                  
                outfile.write(outline + '\r\n')
                ###################
                nextLine=fsock.readline()
                nextLine=nextLine.rstrip('\r\n')
        finally:
            fsock.close()
            outfile.write('\n')
            outfile.close()
    except IOError:
        logging.debug("error opening file %s " % inputParams["srcName"]) 
    return 1




############################################################################
# main starts here

rootLogger = initLogger()

if sys.platform == "win32":
  #defaultEncoding="latin1"
  defaultEncoding="UTF-8"
else:
  defaultEncoding="UTF-8"


if len(sys.argv) < 2 :
  print description
  print sys.argv[0] + "<xml_configfile>"
elif len(sys.argv) == 2:
  configFileName="ProcessFile.xml" 
else:
  configFileName=sys.argv[2]
action=sys.argv[1]

inputParams={}

inputParms = readConfigFromXML(configFileName)

# select action

processFile(inputParams)
#print "action = " + action 
#if action == "1":
#  (listOfAbsoluteLinkNames,listOfRelativeLinkNames) = createFileListFromAbsoluteLinks(workDirName)
#  writeAbsoluteFilenamesList(workDirName, listOfAbsoluteLinkNames)
#  writeRelativeFilenamesList(workDirName, listOfRelativeLinkNames)
#elif action == "2":
#  processFavoritesList_CreateRelativeLinks(srcName)


