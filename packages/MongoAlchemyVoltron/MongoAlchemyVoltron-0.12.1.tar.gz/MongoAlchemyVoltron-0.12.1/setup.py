#!/usr/bin/env python
import os
from distutils.core import setup

def read(fname):
    """ Utility function for loading the long description. """
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
        return ''

VERSION = '0.12.1'
DESCRIPTION = 'Document-Object Mapper/Toolkit for MongoDB - Voltron Fork'
LONG_DESCRIPTION = read('README.rst')

setup(
    name='MongoAlchemyVoltron',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Jake Alheid',
    license='MIT',
    author_email='jake@about.me',
    url='https://github.com/shakefu/MongoAlchemy',
    packages=['mongoalchemy'],
    install_requires=['pymongo'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
