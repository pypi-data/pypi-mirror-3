#!/usr/bin/env python

from distutils.core import setup

setup(name='proxytcp',
      description='Listen for TCP connections on multiple ports, each of which forwards to another host:port.',
      version='0.3',
      author='Nathan Wilcox',
      author_email='nejucomo@gmail.com',
      license='GPLv3',
      url='https://bitbucket.org/nejucomo/proxytcp',
      scripts=['proxytcp.py'],
     )
