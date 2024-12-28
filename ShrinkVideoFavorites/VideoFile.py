#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re

# dnf install python3-ffmpeg-python.noarch
# docs: https://kkroening.github.io/ffmpeg-python/
import ffmpeg

# dnf install python3-pymediainfo.noarch
# https://pymediainfo.readthedocs.io/en/stable/
from pymediainfo import MediaInfo

# imports of own library using symbolic links in folder to lib files since reltive imports 
# I didn't get to work
from FileObject import FileObject

class VideoFile:
  fileObject = FileObject
  fallBackCameraModel = ""
  fallBackCameraManufacturer = ""
  tgtDirName = ""
  tgtFileName = ""
  metadata = {}  # {"KEY"},[ "string", Boolean ] Boolean True when metadata was empty and changed
  videoProps = {}
  vitalMetaDataKeys = ["date", "movie_name"]
  prgConfig = {}

  def __init__(self, fileObject, prgConfig, logger):
    self.logger = logger
    self.fileObject = fileObject
    self.prgConfig = prgConfig
    self.fallBackCameraManufacturer = prgConfig.get("camera_manufacturer_name")
    self.fallBackCameraModel = prgConfig.get("camera_model_name")
    self.tgtDirName = prgConfig.get("tgtDirName")
    self.tgtVideoType = prgConfig.get("tgtVideoType")
    self.tgtFileName = os.path.join(self.tgtDirName, self.fileObject.srcDirRelativeToRootDir,
                                    self.fileObject.fileNameWithoutExtension + "." + self.tgtVideoType)

  def __str__(self):
    output = "\n" + "VideoFile".ljust(25, ' ') + ": " + self.fileObject.absFileName + "\n"
    for k, v in self.metadata.items():
      output += str(k).ljust(25, ' ') + ": " + str(v[0]) + "\n"
    for k, v in self.videoProps.items():
      output += str(k).ljust(25, ' ') + ": " + str(v) + "\n"
    return output
  # f"""
  #   metadata["date"]   : {self.metadata["date"]}
  #   metadata["camera_manufacturer_name"] : {self.metadata["camera_manufacturer_name"]}
  #   metadata["camera_model_name"] : {self.metadata["camera_model_name"]}
  #   metadata["location"] = {self.metadata["location"]}
  #   metadata["movie_name"] = {self.metadata["movie_name"]}
  # """

  ##############################################################################################
  def ProbeVideoFile(self):
    # videoMetadata = ffmpeg.probe(self.fileObject.absFileName)
    # print(videoMetadata['streams'])
    media_info = MediaInfo.parse(self.fileObject.absFileName)
    for track in media_info.tracks:
      if track.track_type == "General":
        if track.date:
          self.metadata["date"] = [track.date, False]
        if track.camera_manufacturer_name:
          self.metadata["camera_manufacturer_name"] = [track.camera_manufacturer_name, False]
        if track.camera_model_name:
          self.metadata["camera_model_name"] = [track.camera_model_name, False]
        if track.location != 'nul' and track.location:
          self.metadata["location"] = [track.location, False]
        else:
          self.metadata["location"] = ["unknown", False]
        if track.movie_name:
          self.metadata["movie_name"] = [track.movie_name, False]
        elif track.title:
          self.metadata["movie_name"] = [track.title, False]
      elif track.track_type == "Video":
        if track.rotation:
          self.videoProps["rotation"] = track.rotation
        else:
          self.videoProps["rotation"] = 0
        self.videoProps["width"] = track.width   # Breite des Videos in Pixel
        self.videoProps["height"] = track.height  # Höhe des Videos in Pixel

  ##############################################################################################
  def FillMetadata(self):
    if not self.metadata.get("date"):
      self.logger.info("trying to compute date from filename %s ", os.path.join(
        self.fileObject.srcDirRelativeToRootDir, self.fileObject.fileBaseName))
      computedDate = self.computeDateFromFileName()
      if computedDate != "":
        self.metadata["date"] = [computedDate, True]
    if not self.metadata.get("movie_name"):
      self.logger.info("trying to compute movie_name from filename %s ", os.path.join(
        self.fileObject.srcDirRelativeToRootDir, self.fileObject.fileBaseName))
      computedMovieName = "TBD"
      self.metadata["movie_name"] = [computedMovieName, True]
    # if not self.metadata.get("camera_manufacturer_name"):
    #   self.logger.info("setting camera_manufacturer_name to %s", self.fallBackCameraManufacturer)
    #   # self.metadata["camera_manufacturer_name"] = [ self.fallBackCameraManufacturer, True ]
    # if not self.metadata.get("camera_model_name"):
    #   self.logger.info("setting camera_model_name to %s", self.fallBackCameraModel)
    #   # self.metadata["camera_model_name"] = [ self.fallBackCameraModel, True ]

  ##############################################################################################
  def computeDateFromFileName(self):
    # 2015/0807_Henry und Valentin springen im Freibad_1546.mp4
    dirName = self.fileObject.srcDirRelativeToRootDir
    fileName = self.fileObject.fileBaseName
    computedDate = ""
    x = re.search(r" *([0-9]{4})", dirName)
    if x:
      # 0807_Henry und Valentin springen im Freibad_1546.mp4
      year = x.group(1)

      y = re.findall(r"([0-9]{4})_.*_([0-9]{4})\..*", fileName)
      # [('0807', '1546')]
      resultTuple = y[0]
      # ('0807', '1546')
      monthDay = resultTuple[0] + "_" + resultTuple[1] + "00"
      computedDate = year + monthDay
    return computedDate

  ##############################################################################################
  def isMetadataUpdated(self):
    for v in self.metadata.values():
      if v[1] == True:
        return True
    return False

  ##############################################################################################
  def isEssentialMetadataUpdated(self):
    metadata_updated = False
    if self.metadata.get("date")[1] == True:
      metadata_updated = True
    if self.metadata.get("movie_name")[1] == True:
      metadata_updated = True
    return metadata_updated

  ##############################################################################################
  def isEssentialMetadataMissing(self):
    metadata_missing = False
    if self.metadata.get("date")[0] == "":
      metadata_missing = True
    if self.metadata.get("movie_name")[0] == "":
      metadata_missing = True
    return metadata_missing

  ##############################################################################################
  def printEssentialMetadata(self):
    for index, entry in enumerate(self.vitalMetaDataKeys):
      if index == 0:
        output = str(entry).ljust(14, ' ') + ": " + self.metadata.get(entry)[0] + "\n"
      elif index == len(self.vitalMetaDataKeys) - 1:
        output += str(entry).ljust(15, ' ') + ": " + self.metadata.get(entry)[0]
      else:
        output += str(entry).ljust(15, ' ') + ": " + self.metadata.get(entry)[0] + "\n"
    return output

  ##############################################################################################
  def targetFileExists(self):
    if os.path.exists(self.tgtFileName):
      self.logger.info("File %s already exists - skipping ", self.tgtFileName)
      return True
    else:
      return False

  ##############################################################################################
  def ConvertVideoFile(self):
    if self.targetFileExists():
      return
    if not os.path.exists(os.path.dirname(self.tgtFileName)):
      os.makedirs(os.path.dirname(self.tgtFileName))
    self.logger.info("Converting to %s", self.tgtFileName)
    ffmpegArgs = {}
    ffmpegArgs["loglevel"] = "panic"
    ffmpegArgs["c:v"] = "libsvtav1"
    ffmpegArgs["crf"] = 40
    ffmpegArgs["c:a"] = "libopus"
    ffmpegArgs["c:s"] = "copy"
    ffmpegArgs["map_metadata"] = 0
    # reduce size for 4k videos
    if float(self.videoProps.get("rotation")) > 0:
      if self.videoProps.get("height") > 1920:
        ffmpegArgs["vf"] = "scale=iw/2:ih/2"
    elif self.videoProps.get("width") > 1920:
      ffmpegArgs["vf"] = "scale=iw/2:ih/2"
    # add metadata which didn't exist in source file
    if self.isEssentialMetadataUpdated():
      ffmpegArgs |= self.addUnsetMetadataParams()

    try:
      input = ffmpeg.input(self.fileObject.absFileName)
      output = ffmpeg.output(input, self.tgtFileName, **ffmpegArgs)
      ffmpeg.run(output)
    except ffmpeg.Error as e:
      self.logger.error("Error converting %s ", self.tgtFileName)
      self.logger.error("deleting file %s ", self.tgtFileName)
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
