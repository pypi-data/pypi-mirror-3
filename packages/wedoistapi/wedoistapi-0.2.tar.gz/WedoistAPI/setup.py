import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "wedoistapi",
    version = "0.2",
    author = "Chris Statzer",
    author_email = "chris.statzer@gmail.com",
    description = ("A pythonic API to authenticate, fetch, and post data to your Wedoist.com account."),
    license = "BSD",
    keywords = "library wedoist todo task project management",
    url = "http://wedoist.com",
    packages=['wedoistapi'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
    ],
)
