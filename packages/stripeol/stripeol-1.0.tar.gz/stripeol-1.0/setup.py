#!/usr/bin/env python

from stripeol import __version__, __author__

from setuptools import setup

long_description = open("README").read()

setup(
    name="stripeol",
    license="BSD License",
    version=__version__,
    description="Simple tool to strip whitespace from files",
    long_description=long_description,
    maintainer=__author__,
    author=__author__,
    author_email="trbs @ trbs",
    url="https://bitbucker.org/trbs/stripeol/",
    keywords="strip eol cleanup white space files",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: Unix",


    ],
    packages=['stripeol'],
    package_dir={'stripeol': 'stripeol'},
    entry_points={'console_scripts': ['stripeol = stripeol.cli:main']},
)
