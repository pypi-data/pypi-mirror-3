#!/usr/bin/env python
# encoding: utf-8
from setuptools import setup
import os


BASE_PATH = os.path.dirname(__file__)

setup(
  name="alfredo",
  version="0.2",
  url="https://github.com/daltonmatos/alfredo",
  license="3-BSD",
  description="Alfredo is a gtalk bot born so serve you.",
  author="Dalton Barreto",
  author_email="daltonmatos@gmail.com",
  long_description=open(os.path.join(BASE_PATH, 'README.rst')).read(),
  packages=['alfredo', 'alfredo/commands'],
  scripts=[os.path.join(BASE_PATH, 'script/alfredo'), os.path.join(BASE_PATH, 'script/ud')],
  install_requires=['BeautifulSoup==3.2.1', 'plugnplay==0.5.0', 'requests==0.13.2', 'simplejson==2.6.0', 'xmpppy==0.5.0rc1', ],
  classifiers=[
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Application Frameworks"
    ])
