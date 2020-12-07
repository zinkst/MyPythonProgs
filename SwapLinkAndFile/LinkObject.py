#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import string
import logging
import logging.config 
import os

    
class LinkObject:
 
  """
baseName = 20080514_123708_ZweiterHaltKurzVorAKHamburg.jpg
fileAbsLocation = /home/zinks/Stefan/myPrg/MyPythonPrgs/SwapLinkAndFile/testdata/test/2008/20080506_Schweden/20080514_123708_ZweiterHaltKurzVorAKHamburg.jpg
linkAbsLocation = /home/zinks/Stefan/myPrg/MyPythonPrgs/SwapLinkAndFile/testdata/test/2008/Favoriten/SchwedenLinksRel/20080514_123708_ZweiterHaltKurzVorAKHamburg.jpg
linkAbsLocationDir = /home/zinks/Stefan/myPrg/MyPythonPrgs/SwapLinkAndFile/testdata/test/2008/Favoriten/SchwedenLinksRel
linkAbsLocationSplit = Favoriten/SchwedenLinksRel
linkTarget = ../../20080506_Schweden/20080514_123708_ZweiterHaltKurzVorAKHamburg.jpg
linkSplit = 20080506_Schweden/20080514_123708_ZweiterHaltKurzVorAKHamburg.jpg
newLinkTarget = ../Favoriten/SchwedenLinksRel/20080514_123708_ZweiterHaltKurzVorAKHamburg.jpg
newLinkTargetDepth = 1
newLinkAbsoluteDir = /home/zinks/Stefan/myPrg/MyPythonPrgs/SwapLinkAndFile/testdata/test/2008/20080506_Schweden
  """
  linkAbsLocation     = u""
  linkAbsLocationDir  = u""
  linkAbsLocationSplit= u""
  linkTarget          = u""
  linkSplit   = u""
  newLinkTargetDepth = 0
  newLinkTarget   = u""
  newLinkAbsoluteDir = u""
  baseName    = u""
  fileAbsLocation = u""
  linkSeparator   = u'../'
   
  def printOut(self):
    output = "\r\nbaseName = " + self.baseName + \
             "\r\nfileAbsLocation = " + self.fileAbsLocation + \
             "\r\nlinkAbsLocation = " + self.linkAbsLocation + \
             "\r\nlinkAbsLocationDir = " + self.linkAbsLocationDir + \
             "\r\nlinkAbsLocationSplit = " + self.linkAbsLocationSplit + \
             "\r\nlinkTarget = " + self.linkTarget + \
             "\r\nlinkSplit = "+ self.linkSplit + \
             "\r\nnewLinkTarget = "+ self.newLinkTarget + \
             "\r\nnewLinkTargetDepth = "  + str(self.newLinkTargetDepth) + \
             "\r\nnewLinkAbsoluteDir = "+ self.newLinkAbsoluteDir

    return output
  
  def initialize(self,rootDir):
    if os.path.islink(self.linkAbsLocation):
      self.linkTarget = os.readlink(self.linkAbsLocation)
      self.linkAbsLocationDir = os.path.dirname(self.linkAbsLocation) 
      self.baseName = os.path.basename(self.linkAbsLocation) 
      self.linkAbsLocationSplit = self.linkAbsLocationDir[len(rootDir)+1:] 
      linkDepth=self.linkTarget.count(self.linkSeparator)
      self.linkSplit=self.linkTarget[linkDepth*3:]
      self.fileAbsLocation = os.path.join(rootDir,self.linkSplit)
      newLinkTargetAbsName = self.fileAbsLocation[len(rootDir)+1:] 
      self.newLinkTargetDepth = newLinkTargetAbsName.count('/')
      self.newLinkTarget = os.path.join("../"*self.newLinkTargetDepth + self.linkAbsLocationSplit,self.baseName)  
      self.newLinkAbsoluteDir = os.path.join(rootDir,os.path.dirname(self.linkSplit))
################################################################################################      
#end class      
