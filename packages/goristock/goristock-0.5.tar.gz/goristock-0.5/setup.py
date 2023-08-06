#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_description = open('./README.rest', 'r').read()

setup(name='goristock',
      version='0.5',
      description='台灣股市分析機器人',
      long_description=long_description,
      author='Toomore Chiang',
      author_email='toomore0929@gmail.com',
      url='https://github.com/toomore/goristock',
      packages=find_packages(),
      include_package_data=True,
      license='MIT',
      install_requires=['python-memcached'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Financial and Insurance Industry',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: Chinese (Traditional)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Topic :: Office/Business :: Financial :: Investment',
          ],
     )
