#!/usr/bin/python
# Elecraft K2/K3 Rig Control Python Utilities
# Copyright (C) 2006-2011 Leigh L. Klotz, Jr <Leigh@WA5ZNU.org>
# Licensed under Academic Free License 3.0 (See LICENSE)

import string, serial, time, os
from lxml import etree

CONFIGFILE = "~/.rigcontrol/k3.xml"

class K3:
  def __init__(self):
    configfile = os.path.expanduser(CONFIGFILE)
    if not os.path.exists(configfile):
      raise "Please create %s" % (configfile)
    config = etree.parse(configfile).getroot()
    assert config.tag == "rig"
    device=config.findtext("port/device")
    baudrate=config.findtext("port/baud")
    init=config.findtext("init")
    self.ser = serial.Serial(device,baudrate=baudrate)
    self.write(init)
    self.ser.flushInput()
    self.ser.flushOutput()

  def close(self):
    self.ser.flushInput()		# until the "quit" comes along.
    self.ser.close()

  def write(self,str):
    self.ser.write(str)

  def read(self,n):
    return self.ser.read(n)

  #
  # Set the VFO current frequency
  # FA00014060000
  # FA00007030000
  def qsy(self, freq):
    if (freq < 10e6):
      cmd = "FA0000%d;" % (freq) # in 7 digits
    else:
      cmd = "FA000%d;" % (freq) # in 8 digits
    self.write(cmd)
    return (self.qsyq())

  #
  # Set the 2ND RX VFO current frequency
  # FB00014060000
  # FB00007030000
  def qsy2(self, freq):
    if (freq < 10e6):
      cmd = "FB0000%d;" % (freq) # in 7 digits
    else:
      cmd = "FB000%d;" % (freq) # in 8 digits
    self.write(cmd)
    return (self.qsyq())

  #
  # Get the VFO current frequency
  # FA00014060000
  # FA00007030000
  def qsyq(self):
    self.write("FA;")
    result = self.read(14)
    if (len(result) <> 14):
      return 0
    return float(result[2:10] + "." + result[10:13])

  #
  # Get the 2ND RX VFO current frequency
  # FA00014060000
  # FA00007030000
  def qsyq2(self):
    self.write("FB;")
    result = self.read(14)
    if (len(result) <> 14):
      return 0
    return float(result[2:10] + "." + result[10:13])

  #
  # Get the First IF current frequency
  # FI;
  # FI6500;
  def fiq(self):
    self.write("FI;")
    result = self.read(7)
    if (len(result) <> 7):
      return 0
    return float("821" + result[2:3] + "." + result[3:6])

  #
  # Set NB to level (off=0, 1, 2)
  # TODO: use SW22; to change thresh but we have to ready it first
  def nb(self, level, thresh):
    self.write("NB%s;" % (level))

  #
  # Get the NB setting
  # NB
  # NB00; Off, hi thresh
  # NB21; NB2, low thres
  def nbq(self):
    self.write("NB;")
    result = self.read(5);
    if (len(result) <> 5):
      return 0
    level = result[2]
    thresh = result[3]
    return "NB: %c %c" % (level, thresh)


  #
  # Set the Mode
  # MD1; LSB
  # FA00007030000
  def mode(self,str):
    if (str == "lsb" or str == "l"):
      modenum = 1
    if (str == "usb" or str=="u"):
      modenum = 2
    if (str == "cw" or str=="c"):
      modenum = 3
    if (str == "cwr"):
      modenum = 5
    if (str == "rtty" or str == "r"):
      modenum = 6
    if (str == "rttyr"):
      modenum = 9
    cmd = "MD%d;" % (modenum)
    self.write(cmd)
    return self.modeq()

  #
  # Get the mode
  def modeq(self):
    self.write("K22;MD;");
    result = self.read(4);
    if (len(result) <> 4):
      return "???: "+result
    modenum = string.atoi(result[2])
    if (modenum == 1):
      return "lsb"
    if (modenum == 2):
      return "usb"
    if (modenum == 3):
      return "cw"
    if (modenum == 5):
      return "cwr"
    if (modenum == 6):
      return "rtty"
    if (modenum == 9):
      return "rttyr"
    return "???"

  #
  # Set the preamp
  # PA0; off
  # PA1; on
  def pa(self,str):
    if (str == "off"):
      modenum = 0
    if (str == "on"):
      modenum = 1
    cmd = "PA%d;" % (modenum)
    self.write(cmd)
    return self.paq()

  #
  # Get the preamp
  def paq(self):
    self.write("PA;");
    result = self.read(4);
    if (len(result) <> 4):
      return 0
    if result == "PA1;":
        return "on"
    else:
        return "off"

  #
  # Set the power output
  # PC000; off
  # PC010; 10 watts
  def power(self,watts):
    cmd = "PC%03d;" % (watts)
    self.write(cmd)
    return self.powerq()

  #
  # Get the power output
  def powerq(self):
    self.write("PC;");
    result = self.read(6);
    if (len(result) <> 6):
      return 0
    return int(result[2:5])

  #
  # Set to VFO A for TX and RX
  def vfoa(self):
    self.write("FT0;FR0;")
    return self.vfoq()

  #
  # Get the B for TX and RX
  def vfob(self):
    self.write("FT1;FR1;")
    return self.vfoq()

  #
  # Get the VFO current frequency
  # FA00014060000
  # FA00007030000
  def vfoq(self):
    self.write("FT;FR;")
    result = self.read(8);
    if (len(result) <> 8):
      return 0
    return "TX: %c; RX: %c" % (65+string.atoi(result[2]), 65+string.atoi(result[6]))

  #
  # Send CW
  # KY text;
  def sendcw(self,str):
    cmd = "KY %s;" % (str)
    self.write(cmd)

  # TODO
  # Set speed 15=K015;
  def cwspeedq(self):
    cmd = "K0;"
    self.write(cmd)
    result = self.read(2);
    if (len(result) <> 5):
      return 0
    return result[1:3]

  # TODO
  def cwspeed(self, speed):
    cmd = "K%3d;"
    self.write(cmd)
    return self.cwspeedq()

  #
  # Set ATT to off=0|on=1
  def ra(self,offon):
    if offon == 'off':
        offon = 0
    elif offon == 'on':
        offon = 1
    self.write("RA0%s;" % offon)
    return self.raq()

  #
  # Get the ATT setting
  # RA;
  # RA00; off
  # RA01; on
  def raq(self):
    self.write("RA;")
    result = self.read(5);
    if (len(result) <> 5):
      return 0
    offon = result[3]
    return "RA: %s" % (["off","on"][ord(offon)-ord('0')])

  #
  # Set the filter
  # 1, 2, 3, 4
  # FW00001;
  # 0 means "next"
  def filter(self,n):
    cmd = "FW0000%d;" % (n)
    self.write(cmd)

  #
  # Get the filter number
  def filtern(self):
    self.write("FW;");
    result = self.read(9);
    if (len(result) <> 9):
      return 0
    return string.atoi(result[6])

  #
  # Get the filter info
  def filterq(self):
    self.write("FW;");
    result = self.read(9);
    if (len(result) <> 9):
      return 0
    return result[2:6] + "Hz " + result[7]

  #
  # Get the display
  def displayq(self):
    self.write("DS;");
    result = self.read(13);
    if (len(result) <> 13):
      return 0
    return result

  #
  # Get the versions
  # RVM;
  # RVD;
  # RVA;
  # RVV;
  # RVF;
  # -> RV*nn.nn;
  def verq(self,x):
    self.write("RV%c;" % (x))
    result = self.read(9);
    if (len(result) <> 9):
      return 0
    ver = result[3:8]
    if ver == '99.99':
      ver = None
    return ver

  def showtext(self,text):
    for letter in text:
      self.write("DB%s;" % (letter));

  def timeq(self):
    def k3LcdChar(c):
      if ord(c) > 127: 
        return ":"+chr(ord(c)&127)
      else:
        return c
    self.write("K31;MN073;")          # todo: save/restore
    time.sleep(0.05)
    self.write("DS;")
    # DSttttttttaf;
    result = self.read(13);
    self.write("MN255;")        # exit menu
    if (len(result) <> 13):
      return None
    # TEXT and decimal point data: 
    # This field contains 8 bytes, with values 0x30 - 0xFF (hex). 
    # The first byte is the left-most displayed character. 
    # Bit 7 (MSB) of each byte indicates whether the decimal point 
    # to the left of each character is on (1) or off (0)1. 
    # The other bits contain an ASCII character that corresponds
    # to the displayed character.
    # first two chars in time are @@
    return "".join([ k3LcdChar(c) for c in result[4:10] ])

  def fixtime(self):
    def k3LcdChar(c):
      return chr(ord(c)&127)
    self.write("K31;MN073;")          # todo: save/restore
    time.sleep(0.05)
    self.write("DS;")
    time.sleep(0.05)
    # DSttttttttaf;
    result = self.read(13);
    if (len(result) <> 13):
      self.write("MN255;")        # exit menu
      return None
    # TEXT and decimal point data: 
    # This field contains 8 bytes, with values 0x30 - 0xFF (hex). 
    # The first byte is the left-most displayed character. 
    # Bit 7 (MSB) of each byte indicates whether the decimal point 
    # to the left of each character is on (1) or off (0)1. 
    # The other bits contain an ASCII character that corresponds
    # to the displayed character.
    # first two chars in time are @@
    k3hour = int("".join([ k3LcdChar(c) for c in result[4:6] ]))
    k3minute = int("".join([ k3LcdChar(c) for c in result[6:8] ]))
    k3second = int("".join([ k3LcdChar(c) for c in result[8:10] ]))

    (year, month, day, hour, minute, second, x, y, z) = time.gmtime()
    self.write("SWT13;")
    time.sleep(0.05)
    while k3second < second:
      self.write("UP;")
      k3second = k3second + 1
    while k3second > second:
      self.write("DN;")
      k3second = k3second - 1
    self.write("SWT12;")
    time.sleep(0.05)
    while k3minute < minute:
      self.write("UP;")
      k3minute = k3minute + 1
    while k3minute > minute:
      self.write("DN;")
      k3minute = k3minute - 1
    self.write("SWT11;")
    time.sleep(0.05)
    while k3hour < hour:
      self.write("UP;")
      k3hour = k3hour + 1
    while k3hour > hour:
      self.write("DN;")
      k3hour = k3hour - 1
    self.write("MN255;")        # exit menu
    return self.timeq()
