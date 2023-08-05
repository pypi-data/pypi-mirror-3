Elecraft K3/K2 Rig Control Python Utilities
Copyright (C) 2006-2011 Leigh L. Klotz, Jr <Leigh@WA5ZNU.org>
Licensed under Academic Free License 3.0 (See LICENSE)

* Setup
tar xzf rigcontrol-0.3.15.tar.gz 
cd rigcontrol
python setup.py install

* Configuration
Put this in ~/.rigcontrol/steppir.xml
    <?xml version="1.0"?>
    <steppir>

      <!-- number of elements -->
      <elements>3</elements>

      <port>
	<device>/dev/ttyS0</device>
	<baud>4800</baud>
      </port>

    </steppir>


Put this in ~/.rigcontrol/k3.xml
    <?xml version="1.0"?>
    <rig>

      <port>
	<baud>38400</baud>
	<device>/dev/k3</device>
      </port>

      <init>AI0;K22;</init>

    </rig>


Put this in ~/.rigcontrol/rotor.xml
    <?xml version="1.0"?>
    <rotor>

      <!-- Adjustable rotor offset:
	   added to SETBEARING, subtracted from BEARING 
      -->
      <offset>0</offset>

      <port>
	<!-- FTDI -->
	<device>/dev/rotor</device>
	<baud>4800</baud>
      </port>

      <reply>
	<symbol>bearing</symbol>
	<size>4</size>
	<string>;</string>
	<data>
	  <dtype>decimal</dtype>
	  <size>3</size>
	  <max>359</max>
	  <min>000</min>
	</data>
      </reply>

      <command>
	<symbol>init</symbol>
	<size>0</size>
    <!--
	<size>1</size>
	<string>v</string>
	<reply>VERSION</reply>
    -->
      </command>

      <command>
	<symbol>setbearing</symbol>
	<size>7</size>
	<string>AP1</string>
	<data>
	  <dtype>decimal</dtype>
	  <size>3</size>
	  <max>359</max>
	  <min>000</min>
	  <resol>1</resol>
	</data>
	<byte>0D</byte>
      </command>

      <command>
	<symbol>rotate</symbol>
	<size>4</size>
	<string>AM1</string>
	<byte>0D</byte>
      </command>

      <command>
	<symbol>bearing</symbol>
	<size>3</size>
	<string>AI1</string>
	<byte>0D</byte>
	<info>bearing</info>
      </command>

    </rotor>

* Use from python
  import k3lib
  k3 = k3lib.K3()
  print k3.qsyq()
  k3.qsy(14070.00)

For other methods, read the k3lib.py.

* Use From shell script
  qrg
  qsy 14070

For other scripts, read scripts/ 
