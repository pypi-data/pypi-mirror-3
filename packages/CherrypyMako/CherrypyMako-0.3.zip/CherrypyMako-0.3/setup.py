# -*- coding: utf-8 -*-
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from CherrypyMako import __version__ as package_version


setup(
    name="CherrypyMako",
    version=package_version,
    author="Vahid Mardani",
    author_email="vahid.mardani@gmail.com",
    url="http://packages.python.org/cherrypymako",
    description="Mako tool for cherrypy",
    maintainer="Vahid Mardani",
    maintainer_email="vahid.mardani@gmail.com",
    packages=["CherrypyMako"],
    platforms=["any"],
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.txt')).read() ,
    install_requires=['mako>=0.5.0'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: Freeware",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
        ],
    )