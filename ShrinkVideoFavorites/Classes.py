#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from pprint import pprint
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
  metadata = {}
   
  def __init__(self, fileObject):
    self.fileObject = fileObject
    self.ProbeVideoFile()

  def __str__(self):
    output = "\n"+   "VideoFile".ljust(25, ' ') + ": " + self.fileObject.absFileName + "\n"
    for k, v in self.metadata.items():
      output += str(k).ljust(25, ' ') + ": " + str(v) + "\n"
    return output
  # f"""
  #   metadata["date"]   : {self.metadata["date"]}
  #   metadata["camera_manufacturer_name"] : {self.metadata["camera_manufacturer_name"]}
  #   metadata["camera_model_name"] : {self.metadata["camera_model_name"]}
  #   metadata["location"] = {self.metadata["location"]}
  #   metadata["movie_name"] = {self.metadata["movie_name"]}
  # """

  def ProbeVideoFile(self):
    # videoMetadata = ffmpeg.probe(self.fileObject.absFileName)
    # print(videoMetadata['streams'])
    media_info = MediaInfo.parse(self.fileObject.absFileName)
    for track in media_info.tracks:
      if track.track_type == "General":
        self.metadata["date"] = track.date
        self.metadata["camera_manufacturer_name"] = track.camera_manufacturer_name
        self.metadata["camera_model_name"] = track.camera_model_name
        self.metadata["location"] = track.location
        self.metadata["movie_name"] = track.movie_name
      # elif track.track_type == "Video":
      #   print("Bit rate: {t.bit_rate}, Frame rate: {t.frame_rate}, "
      #         "Format: {t.format}".format(t=track)
      #         )
      # elif track.track_type == "Audio":
      #   print("Track data:")
      #   pprint(track.to_data())
        
  def ConvertVideoFile(self):
    cmd = """
    ffmpeg -y \
            -loglevel panic \
            -f concat \
            -safe 0 \
            -noautorotate \
            -i ${LIST_FILE} \
            -metadata title=\"${OUTPUTNAME}\" \
            -metadata date=${ORIGTIMESTAMP} \
            -metadata creation_time=\"${ORIGTIMESTAMP_ISO8601}\" \
            -metadata location=\"${GPSCOORDINATES}\" \
            -metadata Make=\"${CAMERA_MANUFACTURER}\" \
            -metadata \"Camera Manufacturer Name\"=\"${CAMERA_MANUFACTURER}\" \
            -metadata \"Camera Model Name\"=\"${CAMERA_MODEL_NAME}\" \
            -codec copy -map 0 \
            -avoid_negative_ts 1 \
            -ignore_unknown \
            -movflags use_metadata_tags \
            \"${OUTPUTFILENAME}\" 
"""