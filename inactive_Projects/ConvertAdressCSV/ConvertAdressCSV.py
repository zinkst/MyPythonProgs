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
from datetime import date,timedelta


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
                if l2Node.nodeName == "tgtThunderbirdName":
                    tgtThunderbirdName = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "tgtGigasetName":
                    tgtGigasetName = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "tgtTSinusName":
                    tgtTSinusName = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "tgtGMXName":
                    tgtGMXName = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "tgtSamsungKiesName":
                    tgtSamsungKiesName = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "tgtSamsungAndroidVCFName":
                    tgtSamsungAndroidVCFName = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "tgtGeburtstageICSName":
                    tgtGeburtstageICSName = l2Node.getAttribute("value").encode(defaultEncoding)
                if l2Node.nodeName == "tgtGMailContactsCSVName":
                    tgtGMailContactsCSVName = l2Node.getAttribute("value").encode(defaultEncoding)
                                 
             
    
    inputDataDict["srcName"]=os.path.join(srcDirName, srcFilename)
    inputDataDict["tgtThunderbirdAbsName"]=os.path.join(tgtDirName, tgtThunderbirdName)
    inputDataDict["tgtGigasetAbsName"]=os.path.join(tgtDirName, tgtGigasetName)
    inputDataDict["tgtTSinusAbsName"]=os.path.join(tgtDirName, tgtTSinusName)
    inputDataDict["tgtGMXAbsName"]=os.path.join(tgtDirName, tgtGMXName)
    inputDataDict["tgtSamsungKiesAbsName"]=os.path.join(tgtDirName, tgtSamsungKiesName)
    inputDataDict["tgtSamsungAndroidVCFName"]=os.path.join(tgtDirName, tgtSamsungAndroidVCFName)
    inputDataDict["tgtGMailContactsCSVName"]=os.path.join(tgtDirName, tgtGMailContactsCSVName)
    inputDataDict["tgtGeburtstageICSName"]=os.path.join(tgtDirName, tgtGeburtstageICSName)
    
    for key,value in inputDataDict.iteritems():
      logging.info(key +":\t" +value)
    return inputDataDict

############################################################################
def printDictionaryDynamic(inDict):
  for curKey in inDict.keys():
    logging.debug("Dictionary["+curKey+"]="+inDict[curKey])

############################################################################
def getNextLineEntry(inputString, keyname):
  #logging.debug("inputString="+inputString)
  inMiddleSeparator = inEnclosingChar+inSeparator
  if re.search(',',inputString):
    if inputString.startswith('\''+inEnclosingChar):
      # nextentry is inbetween ".."
      (next,rest)=inputString.split(inMiddleSeparator,1)
      # next = '"??
    else:
      (next,rest)=inputString.split(inSeparator,1)
    if next != '':
      if re.search(inEnclosingChar,next):
        #logging.debug("next="+next)
        nextEntry = next.replace('\''+inEnclosingChar,'')
        nextEntry =nextEntry.replace(inEnclosingChar,'')
      else:
        # this must be Geburstdatum 
        nextEntry = next.replace("\'",'')
    else:
      nextEntry = next
    rest = "'"+rest
  else:
    #last Entry eached  
    nextEntry = inputString.replace(inMiddleSeparator,'')
    nextEntry =nextEntry.replace(inEnclosingChar,'')
    rest = ''  
  curDict[keyname]=nextEntry  
  logging.debug("curDict["+keyname+"]="+curDict[keyname])
  return rest    

############################################################################
def handleSrcFileLine(curLine):
#  "Vorname","Nachname","Straße privat","Postleitzahl privat","Ort privat","Staat privat","Telefon privat","Pager","Telefon geschäftlich","Geburtstag",
#  "E-Mail-Adresse","E-Mail 2:Adresse","Nickname","Webseite"
    keyGeburtsdatum="Geburtsdatum"
    logging.debug("curLine="+curLine)
    #curLine = curLine.replace(',',separator)
    if curLine.startswith('#'):
      logging.debug("do nothing")
    elif curLine.startswith('\'"Vorname'):
      logging.debug("do not process headerline")
    else: 
      rest = getNextLineEntry(curLine,"Telefonbucheintrag")
      rest = getNextLineEntry(rest,"Gruppe")
      rest = getNextLineEntry(rest,"Export")
      rest = getNextLineEntry(rest,"Vorname")
      rest = getNextLineEntry(rest,"Nachname")
      rest = getNextLineEntry(rest,"Strasse")
      rest = getNextLineEntry(rest,"PLZ")
      rest = getNextLineEntry(rest,"Ort")
      rest = getNextLineEntry(rest,"Staat")
      rest = getNextLineEntry(rest,"Telefon")
      rest = getNextLineEntry(rest,"mobil")
      rest = getNextLineEntry(rest,"Telefongesch")
      rest = getNextLineEntry(rest,"Fax")
      rest = getNextLineEntry(rest,keyGeburtsdatum)
      rest = getNextLineEntry(rest,"EMail1")
      rest = getNextLineEntry(rest,"EMail2")
      rest = getNextLineEntry(rest,"Nickname")
      rest = getNextLineEntry(rest,"Webseite")
      rest = getNextLineEntry(rest,"Kommentar")
      #logging.debug("curDict[Geburtsdatum]="+curDict[keyGeburtsdatum])
      computeBirthdayValues(curDict[keyGeburtsdatum])
      #printDictionary(curDict)
      addressLines.append(curDict.copy())
      
