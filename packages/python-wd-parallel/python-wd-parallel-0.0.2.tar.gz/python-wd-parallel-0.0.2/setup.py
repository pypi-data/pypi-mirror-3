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
    packages = ['wd'],
    version = "0.0.2",
    author = "Mathieu Sabourin",
    author_email = "mathieu.c.sabourin@gmail.com",
    maintainer = "Mathieu Sabourin",
    maintainer_email = "mathieu.c.sabourin@gmail.com",
    description = ("python-wd-parallel lets you easilly run your test in multiple borwsers."),
    keywords = " Testing, Selenium",
    url = " https://github.com/OniOni/python-parallel-wd",
    classifiers=[
        "Classifier: Development Status :: 3 - Alpha",
        "Classifier: Environment :: No Input/Output (Daemon)",
        "Classifier: Intended Audience :: Developers",
        "Classifier: License :: OSI Approved :: Apache Software License",
        "Classifier: Natural Language :: English",
        "Classifier: Operating System :: POSIX",
        "Classifier: Programming Language :: Python :: 2.7",
        "Classifier: Programming Language :: Python :: Implementation :: CPython",
        "Classifier: Topic :: Software Development :: Libraries",
        "Classifier: Topic :: Software Development :: Quality Assurance",
        "Classifier: Topic :: Software Development :: Testing"
        ]
)


