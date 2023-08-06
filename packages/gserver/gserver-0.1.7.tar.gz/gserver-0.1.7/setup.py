import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "gserver",
    version = "0.1.7",
    author = "Justin Wilson",
    author_email = "justinwilson1@gmail.com",
    description = ("Simple wrapper around gevent's wsgi server."
        "Adds simple regex routing, error handling, and json/jsonp handling."),
    license = "Simplified BSD",
    url = "http://pypi.python.org/pypi/gserver",
    packages=['gserver',],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
        "gevent >= 0.13.6",
    ],
)