############################################################################
def computeBirthdayValues(Geburtsdatum):
  #logging.debug("Geburtsdatum="+Geburtsdatum)
  if re.match(u'\d\d\.\d\d\.\d\d..',Geburtsdatum):
    (Geburtstag,Geburtsrest)=Geburtsdatum.split('.',1)
    curDict["Geburtstag"]=Geburtstag
    (Geburtsmonat,Geburtsrest)=Geburtsrest.split('.',1)
    curDict["Geburtsmonat"]=Geburtsmonat
    Geburtsjahr=Geburtsrest
    curDict["Geburtsjahr"]=Geburtsjahr
  else:
    #logging.debug("Geburtsdatum is empty="+Geburtsdatum)
    curDict["Geburtsjahr"]=''
    curDict["Geburtsmonat"]=''
    curDict["Geburtstag"]=''




############################################################################
def processSrcFile(srcName):
    #logging.debug("addressLines[0] = %s " % str(addressLines[0]))
    try:
        fsock = codecs.open(srcName, "rb", "utf8")
        #fsock = open(srcName, "r")
        try:
            #nextLine=unicode(fsock.readline())
            nextLine=fsock.readline()
            curLine=nextLine.rstrip(lineEnd)
            curLine="'"+nextLine+"'"
            while nextLine:
                #logging.debug("curLine = %s" % curLine)
                #addressLinesIndex=handleSrcFileLine(curLine, fsock, addressLinesIndex)
                #printDictionary(addressLines[addressLinesIndex-1])
                handleSrcFileLine(curLine)
                curDict.clear() 
                nextLine=fsock.readline()
                curLine=nextLine.rstrip(lineEnd)
                curLine="'"+curLine+"'"
                #logging.debug("curline="+curLine)
        finally:
            fsock.close()
    except IOError:
        logging.debug("error opening file %s" % srcName) 
    return 1


############################################################################
def formatDictAsThunderbirdLine(inDict):
    tbSeparator = ','
    tbEnclosingChar='"'
    outSep = tbEnclosingChar+tbSeparator+tbEnclosingChar
    #printDictionary(inDict)
    printDictionaryDynamic(inDict)
    line = tbEnclosingChar + inDict["Nachname"] + \
           outSep +  inDict["Vorname"] + \
           outSep + inDict["Nickname"] + \
           outSep + inDict["Nickname"] + \
           outSep + inDict["EMail1"] + \
           outSep + inDict["EMail2"] + \
           outSep + inDict["Telefongesch"] + \
           outSep + inDict["Telefon"] + \
           outSep + inDict["Fax"] + \
           outSep + \
           outSep + inDict["mobil"] + \
           outSep + inDict["Strasse"] + \
           outSep + \
           outSep + inDict["Ort"] + \
           outSep + \
           outSep + inDict["PLZ"] + \
           outSep + inDict["Staat"] + \
           '",,,,,,,,,"' + \
           outSep + inDict["Webseite"] + \
           outSep + \
           outSep + inDict["Geburtsjahr"] + \
           outSep + inDict["Geburtsmonat"] + \
           outSep + inDict["Geburtstag"] + \
           '",,,,,'
    return line

###########################################################################
def writeThunderbirdOutput(tgtThunderbirdAbsName):
    try:
        outfile = codecs.open(tgtThunderbirdAbsName, "wb","latin1","xmlcharrefreplace")
        #outfile = codecs.open(tgtName, "wb", "utf8")
        try:
            for curAddressDict in addressLines:
                #logging.info("curAddress = %s" % curAddress)
                outline=formatDictAsThunderbirdLine(curAddressDict)
                logging.info("outline="+outline)
                outLine=outline + lineEnd
                outfile.write(outLine)
        finally:
            outfile.close()
    except IOError:
        logging.info("error opening file %s" % tgtThunderbirdName) 
    return 1
    
