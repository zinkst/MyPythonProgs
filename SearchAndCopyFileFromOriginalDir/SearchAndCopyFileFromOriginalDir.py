#!/usr/bin/python3
# -*- coding: utf-8 -*-

description = """This program handles handles directories with favorite Photos and creates a directory with absolute links to the original file
if found on the originals dir  

SearchAndCopyFile.py <option> [<xml_configfile>]

"""

import os
import shutil
import glob
import sys
import re
import string
import logging
import logging.config 
# from xml import dom
from xml.dom import minidom
from xml.dom import Node
import codecs
import json
import yaml
import shutil
from FileObject import FileObject
import time,datetime
#efrom functions import initLogger
# import scriptutil as SU
    

def initLogger(config):
    handler = logging.StreamHandler(sys.stdout)
    frm = logging.Formatter("%(asctime)s [%(levelname)-5s]: %(message)s", "%Y%m%d %H:%M:%S")
    handler.setFormatter(frm)
    logger = logging.getLogger()
    logger.addHandler(handler)
    if config["loglevel"] == "DEBUG":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger


###########################################################################
def extendInputParams(inputParams):
#  inputParams["ABS-ORIGINALS-DIR"]=os.path.join(inputParams["ROOT-DIR"],inputParams["ORIGINALS-DIRS"])
  inputParams["ABS-COPIES-ORIG-DIR"] = os.path.join(inputParams["ROOT-DIR"], inputParams["COPIES-ORIG-DIR"])
  inputParams["ABS-COPIES-TGT-DIR"] = os.path.join(inputParams["ROOT-DIR"], inputParams["COPIES-TGT-DIR"])
  inputParams["ROOT-DIR_LENGTH"] = len(inputParams["ROOT-DIR"])
  logging.debug("extended inputParams = \n%s" % inputParams) 
  return inputParams

###########################################################################
def createFileObjectsList(inputParams):
  fileObjects = []
  notFoundFileObjects = []
  originalFilesDict = {}
  # create searchPattern from extensions
  searchPattern = r"("
  for i in range (0,len(config['searchExtension'])):
      if i == 0:
          searchPattern = searchPattern + "\." + config['searchExtension'][i] 
      else:
          searchPattern = searchPattern + "|" + "\." + config['searchExtension'][i]
  searchPattern = searchPattern + ")"    
  logging.info("searchPattern :" + searchPattern )
      
  # create dictionary with original files to improve performance
  for relDirName in inputParams["ORIGINALS-DIRS"]:
      dirName = os.path.join(inputParams["ROOT-DIR"], relDirName)
      logging.debug(" dirName = " + dirName)
      for dir, dirList, fileList in os.walk (dirName):
  #      logging.debug(" dirList = " + str(dirList) )
  #      logging.debug(" fileList = " + str(fileList))
        for file in fileList:
            result = re.search(searchPattern, file, re.IGNORECASE)
            if result != None:
                origFileDict = {}
                origFileDict['absOrigFileName']=os.path.join(dir, file)
                origFileDict['exifDateTimeString']=FileObject.getDateTimeStringFromExif(os.path.join(dir, file))
                originalFilesDict[os.path.basename(file)] = origFileDict
  #iterate over source files 
  for verz, verzList, dateiListe in os.walk (inputParams["ABS-COPIES-ORIG-DIR"]):
      logging.debug(" verzList = " + str(verzList))
      logging.debug(" dateiListe = " + str(dateiListe))
      for datei in dateiListe:
          resultRE2 = re.search(searchPattern, datei, re.IGNORECASE)
          if resultRE2 != None:
              absCopiesOrigDateiName = os.path.join(verz, datei)
              logging.debug(" absCopiesOrigDateiName = " + str(absCopiesOrigDateiName))
              newFile = FileObject()
              FileObject.initialize(newFile, inputParams, absCopiesOrigDateiName,originalFilesDict)
              logging.debug(FileObject.printOut(newFile))
              if newFile.foundOriginal == False:
                notFoundFileObjects.append(newFile)
                logging.info(newFile.findMethod.rjust(16) +" match found for: " + str(absCopiesOrigDateiName))
              else:
                fileObjects.append(newFile) 
                logging.info(newFile.findMethod.rjust(16) + " match found for: " + str(absCopiesOrigDateiName))
