#
# Copyright John Reid 2011, 2012
#

from distutils.core import setup
import cookbook
setup(
    name='cookbook',
    version=cookbook.__release__,
    packages=['cookbook'],
    py_modules=['process_priority'],
    description='Some useful Python code, mainly from the Python cookbook',
    author='John Reid',
    author_email='john.reid@mrc-bsu.cam.ac.uk',
    url = "http://sysbio.mrc-bsu.cam.ac.uk/johns/Cookbook/docs/build/html/",
    download_url = "http://sysbio.mrc-bsu.cam.ac.uk/johns/Cookbook/dist/cookbook-%s.tar.gz" % cookbook.__release__,
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
    ],
    long_description = """\
Python cookbook recipes
-----------------------

This package gathers together some useful recipes from the python cookbook.
I have added some of my own and extended or modified some of the existing
recipes.
"""
)
