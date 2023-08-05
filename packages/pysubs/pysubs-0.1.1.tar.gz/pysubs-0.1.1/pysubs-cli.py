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

import os, sys, glob, argparse, re, codecs, textwrap
from collections import OrderedDict
import pysubs

# ------------------------------------------------------------------------------
# argument converters / basic checkers

def check_encoding(arg):
    try:
        codecs.lookup(arg)
        return arg
    except LookupError:
        raise argparse.ArgumentError

def check_time(arg):
    # As we use "-" for option delimiter, negative argument to --shift isn't
    # possible directly. Rather, we use special value "NEG_TIME" for argument-less --shift
    # invocation and then pick up the negative time pseudo-option via parse_known_args.
    if arg == "NEG_TIME":
        return arg
    
    sign = (-1) ** int(arg.startswith("-"))
    kwargs = {}
    try:
        for amount, order in re.findall(r"([0-9.]+)(h|m|s|ms)", arg):
            kwargs[order] = sign * float(amount)
    except ValueError:
        raise argparse.ArgumentError

    if not kwargs:
        raise argparse.ArgumentError
    else:
        return pysubs.Time(**kwargs)

def check_fps(arg):
    try:
        return pysubs.Time.sanitize_framerate(arg)
    except (ValueError, pysubs.UnknownFPSError):
        raise argparse.ArgumentError

def check_attachments(arg):
    files = arg.split(",")
    if not all(map(lambda x: x.lower().endswith(".ttf"), files)):
        raise argparse.ArgumentError
    return files

# ------------------------------------------------------------------------------
# path manipulation

filename_sans_extension = lambda file: os.path.splitext(os.path.split(file)[1])[0]

def expand_paths(path_list):
    """
    Expand * and ? characters in paths, return absolute paths.

    Existing and non-existent paths without expansion characters are output
    as they are. Note that [] or ~ characters are not expanded.

    Arguments:
        path_list: List of paths to be expanded.

    Returns:
        List of absolute paths after expansion.

    Raises:
        TypeError: path_list was a single string; use 1-tuple instead.
        
    """
    escapes = "\ue000\ue001"
    output = []

    if isinstance(path_list, str):
        raise TypeError("path_list was a string; use 1-tuple instead")

    for path in path_list:
        path = os.path.abspath(path)
        if "*" in path or "?" in path:
            path = path.replace("[", escapes[0]).replace("]", escapes[1])
            path = path.replace(escapes[0], "[[]").replace(escapes[1], "[]]")
            output.extend(glob.glob(path))
        else:
            output.append(path)

    return output

TRANS_TABLE = bytearray(256 * b"_")
TRANS_TABLE[ord("0"):ord("9")+1] = range(ord("0"), ord("9")+1)
TRANS_TABLE[ord("a"):ord("z")+1] = range(ord("a"), ord("z")+1)
TRANS_TABLE[ord("A"):ord("Z")+1] = range(ord("A"), ord("Z")+1)

def sanitize_name(name):
    """return ASCII & special chars safe name"""
    return name.encode("ascii", "replace").translate(TRANS_TABLE).decode("ascii")

# ------------------------------------------------------------------------------
# main

