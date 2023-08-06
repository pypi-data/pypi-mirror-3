#!/usr/bin/env python

"""colorbrewer: constants from Cynthia Brewer's ColorBrewer

An easy way to get access to ColorBrewer schemes from within a Python program
"""

__version__ = "0.1.1"

# Copyright 2009, 2012 Michael M. Hoffman <mmh1@washington.edu>

from ez_setup import use_setuptools
use_setuptools()

from setuptools import find_packages, setup

doclines = __doc__.splitlines()
name, short_description = doclines[0].split(": ")
long_description = "\n".join(doclines[2:])

url = "http://noble.gs.washington.edu/~mmh1/software/%s/" % name.lower()
download_url = "%s%s-%s.tar.gz" % (url, name, __version__)

classifiers = ["Natural Language :: English",
               "Programming Language :: Python"]

if __name__ == "__main__":
    setup(name=name,
          version=__version__,
          description=short_description,
          author="Michael Hoffman",
          author_email="mmh1@uw.edu",
          url=url,
          download_url=download_url,
          classifiers=classifiers,
          long_description=long_description,
          zip_safe=True,
          packages=find_packages("."),
          include_package_data=True
          )
