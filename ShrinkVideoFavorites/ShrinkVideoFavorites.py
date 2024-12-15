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
from Classes import FileObject, VideoFile
description = """
This program processes all files in a directory
"""


############################################################################
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
  filesWithMissingMetadata = []
  searchPattern = createSearchPattern(config["searchExtension"])
  fullSrcDirName = os.path.join(config["srcRootDir"], config["srcRelativeDirName"], config["year"])
  for srcDir, dirList, srcDirList in os.walk(fullSrcDirName):
    for srcFile in srcDirList:
      if re.search(searchPattern, srcFile, re.IGNORECASE) != None:
        srcAbsFileName = os.path.join(srcDir, srcFile)
        logging.debug("Processing File: %s", srcAbsFileName)
        newFile = FileObject(srcAbsFileName, config["srcRootDir"], config["srcRelativeDirName"])
        logging.debug("Fileinfo for %s %s", newFile.fileBaseName, newFile)
        videoFile = VideoFile(newFile, config)
        logging.debug("Videoinfo %s", videoFile)
        if videoFile.targetFileExists() and not config.get("probeSrcFile") :
          logging.info("File %s already exists - skipping ", videoFile.tgtFileName)
        else: 
          videoFile.ProbeVideoFile()
          if videoFile.isMetadataUpdated() == True:
            logging.info("Metadata was updated for Video \n %s", videoFile.fileObject.absFileName)
            filesWithMissingMetadata.append(videoFile.fileObject.absFileName)
          videoFile.FillMetadata()
          logging.debug("Vital Video Metadata:\n %s", videoFile.printEssentialMetadata())
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
        logging.info(outline)
        outfile.write(entry + '\n')
      outfile.write("Number of Found files : " + str(len(missingMetadataFiles)) + "\n") 

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

logger = initLogger(config)

if args.year != None:
  config["year"] = args.year
else:
  config["year"] = ""

configStr = ""
for k, v in config.items():
  configStr += str(k).ljust(31, ' ') + ": " + str(v) + "\n"
logging.info("configuration used\n%s", configStr)

begin = datetime.datetime.now()
beginFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logging.info("starting processing at " + beginFormatted)

filesWithMissingMetadata = processDir(config)
writeFilesWithMissingMetadataToFile(filesWithMissingMetadata, config)

end = datetime.datetime.now()
endFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logging.info("finished processing at " + endFormatted)
