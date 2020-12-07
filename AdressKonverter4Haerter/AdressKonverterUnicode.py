#!/usr/bin/python
# -*- coding: utf-8 -*-
description = """This program converts Adresses obtained
from the import Internet into CSVs for importing into OpenOffice

it uses Unicode strings for internal processing. (For the Architekt part)
all Strings which have non 7-Bit chars must be proceeded with u'

"""

import os
import shutil
import glob
import sys
import re
import string
import logging
import logging.config 
#from xml import dom
from xml.dom import minidom
from xml.dom import Node
import codecs



############################################################################
    
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
                  
        elif l1Node.nodeName == "generic":
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "srcFilename":
                    srcFilename = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "tgtFilename":
                    tgtFilename = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "fileformat":
                    fileformat = l2Node.getAttribute("value").encode(defaultEncoding)
                                 
             
    logging.debug("srcDirName = %s" % srcDirName) 
    logging.debug("tgtDirName = %s" % tgtDirName) 
    logging.debug("srcFilename = %s" % srcFilename) 
    logging.debug("tgtFilename = %s" % tgtFilename) 
    logging.debug("fileformat = %s" % fileformat) 
    
    return (srcDirName,tgtDirName,srcFilename,tgtFilename,fileformat)

############################################################################
def handleVersicherungLine(curLine,fsock,addressLinesIndex):
    if curLine.startswith('#'):
        "do nothing"
    elif re.match('mehr Informationen',curLine):
        "do nothing"
    elif re.search('[0-9]*\s*km.*',curLine):
        addressLinesIndex = addressLinesIndex+1
        logging.debug("new entry started")
        addressLines.append('')
    elif re.search ('Telef.*:',curLine):
        curLine = fsock.readline()
        telefon = curLine.rstrip('\r\n')
        #telefon = curLine
        entry = ',"'+ telefon + '"'
        addressLines[addressLinesIndex]=addressLines[addressLinesIndex]+entry
    elif re.search('\s*\d{5,5}',curLine):
        logging.debug("found an address line")
        if curLine.find(',') == -1:
            rest = curLine
            street = ''
        else:
            (street,rest) = curLine.split(',',1)
        logging.debug("street = %s " % street)
        logging.debug("rest = %s " % rest)
        rest=rest.strip()
        (plz,city)=rest.split(' ',1)
        logging.debug("plz = %s " % plz)
        logging.debug("city = %s " % city)
        entry=',"'+ street + '","' +plz + '","' + city + '"'
        addressLines[addressLinesIndex]=addressLines[addressLinesIndex]+entry
    #elif re.match('\w*',curLine) is not None:
    #elif re.match('[^a-zA-Z]',curLine):
    elif re.match('\s*$',curLine):
        logging.debug("line does not contain alphanumeric characters -> do nothing")
    else:
        logging.debug("Name = %s" % curLine)
        if addressLines[addressLinesIndex].find('"') == -1:
            addressLines[addressLinesIndex]=addressLines[addressLinesIndex]+'"'+curLine.strip()+'"'
        else:
            addressLines[addressLinesIndex]=addressLines[addressLinesIndex].rstrip('"')
            addressLines[addressLinesIndex]=addressLines[addressLinesIndex]+' '+curLine.strip()+'"'
        logging.debug("addressLines[%i] = %s" % (addressLinesIndex,addressLines[addressLinesIndex]) )

    return addressLinesIndex

############################################################################
def handleVersicherung(srcName):
    
    addressLinesIndex = 0  
    #logging.debug("addressLines[0] = %s " % str(addressLines[0]))
    try:
        fsock = codecs.open(srcName,"rb","utf8")
        #fsock = open(srcName, "r")
        try:
            #curLine=fsock.readline().encode(defaultEncoding)
            nextLine=fsock.readline()
            curLine=nextLine.rstrip('\r\n')
            while nextLine:
            #for curLine in fsock:
                #logging.debug("curLine = %s" % curLine) 
                addressLinesIndex=handleVersicherungLine(curLine,fsock,addressLinesIndex)
                #curLine=fsock.readline().encode(defaultEncoding)
                nextLine=fsock.readline()
                curLine=nextLine.rstrip('\r\n')
        finally:
            fsock.close()
    except IOError:
        logging.debug("error opening file %s" % srcName) 
    return 1