###########################################################################
def writeGigasetOutput(tgtGigasetAbsName):
#BEGIN:VCARD
#VERSION:2.1
#N:Röhm;Martin
#TEL;HOME:373039
#TEL;WORK:07051168135
#TEL;CELL:0162811892
#EMAIL:martin.roehm@gmx.net
#END:VCARD  
  try:
    # nested try necessary for finally in Python 2.4
    try:
      #outfile = codecs.open(tgtGigasetAbsName, "wb","latin1","xmlcharrefreplace")
      outfile = codecs.open(tgtGigasetAbsName, "wb", "utf8")
      for curAddressDict in addressLines:
        createEntry=curAddressDict["Telefonbucheintrag"]
        if createEntry == 'j':
          outfile.write(lineEnd)
          outfile.write('BEGIN:VCARD'+lineEnd)
          outfile.write('VERSION:2.1'+lineEnd)
          nameLine='N:'+curAddressDict["Nachname"] + ";" + curAddressDict["Vorname"] + lineEnd
          logging.info("nameLine="+nameLine)
          outfile.write(nameLine)
          telHome=formatTelefonForGigaset(curAddressDict["Telefon"])
          if len(telHome) != 0:
            telHomeLine='TEL;HOME:'+telHome + lineEnd
            logging.info("telHomeLine="+telHomeLine)
            outfile.write(telHomeLine)
          telWork=formatTelefonForGigaset(curAddressDict["Telefongesch"])
          if len(telWork) != 0:
            telWorkLine='TEL;WORK:'+telWork + lineEnd
            logging.info("telWorkLine="+telWorkLine)
            outfile.write(telWorkLine)
          telCell=formatTelefonForGigaset(curAddressDict["mobil"])
          if len(telCell) != 0:
            telCellLine='TEL;CELL:'+telCell + lineEnd
            logging.info("telCellLine="+telCellLine)
            outfile.write(telCellLine)
          outfile.write('END:VCARD'+lineEnd)
      outfile.write(preconfiguredGigasetNumbers())  
    except IOError:
      logging.info("error opening file %s" % tgtGigasetAbsName) 
  finally:
    outfile.close()
  return 1

###########################################################################
def formatTelefonForGigaset(srcPhoneNumber):
    tgtPhoneNumber = srcPhoneNumber.replace('-','')
    tgtPhoneNumber = tgtPhoneNumber.replace('07054','')
    return tgtPhoneNumber

def preconfiguredGigasetNumbers():
    val= lineEnd
    val= val+'BEGIN:VCARD'+lineEnd
    val= val+'VERSION:2.1'+lineEnd
    val= val+'N: Gigaset.net;'+lineEnd
    val= val+'TEL;HOME:1188#9'+lineEnd
    val= val+'END:VCARD'+lineEnd
    val= val+lineEnd
    val= val+'BEGIN:VCARD'+lineEnd
    val= val+'VERSION:2.1'+lineEnd
    val= val+'N: kT Bran.buch;'+lineEnd
    val= val+'TEL;HOME:2#91'+lineEnd
    val= val+'END:VCARD'+lineEnd
    val= val+lineEnd
    val= val+'BEGIN:VCARD'+lineEnd
    val= val+'VERSION:2.1'+lineEnd
    val= val+'N: kT Tel.buch;'+lineEnd
    val= val+'TEL;HOME:1#91'+lineEnd
    val= val+'END:VCARD'+lineEnd
    return val


