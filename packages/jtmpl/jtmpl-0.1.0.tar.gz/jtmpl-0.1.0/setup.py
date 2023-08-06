#!/usr/bin/env python

from distutils.core import setup

import os

"""

jtmpl - commandline app for quickly running jsontemplate

there is no "canonical" installer;
* this method: uses cheeseshop, convenient for py people, but changes env
* configure / make / install: traditional unix, slightly funky methods
* untar / symlink: easy, requires unix know-how

THERE IS NO WINNING WITH INSTALLERS.

"""



def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (read('README.rst'))


setup(
    name='jtmpl',
    version='0.1.0',
    description='commandline app for quickly running jsontemplate',
    long_description=long_description,
    #packages=['jtmpl'],
    #py_modules=['jtmpl'],
    scripts=['jtmpl'],
    provides=['jtmpl'],
    requires=['jsontemplate'],
    license="BSD",
    author='Paul Oppenheim',
    author_email='poppy@pauloppenheim.com',
    url='http://www.pauloppenheim.com/projects/jtmpl/',
    keywords=['jtmpl', 'json', 'template', 'templating', 'jsontemplate'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Unix Shell",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Text Processing"
    ]
)