############################################################################
def handleArchitektLine(curLine,fsock,addressLinesIndex,curDict):
    if curLine.startswith('#'):
        "do nothing"
    elif re.match(u'\s*\n',curLine):
        "do nothing"
    elif re.match('Stellenangebote.*\n',curLine):
        "do nothing"
    elif re.match('> Kleinanzeigen.*\n',curLine):
        "do nothing"
    elif re.match('Informationsmaterialien.*\n',curLine):
        "do nothing"
    elif re.search('.*[Aa]rchitekt.*',curLine):
        logging.debug("found title line %s" % curLine)
        curDict["title"] = curLine.rstrip('\n').strip()
    elif re.search('\s*\d{5,5}',curLine):
        logging.debug("found an address line")
        if curLine.find(',') == -1:
            logging.debug("found an address line without comma")
            #reobj=re.compile(u'Brosch�ren/Merkbl�tter'.encode("utf8"))
            #reobj=re.compile(u'Brosch.ren/Merkbl.tter')
            reobj=re.compile('Brosch.ren/Merkbl.tter')
            #reobj=re.compile(u'Brosch..ren..Merkbl..tter'.encode("utf8"))
            if reobj.search(curLine): 
                logging.debug("remove Broschüren/Merkblätter")
                #curLine=curLine.replace('Brosch.ren/Merkbl.tter','')
                curLine=re.sub(reobj,'',curLine)
                logging.debug("remove Broschüren/Merkblätter %s" % repr(curLine))
                #reobj.sub('',curLine)
            if re.search("Kleinanzeigen",curLine): 
                logging.debug("remove Kleinanzeigen")
                curLine=curLine.replace("Kleinanzeigen",'')
            (plz,city) = curLine.split(' ',1)
            curDict["plz"] = plz.strip()
            curDict["city"] = city.rstrip('\n').strip()
            logging.debug("plz = %s " % curDict["plz"])
            logging.debug("city = %s " % curDict["city"])
            addressLines.append(formatDictAsLine(curDict))
            curDict.clear()
        else:
            (rest,forename) = curLine.split(',',1)
            forename = forename.rstrip('\n').strip()
            (plz,city,surname) = rest.split(' ',2)
            #temp=surname.strip(u'\t')
            #surname = temp
            #surname = surname.strip(chr(0xA0))
            curDict["plz"] = plz
            curDict["city"] = city
            logging.debug("plz = %s " % curDict["plz"])
            logging.debug("city = %s " % curDict["city"])
            addressLines.append(formatDictAsLine(curDict))
            curDict.clear()
            curDict["forename"] = forename 
            curDict["surname"] = surname.strip() 
            logging.debug("name = %s %s" % (curDict["forename"], curDict["surname"]) )
    elif curLine.find(',') != -1:
        logging.debug("found line with comma => single name")
        curDict.clear()
        (surname,forename) = curLine.split(',')
        forename = forename.rstrip('\n').strip()
        surname = surname.strip() 
        curDict["forename"] = forename 
        curDict["surname"] = surname 
            
    else:
        logging.debug("street = %s" % curLine)
        curDict["street"] = curLine.rstrip('\n').strip()
    return (addressLinesIndex,curDict)

############################################################################
def formatDictAsLine(curDict):
    line = u'"' + curDict["title"] + '","' + curDict["forename"] + '","' + curDict["surname"] + '","' + curDict["street"]  + '","' + curDict["plz"] + '","' + curDict["city"] + '"'
    return line

############################################################################
def handleArchitekt(srcName):
    
    addressLinesIndex = 0  
    try:
        fsock = codecs.open(srcName,"rb","utf8")
        #fsock = open(srcName, "r")
        try:
            curLine=fsock.readline()
            logging.debug("type(curLine) %s" % type(curLine))            
            curDict = {'title':'title' , 'name':'name', 'street':'street' ,'plz':'plz', 'city':'city'}
            while curLine:
            #for curLine in fsock:
                #logging.debug("curLine = %s" % curLine) 
                (addressLinesIndex,curDict)=handleArchitektLine(curLine,fsock,addressLinesIndex,curDict)
                #curLine=fsock.readline().encode(defaultEncoding)
                #curLine=unicode(fsock.readline())
                curLine=fsock.readline()  
                curLine=re.sub('\t*','',curLine)
                # string ist jetzt Unicode und wird mit enocoding utf8 aus file gelesen
                #curLine=curLine.decode('utf8')
                #logging.debug("type(curLine) %s" % type(curLine))            
                #curLine=curLine.expandtabs()
        finally:
            fsock.close()
    except IOError:
        logging.debug("error opening file %s" % srcName) 
    return 1



###########################################################################
def writeOutput(tgtName):
    try:
        #outfile = open(tgtName, "w")
        outfile = codecs.open(tgtName,"wb","utf8")
        
        try:
            for curAddress in addressLines:
                logging.info("curAddress = %s" % curAddress)
                outLine=curAddress + '\n'
                #outLine=outLine.encode('utf8')
                outfile.write(outLine)
        finally:
            outfile.close()
    except IOError:
        logging.info("error opening file %s" % srcName) 
    return 1
    
        

############################################################################
# main starts here
# global variables


rootLogger = initLogger()
if sys.platform == "win32":
  defaultEncoding="latin1"
  #defaultEncoding="UTF-8"
else:
  defaultEncoding="UTF-8"


if len(sys.argv) == 1 :
    print description
    print sys.argv[0] + "<xml_configfile>"
    configFileName = 'AdressKonverterConfig.xml'
else:
    configFileName=sys.argv[1]

(srcDirName,tgtDirName,srcFilename,tgtFilename,fileformat) = readConfigFromXML(configFileName)

logging.info("srcDirName = %s" % srcDirName) 
logging.info("tgtDirName = %s" % tgtDirName) 
logging.info("srcFilename = %s" % srcFilename) 
logging.info("tgtFilename = %s" % tgtFilename) 
logging.info("fileformat = %s" % fileformat) 

srcName=os.path.join(srcDirName,srcFilename)
tgtName=os.path.join(tgtDirName,tgtFilename)

logging.info("srcName = %s" % srcName) 

# global Array
addressLines = []
addressLines.append("") 
  
if fileformat == "Versicherung":
    handleVersicherung(srcName)
elif fileformat == "Architekt":
    handleArchitekt(srcName)

writeOutput(tgtName)