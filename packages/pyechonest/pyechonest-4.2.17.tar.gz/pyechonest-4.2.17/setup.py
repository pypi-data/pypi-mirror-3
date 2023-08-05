#!/usr/bin/env python
# encoding: utf-8

__version__ = "4.2.17"

# $Source$
from sys import version
import os
from setuptools import setup

if version < '2.6':
    requires=['urllib', 'urllib2', 'simplejson']
elif version >= '2.6':
    requires=['urllib', 'urllib2', 'json']
else:
    #unknown version?
    requires=['urllib', 'urllib2']

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pyechonest',
    version=__version__,
    description='Python interface to The Echo Nest APIs.',
    long_description="""Pyechonest is an open source Python library for the Echo Nest API.  With Pyechonest you have Python access to the entire set of API methods including:

  * artist - search for artists by name, description, or attribute, and get back detailed information about any artist including audio, similar artists, blogs, familiarity, hotttnesss, news, reviews, urls and video.
  * song - search songs by artist, title, description, or attribute (tempo, duration, etc) and get detailed information back about each song, such as hotttnesss, audio_summary, or tracks.
  * track - upload a track to the Echo Nest and receive summary information about the track including key, duration, mode, tempo, time signature along with detailed track info including timbre, pitch, rhythm and loudness information.""",
    author='Tyler Williams',
    author_email='tyler@echonest.com',
    maintainer='Tyler Williams',
    maintainer_email='tyler@echonest.com',
    url='https://github.com/echonest/pyechonest',
    download_url='https://github.com/echonest/pyechonest',
    package_dir={'pyechonest':'pyechonest'},
    packages=['pyechonest'],
    requires=requires
)
