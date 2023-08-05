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

from .subtitles import SSAFile, SSAEvent, SSAStyle, SSAAttachment, resolve_format
from .misc import Color, Time, Vec2
from .exceptions import *
from . import effects, mkv, uuencoder

__VERSION__ = (0, 1, 1)
_version_str = ".".join(map(str, __VERSION__))

def load(file, encoding=None, fps=None):
    """
    Load single subtitle file or tuple of MKV subtitle tracks.

    For subtitle file, this is equivalent to pysubs.SSAFile(file, encodng, fps).
    For MKV, this is equivalent to pysubs.mkv.read_subtitle_tracks(file).

    Arguments:
        file: ASS/SSA/SRT/SUB/MKV file to be loaded. MKV file is recognised by
            ".mkv" extension.
        encoding: Character encoding of the subtitle file. When None,
            autodetection takes place. Does not affect MKV files.
        fps: Frame rate for SUB files, in case they don't specify it on their
            first line. Does not affect any other format.

    Returns:
        Subtitle file: single SSAFile instance.
        MKV file: list of 2-tuples (SSAFile, metadata_dict).

    Raises:
        IOError: Non-existent or unreadable file.
        UnicodeDecodeError: Cannot decode file with given encoding.
        EncodingDetectionError: Cannot autodetect encoding, please specify.
        UnknownFPSError: fps unspecified and SUB file didn't declare it.
        UnknownFormatError: Subtitle format could not be resolved.
        MkvtoolnixError: mkvextract/mkvinfo failed with the file (not an MKV?).
        MkvtoolnixUnavailableError: mkvextract/mkvinfo not available
    
    """
    if file.lower().endswith(".mkv"):
        return mkv.read_subtitle_tracks(file)
    else:
        return SSAFile(file, encoding, fps)
