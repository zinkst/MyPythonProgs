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
  searchPattern = createSearchPattern(config["searchExtension"])
  srcDirName = os.path.join(config["srcRootDir"], config["srcRelativeDirName"])
  for srcDir, dirList, srcDirList in os.walk(srcDirName):
    for srcFile in srcDirList:
      resultRE2 = re.search(searchPattern, srcFile, re.IGNORECASE)
      if resultRE2 != None:
        srcAbsFileName = os.path.join(srcDir, srcFile)
        logging.info("Processing File: %s", srcAbsFileName)
        newFile = FileObject(srcAbsFileName, config["srcRootDir"])
        logging.debug("Fileinfo for %s %s", newFile.fileBaseName, newFile)
        videoFile = VideoFile(newFile)
        logging.debug("Videoinfo %s", videoFile)


############################################################################
# main starts here
prgPath = pathlib.Path(__file__).parent.resolve()
prgName = os.path.basename(__file__)
defaultConfigFileName = os.path.join(os.environ["HOME"], ".config", prgName, "config.yml")
defaultConfigFileName = os.path.join(prgPath, "config.yml")

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--configFileName", type=str, nargs='?', default=defaultConfigFileName, help="path to config file")
args = parser.parse_args()
print(args)

config = parse_config(args.configFileName)

logger = initLogger(config)

configStr = ""
for k, v in config.items():
  configStr += str(k).ljust(21, ' ') + ": " + str(v) + "\n"
logging.info("configuration used\n%s", configStr)

begin = datetime.datetime.now()
beginFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logging.info("starting processing at " + beginFormatted)

processDir(config)

end = datetime.datetime.now()
endFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logging.info("finished processing at " + endFormatted)
