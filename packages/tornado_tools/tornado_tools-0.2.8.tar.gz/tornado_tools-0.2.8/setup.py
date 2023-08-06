#!/usr/bin/env python

import distutils.core
import sys

try:
    import setuptools
except ImportError:
    pass

from tornado_tools import version

distutils.core.setup(
    name="tornado_tools",
    version=version,
    packages = ["tornado_tools"],
    author="Gregory Sitnin",
    author_email="sitnin@gmail.com",
    url="http://github.com/sitnin",
    download_url="https://github.com/sitnin/tornado_tools/tarball/%s"%version,
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="Classes and functions for extending Tornado",
    requires=["tornado (>=2.1.0)"],
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
