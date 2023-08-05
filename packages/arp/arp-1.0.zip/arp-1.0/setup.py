""" Setup script for ARP / RARP module arp.py"""

from distutils.core import setup

setup(name = 'arp',
      version='1.0',
      py_modules = ['arp'],
      scripts = [],
      author = 'Andreas Urbanski',
      author_email = 'urbanski.andreas@gmail.com',
      description = 'Raw packets, ARP /RARP queries and replies and MAC resolution',
      keywords = 'arp rarp raw packet ethernet frame mac ip',
      license = 'GPLv3',
      platforms = 'Windows'
      )

