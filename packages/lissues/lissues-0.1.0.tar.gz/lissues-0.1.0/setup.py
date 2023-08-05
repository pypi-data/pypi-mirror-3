#!/usr/bin/env python
import sys
from setuptools import setup

setup(
        name='lissues',
        version='0.1.0',
        description='A simple client to redmine issues tracker',
        author='Hugo Ruscitti',
        author_email='hugoruscitti@gmail.com',
        install_requires=['setuptools', 'pyactiveresource'],
        packages=['lissues'],
        url='http://www.gcoop.coop',
        scripts=['bin/li'],
        classifiers = [
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Natural Language :: Spanish',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries',
          ],
    )