###########################################################################
def writeTSinusOutput(tgtTSinusAbsName):
  # nested try necessary for finally in Python 2.4
  try:
    try:
      outfile = codecs.open(tgtTSinusAbsName, "wb","latin-1","xmlcharrefreplace")
      #outfile = codecs.open(tgtTSinusAbsName, "wb", "utf8")
      for curAddressDict in addressLines:
        createEntry=curAddressDict["Telefonbucheintrag"]
        if createEntry == 'j':
          nameMax10=curAddressDict["Nachname"]+ "," + curAddressDict["Vorname"]
          if len(nameMax10)>=10:
            nameMax10=nameMax10[0:11]#.encode('latin1')
          logging.info("nameMax10="+nameMax10)
          telHome=formatTelefonForGigaset(curAddressDict["Telefon"])
          if len(telHome) != 0:
            outfile.write(lineEnd)
            outfile.write('BEGIN:VCARD'+lineEnd)
            outfile.write('VERSION:2.1'+lineEnd)
            outfile.write('N:'+nameMax10+' hom'+lineEnd)
            telHomeLine='TEL;HOME:'+telHome + lineEnd
            logging.info("telHomeLine="+telHomeLine)
            outfile.write(telHomeLine)
            outfile.write('END:VCARD'+lineEnd)
            
          telWork=formatTelefonForGigaset(curAddressDict["Telefongesch"])
          if len(telWork) != 0:
            outfile.write(lineEnd)
            outfile.write('BEGIN:VCARD'+lineEnd)
            outfile.write('VERSION:2.1'+lineEnd)
            outfile.write('N:'+nameMax10+' wrk'+lineEnd)
            telWorkLine='TEL;HOME:'+telWork + lineEnd
            logging.info("telWorkLine="+telWorkLine)
            outfile.write(telWorkLine)
            outfile.write('END:VCARD'+lineEnd)
  
          telCell=formatTelefonForGigaset(curAddressDict["mobil"])
          if len(telCell) != 0:
            outfile.write(lineEnd)
            outfile.write('BEGIN:VCARD'+lineEnd)
            outfile.write('VERSION:2.1'+lineEnd)
            outfile.write('N:'+nameMax10+' hdy'+lineEnd)
            telCellLine='TEL;HOME:'+telCell + lineEnd
            logging.info("telCellLine="+telCellLine)
            outfile.write(telCellLine)
            outfile.write('END:VCARD'+lineEnd)
    except IOError:
      logging.info("error opening file %s" % tgtTSinusAbsName) 
  finally:
    outfile.close()
  return 1


###########################################################################
def writeGMXCSVOutput(tgtGMXAbsName):
  gmxSeparator = ','
  gmxEnclosingChar='"'
  outSep = gmxEnclosingChar+gmxSeparator+gmxEnclosingChar

  try:
    # nested try necessary for finally in Python 2.4
    try:
      #outfile = codecs.open(tgtGigasetAbsName, "wb","latin1","xmlcharrefreplace")
      outfile = codecs.open(tgtGMXAbsName, "wb", "utf8")
      for curAddressDict in addressLines:
        if len(curAddressDict["EMail1"]) != 0:
          line = gmxEnclosingChar + curAddressDict["Nachname"] + outSep +  curAddressDict["Vorname"] +  outSep + curAddressDict["EMail1"] +  gmxEnclosingChar + lineEnd
          logging.debug("line = " + line)   
          outfile.write(line)        
          if len(curAddressDict["EMail2"]) != 0:
            line2 = gmxEnclosingChar + curAddressDict["Nachname"] + outSep +  curAddressDict["Vorname"] + outSep + curAddressDict["EMail2"] + gmxEnclosingChar + lineEnd
            logging.debug("line2 = " + line2)   
            outfile.write(line2)        
    except IOError:
      logging.info("error opening file %s" % tgtGMXAbsName) 
  finally:
    outfile.close()
  return 1

###########################################################################
def formatTelefonForInternational(srcPhoneNumber):
    tgtPhoneNumber = srcPhoneNumber.replace('-','')
    if (tgtPhoneNumber.startswith('0')):
      tgtPhoneNumber=tgtPhoneNumber[1:]
      tgtPhoneNumber='+49'+tgtPhoneNumber
    return tgtPhoneNumber


