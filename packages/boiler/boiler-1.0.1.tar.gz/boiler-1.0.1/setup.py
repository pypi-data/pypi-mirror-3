#!/usr/bin/env python

from distutils.core import setup

with open('README.rst') as file:
    long_description = file.read()

setup(name='boiler',
      version='1.0.1',
      description='A command line tool to quick manage boilerplate structures called **plates**, it is extensible',
      long_description=long_description,
      author='Niko Usai / mogui',
      author_email='usai.niko@gmail.com',
      url='http://mogui.it',
      scripts=['./boiler']
     )