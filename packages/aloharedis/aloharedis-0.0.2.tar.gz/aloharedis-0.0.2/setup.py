# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

from distutils.core import setup
from aloharedis import __version__

with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name = "aloharedis",
    version = __version__,
    packages = ["aloharedis"],
    requires = ["redis"],
    author = "Xue Can",
    author_email = "xuecan@gmail.com",
    url = "https://bitbucket.org/xuecan/aloharedis",
    keywords = ["redis", "lock", "cache", "ohm", "object hash mapper"],
    description = "Aloharedis is a set of tools for working with redis-py.",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description = long_description
)
