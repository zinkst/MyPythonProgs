#!/usr/bin/python
# -*- coding: utf-8 -*-

description = """This program has two modies:
As input you can either give a Source Directory or a file with list files to process 
Currently when a directory is given it search for files with rating equal or higher the ratingThreshold and 
copies found files to the target dir with an indes structure

When a playlist is given default is to add the newFMPSRating is set for all found files. Also POPM and RATING tags are set accordingly
 
"""

import os
import fnmatch
import shutil
#import glob
import sys
import re
import string
import logging
import logging.config 

import json
import yaml
import taglib # https://pypi.python.org/pypi/pytaglib
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC,TXXX, POPM, TCMP, ID3NoHeaderError
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3, HeaderNotFoundError

import math
import subprocess
#from xml import dom
#from xml.dom import minidom
#from xml.dom import Node
import urllib.parse


     
############################################################################
def initLogger(config):
    handler = logging.StreamHandler(sys.stdout)
    frm = logging.Formatter("%(asctime)s [%(levelname)-5s]: %(message)s", "%Y%m%d %H:%M:%S")
    handler.setFormatter(frm)
    logger = logging.getLogger()
    logger.addHandler(handler)
    print('config["loglevel"] = ' + config["loglevel"])
    if config["loglevel"] == "DEBUG":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger


############################################################################
def tagFoundButUnratedFile(srcCompleteFileName, toolName, toolOptions,foundNoRating,foundWithRating,foundWithUpperCaseRating):
    """
    This method adds FMPS_RATING to all files given. It adds a default rating of 0.4 if no FMPS_RATING is found.
    In addition it computes POPM (e.g Windows Media Player) and RATING (e.g. xbmc) tags to files     
    """
    os.chdir(os.path.dirname(srcCompleteFileName))
    f = taglib.File(srcCompleteFileName)
    mutID3 = ID3(srcCompleteFileName)
    logging.debug("working dir: " + os.getcwd())
    rating='0.4'
    if 'FMPS_RATING' in f.tags:
      logging.info("Rating with wrong case set for " + srcCompleteFileName)
      rating=f.tags['FMPS_RATING'][0]
      logging.debug(str(f.tags['FMPS_RATING']) + str(f.tags))
      new_entry={'srcCompleteFileName' : srcCompleteFileName , 'TAGS' : f.tags }
      foundWithUpperCaseRating.append(new_entry)
      # pytaglib can only write  tags in uppercase so these 2 lines below do not work
      del f.tags['FMPS_RATING']
      mutID3.delall('TXXX:FMPS_RATING')
      mutID3.add(TXXX(encoding=3, desc='FMPS_Rating', text=rating))
      # add xbmcratings see http://kodi.wiki/view/Adding_music_to_the_library#Ratings_in_ID3_tags
    elif 'FMPS_Rating' in f.tags:
      logging.info("Rating set for " + srcCompleteFileName)
      logging.debug(str(f.tags['FMPS_Rating']) + str(f.tags))
      foundWithRating.append(new_entry)
      rating=f.tags['FMPS_Rating'][0]
    else:   
      logging.info("No Rating set for " + srcCompleteFileName)
      new_entry={'srcCompleteFileName' : srcCompleteFileName , 'TAGS' : f.tags }
      foundNoRating.append(new_entry)
      mutID3.add(TXXX(encoding=3, desc='FMPS_Rating', text=u'0.4'))
    xbmc_rating=math.trunc(float(rating)*5)
    mutID3.add(TXXX(encoding=3, desc='RATING', text=str(xbmc_rating)))
    popm_rating=math.trunc(float(rating)*255)
    mutID3.add(POPM(rating=popm_rating))
    MP3CARidx=srcCompleteFileName.find('MP3CAR') 
    szCarDir=srcCompleteFileName[MP3CARidx-3:MP3CARidx]
    mutID3.add(TXXX(encoding=3, desc='SZ_CarDir', text=szCarDir))
    #f.tags['SZ_CarDir']=szCarDir
    mutID3.save()

