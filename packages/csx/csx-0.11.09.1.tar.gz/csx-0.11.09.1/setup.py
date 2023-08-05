#! /usr/bin/env python3

from distutils.core import setup

import csx

setup(
    author = "Zero Piraeus",
    author_email = "z@etiol.net",
    description = "Extended Cascading Stylesheets",
    keywords = "css web",
    license = "GPLv3",
    long_description = csx.__doc__,
    name = "csx",
    py_modules = ["csx"],
    scripts = ["csx"],
    version = csx.__version__,

    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.0",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ]
)

