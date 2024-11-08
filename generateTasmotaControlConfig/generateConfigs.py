#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
# import shutil
# import glob
import sys
# import re
# import string
import logging
import logging.config 
import json
import yaml
import base64
import os.path

description = """
This program reads a master config json file for TasmotaControl (https://play.google.com/store/apps/details?id=de.grings_software.TasmotaControl&hl=de&gl=US
It creates multiple configs each with a conifgurable subset of configs
For each config it then does a base 64 encoding so thet the file can be imported into tasmotacontrol app

To print the available names and host from tasmotaControlMasterConfig.json use the followng jq

jq -jr '.[] |  .name," : ", .host,"\n" ' tasmotaControlMasterConfig.json
"""


############################################################################
def initLogger(logLevel):
    try: 
        rootLogger = logging.getLogger()
        logging.config.fileConfig("pyLoggerConfig.cfg")
    except:    
        logHandler = logging.StreamHandler(sys.stdout)
        #logging.basicConfig(stream=logHandler)
        rootLogger.addHandler(logHandler)
        match logLevel:
            case "DEBUG":
                rootLogger.setLevel(logging.DEBUG)
            case "INFO" | _ :    
                rootLogger.setLevel(logging.INFO)
    return rootLogger

############################################################################
def extractConfig(tasmotaMasterConfig, curUserConfig, tgtDir):
  configsToExtract=curUserConfig["configsToExtract"]
  user=curUserConfig["user"]
  logging.info("############ Generating config for user %s #############"  % (user) )
  newTasmotaConfig=[]
  for curTasmotaConfigHost in configsToExtract:
    for curMasterConfig in tasmotaMasterConfig:
      if curTasmotaConfigHost == curMasterConfig["host"]:
        newTasmotaConfig.append(curMasterConfig)
        logging.info("adding config %s for user %s"  % (curMasterConfig["name"], user) )
    logging.debug("######## newTasmotaConfig for user %s ############ \n: %s"  % (user, newTasmotaConfig) )
  
  newTasmotaConfigB64=base64.b64encode(json.dumps(newTasmotaConfig).encode('utf-8')) 
  tgtFileName = os.path.join(tgtDir, user + ".json.b64")  
  with open(tgtFileName, "wb") as tgtFile:
    tgtFile.write(newTasmotaConfigB64)

############################################################################
# main starts here

if len(sys.argv) == 1  :
    configFile="/links/Dokumente Marion Stefan/Burghalde/HeimNetz/tasmota/tasmotaControl/generateConfigs_cfg.yml"
else:
    configFile = sys.argv[1]

with open(configFile, 'rb') as cfgfile:
    config = yaml.load(cfgfile, Loader=yaml.Loader)

logLevel = config.get("logLevel","INFO")
rootLogger = initLogger(logLevel)
logging.debug("workingDir = %s" % os.getcwd())
logging.debug("config = %s" % config) 

masterFileName = config["masterFileName"]
with open(masterFileName, 'rb') as masterFile:
    tasmotaMasterConfig = json.load(masterFile)


for curUserConfig in config["userConfigs"]:
   extractConfig(tasmotaMasterConfig, curUserConfig, config["tgtDir"])
    
