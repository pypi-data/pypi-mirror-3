#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup, Extension
from textwrap import dedent
import sys

if sys.version_info < (3, 0):
    print("PySubs requires Python 3.")
    sys.exit(1)

from pysubs import _version_str

uuencoder = Extension(
    'pysubs._uuencoder',
    sources = ['ext/_uuencoder.c'],
    optional = True
    )

setup(
    name = "pysubs",
    packages = ["pysubs", "pysubs.effect_definitions"],
    scripts = ["pysubs-cli.py"],
    version = _version_str,
    author = "Tigr",
    author_email = "tigr42@centrum.cz",
    ext_modules = [uuencoder],
    url = "https://github.com/tigr42/pysubs",
    license = "2-clause BSD",
    keywords = "SubStation SubRip ass srt sub subtitles",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: C",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Topic :: Multimedia :: Video",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License"
        ],
    description = "SubStation-based subtitle framework",
    long_description = dedent(r"""\
        PySubs is a subtitle framework written in Python 3. While aimed at
        developers, it comes with a script to do batch retiming/conversion
        from commandline -- a feature some users may find useful as well.

        Supported formats
        -----------------

        - SubStation Alpha (ASS, SSA files) as the native format
        - SubRip Text (SRT files) import/export
        - MicroDVD (SUB files) import/export
        - Matroska (MKV) subtitle track import via mkvtoolnix

        Commandline example
        -------------------

        ::

            $ pysubs-cli.py --output-dir retimed --shift 1.3s *.srt

        Framework example
        -----------------

        >>> import pysubs
        >>> subs = pysubs.load("subtitles.ass", encoding="utf-8")
        >>> subs.styles["Default"].fontname = "Calibri"
        >>> for line in subs:
        ...     line.text = "{\be1}" + line.text
        >>> subs.save("subtitles_fancy.ass")
        """)
    )
