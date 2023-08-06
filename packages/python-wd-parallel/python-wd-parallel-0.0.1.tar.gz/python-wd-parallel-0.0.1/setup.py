import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "python-wd-parallel",
    version = "0.0.1",
    author = "Mathieu Sabourin",
    author_email = "mathieu.c.sabourin@gmail.com",
    description = ("python-wd-parallel lets you easilly run your test in multiple borwsers."),
    keywords = " Testing, Selenium",
    url = " https://github.com/OniOni/python-parallel-wd",
)
