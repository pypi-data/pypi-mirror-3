# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
from os.path import join as pathjoin

VERSION = "0.5.3"
LONG_DESCRIPTION = "".join([
    open(pathjoin("src","README.txt")).read(),
    open(pathjoin("src","TODO.txt")).read()])

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Software Development :: Internationalization",
]

INSTALL_REQUIRES = ["distribute"]
if sys.version_info < (2, 7):
    INSTALL_REQUIRES.append("argparse")

setup(
     name="ikazuchi",
     version=VERSION,
     description="ikazuchi helps to translate document using web translate APIs efficiently",
     long_description=LONG_DESCRIPTION,
     classifiers=CLASSIFIERS,
     keywords=["translate", "i18n", "internationalization"],
     author="Tetsuya Morimoto",
     author_email="tetsuya dot morimoto at gmail dot com",
     url="http://t2y.bitbucket.org/ikazuchi/build/html/index.html",
     license="Apache License 2.0",
     py_modules=[],
     scripts=["src/ikazuchi/vim/raimei", "src/ikazuchi/vim/enrai"],
     packages=find_packages("src"),
     package_dir={"": "src"},
     package_data={"": ["buildout.cfg"]},
     namespace_packages=["ikazuchi", "ikazuchi.plugins"],
     include_package_data=True,
     install_requires=INSTALL_REQUIRES,
     extras_require=dict(
         test=[
             "Nose",
             "minimock",
             "pep8",
         ],
     ),
     test_suite="nose.collector",
     tests_require=["Nose","minimock","pep8"],
     entry_points={
        "console_scripts": [
            "ikazuchi = ikazuchi.ikazuchi:main",
        ],
        "ikazuchi": [
            "ikazuchi = ikazuchi.ikazuchi",
            "raimei = ikazuchi.vim.raimei:main",
            "enrai = ikazuchi.vim.enrai:main",
        ],
        "ikazuchi.plugins": [
            "rstfile = ikazuchi.plugins.rstfile",
        ],
     }
)
