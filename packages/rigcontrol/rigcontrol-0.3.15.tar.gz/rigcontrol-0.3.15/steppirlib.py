#!/usr/bin/python
# Rig Control Python Utilities
# Copyright (C) 2006-2011 Leigh L. Klotz, Jr <Leigh@WA5ZNU.org>
# Licensed under Academic Free License 3.0 (See LICENSE)

import string
import serial
import sys
import os
from lxml import etree
from time import sleep

# plug RS232 cable into lower connector with null modem and setp for SteppIR protocol, 4800 baud
CONFIGFILE="~/.rigcontrol/steppir.xml"

class Bits:
  DVR_MASK=1<<2
  REFL_MASK=1<<4
  DIR1_MASK=1<<3
  DIR2_MASK=1<<5
  S1=0x40
  S2=0x41
  S3=0x00
  S7_AC=0x00                      # Motor flags AC=0
  S8_DIR_NORM=0                   # 8=dir
  S8_DIR_REV=0x40
  S8_DIR_BIDI=0x80
  S8_DIR_THREE_QUARTER_VERTICAL=0x20
  S8_DIR_ALL = (S8_DIR_NORM | S8_DIR_REV | S8_DIR_BIDI | S8_DIR_THREE_QUARTER_VERTICAL)
  S9_CMD_SET_FREQ_AND_DIR='1'
  # SET FREQ BYTES to 0=0=0 first
  S9_CMD_REENABLE_FREQ_UPDATE='R'
  # SET FREQ BYTES to 0=0=0 first
  S9_CMD_HOME='S'
  S9_CMD_DISABLE_FREQUENCY_UPDATE='U'
  S9_CMD_CALIBRATE='V'
  S10_VERSION='0'
  S11=0x0D

class Steppir:
  def __init__(self):
      configfile = os.path.expanduser(CONFIGFILE)
      if not os.path.exists(configfile):
        raise "Please create %s" % (configfile)
      self.config = etree.parse(os.path.expanduser(configfile)).getroot()
      assert self.config.tag == "steppir"
      self.device=self.config.findtext("port/device")
      self.baudrate=int(self.config.findtext("port/baud"))
      self.elts = int(self.config.findtext("elements"))
      self.serio = None

  def open(self):
    self.serio = serial.Serial(self.device, self.baudrate)
    self.serio.open()
    self.serio.setDTR(level=True)
    self.serio.setRTS(level=True)

  def close(self):
    if self.serio != None:
      self.serio.close()

  def setfreqdir(self, freq, dir_bits):
    self.output(Bits.S1)                      # 1
    self.output(Bits.S2)                      # 2
    self.output(Bits.S3)                      # 3
    Fh = freq / (256 * 256)
    Fm = ((freq % (256 * 256)) / 256) & 0xff
    Fl = (freq % 256) & 0xff
    self.output(Fh)                           # 4
    self.output(Fm)                           # 5
    self.output(Fl)                           # 6
    self.output(Bits.S7_AC)                   # 7
    self.output(dir_bits)                     # 8
    self.output(Bits.S9_CMD_SET_FREQ_AND_DIR) # 9
    self.output(Bits.S10_VERSION)             # 10
    self.output(Bits.S11)                     # 11
    sleep(0.5)

  def home(self):
    self.output(Bits.S1)              # 1
    self.output(Bits.S2)              # 2
    self.output(Bits.S3)              # 3
    Fh = 0
    Fm = 0
    Fl = 0
    self.output(Fh)                   # 4
    self.output(Fm)                   # 5
    self.output(Fl)                   # 6
    self.output(Bits.S7_AC)           # 7
    self.output(0)                    # 8
    self.output(Bits.S9_CMD_HOME)     # 9
    self.output(Bits.S10_VERSION)     # 10
    self.output(Bits.S11)             # 11

  def output(self, c):
      self.serio.write("%c" % (c))
      self.serio.flush()

  def input(self):
      c = self.serio.read(1)
      c = ord(c)
      return c

  def status(self):
    self.output('?')
    self.output('A')
    self.output(0x0d)

  def readin(self):
    c=self.input()                    # 1
    c=self.input()                    # 2
    c=self.input()                    # 3
    c=self.input()                    # 4
    frequency = c * 256 * 256
    c=self.input()                    # 5
    frequency += c * 256
    c=self.input()                    # 6
    frequency += c
    frequency = frequency/100
    c=self.input()                    # 7
    ac_bits = c
    c=self.input()                    # 8
    current_dir_bits = (c & Bits.S8_DIR_ALL)
    c=self.input()                    # 9
    c=self.input()                    # 10
    c=self.input()                    # 11
    dir = self.formatDir(current_dir_bits)
    return (frequency, dir, self.formatElts(ac_bits))

  def formatElts(self, ac_bits):
    if self.elts == 4:
      return ("(%c-%c-%c-%c)" % (self.formatElt(ac_bits, Bits.DIR2_MASK), self.formatElt(ac_bits, Bits.DIR1_MASK), self.formatElt(ac_bits, Bits.DVR_MASK), self.formatElt(ac_bits, Bits.REFL_MASK)))
    elif self.elts == 3:
      return("(%c-%c-%c)" % (self.formatElt(ac_bits, Bits.DIR1_MASK), self.formatElt(ac_bits, Bits.DVR_MASK), self.formatElt(ac_bits, Bits.REFL_MASK)))
    elif self.elts == 2:
      return("(%c-%c)" % (self.formatElt(ac_bits, Bits.REFL_MASK), self.formatElt(ac_bits, Bits.DVR_MASK)))
    elif self.elts == 1:
      return("(%c)" % (self.formatElt(ac_bits, Bits.DVR_MASK)))

  def formatElt(self, bits, mask):
      if bits & mask == 0:
          return '|'
      else:
          return '+'

  def formatDir(self, bits):
    if bits == Bits.S8_DIR_NORM:
      return'N'
    elif bits == Bits.S8_DIR_REV:
      return'R'
    elif bits == Bits.S8_DIR_BIDI:
      return'B'
    elif bits == Bits.S8_DIR_THREE_QUARTER_VERTICAL:
      return 'V'
    else:
      return None

  def parseFrequency(self, s, frequency):
    if s=="home": return None
    elif s==".": return frequency
    else: return 100 * int(s)

  def parseDir(self, s, dir):
    s = string.upper(s)
    if (s == '.'): return dir
    elif (s == 'N'): return Bits.S8_DIR_NORM
    elif (s == 'R'): return Bits.S8_DIR_REV
    elif (s == 'B'): return Bits.S8_DIR_BIDI
    elif (s == 'V'): return Bits.S8_DIR_THREE_QUARTER_VERTICAL
    else: return s
