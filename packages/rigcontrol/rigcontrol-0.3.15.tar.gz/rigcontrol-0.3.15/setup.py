#!/usr/bin/python

from setuptools import setup
import os

VERSION = '0.3.15'
LXML_VERSION = '2.2.4'

setup(name='rigcontrol',
      version=VERSION,
      install_requires = [ "lxml >= %s" % (LXML_VERSION) ],
      description="Python rig control utilities and libraries for amateur radio equipment",
      long_description = """	Python rig control utilities and libraries for amateur radio equipment
        This package control libraries and command-line programs for
        controlling the Elecraft K3, Idiom Press rotors, FluidMotion SteppIR, and other devices.
""",
      author="Leigh L. Klotz, Jr. WA5ZNU",
      url='http://wa5znu.org/2009/02/python-rigcontrol',
      author_email='leigh@wa5znu.org',
      py_modules=['k3lib', 'rotorlib', 'steppirlib'],
      package_data={'config': ['config/*.xml']},
      license='Academic Free License (AFL)',
      platforms = ['POSIX'],
      classifiers = [
		'Development Status :: 3 - Alpha',
		'Environment :: X11 Applications',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: Academic Free License (AFL)',
		'Natural Language :: English',
		'Operating System :: POSIX',
		'Programming Language :: Python',
		'Topic :: Communications :: Ham Radio',
	],
      scripts=[os.path.join("scripts", fn) for fn in os.listdir(os.path.join("scripts")) if not "RCS" in fn ])

