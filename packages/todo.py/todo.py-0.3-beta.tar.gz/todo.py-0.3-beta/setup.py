#!/usr/bin/env python

import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] in ("submit", "publish"):
    os.system("python setup.py sdist upload")
    sys.exit()

packages = []
requires = []
readme = open("README.rst").read()
history = open("HISTORY.rst").read()

setup(
    name="todo.py",
    version="0.3-beta",
    description="Python version of Gina Trapani's popular bash script.",
    long_description="\n\n".join([readme, history]),
    author="graffatcolmingov",
    author_email="graffatcolmingov@gmail.com",
    url="https://github.com/sigmavirus24/Todo.txt-python",
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console', 
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: IronPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        ),
    scripts=["todo.py"]
    )
