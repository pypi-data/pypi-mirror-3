#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages
from boxdotcom import __version__

setup(name="boxdotcom",
      version=__version__,
      description="Python wrapper for Box.com/.net API",
      long_description="""You can use the Box API to create applications and websites that integrate with Box.com/.net and can perform the following functions:
* Store and retrieve files from Box
* Organize files into folders
* Move, rename and delete files
* Share files""",
      license="Apache License",
      author="Sean Rose",
      author_email="sean.andrew.rose@gmail.com",
      url="http://github.com/dvska/python-boxdotcom",
      packages=find_packages(),
      install_requires=[],
      keywords= ["python", "box", "box.net", "box.com", "api", "wrapper"],
      classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development",
        ],      
      )
