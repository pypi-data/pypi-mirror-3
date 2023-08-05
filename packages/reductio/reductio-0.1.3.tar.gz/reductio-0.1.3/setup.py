import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "reductio",
    version = "0.1.3",
    author = "Rob Speer",
    author_email = "rspeer@mit.edu",
    description = ("Map/Reduce for Fabric"),
    license = "AGPLv3",
    keywords = "mapreduce distributed fabric",
    url = "http://github.com/rspeer/reductio",
    packages=['reductio'],
    install_requires=['fabric', 'paramiko', 'importlib'],
    long_description=read('README'),
)
