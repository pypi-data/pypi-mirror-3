# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

LONG_DESC = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()

setup(
    name = "raw-import",
    version = "0.1.0",
    description = "Copy your docs directly to the dedicate branch.",
    long_description = LONG_DESC,
    author = "Christophe CHAUVET",
    author_email = "christophe.chauvet@gmail.com",
    license = "Tumbolia Public License",
    url = "http://kryskool.github.com/raw-import/",
    download_url = "http://github.com/kryskool/raw-import",
    zip_safe = False,

    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'Natural Language :: English',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],

    scripts = ['raw-import']
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
