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

"""
pysubs.uuencoder module
=======================

SubStation format defines its own method of ASCII encoding of binary data.
This module provides the encoder and decoder function.

Note: This module uses _uuencoder fast C implementation when available.
Falls back to pure Python implementation otherwise.

Functions
---------
bin2ascii(): SSA's uuencoder.
ascii2bin(): SSA's uudecoder.

"""

def _bin2ascii(data):
    """SSA's uuencoder"""
    output = bytearray()

    for i in range(0, len(data) - (len(data) % 3), 3):
        """
        IN:  aaaa aaaa  bbbb bbbb  cccc cccc  [  N/A  ]
        OUT: 00aa aaaa  00aa bbbb  00bb bbcc  00cc cccc
        """
        a, b, c = data[i:i+3]
        output.append(33 + (a >> 2))
        output.append(33 + (((a << 4) | (b >> 4)) & 0x3f))
        output.append(33 + (((b << 2) | (c >> 6)) & 0x3f))
        output.append(33 + (c & 0x3f))

    if len(data) % 3 == 1:
        """
        IN:  aaaa aaaa  [  N/A  ]
        OUT: 00aa aaaa  00aa 0000
        """
        a = data[-1]
        output.append(33 + (a >> 2))
        output.append(33 + ((a << 4) & 0x3f))
    elif len(data) % 3 == 2:
        """
        IN:  aaaa aaaa  bbbb bbbb  [  N/A  ]
        OUT: 00aa aaaa  00aa bbbb  00bb bb00
        """
        a, b = data[-2:]
        output.append(33 + (a >> 2))
        output.append(33 + (((a << 4) | (b >> 4)) & 0x3f))
        output.append(33 + ((b << 2) & 0x3f))

    return "\n".join([output[i:i+80].decode("ascii")
                      for i in range(0, len(output), 80)])

_translate_table = bytes(max(0, i-33) for i in range(256))
_delete_table = bytes(i for i in range(256) if i < 33 or i > 0x3f + 33)

def _ascii2bin(data):
    """SSA's uudecoder"""
    data = data.encode("ascii")
    data = data.translate(_translate_table, _delete_table)
    output = bytearray()
    
    for i in range(0, len(data) - (len(data) % 4), 4):
        """
        IN:  00aa aaaa  00aa bbbb  00bb bbcc  00cc cccc
        OUT: aaaa aaaa  bbbb bbbb  cccc cccc  [  N/A  ]
        """
        x, y, z, w = data[i:i+4]
        output.append((x << 2) | (y >> 4))
        output.append(((y << 4) | (z >> 2)) & 0xff)
        output.append(((z << 6) | (w)) & 0xff)

    if len(data) % 4 == 1:
        raise ValueError("malformed data (1 extra byte)")
    elif len(data) % 4 == 2:
        """
        IN:  00aa aaaa  00aa 0000
        OUT: aaaa aaaa  [  N/A  ]
        """
        x, y = data[-2:]
        output.append((x << 2) | (y >> 4))
    elif len(data) % 4 == 3:
        """
        IN:  00aa aaaa  00aa bbbb  00bb bb00
        OUT: aaaa aaaa  bbbb bbbb  [  N/A  ]
        """
        x, y, z = data[-3:]
        output.append((x << 2) | (y >> 4))
        output.append(((y << 4) | (z >> 2)) & 0xff)
    
    return bytes(output)

# -----------------------------------------------------------------------------
# use C implementation if possible

try:
    from ._uuencoder import bin2ascii, ascii2bin
except ImportError:
    bin2ascii = _bin2ascii
    ascii2bin = _ascii2bin