############################################################################
def setCompilationTag(srcCompleteFileName):
    """
    set the compilation tag TCMP to file
    """
    mutID3 = ID3(srcCompleteFileName)
    logging.info("setting compilation tag for " + os.path.basename(srcCompleteFileName))
    mutID3.add(TCMP(encoding=3, text='1'))
    mutID3.save()
    
      
 
############################################################################
def writeDictsToFile(inputParams, logging,foundNoRating,foundWithRating,foundWithUpperCaseRating):
  
  if not os.path.exists(inputParams['tgtDirName']):
     logging.debug("Creating" + inputParams['tgtDirName'])
     os.makedirs(inputParams['tgtDirName'], 0o775)
  WithRatingFileName=os.path.join(inputParams['tgtDirName'], 'foundWithRating.lst')
  logging.debug("WithRatingFileName = " + WithRatingFileName)
  with open(WithRatingFileName, 'w') as withRatingfile:
     for entry in foundWithRating:
       #output=(str(entry['FMPS_RATING']) + '|' + str(entry['ARTIST']) + '|' + str(entry['TITLE']) + '|' + str(entry['srcCompleteFileName']) )
       output=(entry['srcCompleteFileName'])
       logging.debug(output)
       withRatingfile.write(str(output) + '\n') 
  NoRatingFileName=os.path.join(inputParams['tgtDirName'], 'NoRating.lst')
  logging.debug("NoRatingFileName = " + NoRatingFileName)
  with open(NoRatingFileName, 'w') as noRatingFile:
     for entry in foundNoRating:
       #output=(str(entry['ARTIST']) + '|' + str(entry['TITLE']) + '|' + str(entry['srcCompleteFileName']) )
       output=(entry)
       logging.debug(output)
       noRatingFile.write(str(output)+ '\n')
  UpperCaseRatingFileName=os.path.join(inputParams['tgtDirName'], 'UpperCaseRating.lst')
  logging.debug("UpperCaseRatingFileName = " + UpperCaseRatingFileName)
  with open(UpperCaseRatingFileName, 'w') as upperCaseRatingFile:
     for entry in foundWithUpperCaseRating:
       #output=(str(entry['ARTIST']) + '|' + str(entry['TITLE']) + '|' + str(entry['srcCompleteFileName']) )
       output=(entry)
       logging.debug(output)
       upperCaseRatingFile.write(str(output)+ '\n')

############################################################################

def testMutagen(logging, srcCompleteFileName):
    audio = MP3(srcCompleteFileName, ID3=EasyID3)
    logging.info(audio.pprint())
#         MPEG 1 layer 3, 160000 bps, 44100 Hz, 270.63 seconds (audio/mp3)
#         album=Odyssey
#         artist=Yngwie J. Malmsteen's Rising Force
#         date=1988
#         genre=Hard Rock
#         length=270628
#         media=DIG
#         title=Faster Than The Speed Of Light
#         tracknumber=10/12
    audio2 = ID3(srcCompleteFileName)
#          {'TALB': TALB(encoding=3, text=['Odyssey']), 
#           'TMED': TMED(encoding=0, text=['DIG']), 
#           'TXXX:SZ_CARDIR': TXXX(encoding=3, desc='SZ_CARDIR', text=['001']),
#           'TDRC': TDRC(encoding=3, text=['1988']), 
#           'TLEN': TLEN(encoding=0, text=['270628']),
#           'TCON': TCON(encoding=3, text=['Hard Rock']),
#           'TXXX:FMPS_RATING': TXXX(encoding=3, desc='FMPS_RATING', text=['0.4']),
#           'TIT2': TIT2(encoding=3, text=['Faster Than The Speed Of Light']),
#           'TPE1': TPE1(encoding=3, text=["Yngwie J. Malmsteen's Rising Force"]),
#           'TRCK': TRCK(encoding=3, text=['10/12']) }
    #audio.add(TIT2(encoding=3, text=u"An example"))
    audio2.add(TXXX(encoding=3, desc='FMPS_Rating', text=u'0.4'))
    audio2.save()
    logging.info(audio2)

