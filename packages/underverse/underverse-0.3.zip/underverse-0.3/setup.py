import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "underverse",
    version = "0.3",
    author = "Max Franks",
    author_email = "eliquious@gmail.com",
    description = ("A zero-configuration, non-distributed, JSON-based document storage and analysis module focusing on the manipulation, \
                    grouping and filtering of unstructured data from various sources. MapReduce is also supported for more advanced \
                    analysis methods. Query syntax is similar to SQL-Alchemy's filter method."),
    license = "MIT",
    keywords = "unstructured data analysis nosql map reduce mapreduce sql alchemy",
    url = "http://packages.python.org/underverse",
    packages=['underverse','doc'],
    # long_description=read('README'),
    long_description="Change Log can be viewed `here <http://packages.python.org/underverse/#change-log>`_.",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
    ],
)
