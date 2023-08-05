from setuptools import setup
import sys, os

METADATA = dict(
  name = 'heywatch',
  version = '1.0.1',
  py_modules = ['heywatch.api'],
  author='Bruno Celeste',
  author_email='bruno@particle-s.com',
  description='A python wrapper around the HeyWatch API',
  license='MIT License',
  url='http://heywatch.com',
  keywords='heywatch api',
	long_description="""Client Library for encoding Videos with HeyWatch

HeyWatch is a Video Encoding Web Service.

For a CLI, look at the ruby version: http://github.com/particles/heywatch-ruby

For more information:

* HeyWatch: http://heywatch.com
* API Documentation: http://dev.heywatch.com
* Twitter: @particles / @sadikzzz

Changelogs

1.0.1
Return True instead of '' in update and delete methods

"""
)

def Main():
  # Use setuptools if available, otherwise fallback and use distutils
  try:
    import setuptools
    setuptools.setup(**METADATA)
  except ImportError:
    import distutils.core
    distutils.core.setup(**METADATA)

if __name__ == '__main__':
  Main()