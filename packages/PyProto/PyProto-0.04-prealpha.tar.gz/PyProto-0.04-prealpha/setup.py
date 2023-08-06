#!/usr/bin/env python3

from setuptools import setup, find_packages
from os import listdir
from os.path import isdir, join

PKGNAME='PyProto'

setup(name=PKGNAME,
      description='High-level protocol abstraction for Python',
      long_description="""A high-level protocol abstraction library for Python.

Created out of frustration with twisted, this is an event-based library that
attempts to choose the most efficient eventloop system on your platform.

Initial protocols will include HTTP and IRC; more to come.
""",
      author='Elizabeth Myers',
      author_email='elizabeth@sporksmoo.net',
      url='http://github.com/Elizacat/PyProto',
      license='BSD',
      version='0.04-prealpha',
      keywords=['eventloop', 'protocol', 'epoll', 'poll', 'select'],
      packages=find_packages(),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: Microsoft',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Internet',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ]
)
