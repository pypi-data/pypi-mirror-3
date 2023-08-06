import os

from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "dummycache",
    version = "0.0.1",
    author = "The Sirisanthana Team",
    author_email = "vsirisanthana@gmail.com",
    description = ("A dummy in-memory cache for development and testing (never use in production)."),
    long_description = read('README.txt'),
    license = "GPL-3.0",
    keywords = "cache python",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)"
    ],
    packages = ['dummycache'],
    install_requires = [],
)