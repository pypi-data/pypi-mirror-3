#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from distutils.core import setup

try:
	import argparse
	requires = []
except:
	requires=['argparse']

with open('README') as f:
	setup(name='fmorgue',
	      version='1.2',
	      description='Mirror files to a remote server, regardless of their name.',
	      author='Peter Tröger',
	      author_email='peter@troeger.eu',
	      url='https://bitbucket.org/troeger/fmorgue',
	      py_modules=['fmorgue'],
	      scripts=['scripts/fmorgue', 'scripts/fmorgue-server'],
#             data_files=[('/etc', ['cfg/fmorgue'])],
	      long_description=f.read(),
	      install_requires = requires,
	      classifiers=["Development Status :: 4 - Beta","Intended Audience :: System Administrators", "Topic :: System :: Archiving :: Mirroring"]
)
