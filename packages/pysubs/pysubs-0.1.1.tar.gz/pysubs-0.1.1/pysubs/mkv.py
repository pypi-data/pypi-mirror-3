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
pysubs.mkv module
=================

Helper functions for working with MKV files. They rely on mkvtoolnix programs
mkvextract and mkvinfo. See http://www.bunkus.org/videotools/mkvtoolnix

Attributes
----------
MKVEXTRACT: Name under which mkvextract is callable from shell.
MKVINFO: Name under which mkvinfo is callable from shell.

Classes
-------
SubtitleTrack: A namedtuple subclass with track's contents and metadata.

Functions
---------
get_tracks_info(): Return list of dicts with MKV file tracks' metadata.
read_subtitle_tracks(): Return list of MKV's subtitle tracks as SSAFiles and
    metadata dicts.

"""

import re, subprocess, os, tempfile
from .subtitles import SSAFile
from .exceptions import MkvtoolnixError, MkvtoolnixUnavailableError

MKVEXTRACT = "mkvextract"
MKVINFO = "mkvinfo"

def get_tracks_info(file):
    """
    Run mkvinfo and return list with info on file's tracks.

    Note that mkvinfo must be executable from shell. If it is accessible
    under a different name, please modify MKVINFO variable accordingly.

    Arguments:
        file: Path to an MKV file.

    Returns:
        A list containing dicts with Codec ID, Name and other metadata
        that are provided. The list ought to be ordered, starting from track 1.

        Example:
        [{"Track number": "1", "Codec ID": "V_MPEG4/ISO/AVC", ...},
         {"Track number": "2", "Codec ID": "S_TEXT/UTF8", ...}, ...]

    Raises:
        IOError: Error when accessing the file.
        MkvtoolnixError: mkvinfo failed with the file (not an MKV file?).

    """
    if not os.access(file, os.R_OK):
        raise IOError("File '{}' doesn't exist or isn't readable.".format(file))

    try:
        mkvinfo_output = subprocess.check_output([MKVINFO,
                                                 "--output-charset", "utf-8",
                                                 file])
    except subprocess.CalledProcessError:
        raise MkvtoolnixError(
            "mkvinfo failed on file '{}' (not an MKV?).".format(file))
    except (OSError, WindowsError):
        raise MkvtoolnixUnavailableError("mkvinfo not available")
        
    mkvinfo_output = str(mkvinfo_output, "utf8")

    # TODO: replace hacky parsing with something more appropriate
    
    mkvinfo_parts = mkvinfo_output.split("\n|+ ")
    for part in mkvinfo_parts:
        if part.startswith("Segment tracks"):
            tracks = part.split("| + A track")
            tracks = tracks[1:]
            break
    
    tracks_list = []
    
    for track in tracks:
        track_dict = {}
        for line in track.splitlines():
            if line.startswith("|  +"):       # this doesn't capture nested info
                info = line[5:].split(": ", 1)
                if len(info) == 2:
                    track_dict[info[0]] = info[1]
        tracks_list.append(track_dict)

    return tracks_list


def read_subtitle_tracks(file):
    """
    Return a list of file's subtitle tracks and metadata.
    
    ASS, SSA and SRT tracks will be extracted. Note that mkvextract must be
    executable from shell. If it is accessible under a different name,
    please modify MKVEXTRACT variable accordingly.

    Arguments:
        file: Path to an MKV file.

    Returns:
        List of 2-tuples (SSAFile, metadata_dict).

    Raises:
        IOError: Error when accessing the file.
        MkvtoolnixError: mkvextract/mkvinfo failed with the file (not an MKV?).
        MkvtoolnixUnavailableError: mkvextract/mkvinfo not available

    """

    if not os.access(file, os.R_OK):
        raise IOError("File '{}' doesn't exist or isn't readable.".format(file))

    mkv_tracks = get_tracks_info(file)
    subtitle_tracks = [track_dict for track_dict in mkv_tracks
                       if track_dict["Codec ID"].startswith("S_TEXT/")]
    mkvextract_args = [MKVEXTRACT, "tracks", file]

    for track in subtitle_tracks:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        track["_tempfile"] = tmp.name
        mkvextract_args.append("{}:{}".format(track["Track number"], tmp.name))

    try:
        subprocess.check_output(mkvextract_args)
    except subprocess.CalledProcessError:
        raise MkvtoolnixError("mkvextract failed on file '{}'.".format(file))
    except (OSError, WindowsError):
        raise MkvtoolnixUnavailableError("mkvextract not available")
    
    output_list = []

    for track in subtitle_tracks:
        with open(track["_tempfile"], encoding="utf8") as tmp_file:
            content = tmp_file.read()
        os.unlink(track["_tempfile"])
        del track["_tempfile"]

        subs = SSAFile()
        subs.from_str(content)
        
        output_list.append((subs, track))

    return output_list