#           else:     
#                 logging.info("no".rjust(16) + " match found for: " + str(absCopiesOrigDateiName))
  return (fileObjects, notFoundFileObjects)

###########################################################################
def processFileObjects(fileObjects,inputParams):
  outFilePath = os.path.join(inputParams['ROOT-DIR'], inputParams['COPIES-TGT-DIR'])
  os.makedirs(outFilePath,exist_ok=True)  # ,'0775')
  with open(os.path.join(outFilePath,"FoundFiles.txt"), 'w') as outfile:
      for fileObject in fileObjects:
          try:
              newTgtDir = os.path.join(fileObject.ip['ROOT-DIR'], fileObject.copiesTgtDirRelativeToRootDir)
              if  not os.path.exists(newTgtDir):
                  logging.debug("calling   os.makedirs(" + newTgtDir + ",'0775')")
                  if inputParams["SIMULATE"] == False: 
                      os.makedirs(newTgtDir)  # ,'0775')
              # os.chdir(fileObject.ROOT-DIR)
                
              logging.debug("calling os.chdir(" + newTgtDir + ")")
              if inputParams["SIMULATE"] == False: 
                os.chdir(newTgtDir)
              
              #newRelLink = os.path.join("../"*fileObject.copiesLinkDepthToBaseDir, fileObject.dateiNameOnOriginalRelativeToRootDir)
              #logging.debug("checking os.symlink(" + newRelLink + "," + fileObject.fileBaseName + ")")
              newAbsLink = os.path.join(fileObject.ip['ROOT-DIR'], fileObject.dateiNameOnOriginalRelativeToRootDir)
              logging.debug("checking os.symlink(" + newAbsLink + "," + fileObject.fileBaseName + ")")
              if  not os.path.exists(fileObject.fileBaseName):
                #logging.debug("calling os.symlink(" + newRelLink + "," + fileObject.fileBaseName + ")")
                logging.debug("calling os.link(" + newAbsLink + "," + fileObject.fileBaseName + ")")
                if inputParams["SIMULATE"] == False: 
                  # os.symlink(newRelLink,fileObject.fileBaseName)
                  if config['linkType'] == 'hard':
                      os.link(newAbsLink, fileObject.fileBaseName)
                  else:
                      os.symlink(newAbsLink, fileObject.fileBaseName)  
                      
          except (OSError,IOError):
              logging.error("error in processing " + fileObject.printOut())
              logging.error("continuing .... ")
              
          
          outLine = fileObject.findMethod.rjust(16) +":" + fileObject.fileBaseName.rjust(60) + " == " + os.path.basename(fileObject.absDateiNameOnOriginal) + " ## " + fileObject.absCopiesOrigDateiName + " == " + fileObject.absDateiNameOnOriginal 
          logging.debug("outLine=" + outLine)
          outfile.write(outLine + '\n')
    
############################################################################
def writeNotFoundFilesToFile(notFoundFileObjects):
    outFileName = os.path.join(inputParams['ROOT-DIR'], inputParams['COPIES-ORIG-DIR'], "notFoundFiles.txt")
#    with open(outFileName, 'w',encoding='utf-8') as outfile:
    with open(outFileName, 'w') as outfile:
        for curNotFoundFileObj in notFoundFileObjects:
            outLine = curNotFoundFileObj.absCopiesOrigDateiName
            logging.info("outLine=" + outLine)
            outfile.write(outLine + '\n')
    

#############################################################################################
def processNotFoundFiles(notFoundFileObjects):
    for fileObject in notFoundFileObjects:
        newTgtDir = os.path.join(fileObject.ip['ROOT-DIR'], fileObject.copiesTgtDirRelativeToRootDir)
        logging.debug("calling   os.makedirs(" + newTgtDir + ",'0775')")
        if inputParams["SIMULATE"] == False: 
            os.makedirs(newTgtDir,exist_ok=True)  # ,'0775')
        if  not os.path.exists(os.path.join(newTgtDir, fileObject.fileBaseName)):
            logging.debug("checking shutil.copy(" + fileObject.absCopiesOrigDateiName + "," + newTgtDir)
            if inputParams["SIMULATE"] == False: 
                shutil.copy(fileObject.absCopiesOrigDateiName, newTgtDir)
    writeNotFoundFilesToFile(notFoundFileObjects)       
  

