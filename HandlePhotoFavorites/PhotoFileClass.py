#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import re

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
  tgtDirName = ""
  tgtFileNameCompressed = ""
  tgtFileNameSymlink = ""
  srcLinkDepthToBaseDir = ""
  isFavoritePhoto = False

  metadata = {}
  # photoProps = {}
  vitalMetaDataKeys = ["date", "movie_name"]
  prgConfig = {}

  def __init__(self, fileObject, prgConfig, logger):
    self.logger = logger
    self.fileObject = fileObject
    self.prgConfig = prgConfig
    self.tgtDirName = prgConfig.get("tgtDirName")
    self.tgtFileNameCompressed = os.path.join(self.tgtDirName, "Compressed",
                                              self.fileObject.srcDirRelativeToRootDir,
                                              self.fileObject.fileBaseName)
    self.srcLinkDepthToBaseDir = self.fileObject.srcRelativeDirName.count(os.sep) + 2 + self.fileObject.srcDirRelativeToRootDir.count(os.sep) + 1
    self.tgtFileNameSymlink = os.path.join(self.tgtDirName, "SymlinksNew/Familie Zink",
                                           self.fileObject.srcDirRelativeToRootDir,
                                           self.fileObject.fileBaseName)
    self.tgtRelativeLink = os.path.join((".." + os.sep) * self.srcLinkDepthToBaseDir,
                                        self.fileObject.srcRelativeDirName,
                                        self.fileObject.srcDirRelativeToRootDir,
                                        self.fileObject.fileBaseName)

  def __str__(self):
    output = "PhotoFile \n"
    output += "FileName".ljust(25, ' ') + ": " + self.fileObject.absFileName + "\n"
    output += "tgtFilenameCompressed".ljust(25, ' ') + ": " + self.tgtFileNameCompressed + "\n"
    output += "tgtFilenameSymlink".ljust(25, ' ') + ": " + self.tgtFileNameSymlink + "\n"
    for k, v in self.metadata.items():
      output += str(k).ljust(25, ' ') + ": " + str(v) + "\n"
    # for k, v in self.photoProps.items():
    #   output += str(k).ljust(25, ' ') + ": " + str(v) + "\n"
    return output

  ##############################################################################################
  def ProbePhotoFile(self):
    photo = Image.open(self.fileObject.absFileName)
    photoExifdata = photo.getexif()
    # tag_id 18246 -> tag : Rating
    ratingTagID = 18246
    rating = photoExifdata.get(ratingTagID)
    if rating:
      self.logger.info("Rating %d for file %s", rating, self.fileObject.fileBaseName)
      self.metadata["rating"] = photoExifdata.get(ratingTagID)
      self.isFavoritePhoto = True
    # for tag_id in photoExifdata:
    #   # get the tag name, instead of human unreadable tag id
    #   tag = TAGS.get(tag_id, tag_id)
    #   data = photoExifdata.get(tag_id)
    #   # decode bytes
    #   if isinstance(data, bytes):
    #     data = data.decode()
    #   logger.debug(f"{tag_id:5}: {data}{tag:25}: {data}")

  ##############################################################################################
  def targetFileCompressedExists(self):
    if os.path.exists(self.tgtFileNameCompressed):
      self.logger.info("Compressed File %s already exists - skipping ", self.tgtFileNameCompressed)
      return True
    else:
      os.makedirs(os.path.dirname(self.tgtFileNameCompressed), exist_ok=True)
      return False

  ##############################################################################################
  def targetFileSymlinkExists(self):
    if os.path.exists(self.tgtFileNameSymlink):
      self.logger.info("Compressed File %s already exists - skipping ", self.tgtFileNameSymlink)
      return True
    else:
      os.makedirs(os.path.dirname(self.tgtFileNameSymlink), exist_ok=True)
      return False

  ##############################################################################################
  def CreateSymlinkForPhoto(self):
    if self.targetFileSymlinkExists():
      self.logger.info("Symlink %s exists - skipping", self.tgtFileNameSymlink)
    else:
      self.logger.info("calling os.symlink(" + self.tgtRelativeLink + "," + self.tgtFileNameSymlink + ")")
      os.symlink(self.tgtRelativeLink, self.tgtFileNameSymlink)

  ##############################################################################################
  def CompressPhoto(self):
    if self.targetFileCompressedExists():
      self.logger.info("Compressed Photo  %s exists - skipping", self.tgtFileNameCompressed)
    else:
      self.logger.info("Compressing Photo: %s ", self.tgtFileNameCompressed)

  ##############################################################################################

  def ConvertVideoFile(self):
    if self.targetFileExists():
      return
    if not os.path.exists(os.path.dirname(self.tgtFileName)):
      os.makedirs(os.path.dirname(self.tgtFileName))
    logger.info("Converting to %s", self.tgtFileName)
    ffmpegArgs = {}
    ffmpegArgs["loglevel"] = "panic"
    ffmpegArgs["c:v"] = "libsvtav1"
    ffmpegArgs["crf"] = 40
    ffmpegArgs["c:a"] = "libopus"
    ffmpegArgs["c:s"] = "copy"
    ffmpegArgs["map_metadata"] = 0
    # reduce size for 4k videos
    if float(self.photoProps.get("rotation")) > 0:
      if self.photoProps.get("height") > 1920:
        ffmpegArgs["vf"] = "scale=iw/2:ih/2"
    elif self.photoProps.get("width") > 1920:
      ffmpegArgs["vf"] = "scale=iw/2:ih/2"
    # add metadata which didn't exist in source file
    if self.isEssentialMetadataUpdated():
      ffmpegArgs |= self.addUnsetMetadataParams()

    try:
      input = ffmpeg.input(self.fileObject.absFileName)
      output = ffmpeg.output(input, self.tgtFileName, **ffmpegArgs)
      ffmpeg.run(output)
    except ffmpeg.Error as e:
      logger.error("Error converting %s ", self.tgtFileName)
      logger.error("deleting file %s ", self.tgtFileName)
      os.remove(self.tgtFileName)

  ##############################################################################################
  def addUnsetMetadataParams(self):
    ffmpegArgs = {}
    for k, v in self.metadata.items():
      if v[1] == True:
        match k:
          case "date":
            ffmpegArgs["metadata"] = "date=" + v[0]
          case "movie_name":
            ffmpegArgs["metadata"] = "title" + v[0]
    return ffmpegArgs
