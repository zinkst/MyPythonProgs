#!/usr/bin/python3
# -*- coding: utf-8 -*-
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
from VideoFile import VideoFile


description = """
This program searches for Videos in ${srcRootDir}/${srcRelativeDirName}. The Videos there are symlinks to the Favorite Videos.
It then creates a shrinked version of each found Video in ${tgtDirName}. It preserves the Directory structure of source Dir.
If a corresponding videofile already exists in ther target dir, the shrinking is skipped.

To process only subdir of ${srcRootDir}/${srcRelativeDirName} the parameter -y ${subdirName} is available. Usually that is a year.
"""

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
  logger.info("searchPattern :" + searchPattern)
  return searchPattern


############################################################################
def processDir(config):
  filesWithMissingMetadata = []
  searchPattern = createSearchPattern(config["searchExtension"])
  fullSrcDirName = os.path.join(config["srcRootDir"], config["srcRelativeDirName"], config["year"])
  for srcDir, dirList, srcDirList in os.walk(fullSrcDirName):
    for srcFile in srcDirList:
      if re.search(searchPattern, srcFile, re.IGNORECASE) != None:
        srcAbsFileName = os.path.join(srcDir, srcFile)
        logger.debug("Processing File: %s", srcAbsFileName)
        newFile = FileObject(srcAbsFileName, config["srcRootDir"], config["srcRelativeDirName"])
        logger.debug("Fileinfo for %s %s", newFile.fileBaseName, newFile)
        videoFile = VideoFile(newFile, config, logger)
        logger.debug("Videoinfo %s", videoFile)
        if videoFile.targetFileExists() and not config.get("probeSrcFile") :
          logger.info("File %s already exists - skipping ", videoFile.tgtFileName)
        else: 
          videoFile.ProbeVideoFile()
          if videoFile.isMetadataUpdated() == True:
            logger.info("Metadata was updated for Video \n %s", videoFile.fileObject.absFileName)
            filesWithMissingMetadata.append(videoFile.fileObject.absFileName)
          videoFile.FillMetadata()
          logger.debug("Vital Video Metadata:\n %s", videoFile.printEssentialMetadata())
          if config.get("convertVideoFile"):
            videoFile.ConvertVideoFile()
  return filesWithMissingMetadata

############################################################################
def writeFilesWithMissingMetadataToFile(missingMetadataFiles, config):
  if len(missingMetadataFiles) > 0:
    outFileName = os.path.join(config["tgtDirName"], config["year"], "missingMetadataFiles.txt")
    with open(outFileName, 'w') as outfile:
      for idx, entry in enumerate(missingMetadataFiles):
        outline = str(k).ljust(5, ' ') + ": " + str(entry)
        logger.info(outline)
        outfile.write(entry + '\n')
      outfile.write("Number of Found files : " + str(len(missingMetadataFiles)) + "\n") 

############################################################################
# main starts here
prgPath = pathlib.Path(__file__).parent.resolve()
prgName = prgName = pathlib.Path(__file__).stem # os.path.basename(__file__)
defaultConfigFileName = os.path.join(os.environ["HOME"], ".config", prgName, "config.yml")
# defaultConfigFileName = os.path.join(prgPath, "config.yml")

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--configFileName", type=str, nargs='?', default=defaultConfigFileName, help="path to config file")
parser.add_argument("-y", "--year", type=str, nargs='?', help="year to proccess")
args = parser.parse_args()
print(args)

config = parse_config(args.configFileName)

logger = initLogger(config["loglevel"],__name__)

if args.year != None:
  config["year"] = args.year
else:
  config["year"] = ""

configStr = ""
for k, v in config.items():
  configStr += str(k).ljust(31, ' ') + ": " + str(v) + "\n"
logger.info("configuration used\n%s", configStr)

begin = datetime.datetime.now()
beginFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logger.info("starting processing at " + beginFormatted)

filesWithMissingMetadata = processDir(config)
writeFilesWithMissingMetadataToFile(filesWithMissingMetadata, config)

end = datetime.datetime.now()
endFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logger.info("finished processing at " + endFormatted)
