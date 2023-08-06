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
    version = "0.1.1",
    author = "Max Franks",
    author_email = "eliquious@gmail.com",
    description = ("A non-distributed, JSON-based document storage and analysis module focusing on the manipulation, \
                    grouping and filtering of unstructured data from various sources. \
                    ."),
    license = "MIT",
    keywords = "unstructured data analysis nosql",
    url = "http://packages.python.org/underverse",
    packages=['underverse','doc'],
    # long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
    ],
    requires=["stream"],
)
