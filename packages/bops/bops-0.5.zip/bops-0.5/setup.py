import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "bops",
    version = "0.5",
    author = "Max Franks",
    author_email = "eliquious@gmail.com",
    description = ("A non-distributed numpy-based analysis module focusing on the manipulation, \
                    grouping and filtering of data from various sources. \
                    Bops also has map-reduce functionality."),
    license = "MIT",
    keywords = "mapreduce data analysis map-reduce",
    url = "http://packages.python.org/bops",
    packages=['bops', 'examples', 'doc'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
    ],
    requires=["numpy"],
)
