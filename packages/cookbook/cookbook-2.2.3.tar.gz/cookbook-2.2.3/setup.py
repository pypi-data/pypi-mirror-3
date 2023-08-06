#
# Copyright John Reid 2011, 2012
#

from setuptools import setup
import os, cookbook



def read(fname):
    """
    Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a top level
    README file and 2) it's easier to type in the README file than to put a raw
    string in below ...
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name          = 'cookbook',
    version       = cookbook.__release__,
    packages      = ['cookbook'],
    py_modules    = ['process_priority'],
    description   = 'Some useful Python code, mainly from the Python cookbook',
    author        = 'John Reid',
    author_email  = 'john.reid@mrc-bsu.cam.ac.uk',
    url           = "http://sysbio.mrc-bsu.cam.ac.uk/johns/Cookbook/docs/build/html/",
    download_url  = "http://sysbio.mrc-bsu.cam.ac.uk/johns/Cookbook/dist/cookbook-%s.tar.gz" % cookbook.__release__,
    classifiers   = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
    ],
    long_description = read('README.txt'),
)
