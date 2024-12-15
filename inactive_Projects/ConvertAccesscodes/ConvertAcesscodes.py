#!/usr/bin/python
# -*- coding: utf-8 -*-
description = """This program handles hadles directories with absolutelinks to 
favorite Photos, or files with lists to favorites Photos 

ManagePhotoFavorites.py <option> [<xml_configfile>]

where option is one of : 

1: as input a directory containing absolute links to Favorite Photos and create a file  
   containing a list with relative links to those Photos and a file containing absolute links
   
2: as input take a file with a list of relative links and create those links in <workDirName>/linksrel   

3: (not implemented, can be done with a cp option) copy files contained in linksrel to folder files as new files ...

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
import csv
import pprint
from xml.dom.minidom import Document
import datetime



import functions
#from AccessCodeSheets import AccessCodeSheets

################################################################################
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
        print ("config file " + configFileName + " not found")
        sys.exit(1)
        
    #print xmldoc.toxml().encode("utf-8")
    logging.debug(xmldoc.toxml(defaultEncoding))
    listOfSrcFilenames= []
    configNode = xmldoc.firstChild
    for l1Node in configNode.childNodes:
        if l1Node.nodeName == sys.platform:
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "srcDirName":
                    """ Zugriff auf den Wert des tags """
                    #srcDirName=l2Node.firstChild.nodeValue.encode(defaultEncoding)
                    srcDirName=l2Node.firstChild.nodeValue
                if l2Node.nodeName == "tgtDirName":
                    """ Zugriff auf den Wert des tags """
                    #workDirName = l2Node.firstChild.nodeValue.encode(defaultEncoding)
                    tgtDirName = l2Node.firstChild.nodeValue
                    """ Zugriff auf ein Attribut des tags """
                    #workDirName = l2Node.getAttribute("value").encode(defaultEncoding)
                  
        elif l1Node.nodeName == "generic":
            for l2Node in l1Node.childNodes:
                if l2Node.nodeName == "srcFileNames":
                    for l3Node in l2Node.childNodes: 
                       if l3Node.nodeName == "el":
                           listOfSrcFilenames.append(l3Node.firstChild.nodeValue)
                if l2Node.nodeName == "tgtFileName":
#                    linkPrefix = l2Node.getAttribute("value").encode(defaultEncoding)
                    tgtFileName = l2Node.getAttribute("value")
                                 
#    inputParams={}
             
    inputParams["srcDirName"]=srcDirName.encode(defaultEncoding)
    inputParams["tgtDirName"]=tgtDirName.encode(defaultEncoding)
    inputParams["srcFileNames"]=listOfSrcFilenames
    inputParams["tgtFileName"]=tgtFileName.encode(defaultEncoding)
    
    logging.debug("srcDirName = %s" % inputParams["srcDirName"]) 
    logging.debug("srcFileNames = %s" % inputParams["srcFileNames"]) 
    logging.debug("tgtDirName = %s" % inputParams["tgtDirName"]) 
    logging.debug("tgtFileName = %s" % inputParams["tgtFileName"]) 
    
    inputParams["tgtName"]=os.path.join(inputParams["tgtDirName"], inputParams["tgtFileName"])
    
    logging.info("srcFileNames = %s" % inputParams["srcFileNames"]) 
    logging.info("tgtName = %s" % inputParams["tgtName"]) 
    return (inputParams)


############################################################################
def tagFoundButUnratedFile(inputParams):
    #logging.debug("addressLines[0] = %s " % str(addressLines[0]))
    try:
        fsock = codecs.open(inputParams["srcName"], "rb", "utf8")
        outfile = codecs.open(inputParams["tgtName"], "wb", "utf8")
        try:
            nextLine=fsock.readline()
            nextLine=nextLine.rstrip('\r\n')
            logging.debug("curLine="+nextLine)
            while nextLine:
                ## put your line handling code here ###
                arrowIndex = nextLine.find('->')
                outline = nextLine[arrowIndex+2:]  
                
                outline = 'ln -sf "' + outline +'"'
                logging.debug("outline="+outline)
                  
                outfile.write(outline + '\r\n')
                ###################
                nextLine=fsock.readline()
                nextLine=nextLine.rstrip('\r\n')
        finally:
            fsock.close()
            outfile.write('\n')
            outfile.close()
    except IOError:
        logging.debug("error opening file %s " % inputParams["srcName"]) 
    return 1

def convertDate(datumAsString):
    logging.debug("datumAsString="+datumAsString)
    dateDT = None
    dateSeparator='.'
    if re.match('[\d]*.[\d]{1,2}.[\d]{1,2}.',datumAsString):
        (day,rest)=datumAsString.split(dateSeparator,1)
        (month,year)=rest.split(dateSeparator,1)
        dateDT = datetime.datetime(int(year),int(month),int(day))
    return dateDT

     

def createGroupDom(groupname,filename):
    logging.info("groupname = %s ; filename = %s" % (groupname,filename) )
    group = doc.createElement("group")
    database.appendChild(group)
    title=doc.createElement("title")
    titleval=doc.createTextNode(groupname)
    title.appendChild(titleval)
    group.appendChild(title)
    
    icon = doc.createElement("icon")
    iconval=doc.createTextNode('0')
    icon.appendChild(iconval)
    group.appendChild(icon)
    csv.register_dialect('standard', delimiter=',', quotechar='"')
    with open(filename, 'r') as f:
        reader = csv.reader(f, 'standard')
        firstLine=True
        for row in reader:
            if firstLine:
                firstLine=False
            else:
                newEntry = createNewEntry(row)
                group.appendChild(newEntry)


def createNewEntry(row):
    """      <entry>
       <title>zifts@gmx.de</title>
       <username>zifts@gmx.de</username>
       <password>pw4zifts</password>
       <url>http://gmx.net</url>
       <comment>standard</comment>
       <icon>0</icon>
       <creation>2012-03-20T22:20:07</creation>
       <lastaccess>2012-03-20T22:21:01</lastaccess>
       <lastmod>2012-03-20T22:21:01</lastmod>
       <expire>Nie</expire>
      </entry>
    """
    entry = doc.createElement("entry")
    title=doc.createElement("title")
    titleval=doc.createTextNode(row[0])
    title.appendChild(titleval)
    entry.appendChild(title)
    
    username=doc.createElement("username")
    usernameval=doc.createTextNode(row[1])
    username.appendChild(usernameval)
    entry.appendChild(username)
    
    password=doc.createElement("password")
    passwordval=doc.createTextNode(row[2])
    password.appendChild(passwordval)
    entry.appendChild(password)
    
    lastmod=doc.createElement("lastmod")
    lastmodDT=convertDate(row[3])
    if lastmodDT != None:
        lastmodval=doc.createTextNode(lastmodDT.strftime("%Y-%m-%d"))
        lastmod.appendChild(lastmodval)
    entry.appendChild(lastmod)
    
    comment=doc.createElement("comment")
    commentval=doc.createTextNode(row[4])
    comment.appendChild(commentval)
    entry.appendChild(comment)
    logging.debug("newEntry="+ entry.toprettyxml(indent="  "))
    return entry



############################################################################
# main starts here

rootLogger = initLogger()

if sys.platform == "win32":
  #defaultEncoding="latin1"
  defaultEncoding="UTF-8"
else:
  defaultEncoding="UTF-8"


if len(sys.argv) == 1:
  configFileName="ConvertAccesscodes.xml" 
else:
  configFileName=sys.argv[1]
#action=sys.argv[1]

inputParams={}

inputParms = readConfigFromXML(configFileName)

# Create the minidom document
doc = Document()
database = doc.createElement("database")
doc.appendChild(database)
for curFileName in inputParams["srcFileNames"]:
    (groupName,rest)=os.path.splitext(curFileName)
    createGroupDom(groupName,os.path.join(inputParams["srcDirName"],curFileName))

# Print our newly created XML
print (doc.toprettyxml())
#print doc.toxml()
with open(inputParams["tgtName"], 'w') as o:
    doc.writexml(o)
    #o.write(doc.toprettyxml())


# select action
#acSheets = None
#acSheets = AccessCodeSheets(inputParams["srcName"])
#privat = acSheets.getSheet('privat')


#print "action = " + action 
#if action == "1":
#  (listOfAbsoluteLinkNames,listOfRelativeLinkNames) = createFileListFromAbsoluteLinks(workDirName)
#  writeAbsoluteFilenamesList(workDirName, listOfAbsoluteLinkNames)
#  writeRelativeFilenamesList(workDirName, listOfRelativeLinkNames)
#elif action == "2":
#  processFavoritesList_CreateRelativeLinks(srcName)


