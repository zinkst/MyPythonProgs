#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging

# dnf install python3-ffmpeg-python.noarch
# docs: https://kkroening.github.io/ffmpeg-python/
import ffmpeg

# dnf install python3-pymediainfo.noarch
# https://pymediainfo.readthedocs.io/en/stable/
from pymediainfo import MediaInfo


class FileObject:
  absFileName = ""              # e.g  : /srcfiles/Videos/2024/202400_Sonstige/20020309_Video.mkv
  dirName = ""                  # e.g. : /srcfiles/Videos/2024/202400_Sonstige/
  fileBaseName = ""             # e.g. : 20020309_Video.mkv
  extension = ""                # e.g. : mkv
  srcRootDir = ""               # e.g. : /srcfiles/Videos
  srcDirRelativeToRootDir = ""  # e.g. : Videos/2024/202400_Sonstige/

  def __init__(self, absFileName, srcRootDir):
    self.absFileName = absFileName
    self.dirName = os.path.dirname(self.absFileName)
    self.fileBaseName = os.path.basename(self.absFileName)
    self.extension = os.path.splitext(self.fileBaseName)[1][1:]
    self.srcRootDir = srcRootDir
    self.srcDirRelativeToRootDir = self.dirName[len(self.srcRootDir) + 1:]

  def __str__(self):
    return f""" 
  {"fileBaseName".ljust(25,' ')} : {self.fileBaseName}
  {"dirName".ljust(25,' ')} : {self.dirName}
  {"fileBaseName".ljust(25,' ')} : {self.fileBaseName}
  {"extension".ljust(25,' ')} : {self.extension}
  {"srcRootDir".ljust(25,' ')} : {self.srcRootDir}
  {"srcDirRelativeToRootDir".ljust(25,' ')} : {self.srcDirRelativeToRootDir}
  """


class VideoFile:
  fileObject = FileObject
  fallBackCameraModel = ""
  fallBackCameraManufacturer = ""
  metadata = {} # {"KEY"},[ "string", Boolean ] Boolean True when metadata was empty and changed
  videoProps = {}
  vitalMetaDataKeys = [ "date", "movie_name" ]

  def __init__(self, fileObject, CameraModel, CameraManufacturer):
    self.fileObject = fileObject
    self.fallBackCameraManufacturer = CameraManufacturer
    self.fallBackCameraModel = CameraModel
    self.ProbeVideoFile()
    self.FillMetadata()

  def __str__(self):
    output = "\n"+   "VideoFile".ljust(25, ' ') + ": " + self.fileObject.absFileName + "\n"
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
        self.metadata["date"] = [ track.date, False ]
        if track.camera_manufacturer_name != None:
          self.metadata["camera_manufacturer_name"] = [ track.camera_manufacturer_name,  False ]
        if track.camera_model_name != None:
          self.metadata["camera_model_name"] = [ track.camera_model_name,  False ]
        if track.location != 'nul' and track.location != None:
          self.metadata["location"] = [ track.location, False ]
        else:
          self.metadata["location"] = [ "unknown", False ]
        if track.movie_name != None:
          self.metadata["movie_name"] = [ track.movie_name, False ]
        elif track.title != None:
          self.metadata["movie_name"] = [ track.title, False ]  
      elif track.track_type == "Video":
        self.videoProps["width"] = track.width   # Breite des Videos in Pixel
        self.videoProps["height"] = track.height # Höhe des Videos in Pixel
      # elif track.track_type == "Audio":
      #   print("Track data:")
      #   pprint(track.to_data())
        
  ##############################################################################################
  def FillMetadata(self):
    if not self.metadata.get("date"):
       logging.info("trying to compute date from filename %s ", os.path.join(self.fileObject.srcDirRelativeToRootDir, self.fileObject.fileBaseName))
       computedDate = "TBD"
       self.metadata["date"] = [ computedDate, True ]
    if not self.metadata.get("movie_name"):
      logging.info("trying to compute movie_name from filename %s ", os.path.join(self.fileObject.srcDirRelativeToRootDir, self.fileObject.fileBaseName))
      computedMovieName = "TBD"
      self.metadata["movie_name"] = [ computedMovieName, True ]
    if not self.metadata.get("camera_manufacturer_name"):
      logging.info("setting camera_manufacturer_name to %s", self.fallBackCameraManufacturer)
      # self.metadata["camera_manufacturer_name"] = [ self.fallBackCameraManufacturer, True ]
    if not self.metadata.get("camera_model_name"):
      logging.info("setting camera_model_name to %s", self.fallBackCameraModel)
      # self.metadata["camera_model_name"] = [ self.fallBackCameraModel, True ]
  
  ##############################################################################################
  def isMetadataUpdated(self):
    for v in self.metadata.values:
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
  def printEssentialMetadata(self):
    for index, entry in enumerate(self.vitalMetaDataKeys):
      if index == 0:
        output = str(entry).ljust(14, ' ') + ": " + self.metadata.get(entry)[0] + "\n"
      elif index == len(self.vitalMetaDataKeys) -1:
        output += str(entry).ljust(15, ' ') + ": " + self.metadata.get(entry)[0]  
      else:
        output += str(entry).ljust(15, ' ') + ": " + self.metadata.get(entry)[0] + "\n"  
    return output
        
  ##############################################################################################
  def ConvertVideoFile(self):
    cmd = """
      ffmpeg -y \
      -loglevel error \
      -i \"${SRC_FILENAME}\" \
      -metadata title=\"${OUTPUTNAME}\" \
      -metadata date=${ORIGTIMESTAMP} \
      -metadata creation_time=\"${ORIGTIMESTAMP_ISO8601}\" \
      -metadata location=\"${GPSCOORDINATES}\" \
      -metadata Make=\"${CAMERA_MANUFACTURER}\" \
      -metadata \"Camera Manufacturer Name\"=\"${CAMERA_MANUFACTURER}\" \
      -metadata \"Camera Model Name\"=\"${CAMERA_MODEL_NAME}\" \
      -c:v libsvtav1 -crf 50 \
      -c:a libopus \
      -c:s copy \
      -map_metadata 0 \
      -vf scale=1920:-1 \
      \"${TGT_FILENAME}\""
"""
  # output AV1 see https://filmora.wondershare.de/more-tips/av1-vs-vp9.html
  # https://trac.ffmpeg.org/wiki/Encode/AV1
  # https://apps.theodo.com/article/optimizing-video-assets-to-drastically-reduce-app-size