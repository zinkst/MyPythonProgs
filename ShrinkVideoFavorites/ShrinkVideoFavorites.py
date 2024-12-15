#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging.config
from pyaml_env import parse_config
import codecs
import logging
import pathlib
import sys
import os
import datetime
import argparse
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
def processDir(config):
  for dir, dirList, fileList in os.walk(config["srcDirName"]):
    for file in fileList:
      ############################################################################
      logging.info("Processing File: %s", file)



############################################################################
def processFile(srcFileName, tgtFileName):
  try:
    fsock = codecs.open(srcFileName, "rb", "utf8")
    outfile = codecs.open(tgtFileName, "wb", "utf8")
    try:
      nextLine = fsock.readline()
      nextLine = nextLine.rstrip('\r\n')
      logging.debug("curLine=" + nextLine)
      while nextLine:
        ## put your line handling code here ###
        ###################
        nextLine = fsock.readline()
        nextLine = nextLine.rstrip('\r\n')
    finally:
      fsock.close()
      outfile.write('\n')
      outfile.close()
  except IOError:
    logging.debug("error opening file %s " % srcFileName)
  return 1


############################################################################
# main starts here
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

logging.info("srcDirName = %s" % config["srcDirName"])
logging.info("tgtDirName = %s" % config["tgtDirName"])

begin = datetime.datetime.now()
beginFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logging.info("starting processing at " + beginFormatted)

processDir(config)

end = datetime.datetime.now()
endFormatted = begin.strftime('%Y-%m-%d %H:%M:%S')
logging.info("finished processing at " + endFormatted)
