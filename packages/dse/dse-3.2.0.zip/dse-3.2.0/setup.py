#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='dse',
      version='3.2.0',
      description='DSE - Simplified "bulk" insert/update/delete for Django.',
      author='Thomas Weholt',
      author_email='thomas@weholt.org',
      long_description=open('README.txt').read(),
      packages = ['dse'],
      install_requires = ['django'],
      url = "https://bitbucket.org/weholt/dse2",
      classifiers=[
          #'Development Status :: 4 - Beta',
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Framework :: Django',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Database',
          ],
      )
