#!/usr/bin/python
# -*- coding: utf-8 -*-
description = """This program handles handles directories with relativeLinks to 
favorite Photos and swap the links with the files  

SwapAndLinkFile.py <option> [<xml_configfile>]

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
from LinkObject import LinkObject
from functions import initLogger
    
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
                if l2Node.nodeName == "rootDir":
                    """ Zugriff auf den Wert des tags """
                    #srcDirName=l2Node.firstChild.nodeValue.encode(defaultEncoding)
                    rootDir=l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "relPathToLinks":
                    """ Zugriff auf den Wert des tags """
                    #workDirName = l2Node.firstChild.nodeValue.encode(defaultEncoding)
                    relPathToLinks = l2Node.firstChild.nodeValue
                    """ Zugriff auf ein Attribut des tags """
                    #workDirName = l2Node.getAttribute("value").encode(defaultEncoding)
                  
        elif l1Node.nodeName == "generic":
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "srcFilename":
                    #srcFilename = l2Node.getAttribute("value").encode(defaultEncoding)
                    srcFilename = l2Node.getAttribute("value")
                if l2Node.nodeName == "linkPrefix":
#                    linkPrefix = l2Node.getAttribute("value").encode(defaultEncoding)
                    linkPrefix = l2Node.getAttribute("value")
                                 
             
    
    logging.debug("rootDirName = %s" % rootDir) 
    logging.debug("relPathToLinks = %s" % relPathToLinks) 
    #logging.debug("tgtDirName = %s" % tgtDirName) 
    return (rootDir,relPathToLinks)

###########################################################################
def createLinkObjectsList(rootDir,relPathToLinks):
  absLinkDirName=os.path.join(rootDir,relPathToLinks)
  logging.debug("absLinkDirName = " + absLinkDirName)
  listOfLinks=os.listdir(absLinkDirName)
  linkObjects = []
  for curFile in listOfLinks:
    newLink = LinkObject()
    newLink.linkAbsLocation = os.path.join(absLinkDirName,curFile)
    LinkObject.initialize(newLink,rootDir)
    linkObjects.append(newLink)
    logging.debug(LinkObject.printOut(newLink))
  return linkObjects 


###########################################################################
def processLinkObjects(linkObject):
  logging.debug("calling os.remove("+linkObject.linkAbsLocation+")" )
  #os.remove(linkObject.linkAbsLocation)
  logging.debug("calling shutil.move("+linkObject.fileAbsLocation+","+linkObject.linkAbsLocationDir +") )")
  #shutil.move(linkObject.fileAbsLocation,linkObject.linkAbsLocationDir )
  logging.debug("calling os.chdir("+linkObject.newLinkAbsoluteDir+")")
  #os.chdir(linkObject.newLinkAbsoluteDir)
  logging.debug("calling os.symlink("+linkObject.newLinkTarget+","+linkObject.baseName+")")
  #os.symlink(linkObject.newLinkTarget,linkObject.baseName)
  

############################################################################
# main starts here

rootLogger = initLogger()

if sys.platform == "win32":
  #defaultEncoding="latin1"
  defaultEncoding="UTF-8"
else:
  defaultEncoding="UTF-8"


if len(sys.argv) == 1 :
    print description
    print sys.argv[0] + "<xml_configfile>"
    configFileName = 'SwapLinkAndFile.xml'
else:
    configFileName=sys.argv[1]


(rootDir, relPathToLinks) = readConfigFromXML(configFileName)
linkObjects = createLinkObjectsList(rootDir, relPathToLinks)
for curLinkObj in linkObjects:
  processLinkObjects(curLinkObj)
