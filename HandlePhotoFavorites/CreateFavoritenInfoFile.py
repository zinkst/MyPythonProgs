#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
from pyaml_env import parse_config
import pathlib
import os
import datetime
import argparse
from pathlib import Path
import yaml

# imports of own library using symbolic links in folder to lib files since reltive imports
# I didn't get to work
from FileObject import FileObject
from functions import initLogger
from PhotoFileClass import PhotoFile
description = """
This program processes all files in a directory
"""

############################################################################


def updateConfig(prgPath, args, config):
  if args.year != None:
    config["year"] = args.year
  else:
    config["year"] = ""
  
  if config["toolMode"] != "production":
    config["srcRootDir"] = os.path.join(prgPath, "testdata")
  
  config["writefavoritenFile"] = args.write
  
############################################################################
def processDir(config):
  foldersWithoutFavortienInfo = []
  fullSrcDirName = os.path.join(config["srcRootDir"], config["srcRelativeDirName"], config["year"])
  for srcDir, dirList, dirFilesList in os.walk(fullSrcDirName):
    if not dirList:
      if not dirFilesList:
        logger.debug("Dir is empty" )  
      else:
        favoritenInfoFileName = os.path.join(srcDir, config.get("favoritenInfoFileBaseName"))
        if os.path.exists(favoritenInfoFileName):
          logger.info("FavoritenInfo exists : %s", favoritenInfoFileName)
        else:
          createFavoritenInfoFile(favoritenInfoFileName, config)

############################################################################


def createFavoritenInfoFile(favoritenInfoFileName, config):
  subDir = os.path.dirname(favoritenInfoFileName)
  favoritenDirConfig = {}
  # e.g. : 2024/202402_DAV Wochenende Ebnat-Kappel
  # e.g. : 2023/202302
  # e.g. : 2010/Gemeinsam/20100708_Skandinavien
  srcDirRelativeToRootDir = subDir[len(config.get("srcRootDir")) + len(config.get("srcRelativeDirName")) + 2:]
  # rootSubFolder: Familie Zink
  # yearSubFolder: 201007_Skandinavien
  dirPathObj = Path(srcDirRelativeToRootDir)
  dirPathParts = dirPathObj.parts
  if len(dirPathParts) > 2:
    # older folders
    match dirPathParts[1]:
      case "Gemeinsam":
        favoritenDirConfig["rootSubFolder"] = "Familie Zink"
      case _:
        favoritenDirConfig["rootSubFolder"] = dirPathParts[1]
  else:
    favoritenDirConfig["rootSubFolder"] = "Familie Zink"
  # compute FavoritenDir Folder
  if len(dirPathParts[-1]) > 6:
    favoritenDirConfig["yearSubFolder"] = dirPathParts[-1] 
  else: 
    favoritenDirConfig["yearSubFolder"] = dirPathParts[1][0:4] + "00_Sonstige"
  
  # print output
  favoritenDirConfigStr = ""
  for k, v in favoritenDirConfig.items():
      favoritenDirConfigStr += str(k).ljust(15, ' ') + ": " + str(v) + "\n"
  logger.info("FavoritenInfo used \n%s", favoritenDirConfigStr)  
  
  if config.get("writefavoritenFile"):
    logger.info("writing new FavoritenFile:  %s", favoritenInfoFileName)
    yaml_string=yaml.dump(favoritenDirConfig)
    logger.info("FavoritenInfo as yaml \n%s", yaml_string) 
    with open(favoritenInfoFileName, "w") as f:
      f.write(yaml_string)
 
############################################################################
# main starts here
prgPath = pathlib.Path(__file__).parent.resolve()
prgName = os.path.basename(__file__)
defaultConfigFileName = os.path.join(os.environ["HOME"], ".config", prgName, "config.yml")
defaultConfigFileName = os.path.join(prgPath, "config.yml")

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--configFileName", type=str, nargs='?', default=defaultConfigFileName, help="path to config file")
parser.add_argument("-y", "--year", type=str, nargs='?', help="year to proccess")
parser.add_argument("-w", "--write", default=False, action='store_true', help="write File to disk")
args = parser.parse_args()
print(args)

config = parse_config(args.configFileName)
updateConfig(prgPath, args, config)

logger = initLogger(config["loglevel"], __name__)

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