############################################################################
# def processDirForUpdateTagsForFile(inputParams, logging):
#   foundNoRating = []
#   foundWithRating = []
#   foundWithUpperCaseRating = []
#   inputParams["srcDirName"]=inputParams["linkDirName"]
#   for Verz, VerzList, DateiListe in os.walk(inputParams["linkDirName"]):
#     logging.debug(" VerzList = " + str(VerzList))
#     logging.debug(" DateiListe = " + str(DateiListe))
#     for Datei in sorted(DateiListe):
#       srcCompleteFileName = os.path.join(Verz, Datei)
#       logging.debug(" srcCompleteFileName  = " + srcCompleteFileName) 
#       if fnmatch.fnmatch(srcCompleteFileName, '*.' + config["fileFilter"]):
#         #tagFoundButUnratedFile(srcCompleteFileName, inputParams["toolName"],inputParams["toolOptions"],foundNoRating,foundWithRating,foundWithUpperCaseRating)
#         resyncMP3Ratings(srcCompleteFileName, foundNoRating, foundWithRating)
#         #setCompilationTag(srcCompleteFileName, foundNoRating, foundWithRating)
#         #testMutagen(logging, srcCompleteFileName)
#   writeDictsToFile(inputParams, logging,foundNoRating,foundWithRating,foundWithUpperCaseRating) 


############################################################################
def processDirForMP3s(inputParams, logging):
  foundNoRating = []
  foundWithRating = []
  foundWithUpperCaseRating = []
  for Verz, VerzList, DateiListe in os.walk(inputParams["srcDirName"]):
    logging.debug(" VerzList = " + str(VerzList))
    logging.debug(" DateiListe = " + str(DateiListe))
    for Datei in sorted(DateiListe):
      srcCompleteFileName = os.path.join(Verz, Datei)
      logging.debug(" srcCompleteFileName  = " + srcCompleteFileName) 
      if fnmatch.fnmatch(srcCompleteFileName, '*.' + config["fileFilter"]):
        findRatedMP3s(srcCompleteFileName,inputParams,foundNoRating,foundWithRating)
  writeDictsToFile(inputParams, logging,foundNoRating,foundWithRating,foundWithUpperCaseRating) 
  return foundWithRating
  
############################################################################
def findTgtDirName(inputParams, f, logging):
    if 'ARTIST' in f.tags:
        startLetter=f.tags['ARTIST'][0][0]
        logging.debug("startLetter = " + startLetter)
        letterCode=ord(startLetter.upper())
        if letterCode in range(65,68):
          letterSubdir = "ABC";
        elif letterCode in range(68,71):
          letterSubdir = "DEF";
        elif letterCode in range(71,74):
          letterSubdir = "GHI";
        elif letterCode in range(74,77):
          letterSubdir = "JKL";
        elif letterCode in range(77,80):
          letterSubdir = "MNO";
        elif letterCode in range(80,83):
          letterSubdir = "PQR";
        elif letterCode in range(83,86):
          letterSubdir = "STU";
        elif letterCode in range(86,91):
          letterSubdir = "VWXYZ";
        else:
           letterSubdir = "Anderer";
        tgtFullDirName = os.path.join(inputParams["tgtDirName"], letterSubdir,f.tags['ARTIST'][0])
    else:
        tgtFullDirName = os.path.join(inputParams["tgtDirName"], 'UNBEKANNT')
    if not os.path.exists(tgtFullDirName):
        logging.debug("Creating" + tgtFullDirName)
        os.makedirs(tgtFullDirName, 0o775)
    return tgtFullDirName

