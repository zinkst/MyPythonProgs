#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
from pyaml_env import parse_config
import pathlib
import os
import datetime
import argparse

# imports of own library using symbolic links in folder to lib files since reltive imports
# I didn't get to work
from FileObject import FileObject
from functions import initLogger
from PhotoFileClass import PhotoFile
description = """
This program searches for Photos in ${srcRootDir}/${srcRelativeDirName} which have a rating defined in their metadata. 
For each found Photo it can do two things
1. create a relative symlink in ${tgtDirName}/${linkRelativeTgtDirName}
   the Directory structure of source Dir is skipped
2. creates a compressed version of the Photo in ${tgtDirName}/${compressedRelativeTgtDirName}
   For the directory strucure of the target Dir in reads the File ${favoritenInfoFileBaseName} which must be created in the source dir. 
   The creation of this fil can be done by the the `./CreateFavoritenInfoFile.py` tool
If a corresponding photofile already exists in ther target dir, the corresponding file processing is skipped.

To process only subdir of ${srcRootDir}/${srcRelativeDirName} the parameter -y ${subdirName} is available. Usually that is a year.
"""


############################################################################
def updateConfig(prgPath, args, config):
  if args.year != None:
    config["year"] = args.year
  else:
    config["year"] = ""
  if config["toolMode"] != "production":
    config["srcRootDir"] = os.path.join(prgPath, "testdata")
    config["tgtDirName"] = os.path.join(prgPath, "testdata", "Favoriten")


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
  filesWithIncompleteMetadata = []
  searchPattern = createSearchPattern(config["searchExtension"])
  fullSrcDirName = os.path.join(config["srcRootDir"], config["srcRelativeDirName"], config["year"])
  for srcDir, dirList, srcDirList in os.walk(fullSrcDirName):
    for srcFile in srcDirList:
      if re.search(searchPattern, srcFile, re.IGNORECASE) != None:
        srcAbsFileName = os.path.join(srcDir, srcFile)
        newFile = FileObject(srcAbsFileName, config["srcRootDir"], config["srcRelativeDirName"])
        logger.debug("Fileinfo for %s %s", newFile.fileBaseName, newFile)
        photoFile = PhotoFile(newFile, config, logger)
        photoFile.ProbePhotoFileRating()
        if photoFile.isFavoritePhoto:
          logger.debug("Photoinfo %s", photoFile)
          if config.get("createSymlinks"):
            photoFile.CreateSymlinkForPhoto()
          if config.get("shrinkPhoto"):
            photoFile.ShrinkPhoto()


############################################################################
# main starts here
prgPath = pathlib.Path(__file__).parent.resolve()
prgName = prgName = pathlib.Path(__file__).stem
defaultConfigFileName = os.path.join(os.environ["HOME"], ".config", prgName, "config.yml")
# defaultConfigFileName = os.path.join(prgPath, "config.yml")

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--configFileName", type=str, nargs='?', default=defaultConfigFileName, help="path to config file")
parser.add_argument("-y", "--year", type=str, nargs='?', help="year to proccess")
args = parser.parse_args()
print(args)

config = parse_config(args.configFileName)

logger = initLogger(config["loglevel"], __name__)
updateConfig(prgPath, args, config)

configStr = ""
for k, v in config.items():
  configStr += str(k).ljust(31, ' ') + ": " + str(v) + "\n"
logger.info("configuration used\n%s", configStr)

begin = datetime.datetime.now()
beginFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logger.info("starting processing at " + beginFormatted)

processDir(config)

end = datetime.datetime.now()
endFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logger.info("finished processing at " + endFormatted)