###########################################################################
def writeSamsungKiesCSVOutput(tgtSamsungKiesAbsName):
  separator = ','
  enclosingChar='"'
  outSep = enclosingChar+separator+enclosingChar

  try:
    # nested try necessary for finally in Python 2.4
    try:
      #outfile = codecs.open(tgtGigasetAbsName, "wb","latin1","xmlcharrefreplace")
      outfile = codecs.open(tgtSamsungKiesAbsName, "wb", "latin1")
      #header = "Nachname","Vorname","Anzeigename","Benutzername","Telefonnummer1(Typ)","Telefonnummer1(Nummer)","Telefonnummer2(Typ)","Telefonnummer2(Nummer)","Telefonnummer3(Typ)","Telefonnummer3(Nummer)","E-Mail1(Typ)","E-Mail1(Adresse)","E-Mail2(Typ)","E-Mail2(Adresse)","Adresse1(Straße)","Adresse1(Ort)","Adresse1(Region)","Adresse1(Land)","Adresse1(Postleitzahl)","Geburtstag(Datum)"
      header = """\"Gruppe","Nachname","Vorname","Anzeigename","Benutzername","Telefonnummer1(Typ)","Telefonnummer1(Nummer)","Telefonnummer2(Typ)","Telefonnummer2(Nummer)","Telefonnummer3(Typ)","Telefonnummer3(Nummer)","Telefonnummer4(Typ)","Telefonnummer4(Nummer)","E-Mail1(Typ)","E-Mail1(Adresse)","E-Mail2(Typ)","E-Mail2(Adresse)","Adresse1(Straße)","Adresse1(Ort)","Adresse1(Region)","Adresse1(Land)","Adresse1(Postleitzahl)","Geburtstag(Datum)\"""" + lineEnd
      outfile.write(header)
      firstline = True;
      for curAddressDict in addressLines:
        if firstline:
           # skip first line 
           firstline = False       
        else:
          homePhoneNumber=formatTelefonForInternational(curAddressDict["Telefon"])
          mobilPhoneNumber=formatTelefonForInternational(curAddressDict["mobil"])
          workPhoneNumber=formatTelefonForInternational(curAddressDict["Telefongesch"])
          faxPhoneNumber=formatTelefonForInternational(curAddressDict["Fax"])
          if (len(curAddressDict["Geburtsjahr"]) != 0):
            birthday=curAddressDict["Geburtstag"] +"."+curAddressDict["Geburtsmonat"]+"."+curAddressDict["Geburtsjahr"]
          else:
            birthday = outSep
          line = enclosingChar + curAddressDict["Gruppe"] + \
          outSep +  curAddressDict["Nachname"] + \
          outSep +  curAddressDict["Vorname"] + \
          outSep + curAddressDict["Nickname"] + \
          outSep + curAddressDict["Nickname"] + \
          outSep + "Custom(heim)" + \
          outSep + homePhoneNumber + \
          outSep + "Mobile" + \
          outSep + mobilPhoneNumber + \
          outSep + "Landline.Business" + \
          outSep + workPhoneNumber + \
          outSep + "Custom" + \
          outSep + faxPhoneNumber + \
          outSep + "none" + \
          outSep + curAddressDict["EMail1"] + \
          outSep + "other" + \
          outSep + curAddressDict["EMail2"] + \
          outSep + curAddressDict["Strasse"] + \
          outSep + curAddressDict["Ort"] + \
          outSep + \
          outSep + curAddressDict["Staat"] + \
          outSep + curAddressDict["PLZ"] + \
          outSep + birthday + \
          enclosingChar + lineEnd
          logging.debug(line)
          outfile.write(line)        
          #logging.debug("%s %s %s %s" % ( homePhoneNumber, mobilPhoneNumber, workPhoneNumber, faxPhoneNumber ))
    except IOError:
      logging.info("error opening file %s" % tgtSamsungKiesAbsName) 
  finally:
    outfile.close()
  return 1



