#!/usr/bin/env python
from distutils.core import setup

version = "0.1.2"

setup(name="stanislaw",
      version=version,
      description="A basic headless browser testing tool",
      author="Ted Dziuba",
      author_email="tjdziuba@gmail.com",
      url="https://github.com/teddziuba/stanislaw",
      download_url="https://github.com/teddziuba/stanislaw/tarball/v" + version,
      packages=["stanislaw"],
      install_requires = [
        "pyquery>=1.1.1",
        "lxml>=2.3",
        ]
      )
