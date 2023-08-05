#!/usr/bin/env python

import distutils.core
import sys

try:
    import setuptools
except ImportError:
    pass

version = "0.2.3"

distutils.core.setup(
    name="tornado_tools",
    version=version,
    packages = ["tornado_tools"],
    author="Gregory Sitnin",
    author_email="sitnin@gmail.com",
    url="http://github.com/sitnin",
    download_url="https://github.com/sitnin/tornado_tools/tarball/0.2.3",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="Classes and functions for extending Tornado web server by Facebook/FriendFeed",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
