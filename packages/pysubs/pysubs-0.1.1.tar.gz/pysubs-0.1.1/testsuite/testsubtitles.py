#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Copyright (c) 2011 Tigr <tigr42@centrum.cz>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pysubs
from pysubs.exceptions import *
import unittest, os.path


STATIC_DIR = os.path.join(
    os.path.split(__file__)[0],
    "static")

def _path(file):
    return os.path.join(STATIC_DIR, file)

def _ssa_equal(str1, str2):
    lines1 = {line.strip() for line in str1
              if line and not line.startswith(";")}
    lines2 = {line.strip() for line in str1
              if line and not line.startswith(";")}
    return lines1 == lines2

def _ssa_difference(str1, str2):
    lines1 = {line.strip() for line in str1
              if line and not line.startswith(";")}
    lines2 = {line.strip() for line in str1
              if line and not line.startswith(";")}
    return lines1 ^ lines2

# ------------------------------------------------------------------------------
# the tests

class TestMalformedSRT(unittest.TestCase):
    def setUp(self):
        self.deformed = pysubs.load(_path("malformed_srt.srt"))
        self.good = pysubs.load(_path("malformed_srt_ok.srt"))

    def runTest(self):
        """tolerant SRT parsing"""
        self.assertEqual(self.deformed, self.good)


class TestSimpleASS_SSA(unittest.TestCase):
    def setUp(self):
        with open(_path("simple_substation.ass"), encoding="utf-8-sig") as fp:
            self.ass_reference = fp.read()
            self.ass = pysubs.SSAFile()
            self.ass.from_str(self.ass_reference)
            
        with open(_path("simple_substation.ssa"), encoding="utf-8-sig") as fp:
            self.ssa_reference = fp.read()
            self.ssa = pysubs.SSAFile()
            self.ssa.from_str(self.ssa_reference)

    def runTest(self):
        """simple ASS/SSA (from_str, to_str)"""
        self.assertEqual(self.ass, self.ssa)
        ssa_str = self.ssa.to_str("ssa")
        ass_str = self.ass.to_str("ass")

        self.assertTrue(_ssa_equal(self.ass_reference, ass_str))
        self.assertTrue(_ssa_equal(self.ssa_reference, ssa_str))


class TestSimpleASS_SRT(unittest.TestCase):
    def setUp(self):
        self.ass = pysubs.load(_path("simple_substation.ssa"))
            
        with open(_path("simple_substation.srt"), encoding="utf-8-sig") as fp:
            self.srt_reference = fp.read()

    def runTest(self):
        """simple ASS -> SRT (no overlap, no tags, remove no-duration line)"""
        srt_str = self.ass.to_str("srt")
        self.assertEqual(self.srt_reference.strip(), srt_str.strip())

class TestSimpleASS_SUB(unittest.TestCase):
    def setUp(self):
        self.ass = pysubs.load(_path("simple_substation.ssa"))
            
        with open(_path("simple_substation.sub"), encoding="utf-8-sig") as fp:
            self.sub_reference = fp.read()

    def runTest(self):
        """simple ASS -> SUB (no overlap, no tags, remove no-duration line)"""
        sub_str = self.ass.to_str("sub", fps="pal")
        self.assertEqual(self.sub_reference.strip(), sub_str.strip())

class TestSimpleSUB_SRT(unittest.TestCase):
    def setUp(self):
        self.sub = pysubs.load(_path("simple_substation.sub"))
            
        with open(_path("simple_substation.srt"), encoding="utf-8-sig") as fp:
            self.srt_reference = fp.read()

    def runTest(self):
        """simple SUB -> SRT"""
        srt_str = self.sub.to_str("srt")
        self.assertEqual(self.srt_reference.strip(), srt_str.strip())

