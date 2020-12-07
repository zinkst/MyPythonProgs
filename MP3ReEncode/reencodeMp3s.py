#!/usr/bin/python
# -*- coding: utf-8 -*-
description = """This program searches a given Source Directory for mp3 files and performs 
reencoding of the mp3's. The reencoded files are stored under target directory
preserving the directory structure. ID3 tag information (album,songname,artist,year
genre) are also preserved.
It uses lame for reencoding. Configuration options must be set in an xml file.
In the xml file srcDir, tgtDir, path to Lame executable, and lame encoding options must be specified
For id3 scanning the module pytagger is used. see: http://www.liquidx.net/pytagger/
"""

import os
import shutil
import glob
import sys
import re
import string
from tagger import *
import logging
import logging.config 
#from xml import dom
from xml.dom import minidom
from xml.dom import Node

############################################################################
def findTGTDirName(srcCompleteFileName,srcDirName):
    logging.debug(" srcCompleteFileName = " + srcCompleteFileName)
    logging.debug(" srcDirName = " + srcDirName)
    fileName = os.path.basename(srcCompleteFileName)
    commonPrefixDirName=os.path.commonprefix((srcDirName,tgtDirName))
    logging.debug(" commonPrefixDirName = " + commonPrefixDirName)
    (head, tgtParentDirName) =os.path.split(srcDirName)
    (head, tgtLastDirName) =os.path.split(tgtDirName)
    if tgtLastDirName == tgtParentDirName:
        tgtSubdirName = tgtDirName
    else:
        tgtSubdirName = os.path.join(tgtDirName,tgtParentDirName)
    tgtCompleteFileName = os.path.join(tgtSubdirName,fileName)
    logging.debug(" tgtSubdirName = " + tgtSubdirName)
    logging.debug(" tgtCompleteFileName = " + tgtCompleteFileName)
   
    if not os.path.exists(tgtSubdirName):
        os.makedirs(tgtSubdirName, 0775)
    return tgtCompleteFileName
     
############################################################################
def processMP3file(srcCompleteFileName,tgtCompleteFileName):
    #mp3_tag2 = ID3v2(srcCompleteFileName)      
    #print mp3_tag2.version
    mp3_tag1 = ID3v1(srcCompleteFileName)      
    
    mp3info_dic = {}
    curArtist = mp3_tag1.artist
    curSongName = mp3_tag1.songname
    curAlbum = mp3_tag1.album
    curTrackNumber = mp3_tag1.track
    curYear = mp3_tag1.year
    curGenre = mp3_tag1.genre
    #print "curArtist + "_" + curSongName + "_" + curAlbum + "_" + curTrackNumber.string
    logging.debug(" %s_%s_%s_%d_%s_%s" % (curArtist,curSongName,curAlbum,curTrackNumber,curYear,curGenre) )
    
    if curGenre == None or curGenre == -1:
        command = "%s --tt \"%s\" --ta \"%s\" --tl \"%s\" --tn %d --ty %s -V %d --silent --add-id3v2 \"%s\" \"%s\"" % (mp3Encoder,curSongName,curArtist,curAlbum,curTrackNumber,curYear,vbrQuality,srcCompleteFileName,tgtCompleteFileName)
    else:
        command = "%s --tt \"%s\" --ta \"%s\" --tl \"%s\" --tn %d --ty %s --tg %s -V %d --silent --add-id3v2  \"%s\" \"%s\"" % (mp3Encoder,curSongName,curArtist,curAlbum,curTrackNumber,curYear,curGenre,vbrQuality,srcCompleteFileName,tgtCompleteFileName)
    print command
    os.system(command)

############################################################################
def processMP3fileDIC(srcCompleteFileName,tgtCompleteFileName):
    #mp3_tag2 = ID3v2(srcCompleteFileName)      
    #logging.debug(" mp3_tag2.version = " + str(mp3_tag2.version))
    mp3_tag1 = ID3v1(srcCompleteFileName)      
    
    mp3info_dic = {}
    if mp3_tag1.artist != None and mp3_tag1.artist != -1:
        mp3info_dic["artist"] = mp3_tag1.artist
    if mp3_tag1.songname != None and mp3_tag1.songname != -1:
        mp3info_dic["songname"] = mp3_tag1.songname
    if mp3_tag1.album != None and mp3_tag1.album != -1:
        mp3info_dic["album"] = mp3_tag1.album
    if mp3_tag1.track != None and mp3_tag1.track != -1:
        mp3info_dic["track"] = mp3_tag1.track
    if mp3_tag1.year != None and mp3_tag1.year != -1:
        mp3info_dic["year"] = mp3_tag1.year
    if mp3_tag1.genre != None and mp3_tag1.genre >= -1:
        mp3info_dic["genre"] = mp3_tag1.genre
    attributeDIC = {"artist": "ta" , "songname" : "tt" , "album" : "tl" , "track" : "tn" , "year" : "ty" , "genre" : "tg" }
    
    id3opts = ""
    for curKey in mp3info_dic.keys():
         if curKey != "genre":
             id3opts = "%s --%s \"%s\"" %(id3opts,attributeDIC[curKey],mp3info_dic[curKey])  
         else:
             id3opts = "%s --%s \"%d\"" %(id3opts,attributeDIC[curKey],mp3info_dic[curKey])  
         #id3opts = id3opts + "--" + attributeDIC[curKey] + " \"" + mp3info_dic[curKey] + "\""
    
    #opts = "-V %s --silent --add-id3v2 " %(vbrQuality)
    srcTgt = "\"%s\" \"%s\"" % (srcCompleteFileName,tgtCompleteFileName)
    logging.debug("srcTgt = " + srcTgt)
    logging.debug("id3opts = " + id3opts)
    logging.debug("encodingOptions = " + encodingOptions)
   
    command = "%s %s %s %s" % (mp3Encoder,id3opts,encodingOptions,srcTgt)
    print command
    os.system(command)

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

