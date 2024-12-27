#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging.config
import re
from pyaml_env import parse_config
import logging
import pathlib
import sys
import os
import datetime
import argparse

# imports of own library using symbolic links in folder to lib files since reltive imports 
# I didn't get to work
from FileObject import FileObject
from functions import initLogger

description = """
This program processes all files in a directory
"""


############################################################################
def updateConfig(prgPath,args, config):
  if args.year != None:
    config["year"] = args.year
  else:
    config["year"] = ""
  if config["toolMode"] != "production":
    config["srcRootDir"] = os.path.join(prgPath,"testdata")
    config["tgtDirName"] = os.path.join(prgPath,"testdata", "Favoriten")


############################################################################
def createSearchPattern(searchExtension):
  # create searchPattern from extensions
  searchPattern = r"("
  for i in range(0, len(searchExtension)):
    if i == 0:
      searchPattern = searchPattern + "." + searchExtension[i]
    else:
      searchPattern = searchPattern + "|" + "." + searchExtension[i]
  searchPattern = searchPattern + ")"
  logging.info("searchPattern :" + searchPattern)
  return searchPattern


############################################################################
def processDir(config):
  filesWithIncompleteMetadata = []
  searchPattern = createSearchPattern(config["searchExtension"])
  fullSrcDirName = os.path.join(config["srcRootDir"], config["srcRelativeDirName"], config["year"])
  for srcDir, dirList, srcDirList in os.walk(fullSrcDirName):
    for srcFile in srcDirList:
      if re.search(searchPattern, srcFile, re.IGNORECASE) != None:
        srcAbsFileName = os.path.join(srcDir, srcFile)
        # logging.debug("Processing File: %s", srcAbsFileName)
        newFile = FileObject(srcAbsFileName, config["srcRootDir"], config["srcRelativeDirName"])
        logging.debug("Fileinfo for %s %s", newFile.fileBaseName, newFile)
        # videoFile = PhotoFile(newFile, config)
        # logging.debug("Videoinfo %s", videoFile)
        # if not videoFile.targetFileExists():
        #   videoFile.ProbeVideoFile()
        #   videoFile.FillMetadata()
        #   if videoFile.() == True:
        #     logging.info("Vital Metadata is missing for Video --- exiting \n %s", videoFile.fileObject.absFileName)
        #     sys.exit(-1)
        #   logging.debug("Vital Video Metadata:\n %s", videoFile.printEssentialMetadata())
        #   videoFile.ConvertVideoFile()


############################################################################
# main starts here
prgPath = pathlib.Path(__file__).parent.resolve()
prgName = os.path.basename(__file__)
defaultConfigFileName = os.path.join(os.environ["HOME"], ".config", prgName, "config.yml")
defaultConfigFileName = os.path.join(prgPath, "config.yml")

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--configFileName", type=str, nargs='?', default=defaultConfigFileName, help="path to config file")
parser.add_argument("-y", "--year", type=str, nargs='?', help="year to proccess")
args = parser.parse_args()
print(args)

config = parse_config(args.configFileName)

logger = initLogger(config["loglevel"])
updateConfig(prgPath,args, config)

configStr = ""
for k, v in config.items():
  configStr += str(k).ljust(31, ' ') + ": " + str(v) + "\n"
logging.info("configuration used\n%s", configStr)

begin = datetime.datetime.now()
beginFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logging.info("starting processing at " + beginFormatted)

processDir(config)

end = datetime.datetime.now()
endFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logging.info("finished processing at " + endFormatted)
