#!/usr/bin/env python

from setuptools import setup
import os
import sys

PACKAGE_PATH = 'src'

sys.path.insert(0, PACKAGE_PATH)
import processedimagefield

setup(
    name='django-processedimagefield',
    url='https://github.com/nathforge/django-processedimagefield',
    version=processedimagefield.version_string(),
    description='Post-processing for Django ImageFields.',
    
    author='Nathan Reynolds',
    author_email='email@nreynolds.co.uk',
    
    packages=['processedimagefield'],
    package_dir={'': PACKAGE_PATH},
    
    install_requires=['django-processedfilefield >= 0.2', 'PIL'],
)