############################################################################
def copyMP3ToTgtDir(srcCompleteFileName, inputParams, f, ezid3):
  sep='_'
  #new_entry = {'srcCompleteFileName':srcCompleteFileName, 'TAGS':f.tags, 'EZID3':ezid3}
  #foundWithRating.append(new_entry)
    
  discnumber = None
  tracknumber = None
  album = None
  if 'TRACKNUMBER' in f.tags:
    tracknumber = f.tags['TRACKNUMBER'][0].split('/')[0].zfill(2)
  if 'DISCNUMBER' in f.tags:
    discnumber = f.tags['DISCNUMBER'][0].split('/')[0]
  if 'ALBUM' in f.tags:
    album = f.tags['ALBUM'][0]
  tgtFullDirName = findTgtDirName(inputParams, f, logging)
  tgtFileName = ""
  if 'compilation' in ezid3.keys() and ezid3['compilation'][0] == '1':
    logging.debug(os.path.basename(srcCompleteFileName) + " is part of compilation")
    tgtFileName = ezid3['artist'][0] + sep + ezid3['title'][0] + '.' + config["fileFilter"]
  elif discnumber and tracknumber and album:
    tgtFileName = album[0:3] + sep + 'D' + discnumber + sep + tracknumber + sep + f.tags['TITLE'][0] + '.' + config["fileFilter"]
  elif tracknumber and album:
    tgtFileName = album[0:3] + sep + tracknumber + sep + f.tags['TITLE'][0] + '.' + config["fileFilter"]
  elif tracknumber:
    tgtFileName = tracknumber + sep + f.tags['TITLE'][0] + '.' + config["fileFilter"]
  elif album:
    tgtFileName = album + sep + f.tags['TITLE'][0] + '.' + config["fileFilter"]
  else:
    tgtFileName = f.tags['TITLE'][0] + '.' + config["fileFilter"]
  tgtFileName = tgtFileName.replace('/', '_')
  tgtFileName = tgtFileName.replace(':', '_')
  tgtFileName = tgtFileName.replace('>', '_')
  tgtFileName = tgtFileName.replace('<', '_')
  tgtFileName = tgtFileName.replace('?', '_')
# tgtFileName=tgtFileName.replace('!','_')
  tgtCompleteFilename = os.path.join(tgtFullDirName, tgtFileName)
  logging.info(srcCompleteFileName + " => " + tgtCompleteFilename)
  if not os.path.exists(tgtCompleteFilename):
    if inputParams['reencode']:
      subprocess.call(['lame', inputParams['lame_params'], srcCompleteFileName, tgtCompleteFilename])
    else:
      shutil.copy(srcCompleteFileName, tgtCompleteFilename)
  else:
    logging.debug("already existing " + tgtCompleteFilename)
  

############################################################################

def findRatedMP3s(srcCompleteFileName,inputParams,foundNoRating,foundWithRating):
    # {'TITLE': ['Foot of the mountain'], 'FMPS_RATING': ['0.8'], 'TRACKNUMBER': ['04/10'], 'COMMENT': ['Created with EAC/REACT v2.0.akku.b03, 2010-01-13'], 'FMPS_RATING_AMAROK_SCORE': ['0.0975'], 'REPLAYGAIN_TRACK_PEAK': ['0.557932'], 'ALBUM': ['Foot of the mountain'], 'ENCODING': ['LAME 3.97 -V2 --vbr-new --noreplaygain --nohist'], 'MP3GAIN_ALBUM_MINMAX': ['136,251'], 'ARTIST': ['A-HA'], 'REPLAYGAIN_ALBUM_GAIN': ['-3.470000'], 'MP3GAIN_UNDO': ['+004,+004,N'], 'MP3GAIN_MINMAX': ['138,251'], 'REPLAYGAIN_ALBUM_PEAK': ['0.606102'], 'COMMENT:ID3V1 COMMENT': ['Created with EAC/REACT v2.0.'], 'REPLAYGAIN_TRACK_GAIN': ['-4.040000 dB'], 'GENRE': ['Pop'], 'DATE': ['2009'], 'ENCODEDBY': ['SZ']}
    #logging.debug(" srcCompleteFileName = " + srcCompleteFileName)
    #logging.debug(" tgtDirName = " + inputParams["tgtDirName"])
    os.chdir(os.path.dirname(srcCompleteFileName))
    f = taglib.File(srcCompleteFileName)
    logging.debug(f.tags)
    ezid3 = EasyID3(srcCompleteFileName)
    # EasyID3: {'artist': ['John Parr'], 'compilation': ['1'], 'date': ['1985'], 'title': ['St. Elmo´s Fire'], 'album': ['Prinz - greatest Film hits'], 'genre': ['Pop'], 'tracknumber': ['03/15']}
    curRating = None
    if 'FMPS_RATING' in f.tags:
        try:
           curRating = float(f.tags['FMPS_RATING'][0])
        except ValueError:
          logging.error(f.tags['FMPS_RATING'][0] + " not a float")
        if curRating >= inputParams['ratingThreshold']:
          new_entry = {'srcCompleteFileName':srcCompleteFileName, 'TAGS':f, 'EZID3':ezid3}
          foundWithRating.append(new_entry)
          logging.info("rating " + str(curRating) + " filename: " + os.path.basename(srcCompleteFileName))
          #copyMP3ToTgtDir(srcCompleteFileName, inputParams, foundWithRating, f, ezid3)
        else:
          logging.debug("tagged file with rating " + f.tags['FMPS_RATING'][0] + " under threshold: " + srcCompleteFileName)
    else:
        new_entry={'srcCompleteFileName' : srcCompleteFileName , 'TAGS' : f.tags }
        foundNoRating.append(new_entry)
        logging.debug("unrated file " + srcCompleteFileName)

