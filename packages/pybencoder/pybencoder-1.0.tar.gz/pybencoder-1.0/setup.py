# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name = 'pybencoder',
    version = '1.0',
    description = 'Module to work with bencoded strings.',
    long_description = """\
PyBencoder - your bencoded strings module
-------------------------------------------

What is a Bencoded String?

Bencode (pronounced like B encode) is the encoding used by the peer-to-peer file sharing system BitTorrent
for storing and transmitting loosely structured data.

For more info on bencoding check out `this <http://en.wikipedia.org/wiki/Bencode/>`_.

It provides:
 - decoding of the different bencoded elements
 - encoding of the allowed types (byte strings, integers, lists, and dictionaries).

Requires Python 2.6 or later.
""",
    author='Cristian Năvălici',
    author_email = 'ncristian@lemonsoftware.eu',
    url = 'https://github.com/cristianav/PyBencoder',
    download_url = 'https://github.com/cristianav/PyBencoder/zipball/master',
    license = "LGPL",
    platforms = ['POSIX', 'Windows'],
    keywords = ['bencoding', 'encode', 'decode', 'bittorrent'],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    packages = ['PyBencoder']
    )