###########################################################################
# Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Group Membership,E-mail 1 - Type,E-mail 1 - Value,E-mail 2 - Type,E-mail 2 - Value,Phone 1 - Type,Phone 1 - Value,Phone 2 - Type,Phone 2 - Value,Phone 3 - Type,Phone 3 - Value,Address 1 - Type,Address 1 - Formatted,Address 1 - Street,Address 1 - City,Address 1 - PO Box,Address 1 - Region,Address 1 - Postal Code,Address 1 - Country,Address 1 - Extended Address,Address 2 - Type,Address 2 - Formatted,Address 2 - Street,Address 2 - City,Address 2 - PO Box,Address 2 - Region,Address 2 - Postal Code,Address 2 - Country,Address 2 - Extended Address
# Marion,,,Zink,,,,,,,,,,,,,,,,,,,,,,,* My Contacts,Home,Marion_zink@gmx.net,* Home,zink.marion@googlemail.com,Home,07054-930711,Mobile,0176-42522511 ,Work,07031-7671-38 ,Home,"Burghalde 93 72218 Wildberg",Burghalde 93,Wildberg,,,72218,,,Work,"Karlstraße 1 71032 Darmsheim","Karlstraße 1 71032 Darmsheim",,,,,,
def writeGMailContactsCSV(tgtGMailContactsCSVName):
  separator = ','
  enclosingChar='"'
  outSep = enclosingChar+separator+enclosingChar

  try:
    # nested try necessary for finally in Python 2.4
    try:
      #outfile = codecs.open(tgtGigasetAbsName, "wb","latin1","xmlcharrefreplace")
      outfile = codecs.open(tgtGMailContactsCSVName, "wb", "latin1")
      header = """\"Name","Given Name","Additional Name","Family Name","Yomi Name","Given Name Yomi","Additional Name Yomi","Family Name Yomi","Name Prefix","Name Suffix","Initials","Nickname","Short Name","Maiden Name","Birthday","Gender","Location","Billing Information","Directory Server","Mileage","Occupation","Hobby","Sensitivity","Priority","Subject","Notes","Group Membership","E-mail 1 - Type","E-mail 1 - Value","E-mail 2 - Type","E-mail 2 - Value","Phone 1 - Type","Phone 1 - Value","Phone 2 - Type","Phone 2 - Value","Phone 3 - Type","Phone 3 - Value","Address 1 - Type","Address 1 - Formatted","Address 1 - Street","Address 1 - City","Address 1 - PO Box","Address 1 - Region","Address 1 - Postal Code","Address 1 - Country","Address 1 - Extended Address","Address 2 - Type","Address 2 - Formatted","Address 2 - Street","Address 2 - City","Address 2 - PO Box","Address 2 - Region","Address 2 - Postal Code","Address 2 - Country","Address 2 - Extended Address\"""" + lineEnd
      outfile.write(header)
      firstline = True;
      for curAddressDict in addressLines:
        if curAddressDict["Export"] == 'x':
            if firstline:
               # skip first line 
               firstline = False       
            else:
              homePhoneNumber=formatTelefonForInternational(curAddressDict["Telefon"])
              mobilPhoneNumber=formatTelefonForInternational(curAddressDict["mobil"])
              workPhoneNumber=formatTelefonForInternational(curAddressDict["Telefongesch"])
              faxPhoneNumber=formatTelefonForInternational(curAddressDict["Fax"])
              if (len(curAddressDict["Geburtsjahr"]) != 0):
                birthday=curAddressDict["Geburtsjahr"] +"-"+curAddressDict["Geburtsmonat"]+"-"+curAddressDict["Geburtstag"]
                # omit birthday for GMailContacts
                #birthday=""
              else:
                birthday = ""
              line=enclosingChar + curAddressDict["Vorname"] +" " + curAddressDict["Nachname"] + \
              outSep + curAddressDict["Vorname"] + \
              outSep +  \
              outSep +  curAddressDict["Nachname"] + \
              outSep + outSep + outSep + outSep + outSep + outSep + outSep + \
              outSep + curAddressDict["Nickname"] + \
              outSep + outSep +\
              outSep + birthday + \
              outSep + outSep + outSep + outSep + outSep + outSep + outSep + outSep + outSep + outSep + outSep + \
              outSep + curAddressDict["Gruppe"] + \
              outSep + "* Home" + \
              outSep + curAddressDict["EMail1"] + \
              outSep + "Home" + \
              outSep + curAddressDict["EMail2"] + \
              outSep + "Home" + \
              outSep + homePhoneNumber + \
              outSep + "Mobile" + \
              outSep + mobilPhoneNumber + \
              outSep + "Work" + \
              outSep + workPhoneNumber + \
              outSep + outSep + \
              outSep + curAddressDict["Strasse"] + \
              outSep + curAddressDict["Ort"] + \
              outSep + outSep + \
              outSep + curAddressDict["PLZ"] + \
              outSep + curAddressDict["Staat"] + \
              outSep + outSep + outSep + outSep + outSep + outSep + outSep + outSep + \
              enclosingChar + lineEnd
              logging.debug(line)
              outfile.write(line)        
          #logging.debug("%s %s %s %s" % ( homePhoneNumber, mobilPhoneNumber, workPhoneNumber, faxPhoneNumber ))
    except IOError:
      logging.info("error opening file %s" % tgtSamsungKiesAbsName) 
  finally:
    outfile.close()
  return 1



