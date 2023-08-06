#! /usr/bin/env python

from distutils.core import setup

setup(name="xdistutils",
      description="provide useful distutils commands",
      long_description=open("README.rst").read(),
      version="0.2.0",
      packages=["xdistutils"],
      maintainer="Ralf Schmitt",
      maintainer_email="ralf@systemexit.de",
      url="https://github.com/schmir/xdistutils")