class TestOverlappingSRT(unittest.TestCase):
    def setUp(self):
        self.ass = pysubs.load(_path("collision_test.ass"))
            
        with open(_path("collision_test.srt"), encoding="utf-8-sig") as fp:
            self.srt_reference = fp.read()

    def runTest(self):
        """ASS -> SRT (multiple overlaps, no tags, remove no-duration line)"""
        srt_str = self.ass.to_str("srt")
        self.assertEqual(self.srt_reference.strip(), srt_str.strip())


class TestSRTDecoding(unittest.TestCase):
    KNOWN_VALUES = [
        ("What a meaningful\nsubtitle line...",
             r"What a meaningful\Nsubtitle line..."),
        ("<i>Foo bar!</i>",
             r"{\i1}Foo bar!{\i0}"),
        ("<i>Foo!</i> <b>Bar!</b> <s>Baz!</s> <u>Qux!</u>",
             r"{\i1}Foo!{\i0} {\b1}Bar!{\b0} {\s1}Baz!{\s0} {\u1}Qux!{\u0}"),
        ("<i>Foo!",
             r"{\i1}Foo!"),
        ("< i >Foo!< / i >",
             r"{\i1}Foo!{\i0}"),
        ("""<font face="Comic Sans MS" size=26 color=red>Foo!</font>""",
             r"{\fnComic Sans MS\c&H0000FF&}Foo!{\r}"),
        ("""<font face=Calibri color="#ff0000">Foo!</font>""",
             r"{\fnCalibri\c&H0000FF&}Foo!{\r}")]
    
    def runTest(self):
        """decoding SRT tags"""
        for text, reference in self.KNOWN_VALUES:
            decoded = pysubs.SSAEvent.decode_tags(text, "srt")
            self.assertEqual(decoded, reference)

class TestSUBDecoding(unittest.TestCase):
    KNOWN_VALUES = [
        ("What a meaningful|subtitle line...",
             r"What a meaningful\Nsubtitle line..."),
        ("{Y:i}Foo|Bar|Baz!",
             r"{\i1}Foo\NBar\NBaz!{\i0}"),
        ("{Y:iub}Foo|Bar|Baz!",
             r"{\i1\u1\b1}Foo\NBar\NBaz!{\i0\u0\b0}"),
        ("{y:i}Foo|{y:b}Bar|{y:u}Baz!",
             r"{\i1}Foo{\i0}\N{\b1}Bar{\b0}\N{\u1}Baz!{\u0}"),
        ("{y:ib}Foo||Bar.",
             r"{\i1\b1}Foo{\i0\b0}\N\NBar.")]
        
    def runTest(self):
        """decoding SUB tags"""
        for text, reference in self.KNOWN_VALUES:
            decoded = pysubs.SSAEvent.decode_tags(text, "sub")
            self.assertEqual(decoded, reference)

class TestSRTEncoding(unittest.TestCase):
    KNOWN_VALUES = [
        (r"Foo\NBar\hBaz.",
             "Foo\nBar Baz."),
        (r"{\i1}Foo bar.{\i0} Baz, {\i1}quux{\i0}.",
             "<i>Foo bar.</i> Baz, <i>quux</i>."),
        (r"{\i1}Foo bar.",
             "<i>Foo bar.</i>"),
        (r"{SomeSophisticatedStuff}Foo bar.",
             "Foo bar.")]
    
    def runTest(self):
        """encoding SRT tags"""
        for text, reference in self.KNOWN_VALUES:
            encoded = pysubs.SSAEvent.encode_tags(text, "srt")
            self.assertEqual(encoded, reference)

class TestSUBEncoding(unittest.TestCase):
    KNOWN_VALUES = [
        (r"Foo\NBar\hBaz.",
             "Foo|Bar Baz."),
        (r"{\i1}Foo\NBar\hBaz.{\i0}",
             "{Y:i}Foo|Bar Baz.")]
    
    def runTest(self):
        """encoding SUB tags"""
        for text, reference in self.KNOWN_VALUES:
            encoded = pysubs.SSAEvent.encode_tags(text, "sub")
            self.assertEqual(encoded, reference)
