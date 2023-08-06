#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = '0.0.2'

setup(name='tornado-redis',
      version=VERSION,
      description='Asynchronous Redis client which works within the Tornado Web Server IO loop.',
      author='Vlad Glushchuk',
      author_email='high.slopes@gmail.com',
      license='WTFPL',
      url='http://github.com/leporo/tornado-redis',
      keywords=['Redis', 'Tornado'],
      packages=['tornadoredis'],
     )