###########################################################################
def writeSamsungAndroidVCard(tgtFileName):
#BEGIN:VCARD
#VERSION:2.1
#N:Zink;Rainer;;;
#FN:Rainer Zink
#TEL;VOICE:+497153540709
#TEL;CELL:+491736592333
#TEL;WORK;VOICE:+4971121734565
#EMAIL;INTERNET:Rainer.Zink@allianz.de
#EMAIL;INTERNET:Rainer_Zink@gmx.de
#ADR;:;;Alte Zimmerei 3;Hochdorf;;73269;D
#BDAY:1971-03-20
#END:VCARD
  try:
    # nested try necessary for finally in Python 2.4
    try:
      #outfile = codecs.open(tgtFileName, "wb","latin1","xmlcharrefreplace")
      outfile = codecs.open(tgtFileName, "wb", "utf8")
      for curAddressDict in addressLines:
        if curAddressDict["Export"] == 'x':
          outfile.write(lineEnd)
          outfile.write('BEGIN:VCARD'+lineEnd)
          outfile.write('VERSION:2.1'+lineEnd)
          nameLine='N:'+curAddressDict["Nachname"] + ";" + curAddressDict["Vorname"] + ';;;' + lineEnd
          logging.info("nameLine="+nameLine)
          outfile.write(nameLine)
          FNameLine='FN:'+curAddressDict["Vorname"] + " " + curAddressDict["Nachname"] + lineEnd
          logging.info("FNameLine="+FNameLine)
          outfile.write(FNameLine)
          homePhoneNumber=formatTelefonForInternational(curAddressDict["Telefon"])
          if len(homePhoneNumber) != 0:
            telHomeLine='TEL;VOICE:'+homePhoneNumber + lineEnd
            logging.info("telHomeLine="+telHomeLine)
            outfile.write(telHomeLine)
          telWork=formatTelefonForInternational(curAddressDict["Telefongesch"])
          if len(telWork) != 0:
            telWorkLine='TEL;WORK;VOICE:'+telWork + lineEnd
            logging.info("telWorkLine="+telWorkLine)
            outfile.write(telWorkLine)
          telCell=formatTelefonForInternational(curAddressDict["mobil"])
          if len(telCell) != 0:
            telCellLine='TEL;CELL:'+telCell + lineEnd
            logging.info("telCellLine="+telCellLine)
            outfile.write(telCellLine)
          #EMAIL;INTERNET:Rainer.Zink@allianz.de
          if len(curAddressDict["EMail1"]) != 0:
            email1Line='EMAIL;INTERNET:'+ curAddressDict["EMail1"] + lineEnd
            logging.info("email1Line="+email1Line)
            outfile.write(email1Line)
          #EMAIL;INTERNET:Rainer_Zink@gmx.de
          if len(curAddressDict["EMail2"]) != 0:
            email2Line='EMAIL;INTERNET:'+ curAddressDict["EMail2"] + lineEnd
            logging.info("email2Line="+email2Line)
            outfile.write(email2Line)
          #ADR;:;;Alte Zimmerei 3;Hochdorf;;73269;D
          addrLine='ADR;:;;'\
            + curAddressDict["Strasse"] + ';' \
            + curAddressDict["Ort"] + ';' \
            + ';' \
            + curAddressDict["PLZ"] + ';' \
            + curAddressDict["Staat"]  \
            + lineEnd
          logging.info("addrLine="+addrLine)
          outfile.write(addrLine)
          #BDAY:1971-03-20
          if (len(curAddressDict["Geburtsjahr"]) != 0):
            birthdayLine='BDAY:'+curAddressDict["Geburtsjahr"] +"-"+curAddressDict["Geburtsmonat"]+"-"+curAddressDict["Geburtstag"]+lineEnd
            logging.info("birthdayLine="+birthdayLine)
            outfile.write(birthdayLine)
          outfile.write('END:VCARD')
    except IOError:
      logging.info("error opening file %s" % tgtFileName) 
  finally:
    outfile.close()
  return 1

###########################################################################
def writeGeburtstagICS(tgtFileName):
  try:
    # nested try necessary for finally in Python 2.4
    try:
      #outfile = codecs.open(tgtFileName, "wb","latin1","xmlcharrefreplace")
      outfile = codecs.open(tgtFileName, "wb", "utf8")
      outfile.write(ICSHeader())
      for curAddressDict in addressLines:
        if (len(curAddressDict["Geburtsjahr"]) != 0):
          try:
            year=int(curAddressDict["Geburtsjahr"])
            month=int(curAddressDict["Geburtsmonat"])
            day=int(curAddressDict["Geburtstag"])
          except:  
             logging.info("error converting date %s %s %s from Name %s %s" % (curAddressDict["Geburtsjahr"],curAddressDict["Geburtsmonat"],curAddressDict["Geburtstag"],curAddressDict["Vorname"],curAddressDict["Nachname"])) 
             continue 
          birthday = date(year,month,day)
          outfile.write('BEGIN:VEVENT'+lineEnd)
          outfile.write('DTSTART;VALUE=DATE:'+birthday.strftime("%Y%m%d")+lineEnd)
          outfile.write('DTEND;VALUE=DATE:'+(birthday+timedelta(1)).strftime("%Y%m%d")+lineEnd)
          outfile.write('RRULE:FREQ=YEARLY;UNTIL=2100'+birthday.strftime("%m%d")+lineEnd)
          outfile.write('CLASS:PRIVATE'+lineEnd)
          outfile.write('SEQUENCE:0'+lineEnd)
          outfile.write('STATUS:CONFIRMED'+lineEnd)
          outfile.write('SUMMARY:'+ curAddressDict["Vorname"] + ' ' + curAddressDict["Nachname"] + ' (' + birthday.strftime("%Y") +') Geburtstag'+ lineEnd)
          outfile.write('BEGIN:VALARM'+lineEnd)
          outfile.write('ACTION:EMAIL'+lineEnd)
          outfile.write('DESCRIPTION:This is an event reminder'+lineEnd)
          outfile.write('SUMMARY:Alarm notification'+lineEnd)
          outfile.write('ATTENDEE:mailto:zifts69@googlemail.com'+lineEnd)
          outfile.write('TRIGGER:-P2D'+lineEnd)
          outfile.write('END:VALARM'+lineEnd)
          outfile.write('END:VEVENT'+lineEnd)
          
      outfile.write('END:VCALENDAR'+lineEnd)
                   
    except IOError:
      logging.info("error opening file %s" % tgtFileName) 
  finally:
    outfile.close()
  return 1

