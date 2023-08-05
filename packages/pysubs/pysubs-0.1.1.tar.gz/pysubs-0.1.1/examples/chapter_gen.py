#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OGM chapters example
====================

MKV chapters are useful, but creating them by hand can be a hassle. Why not
mark them in our SubStation subtitle file and generate them with one click?

This example provides working, if simple, implementation of the idea. Chapters
are marked via SubStation Effect field, like this: "createchapter: Intro".
This creates a new chapter starting with the subtitle's Start time.

Arguments to this script are paths to subtitle files -- it may be used in
a Drag-n-Drop fashion. For each <filename>.ass, an OGM chapter file
<filename>_chapters.txt is generated.

"""

import sys, os.path
import pysubs

CHAPTER_KEYWORD = "createchapter"

def get_OGM_chapters(subtitle_obj):
    """
    Create OGM chapter file from given SSAFile.

    The chapters are marked via SSA lines with Effect field in the following
    format: CHAPTER_KEYWORD: chapter_name, eg. "createchapter: Intro". This
    creates a chapter starting at SSA line's start time called "Intro".

    For info on the OGM chapter format, see:
    https://www.bunkus.org/videotools/mkvtoolnix/doc/mkvmerge-gui.html#cfsimple

    Arguments:
        subtitle_obj: pysubs.SSAFile instance

    Returns:
        str with OGM chapters
    
    """
    data = []
    output = []
    for line in sorted(subtitle_obj.events):
        if line.effect.startswith(CHAPTER_KEYWORD):
            data.append(
                (line.start,
                 line.effect.replace(CHAPTER_KEYWORD, "").strip(": ")))

    for i, (time, name) in enumerate(data, 1):
        output.append("CHAPTER{:02d}={:srt}".format(i, time).replace(",", "."))
        output.append("CHAPTER{:02d}NAME={}".format(i, name).replace(";", ","))

    return "\n".join(output)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: chapter_gen.py SSA_FILE [SSA_FILE ...]")
    
    for path in sys.argv[1:]:
        if not os.path.isfile(path):
            print(path, "is not a file!", file=sys.stderr)
            continue

        # FIXME -- some spaghetti to shut up PySubs about character encoding
        try:
            try:
                subs = pysubs.load(path)
            except pysubs.EncodingDetectionError:
                try:
                    subs = pysubs.load(path, "utf-8")
                except UnicodeDecodeError:
                    with open(path, encoding="cp1250", errors="replace") as fp:
                        subs = pysubs.SSAFile()
                        subs.from_str(fp.read())
        except IOError:
            print("I/O error when reading file", path, file=sys.stderr)
            continue
        except pysubs.UnknownFormatError:
            print("Cannot read malformed subtitle file", path, file=sys.stderr)
            continue

        chapter_data = get_OGM_chapters(subs)
        chapter_path = os.path.splitext(path)[0] + "_chapters.txt"
        with open(chapter_path, "w", encoding="utf-8") as fp:
            print(chapter_data, file=fp)
            print("Wrote chapters for", path)
