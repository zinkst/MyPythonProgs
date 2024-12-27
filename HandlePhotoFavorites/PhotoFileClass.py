#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import re
from pyaml_env import parse_config

# dnf install python3-ffmpeg-python.noarch
# docs: https://kkroening.github.io/ffmpeg-python/
import ffmpeg

# dnf install python3-pillow.x86_64
from PIL import Image
from PIL.ExifTags import TAGS

from FileObject import FileObject
from functions import initLogger


####################################################################


class PhotoFile:
  fileObject = FileObject
  tgtDirName = ""             # e.g.  /links/Photos/Favoriten
  tgtFileNameCompressed = ""  # e.g.   ${tgtDirName}/${Compressed}/${yearOfPhoto}/${favoriteRelativeTgtDir}
  tgtFileNameSymlink = ""     # e.g.  ${tgtDirName}/&{linkRelativeTgtDirName}/${yearOfPhoto}/${favoriteRelativeTgtDir}
  isFavoritePhoto = False
  yearOfPhoto = ""            # e.g. 2024
  tgtLinkLinkDepthToBaseDir = ""  # e.g. 2

  metadata = {}
  favoriteFolderProps = {}
  prgConfig = {}

  def __init__(self, fileObject, prgConfig, logger):
    self.logger = logger
    self.fileObject = fileObject
    self.prgConfig = prgConfig
    self.tgtDirName = prgConfig.get("tgtDirName")
    if prgConfig.get("year"):
      self.yearOfPhoto = prgConfig.get("year")
    else:
      self.yearOfPhoto = self.fileObject.srcDirRelativeToRootDir[0:4]
    self.readTgtFolderInformation(prgConfig.get("favoritenInfoFileBaseName"))
    yearSubFolder = self.favoriteFolderProps.get("yearSubFolder")
    if yearSubFolder != None:
      self.tgtLinkRelativeDir = os.path.join(prgConfig.get("linkRelativeTgtDirName"),
                                             self.favoriteFolderProps.get("rootSubFolder"),
                                             self.yearOfPhoto,
                                             yearSubFolder)
    else:
      self.tgtLinkRelativeDir = os.path.join(prgConfig.get("linkRelativeTgtDirName"),
                                             self.favoriteFolderProps.get("rootSubFolder"),
                                             self.yearOfPhoto)
    self.tgtLinkLinkDepthToBaseDir = 1 + self.tgtLinkRelativeDir.count(os.sep) + 1
    self.tgtFileNameSymlink = os.path.join(self.tgtDirName,
                                           self.tgtLinkRelativeDir,
                                           self.fileObject.fileBaseName)
    self.tgtRelativeLink = os.path.join((".." + os.sep) * self.tgtLinkLinkDepthToBaseDir,
                                        self.fileObject.srcRelativeDirName,
                                        self.fileObject.srcDirRelativeToRootDir,
                                        self.fileObject.fileBaseName)

    if yearSubFolder != None:
      self.tgtFileNameCompressed = os.path.join(self.tgtDirName,
                                                prgConfig.get("compressedRelativeTgtDirName"),
                                                self.favoriteFolderProps.get("rootSubFolder"),
                                                self.yearOfPhoto,
                                                yearSubFolder,
                                                self.fileObject.fileBaseName)
    else:
      self.tgtFileNameCompressed = os.path.join(self.tgtDirName,
                                                prgConfig.get("compressedRelativeTgtDirName"),
                                                self.favoriteFolderProps.get("rootSubFolder"),
                                                self.yearOfPhoto,
                                                self.fileObject.fileBaseName)

  ##############################################################################################
  def __str__(self):
    output = "PhotoFile \n"
    output += "FileName".ljust(25, ' ') + ": " + self.fileObject.absFileName + "\n"
    output += "tgtFilenameCompressed".ljust(25, ' ') + ": " + self.tgtFileNameCompressed + "\n"
    output += "tgtFilenameSymlink".ljust(25, ' ') + ": " + self.tgtFileNameSymlink + "\n"
    output += "srcLinkDepthToBaseDir".ljust(25, ' ') + ": " + str(self.tgtLinkLinkDepthToBaseDir) + "\n"
    output += "tgtLinkRelativeDir".ljust(25, ' ') + ": " + self.tgtLinkRelativeDir + "\n"
    for k, v in self.metadata.items():
      output += str(k).ljust(25, ' ') + ": " + str(v) + "\n"
    # for k, v in self.photoProps.items():
    #   output += str(k).ljust(25, ' ') + ": " + str(v) + "\n"
    return output

  ##############################################################################################
  # reads additional target FilenName Information for file FavoriteProperties.yml
  # e.g.
  # rootSubFolder: Familie Zink
  # yearSubFolder: 201007_Skandinavien

  def readTgtFolderInformation(self, folderPropsFileBaseName):
    folderPropsFile = os.path.join(self.fileObject.srcFileDirName, folderPropsFileBaseName)
    if os.path.exists(folderPropsFile):
      self.favoriteFolderProps = parse_config(folderPropsFile)
    else:
      self.logger.error("Folder Properties File %s does not exist - exiting ", folderPropsFile)
      exit(-1)
  ##############################################################################################

  def ProbePhotoFileRating(self):
    photo = Image.open(self.fileObject.absFileName)
    photoExifdata = photo.getexif()
    # tag_id 18246 -> tag : Rating
    ratingTagID = 18246
    rating = photoExifdata.get(ratingTagID)
    if rating:
      self.logger.debug("Rating %d for file %s", rating, self.fileObject.fileBaseName)
      self.metadata["rating"] = photoExifdata.get(ratingTagID)
      self.isFavoritePhoto = True

  ##############################################################################################
  def targetFileCompressedExists(self):
    if os.path.exists(self.tgtFileNameCompressed):
      return True
    else:
      os.makedirs(os.path.dirname(self.tgtFileNameCompressed), exist_ok=True)
      return False

  ##############################################################################################
  def targetFileSymlinkExists(self):
    if os.path.exists(self.tgtFileNameSymlink):
      return True
    else:
      os.makedirs(os.path.dirname(self.tgtFileNameSymlink), exist_ok=True)
      return False

  ##############################################################################################
  def CreateSymlinkForPhoto(self):
    if self.targetFileSymlinkExists():
      self.logger.info("Photo Symlink %s exists - skipping", self.tgtFileNameSymlink)
    else:
      self.logger.info("calling os.symlink(" + self.tgtRelativeLink + "," + self.tgtFileNameSymlink + ")")
      os.symlink(self.tgtRelativeLink, self.tgtFileNameSymlink)

  ##############################################################################################
  def ShrinkPhoto(self):
    if self.targetFileCompressedExists():
      self.logger.info("Compressed Photo  %s exists - skipping", self.tgtFileNameCompressed)
      return
    self.logger.info("Compressing Photo: %s ", self.tgtFileNameCompressed)
    photo = Image.open(self.fileObject.absFileName)
    height = photo.height
    width = photo.width
    exif = photo.getexif()
    if height > 1920 or width > 1920:
      photo = photo.resize((width // 2, height // 2))
    photo.save(self.tgtFileNameCompressed, quality=40, exif=exif)
    # datetime.strptime(exif["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
    origFileTimeStamp = os.path.getmtime(self.fileObject.absFileName)
    os.utime(self.tgtFileNameCompressed, (origFileTimeStamp, origFileTimeStamp))