def ICSHeader():
  header='BEGIN:VCALENDAR' + lineEnd +\
         'PRODID:-//Google Inc//Google Calendar 70.9054//EN' + lineEnd +\
         'VERSION:2.0' + lineEnd +\
         'CALSCALE:GREGORIAN' + lineEnd +\
         'METHOD:PUBLISH' + lineEnd +\
         'X-WR-CALNAME:Geburtstage' + lineEnd +\
         'X-WR-TIMEZONE:Europe/Berlin' + lineEnd +\
         'X-WR-CALDESC:' + lineEnd +\
         'BEGIN:VTIMEZONE' + lineEnd +\
         'TZID:Europe/Berlin' + lineEnd +\
         'X-LIC-LOCATION:Europe/Berlin' + lineEnd +\
         'BEGIN:DAYLIGHT' + lineEnd +\
         'TZOFFSETFROM:+0100' + lineEnd +\
         'TZOFFSETTO:+0200' + lineEnd +\
         'TZNAME:CEST' + lineEnd +\
         'DTSTART:19700329T020000' + lineEnd +\
         'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU' + lineEnd +\
         'END:DAYLIGHT' + lineEnd +\
         'BEGIN:STANDARD' + lineEnd +\
         'TZOFFSETFROM:+0200' + lineEnd +\
         'TZOFFSETTO:+0100' + lineEnd +\
         'TZNAME:CET' + lineEnd +\
         'DTSTART:19701025T030000' + lineEnd +\
         'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU' + lineEnd +\
         'END:STANDARD' + lineEnd +\
         'END:VTIMEZONE' + lineEnd
  return header       


############################################################################
# main starts here
# global variables


rootLogger = initLogger()
if sys.platform == "win32":
  #defaultEncoding="latin1"
  defaultEncoding="UTF-8"
else:
  defaultEncoding="UTF-8"
lineEnd='\r\n'
#testsnippets()

if len(sys.argv) == 1 :
    print description
    print sys.argv[0] + "<xml_configfile>"
    configFileName = 'ConvertAdressCSV.xml'
else:
    configFileName=sys.argv[1]


# global Variables
inSeparator = ','
inEnclosingChar='"'
addressLines = []
curDict = {}
inputDataDict = {}
#(srcName, tgtThunderbirdAbsName,tgtGigasetAbsName,tgtTSinusAbsName,tgtGMXAbsName,tgtSamsungKiesAbsName) = readConfigFromXML(configFileName)
inputDataDict = readConfigFromXML(configFileName)
processSrcFile(inputDataDict["srcName"])
#writeThunderbirdOutput(inputDataDict["tgtThunderbirdAbsName"])
#writeGigasetOutput(inputDataDict["tgtGigasetAbsName"])
#writeTSinusOutput(inputDataDict["tgtTSinusAbsName"])
#writeGMXCSVOutput(inputDataDict["tgtGMXAbsName"])
#writeSamsungKiesCSVOutput(inputDataDict["tgtSamsungKiesAbsName"])
writeGMailContactsCSV(inputDataDict["tgtGMailContactsCSVName"])
#writeSamsungAndroidVCard(inputDataDict["tgtSamsungAndroidVCFName"])
#writeGeburtstagICS(inputDataDict["tgtGeburtstageICSName"])

###########################################################################
def testsnippets():
  testString ='"test","2test2",,,'
  regexPattern = re.compile(r'\A".*"')
  matchObject = regexPattern.match(testString)
  if matchObject:
    print(matchObject.group())
    print(matchObject.span())
  else:
    print("no match found")  
  
  listOfmatches = regexPattern.findall(testString)
  print listOfmatches
  
  endindex = testString.find('test')
  result = testString[0:endindex+2]
  print (endindex)
  print ("result="+result)

  count = testString.count('test')
  print (count)
  
  (left,sep,right)=testString.partition('\A".*"')
  print("sep="+sep)      
