#!/usr/bin/python
# (c) 2005-2009 Divmod, Inc.  See LICENSE file for details

from distutils.core import setup

setup(
    name="pyflakes3k",
    license="MIT",
    version="0.4.3",
    description="passive checker of Python programs (py3k port)",
    maintainer="Virgil Dupras",
    maintainer_email="hsoft@hardcoded.net",
    url="http://bitbucket.org/hsoft/pyflakes3k",
    packages=["pyflakes", "pyflakes.scripts", "pyflakes.test"],
    scripts=["bin/pyflakes"],
    long_description=open('README').read(),
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Utilities",
        ])
