#!/usr/bin/env python

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = "0.1.0"

setup(name="django-failover",
      version=version,
      description="automatic failover for Django",
      long_description=open("README.rst").read(),
      classifiers=[
          "Development Status :: 4 - Beta",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules",],
      keywords="django failover",
      author="Brian Jay Stanley",
      url="https://github.com/brianjaystanley/django-failover",
      author_email="brian@brianjaystanley.com",
      license="MIT",
      packages=["failover", "failover.services"],
      install_requires=["django",],
)


