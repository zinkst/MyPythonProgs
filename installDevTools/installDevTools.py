#!/usr/bin/python3
# -*- coding: utf-8 -*-

description = """
This tool installs tools (mostly cli) directly from github.
It requires a config for each tool in toolConfigs.yml 
Option:

* You can install a specific tool with the -t <toolName>
* without options it will try to get the latest release from all tools specified in config.yml (toolsToInstall list)

## required Python modules
```bash 
pip install wget jinja2 pyaml-env
```  
"""

import os
import glob
import sys
import re
import string
import logging
import logging.config 
import yaml
import shutil
import time,datetime
from pyaml_env import parse_config
import pprint
import wget
from jinja2 import Template
from pathlib import Path
from enum import StrEnum
import tarfile
import zipfile
import re
import requests
import argparse

############################################################################
class InstallType(StrEnum):
    BINARY_TGZ = 'binaryTgz'
    BINARY = 'binary'
    ZIP = 'zip'

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
def getToolsConfig(toolConfigs, toolName):
   for index, curToolConfig in enumerate(toolConfigs["tools"]):
      if curToolConfig["name"] == toolName:
         return toolConfigs["tools"][index]
   logging.error("Did not find tool %s in array %s", toolName, toolConfigs)
   return None

############################################################################
def setVersion(toolConfig):
  if toolConfig["version"] != "latest":
    return
  
  result = re.search(r"http[s]?://([a-zA-Z0-9.]+)\/([-\w]+)\/([-\w]+).*", toolConfig["downloadUrl"])
  if len(result.groups()) != 3:
    logging.error("could not parse version")
    return 
  repoHost=result.group(1)
  repoOrg=result.group(2)
  repoName=result.group(3) 
  releasesUrl="https://api."+repoHost+"/repos/"+repoOrg+"/" + repoName+ "/releases/latest"
  logging.info("releasesUrl: %s " , releasesUrl)
  
  try:
    response = requests.get(releasesUrl)
  except requests.exceptions.RequestException as e:  
    raise SystemExit(e)

  version=response.json()["tag_name"]
  if version.startswith('v'): 
     version=version[1:]
  logging.info("version: %s " , version)
  toolConfig["version"]=version

############################################################################
def install(toolConfig):
  logging.info("Installing tool: " + toolConfig["name"])
  installDir=os.path.join(config["installDir"], str(toolConfig["name"]+"-versions"))
  os.makedirs(installDir, exist_ok=True)
  toolFileName=os.path.join(installDir,str(toolConfig["name"]+"-"+toolConfig["version"]))
  url = Template(toolConfig["downloadUrl"]).render(VERSION=toolConfig["version"])
  if os.path.exists(toolFileName):
     logging.info("%s is already installed - nothing to do", toolFileName)
     return
  
  if toolConfig["type"] == InstallType.BINARY:
    if not os.path.exists(toolFileName):
      logging.info("downloading: " + url + " to: " + toolFileName)
      wget.download(url, toolFileName)
    else:
      logging.info("%s already downloaded from %s", toolFileName, url ) 
     
  elif toolConfig["type"] == InstallType.BINARY_TGZ:
    tgzFileName=toolFileName + ".tgz" 
    if not os.path.exists(tgzFileName):
      logging.info("downloading: " + url + " to: " + tgzFileName)
      wget.download(url, tgzFileName)
    else:
      logging.info("%s already downloaded from %s", tgzFileName, url ) 
    binaryName = Template(toolConfig.get("binaryTarget", toolConfig["name"])).render(VERSION=toolConfig["version"])
    with tarfile.open(tgzFileName, 'r:gz') as tgzFile:
        toolBinaryFile = tgzFile.extractfile(binaryName)
        with open (toolFileName, "wb") as outfile:
            outfile.write(toolBinaryFile.read())
    os.remove(tgzFileName)
  
  elif toolConfig["type"] == InstallType.ZIP:
    zipFileName=toolFileName + ".zip" 
    if not os.path.exists(zipFileName):
      logging.info("downloading: " + url + " to: " + zipFileName)
      wget.download(url, zipFileName)
    else:
      logging.info("%s already downloaded from %s", zipFileName, url ) 
    binaryName = toolConfig.get("binaryTarget", toolConfig["name"])
    with zipfile.ZipFile(zipFileName, 'r') as myzip:
      myzip.extract(binaryName, path=installDir)
    shutil.move(os.path.join(installDir,binaryName),toolFileName)
    os.remove(zipFileName)
  
  ## link downloaded tool in linkDir
  os.chmod(toolFileName,0o775)
  toolLinkName=os.path.join(config["linkDir"],str(toolConfig["name"]))
  if os.path.exists(toolLinkName):
    os.remove(toolLinkName)
  os.symlink(toolFileName,toolLinkName)  
  
 

############################################################################
# main starts here

defaultConfigFileName = os.path.join(os.environ["HOME"], ".config/installDevTools/config.yml")
defaultToolConfigsFileName = os.path.join(os.environ["HOME"], ".config/installDevTools/toolConfigs.yml")
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--toolToInstall", type=str, help="name of single tool you want to install")
parser.add_argument("-c", "--configFileName", type=str, nargs='?', default=defaultConfigFileName, help="path to config file")
parser.add_argument("-tc", "--toolConfigsFileName", type=str, nargs='?', default=defaultToolConfigsFileName, help="path to tools config file")
args = parser.parse_args()  
print(args)

config = parse_config(args.configFileName)
logger = initLogger(config)

with open(args.toolConfigsFileName, 'r',encoding='utf-8') as cfgfile:
  toolConfigs = yaml.safe_load(cfgfile)

if args.toolToInstall:
  config["toolsToInstall"] = [ args.toolToInstall ]
logging.info("toolsToInstall: " + pprint.pformat(config["toolsToInstall"], indent=2,depth=3))
logging.debug("ToolConfigs:\n %s",  pprint.pformat(toolConfigs, indent=2,depth=3))
for toolName in config["toolsToInstall"]:
  toolConfig = getToolsConfig(toolConfigs, toolName)
  setVersion(toolConfig)
  install(toolConfig)

logging.info("Finished installing tools: " + pprint.pformat(config["toolsToInstall"], indent=2,depth=3))

