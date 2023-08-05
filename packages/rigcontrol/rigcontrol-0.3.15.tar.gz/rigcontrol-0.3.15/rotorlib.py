#!/usr/bin/python
# Rotor Control Python Utilities
# Copyright (C) 2006-2011 Leigh L. Klotz, Jr <Leigh@WA5ZNU.org>
# Licensed under Academic Free License 3.0 (See LICENSE)

import string, serial, time, sys, math, os
from lxml import etree

CONFIGFILE="~/.rigcontrol/rotor.xml"

class Rotor:
  def __init__(self):
    configfile = os.path.expanduser(CONFIGFILE)
    if not os.path.exists(configfile):
      raise "Please create %s" % (configfile)
    self.config = etree.parse(os.path.expanduser(configfile)).getroot()
    assert self.config.tag == "rotor"
    self.device=self.config.findtext("port/device")
    self.baudrate=int(self.config.findtext("port/baud"))
    if (self.config.findtext("offset")):
       self.offset=int(self.config.findtext("offset"))
    else:
       self.offset=0
    self.ser = serial.Serial(self.device,baudrate=self.baudrate,rtscts=0) #timeout=2
    self.ser.flushOutput()

  def close(self):
   self.ser.close()

  #
  # Set the rotor bearing and rotate
  # API1xxx;AM1;
  def rotate(self,deg):
    cmd=self.lookupCommand("setbearing")
    (argp, fmtstring) = self.symbolToFormatString(cmd)
    deg = deg + self.offset
    if (deg >= 360):
     deg = deg - 360
    if (deg < 0):
     deg = deg + 360
    self.writeCommand(argp, fmtstring, deg)
    cmd=self.lookupCommand("rotate")
    (argp, fmtstring) = self.symbolToFormatString(cmd)
    self.writeCommand(argp, fmtstring)

  def rotateq(self):
    cmd=self.lookupCommand("bearing")
    (argp, fmtstring) = self.symbolToFormatString(cmd)
    i = 0
    while i < 5:
      self.writeCommand(argp, fmtstring)
      resp = self.lookupReply("bearing")
      resultString = self.readCommand(resp)
      if resultString is not None: 
        try:
          result = int(resultString)
        except ValueError:
          return None
        result = result-self.offset
        if (result < 0):
         result = result + 360
        if (result >= 360):
         result = result - 360
        return result
      return None

  def writeCommand(self, argp, fmtstring, arg=""):
    if (argp):
     txt=fmtstring % arg
     self.ser.write(txt)
    else:
     txt=fmtstring
     self.ser.write(txt)

  def readCommand(self, resp):
   (argp, fmtstring) = self.symbolToFormatString(resp)
   dataformatsize = int(resp.xpath("size")[0].text)
   data = self.ser.read(dataformatsize)
   if data[0] > ';':
     data = data[1:] + self.ser.read(1)
   if data[0] == ';':
     return data[1:]
   else:
     return None

  def lookupCommand(self, xp):
    return self.config.xpath("command[symbol='"+xp+"']")[0]

  #crock
  def lookupReply(self, xp):
    return self.config.xpath("reply[symbol='"+xp+"']")[0]

  def symbolToFormatString(self, txt):
    fmtstring = ""
    argp=False
    for node in txt.xpath("*"):
      if (node.tag=='symbol'):
       pass
      elif (node.tag=='size'):
       pass
      elif (node.tag=='string'):
       fmtstring = fmtstring + node.text
      elif (node.tag=='byte'):
        fmtstring = fmtstring + chr(int(node.text, 16))
      elif (node.tag=='data'):
        argp=True
        dataformatsize = node.xpath("size")[0].text
        dataformat = node.xpath("dtype")[0].text
        if (dataformat == "decimal"):
          fmtstring = fmtstring +"%0"+dataformatsize+"d"
        else:
         raise "unknown data dtype " + dataformat
      elif (node.tag=='info'):
        pass
      else:
        raise "unknown command " + node.tag
    return (argp,fmtstring)