############################################################################
# main starts here

if len(sys.argv) == 1 :
    print(description)
    print(sys.argv[0] + "<configfile>")
    configFileName = 'SearchAndCopyFileFromOriginalDir_Photos.yaml'
else:
    configFileName = sys.argv[1]


# Python2 
#with open(configFileName, 'r') as cfgfile:
# Python3 
with open(configFileName, 'r',encoding='utf-8') as cfgfile:
    #config = json.load(cfgfile)
    config = yaml.load(cfgfile)
logger = initLogger(config)

#yamlFileName = 'SearchAndCopyFileFromOriginalDir_Photos.yaml'
#with open(yamlFileName, 'w', encoding='utf-8') as outFile:
#   outFile.write(yaml.dump(config))
#exit(0)       

configuration = config["configuration"]  
inputParams = config[configuration]
inputParams = extendInputParams(inputParams)

begin = datetime.datetime.now()
beginFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logging.info("starting processing at " + beginFormatted)

(fileObjects, notFoundFileObjects) = createFileObjectsList(inputParams)
processFileObjects(fileObjects,inputParams)
processNotFoundFiles(notFoundFileObjects)
#time.sleep(5)

end = datetime.datetime.now()
endFormatted = end.strftime('%Y-%m-%d %H:%M:%S')
outFilePath = os.path.join(inputParams['ROOT-DIR'], inputParams['COPIES-TGT-DIR'])
with open(os.path.join(outFilePath,"FoundFiles.txt"), 'a') as outfile:
    logging.info("end processing at " + endFormatted)
    outline = "processing took: " + str(end - begin)
    logging.info(outline)
    outfile.write(outline + '\n')
    outline = ("Number of matched files %d" % len(fileObjects) )
    logging.info(outline)
    outfile.write(outline + '\n')
    outline = ("Number of unmatched files %d" % len(notFoundFileObjects) )
    logging.info(outline)
    outfile.write(outline + '\n')
    


####################################################################
######## Old methods
####################################################################
def readConfigFromXML(configFileName):
    try:
        xmldoc = minidom.parse(configFileName)
    except IOError:
        print("config file " + configFileName + " not found")
        sys.exit(1)
    listOfOrigDirs = []    
    # print xmldoc.toxml().encode("utf-8")
    logging.debug(xmldoc.toxml(defaultEncoding))
    configNode = xmldoc.firstChild
    for l1Node in configNode.childNodes:
        if l1Node.nodeName == sys.platform:
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "ROOT-DIR":
                    """ Zugriff auf ein Attribut des tags """
                    inputParams["ROOT-DIR"] = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "ORIGINALS-DIRS":
                    """ Zugriff auf den Wert des tags """
                    for l3Node in l2Node.childNodes: 
                      if l3Node.nodeName == "el":
                        listOfOrigDirs.append(l3Node.firstChild.nodeValue)
                    inputParams["ORIGINALS-DIRS"] = listOfOrigDirs
                if l2Node.nodeName == "COPIES-ORIG-DIR":
                    """ Zugriff auf den Wert des tags """
                    inputParams["COPIES-ORIG-DIR"] = l2Node.firstChild.nodeValue
                if l2Node.nodeName == "COPIES-TGT-DIR":
                    """ Zugriff auf den Wert des tags """
                    inputParams["COPIES-TGT-DIR"] = l2Node.firstChild.nodeValue
                  
        elif l1Node.nodeName == "generic":
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "debug":
                    inputParams["SIMULATE"] = l2Node.firstChild.nodeValue
                if l2Node.nodeName == "linkPrefix":
#                    linkPrefix = l2Node.getAttribute("value").encode(defaultEncoding)
                    linkPrefix = l2Node.getAttribute("value")
                                 
             
    
    logging.debug("inputParams = \n%s" % inputParams) 
    # logging.debug("tgtDirName = %s" % tgtDirName) 
    return (inputParams)

