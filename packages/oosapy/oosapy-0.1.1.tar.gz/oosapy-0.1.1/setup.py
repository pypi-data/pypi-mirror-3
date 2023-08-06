#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="oosapy",
      version="0.1.1",
      url="http://code.google.com/p/oosapy/",
      description="11870.com v2 API library for python",
      license="Apache License, Version 2.0",
      author="11870.com",
      author_email="api-11870@googlegroups.com",
      packages = find_packages(),
      keywords= "11870.com library",
      zip_safe = True,
      install_requires = ["gdata", "httplib2 >= 0.6"],
      classifiers=[
            "Development Status :: 4 - Beta",
            "Programming Language :: Python",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      )