############################################################################
"""
#EXTM3U
#EXTINF:238,Helene Fischer - Von hier bis unendlich
/shares/Filer/Musik/Sammlung/Alben/Helene Fischer/Best of Live/01_Von hier bis unendlich.mp3
#EXTINF:162,Helene Fischer - Du hast mein Herz berührt
/shares/Filer/Musik/Sammlung/Alben/Helene Fischer/Best of Live/02_Du hast mein Herz berührt.mp3
"""
def writeM3UPlaylistForMatchingMP3s(inputParams, logging,foundWithRating):
  if not os.path.exists(inputParams['m3uDirName']):
     logging.debug("Creating" + inputParams['m3uDirName'])
     os.makedirs(inputParams['m3uDirName'], 0o775)
  M3UFileName=os.path.join(inputParams['m3uDirName'], 'Rating_gr_'+str(inputParams['ratingThreshold'])+'.m3u')
  logging.debug("M3UFileName = " + M3UFileName)
   
  with open(M3UFileName, 'w') as M3Ufile:
     M3Ufile.write('#EXTM3U' + '\n') 
     for entry in foundWithRating:
       #new_entry = {'srcCompleteFileName':srcCompleteFileName, 'TAGS':f.tags, 'EZID3':ezid3}
       audio = MP3(entry['srcCompleteFileName'])
       duration=str(int(audio.info.length))
       output=('#EXTINF:'+duration + ',' + str(entry['EZID3']['artist'][0]) + ' - ' + str(entry['EZID3']['title'][0]) )
       logging.info(output)
       M3Ufile.write(str(output) + '\n') 
       output= str(entry['srcCompleteFileName'])
       logging.info(output)
       M3Ufile.write(str(output) + '\n') 
       
       output=(entry)
       
  
############################################################################
def readPlaylistEntries(inputParams):
  playListEntries = []
  logging.info("Prcessing Playlist " + inputParams['srcPlaylistFile'])
  with open(inputParams['srcPlaylistFile']) as playListFile:
    for curLine in playListFile:
      if not curLine.startswith('#'):
        entry=urllib.parse.unquote(curLine.strip())
        if entry.find('//') != -1:
          entry=entry[entry.find('//')+2:]
        f = taglib.File(entry)
        logging.debug(f.tags)
        ezid3 = EasyID3(entry)
        newEntry = {'srcCompleteFileName':entry, 'TAGS':f, 'EZID3':ezid3}
        logging.debug(newEntry)
        playListEntries.append(newEntry)
  return playListEntries