############################################################################
def readConfigFromXML(configFileName):
    try:
        xmldoc = minidom.parse(configFileName)
    except IOError:
        print "config file " + configFileName + " not found"
        sys.exit(1)
        
    #print xmldoc.toxml().encode("utf-8")
    logging.debug(xmldoc.toxml(defaultEncoding))
    configNode = xmldoc.firstChild
    for l1Node in configNode.childNodes:
        if l1Node.nodeName == sys.platform:
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "srcDirName":
                    """ Zugriff auf den Wert des tags """
                    #srcDirName = l2Node.getAttribute("value").encode(defaultEncoding)
                    srcDirName=l2Node.firstChild.nodeValue.encode(defaultEncoding)
                if l2Node.nodeName == "tgtDirName":
                    """ Zugriff auf ein Attribut des tags """
                    tgtDirName = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "mp3Encoder":
                    mp3Encoder = l2Node.getAttribute("value").encode(defaultEncoding)
         
        elif l1Node.nodeName == "generic":
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "encodingOptions":
                    encodingOptions = l2Node.getAttribute("value").encode(defaultEncoding)
                                 
             
    logging.debug("srcDirName = %s" % srcDirName) 
    logging.debug("tgtDirName = %s" % tgtDirName) 
    logging.debug("mp3Encoder = %s" % mp3Encoder) 
    logging.debug("encodingOptions = %s" % encodingOptions) 
    
    return (srcDirName,tgtDirName,mp3Encoder,encodingOptions)

############################################################################
# main starts here
# global variables


rootLogger = initLogger()
if sys.platform == "win32":
  defaultEncoding="latin1"
else:
  defaultEncoding="UTF-8"

if len(sys.argv) == 1 :
    print description
    print sys.argv[0] + "<xml_configfile>"
    configFileName = 'reencodeMp3sConfig.xml'
else:
    configFileName=sys.argv[1]

(srcDirName,tgtDirName,mp3Encoder,encodingOptions) = readConfigFromXML(configFileName)

logging.info("srcDirName = %s" % srcDirName) 
logging.info("tgtDirName = %s" % tgtDirName) 
logging.info("mp3Encoder = %s" % mp3Encoder) 
logging.info("encodingOptions = %s" % encodingOptions) 
    
 
for Verz, VerzList, DateiListe in os.walk (srcDirName):
    logging.debug(" VerzList = " + str(VerzList) )
    logging.debug(" DateiListe = " + str(DateiListe))
    for Datei in DateiListe:
        srcCompleteFileName  = os.path.join(Verz,Datei)
        logging.debug(" srcCompleteFileName  = " + srcCompleteFileName)
        reMP3 = re.compile('\.mp3',re.IGNORECASE)
        resultRE = reMP3.search(srcCompleteFileName)
        resultRE2 = re.search('\.mp3',srcCompleteFileName,re.IGNORECASE)
        if resultRE2 != None:
            tgtCompleteFileName = findTGTDirName(srcCompleteFileName, Verz)
            processMP3fileDIC(srcCompleteFileName, tgtCompleteFileName)
            #processMP3file(srcCompleteFileName, tgtCompleteFileName)

print ("successfully transfered %s " % srcDirName)

#files = os.listdir (dirname)

#files = glob.glob1("F:\\mp3car\\010MP3CAR\\06_Björk_Telegram","*.mp3")
#for name in files:
#   print name
 #winxmldom= minidom.parseString( winTagXml[0].toxml().encode("utf-8"))
    #winxmldom= minidom.parseString( winTagXml[0].toxml().encode("cp1252"))
    #print winxmldom.toxml().encode("utf-8")
    #print winxmldom.toxml().encode("cp1252")
    #for srcDirNameNode in winxmldom.getElementsByTagName("srcDirName"):
    #    srcDirName = srcDirNameNode.getAttribute("value")
    #for tgtDirNameNode in winxmldom.getElementsByTagName("tgtDirName"):
    #    tgtDirName = tgtDirNameNode.getAttribute("value")
    #for mp3EncoderNode in winxmldom.getElementsByTagName("mp3Encoder"):
    #    mp3Encoder = mp3EncoderNode.getAttribute("value")
    
    #commonTagXml = xmldoc.getElementsByTagName('common')
    #winxmldom= minidom.parseString( winTagXml[0].toxml())
    #print winxmldom.toxml()
    
    #winxmldom.nodeValue
    
    #srcDirName = 'F:\\mp3car\\010MP3CAR'
    #tgtDirName = 'F:\\mp3car\\010MP3STICK2'
    #mp3Encoder = 'D:\\lame\\lame.exe'
    #vbrQuality = 9
#fsock = open('reencodeMp3sConfig.xml')
#xmldoc = minidom.parse(fsock)
#fsock.close()
    