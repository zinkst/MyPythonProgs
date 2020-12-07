#!/usr/bin/python
# -*- coding: utf-8 -*-
description = """This program handles hadles directories with absolutelinks to 
favorite Photos, or files with lists to favorites Photos 

ManagePhotoFavorites.py <option> [<xml_configfile>]

absLink = /home/zinks/Stefan/myPrg/MyPythonPrgs/SwapLinkAndFile/testdata/test/2008/Favoriten/SchwedenLinksRel/20080514_075451_RaststaetteHasselberg.jpg
linkTgt = ../../20080506_Schweden/20080514_075451_RaststaetteHasselberg.jpg
linkRelSplit =20080506_Schweden/20080514_075451_RaststaetteHasselberg.jpg

"""

import os
import sys
import string
import logging
import logging.config 
#from xml import dom

    
############################################################################
def initLogger():
    try: 
        rootLogger = logging.getLogger()
        logging.config.fileConfig("pyLoggerConfig.cfg")
    except:    
        logHandler = logging.StreamHandler(sys.stdout)
        #logging.basicConfig(stream=logHandler)
        rootLogger.addHandler(logHandler)
        rootLogger.setLevel(logging.DEBUG)
        rootLogger.setLevel(logging.INFO)
    return rootLogger

def initLogger(level):
    try: 
        rootLogger = logging.getLogger()
        logging.config.fileConfig("pyLoggerConfig.cfg")
        rootLogger.setLevel(level)
    except:    
        logHandler = logging.StreamHandler(sys.stdout)
        #logging.basicConfig(stream=logHandler)
        rootLogger.addHandler(logHandler)
        rootLogger.setLevel(level)
    return rootLogger
