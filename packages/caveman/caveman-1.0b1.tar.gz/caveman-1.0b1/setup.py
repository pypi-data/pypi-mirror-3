#!/usr/bin/python
""" Setup.py for Caveman
    http://nedbatchelder.com/code/caveman

    Copyright 2011, Ned Batchelder.
"""

from distutils.core import setup

__version__ = "1.0b1"

classifiers = """
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python :: 2.7
"""

long_description = open("README.txt").read()

classifier_list = [c for c in classifiers.split("\n") if c]

if 'a' in __version__:
    devstat = "3 - Alpha"
elif 'b' in __version__:
    devstat = "4 - Beta"
else:
    devstat = "5 - Production/Stable"
classifier_list.append("Development Status :: " + devstat)

setup(
    name = 'caveman',
    version = __version__,
    url = 'http://nedbatchelder.com/code/caveman',
    author = 'Ned Batchelder',
    author_email = 'ned@nedbatchelder.com',
    description = long_description.splitlines()[0], 
    long_description = long_description,
    classifiers = classifier_list,
    license = 'MIT',

    install_requires = [
        'lxml',
        ],

    packages = [
        'caveman',
        ],

    scripts = [
        'scripts/check_manifest.py',
        ],
    )