############################################################################
def setRatingForFiles(filesToProcessDict, newFMPSRating):
  for curFile in filesToProcessDict:
    logging.info("set rating for "+ curFile['srcCompleteFileName'] + " to " + str(newFMPSRating) )
    mutID3 = ID3(curFile['srcCompleteFileName'])
    changedTag=False
    curFMPSRating = mutID3.get(u'TXXX:FMPS_Rating')
    if curFMPSRating == None:
      # No existing tag TXXX for FMPS has been found, so create one...
      logging.debug("no FMPS_RATING found: " + os.path.basename(curFile['srcCompleteFileName']))
      mutID3.add(TXXX(encoding=3, desc=u"FMPS_Rating", text=[str(newFMPSRating)]))
      changedTag=True
    else:
      newFMPSRating=float(curFMPSRating[0])
    syncMP3Ratings(mutID3, newFMPSRating)
    if changedTag:  
      mutID3.save()
   
############################################################################
def syncMP3Ratings(mutID3, newFMPSRating):
  """
  This method resyncs FMPS_RATING to all files given. 
  It resyncs POPM (e.g Windows Media Player) and RATING (e.g. xbmc) tags to files 
  it is given that FMPS_RATING is set
  """
  changedTag=False
  newPopmRating=math.trunc(newFMPSRating*255)
  try:
    curPOPMRating=mutID3.getall('POPM')[0].rating
    if curPOPMRating != newPopmRating:
      mutID3.delall('POPM')
      mutID3.add(POPM(rating=newPopmRating))
      changedTag=True
    else:
      logging.debug("POPM tag found and already synced: ")  
  except (KeyError, IndexError) as e:
    logging.debug('POPM rating did not exist:  adding ... it') 
    mutID3.add(POPM(rating=newPopmRating))
    changedTag=True
 
  # handle RATING  
  newRATING=math.trunc(newFMPSRating*5)
  try:
    curRATINGStr=mutID3.getall('TXXX:RATING')[0].text[0]
    curRATING=float(curRATINGStr)
    if curRATING != newRATING:
      mutID3.add(TXXX(encoding=3, desc='RATING', text=str(newRATING)))
      changedTag=True
    else:
      logging.debug("RATING found and already synced: " )  
  except (KeyError, IndexError) as e :
    logging.debug('RATING rating did not exist:  adding ... it') 
    mutID3.add(TXXX(encoding=3, desc='RATING', text=str(newRATING)))
    changedTag=True
  if changedTag:  
    mutID3.save()

    
############################################################################
# main starts here
# global variables

if len(sys.argv) == 1 :
    print(description)
    print(sys.argv[0] + "<configfile>")
    configFileName = 'ProcessMp3sInDir.yaml'
else:
    configFileName = sys.argv[1]


# Python2 
#with open(configFileName, 'r') as cfgfile:
# Python3 
with open(configFileName, 'r',encoding='utf-8') as cfgfile:
    #config = json.load(cfgfile)
    config = yaml.load(cfgfile)
logger = initLogger(config)

configuration = config["configuration"]  
inputParams = config[configuration]
logging.debug(inputParams)

#processDirForUpdateTagsForFile(inputParams, logging)
if inputParams['srcType'] == 'dir':
  logging.info("input Type directory")
  filesToProcessDict = processDirForMP3s(inputParams, logging)
  for curFile in filesToProcessDict:
    #pass
    copyMP3ToTgtDir(curFile['srcCompleteFileName'], inputParams, curFile['TAGS'], curFile['EZID3'])
  writeM3UPlaylistForMatchingMP3s(inputParams, logging, filesToProcessDict)

elif inputParams['srcType'] == 'playlist': 
  logging.info("input Type playlist")
  filesToProcessDict = readPlaylistEntries(inputParams)
  newFMPSRating=inputParams['newFMPSRating']
  setRatingForFiles(filesToProcessDict, newFMPSRating)

logging.info("Finished -  Number of files processed: " + str(len(filesToProcessDict)) )

