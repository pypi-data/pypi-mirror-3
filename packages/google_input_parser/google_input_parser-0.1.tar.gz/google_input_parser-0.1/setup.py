import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "google_input_parser",
    version = "0.1",
    author = "Adam Matan",
    author_email = "adam@matan.name",
    description = ("A quick-and-dirty input parser for Google Code Jams."),
    license = "GPLv3",
    keywords = "google code jam parser",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['google_input_parser',],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)