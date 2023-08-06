import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "dummycache",
    version = "0.0.2",
    author = "Vichaya Sirisanthana",
    author_email = "vsirisanthana@gmail.com",
    url = "http://code.google.com/p/dummycache/",
    description = "A dummy in-memory cache for development and testing. (Not recommended for production use.)",
    long_description = read("README.txt"),
    download_url = "http://pypi.python.org/pypi/dummycache",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)"
    ],
    license = "GPL-3.0",
    keywords = "cache python",
    packages = ['dummycache'],
    install_requires = [],
)