class PySubsCLI:
    def __init__(self):
        parser = self.parser = argparse.ArgumentParser(
            usage="%(prog)s [options] files",
            description=textwrap.dedent("""\
                PySubs CLI tool (PySubs version {})
                Website: http://github.com/tigr42/pysubs

                This is a tool for batch retiming, conversion and other manipulation
                with subtitles. Examples after argument description.
                """.format(pysubs._version_str)),
            epilog=textwrap.dedent("""\
                examples:
                
                    Shift all SRT subtitles in folder by 1.3 seconds forward and save them
                    to subfolder "retimed":
                    $ pysubs-cli.py --shift 1.3s --output-dir retimed *.srt

                    Convert ASS files in folder to SRT files:
                    $ pysubs-cli.py --convert srt *.ass

                    Make all ASS subtitles in folder use modified styles from one ASS file:
                    $ pysubs-cli.py --update-styles my_styles.ass *.ass

                    Export subtitle tracks from MKVs in current folder:
                    $ pysubs-cli.py *.mkv

                    Attach some fonts to all ASS files in folder:
                    $ pysubs-cli.py --attach calibri.ttf,calibri_bold.ttf *.ass

                    Strip the attached fonts:
                    $ pysubs-cli.py --delete-attached *.ass"""),
            formatter_class=argparse.RawDescriptionHelpFormatter)

        # input
        parser.add_argument("files", nargs="+",
                            metavar = "FILE",
                            help="""Input files. Supported formats: ASS,SSA,SRT,SUB,MKV.
                                MKV is only for subtitle tracks' extraction and requires
                                mkvinfo/mkvextract from mkvtoolnix. Supported wildcards:
                                * and ?. Eg.: *.ass *.srt.""")

        # commands
        parser.add_argument("--shift", nargs="?", const="NEG_TIME", type=check_time,
                            help="""Shift subtitles (positive values = subtitles appear later).
                                Eg.: 1m30s; 1.5m; 90s; -1m30s; -1.5m; -90s.""")
        parser.add_argument("--transform", nargs=2, type=check_fps,
                            metavar=("IN_FPS", "OUT_FPS"),
                            help="""Multiply subtitles' start and end times by ratio of
                                    OUT_FPS/IN_FPS. Frame rates may be either floats or string
                                    aliases. Eg.: ntsc_film ntsc_video; 23.976 29.97.""")
        parser.add_argument("--convert", choices=["ass", "ssa", "srt"],
                            help="""Don't save each subtitle file in its original format,
                                but convert all to a common one.""")
        parser.add_argument("--update-styles",
                            metavar="SUBTITLE_FILE",
                            help="""Append to all subtitles styles from this file, overwriting
                                current ones on name conflicts. Only applies to SubStation files. """)
        parser.add_argument("--attach", type=check_attachments,
                            metavar="TTF_FILE[,TTF_FILE ...]",
                            help="""Attach TrueType fonts -- only applies to SubStation files.
                                Given filenames must not contain commas or whitespace and must
                                have .ttf extension. Multiple files may be given, separated
                                by commas.""")
        parser.add_argument("--delete-attached", action="store_true",
                            help="""Delete any attached fonts -- only applies to SubStation files.
                                Files given with --attach will still get attached.""")
        parser.add_argument("--apply-effects", action="store_true",
                            help="""Apply PySubs effects. Comment out effect lines and append
                                generated lines after them. See PySubs documentation for more.""")
        parser.add_argument("--undo-effects", action="store_true",
                            help="""Clear any PySubs effects' generated lines and uncomment
                                original effect lines.""")
    
        # settings
        parser.add_argument("--encoding", type=check_encoding,
                            help="""Character encoding of input files. PySubs can autodetect
                                UTF-8/UTF-16 via BOM, or use chardet module when installed.
                                Files that cannot be autodetected are skipped and you have
                                to give the encoding explicitly. Eg.: utf8; cp1250; iso-8859-2.""")
        parser.add_argument("--output-encoding", type=check_encoding, default="utf-8-sig",
                            metavar="ENCODING",
                            help="""Character encoding of output files, defaults to UTF-8 with
                                BOM. Note that failure is possible with non-Unicode charsets
                                as some characters may not be representable.""")
        parser.add_argument("--output-dir", default=".",
                            help="""Output directory, defaults to current directory. It is
                                advisable not to stick with this default, as pysubs.py
                                overwrites files without prompting and may mess up (esp. with
                                encoding).""")
        parser.add_argument("--fps", type=check_fps,
                            help="""Only neccessary when opening MicroDVD (SUB) files that don't
                                declare framerate on their first line. Has no effect on other
                                formats.""")
        
    def __call__(self, *args):
        args, unknown = self.parser.parse_known_args(*args)

        # expand paths
        files = expand_paths(args.files)

        # handle negative --shift & unknown arguments
        if args.shift == "NEG_TIME":
            try:
                args.shift = check_time(unknown.pop())
            except argparse.ArgumentError:
                self.parser.error("Cannot read --shift argument")
        if unknown:
            self.parser.error("Unknown arguments: '{}'".format(unknown))

        # handle style import
        self.styles_file = None
        if args.update_styles:
            try:
                self.styles_file = pysubs.SSAFile(
                    args.update_styles, encoding=args.encoding)
            except IOError:
                self.parser.error(
                    "Cannot open file '{}' for style import".format(args.update_styles))
            except (UnicodeDecodeError, pysubs.PySubsError) as e:
                self.parser.error(
                    "Error when opening file '{}' for style import: {}".format(args.update_styles, e))
        
        # handle attachments
        self.attachments = OrderedDict()
        if args.attach:
            for path in args.attach:
                try:
                    filename = os.path.split(path)[1]
                    self.attachments[filename] = pysubs.SSAAttachment(file=path)
                except IOError:
                    self.parser.error("Cannot open file to be attached: '{}'".format(path))

        # handle output dir
        output_dir = self.output_dir = os.path.abspath(args.output_dir)
        if os.path.isdir(output_dir):
            if not os.access(output_dir, os.W_OK):
                self.parser.error("Output directory '{}' isn't writable".format(output_dir))
        else:
            try:
                os.mkdir(output_dir)
            except OSError:
                self.parser.error("Cannot create output directory '{}'".format(output_dir))

        # process files
        self.args = args
        
        for file in files:
            if file.lower().endswith(".mkv"):
                self.process_MKV(file)
            else:
                self.process_regular(file)

    def process_MKV(self, file):
        MKV_filename = filename_sans_extension(file)
        
        try:
            extracted = pysubs.mkv.read_subtitle_tracks(file)
            for subs, info in extracted:
                format_ = "ass" if info["Codec ID"].endswith("ASS") else "srt"

                name_components = [info["Track number"], ]
                if info.get("Name"):
                    name = sanitize_name(info["Name"])
                    name_components.append(name)
                if info.get("Language") and info["Language"] != "und":
                    name_components.append(info["Language"])

                if self.args.convert:
                    output_filename = ".".join(
                        [MKV_filename, "_".join(name_components), self.args.convert])
                else:
                    output_filename = ".".join(
                        [MKV_filename, "_".join(name_components), format_])
                
                self.process(subs, os.path.join(self.output_dir, output_filename))
        except IOError:
            print(file, "...", "ERROR (cannot open the file)")
        except pysubs.MkvtoolnixError:
            print(file, "...", "ERROR (mkvextract/mkvinfo failed on the file)")
        except pysubs.MkvtoolnixUnavailableError:
            print(file, "...", "SKIP (mkvextract/mkvinfo unavailable)")

    def process_regular(self, file):
        filename = filename_sans_extension(file)
        try:
            subs = pysubs.SSAFile(file, self.args.encoding, self.args.fps)
            if self.args.convert:
                output_filename = ".".join([filename, self.args.convert])
            else:
                output_filename = ".".join([filename, subs._format])
            self.process(subs, os.path.join(self.output_dir, output_filename))
        except IOError:
            print(file, "...", "ERROR (cannot open the file)")
        except pysubs.UnknownFormatError:
            print(file, "...", "SKIP (unknown subtitle format)")
        except pysubs.EncodingDetectionError:
            print(file, "...", "SKIP (character encoding autodetection failed)")
        except UnicodeDecodeError:
            print(file, "...", "ERROR (cannot open the file with selected "
                  "encoding '{}')".format(self.args.encoding))
        except pysubs.UnknownFPSError:
            print(file, "...", "SKIP (--fps omitted and file didn't declare "
                  "its framerate)".format(self.args.encoding))

    def process(self, subs, dest_path):
        if self.args.transform:
            subs.transform_framerate(*self.args.transform)
        if self.args.shift is not None:
            subs.shift(ms=int(self.args.shift))
        if self.styles_file:
            subs.update_styles(self.styles_file)
        if self.args.delete_attached:
            subs.fonts = OrderedDict()
        if self.attachments:
            subs.fonts.update(self.attachments)
        if self.args.undo_effects:
            subs.iter_callback(pysubs.effects.effect_undo)
        if self.args.apply_effects:
            subs.iter_callback(pysubs.effects.effect_template)

        try:
            subs.save(dest_path, self.args.output_encoding, self.args.fps)
            print(dest_path, "...", "OK")
        except IOError:
            print(dest_path, "...", "ERROR (cannot save the file)")
        except UnicodeEncodeError:
            print(dest_path, "...", "ERROR (some character(s) irrepresentable in '{}' "
                  "-- try Unicode)".format(self.args.output_encoding))
        except pysubs.MalformedFileError as e:
            print(dest_path, "...", "ERROR ({})".format(str(e)))
        
#-------------------------------------------------------------------------------
# commandline use

if __name__ == "__main__":
    main = PySubsCLI()
    main(sys.argv[1:])
