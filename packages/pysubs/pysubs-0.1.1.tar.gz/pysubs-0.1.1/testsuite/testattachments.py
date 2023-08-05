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
import unittest

class TestAttachmentEncoding_Decoding(unittest.TestCase):
    TEST_DATA = [
        bytes(range(1)),
        bytes(range(2)),
        bytes(range(3)),
        bytes(range(4)),
        bytes(range(256)),
        bytes(range(256)) + b"1",
        bytes(range(256)) + b"12",
        bytes(range(256)) + b"123"]

    def test_fallback_codec(self):
        """test Python implementation of uuencoder"""
        with self.assertRaises(ValueError):
            pysubs.uuencoder._ascii2bin("A")
            
        for reference in self.TEST_DATA:
            encoded = pysubs.uuencoder._bin2ascii(reference)
            decoded = pysubs.uuencoder._ascii2bin(encoded)
            self.assertEqual(decoded, reference)

    @unittest.skipIf(pysubs.uuencoder.bin2ascii == pysubs.uuencoder._bin2ascii,
                     "_bbencoder not compiled")
    def test_native_codec(self):
        """test C implementation of uuencoder"""
        with self.assertRaises(ValueError):
            pysubs.uuencoder.ascii2bin("A")

        for reference in self.TEST_DATA:
            encoded = pysubs.uuencoder.bin2ascii(reference)
            encoded_py = pysubs.uuencoder._bin2ascii(reference)
            self.assertEqual(encoded, encoded_py)
            decoded = pysubs.uuencoder.ascii2bin(encoded)
            self.assertEqual(decoded, reference)
    
    def test_SSAAttachment(self):
        """test SSAAttachment class"""
        for reference in self.TEST_DATA:
            encoded = pysubs.SSAAttachment(reference)
            decoded = encoded.to_bytes()
            self.assertEqual(decoded, reference)
