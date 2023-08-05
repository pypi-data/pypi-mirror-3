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
pysubs.subtitles module
=======================

This is PySubs' core module with SubStation-related classes. This module does
the bulk of work including import/export and subtitle manipulation.

PySubs can itself autodetect UTF-8/UTF-16 encoding via BOM. It can also
take advantage of the Universal Encoding Detector (chardet), when available.

Classes
-------
SSAFile: List-like class representing one SubStation subtitle file.
SSALine: Dict-like abstract class, subclassed by...
SSAEvent: A SubStation "Event" line (one subpicture).
SSAStyle: A SubStation "Style" line (style definition for "Event" lines).
SSAAttachment: Binary file encoded via SubStation uuencoding.

Functions
---------
resolve_format(): Work out subtitle file's format from its contents.

"""

import re, os, bisect, struct, array, sys
from collections import OrderedDict, MutableSequence, Mapping, Iterable

try:
    import chardet
except ImportError:
    chardet = None

from .misc import Color, Time, Vec2
from .exceptions import *
from .uuencoder import bin2ascii, ascii2bin

# ------------------------------------------------------------------------------

class SSAFile(MutableSequence):
    """
    A SubStation subtitle file.

    SSAFile provides list-like interface to its lines (the "events" attribute):

    >>> foo = SSAFile("foo.ass")
    >>> for line in foo:            # "line" is an SSAEvent instance
    ...     line.shift(s=1)         # this is what foo.shift(s=1) does
    >>> bar = foo[:15]              # list of SSAEvents, not an SSAFile
    >>> foo.sort()                  # sort lines by times
    
    Attributes:
        events: List of lines (SSAEvent).
        styles: Dict of styles (SSAStyle).
        info: Dict of metadata (str).
        fonts: Dict of attached fonts (SSAAttachment).
        _format: Format of last loaded subtitles, or None.

    Methods:
        SSAFile(): Optionally load from file.
        from_file(): Load subtitles from file.
        from_str(): Load subtitles from string.
        to_str(): Return string with subtitles in given format.
        save(): Save subtitles to file. (Note: It's called save() as it is
            somewhat the opposite of pysubs.load(), which is not an SSAFile
            method but an ordinary function.)

        shift(): Shift start and/or end of every line.
        transform_framerate(): Do a framerate transform, eg. 25 -> 23.976
            (this is for fixing frame-based subtitles already converted to
            time-based format with bad framerate assumed in the process;
            when loading SUB files directly, use the "fps" argument).

        iter_callback(): Run every line through callback function. iter_callback
            allows for safe addition/deletion of lines and may be used for
            making effects. See pysubs.effects module for more.

        update_styles(): Import styles from other SSAFile.
        rename_style(): Rename style in all lines.

        copy(): Return a shallow copy.

    Overloaded operators:
        == !=: Equality of two SSAFile objects.

    """

    _srt_parser = re.compile(r"^[ ]*(?P<Start>\d{1,2}:\d{2}:\d{2}[,.]\d{3})"  # start
                             r"[ ->]+"  # arrow
                             r"(?P<End>\d{1,2}:\d{2}:\d{2}[,.]\d{3})"  # end
                             "[^\n]*"  # skip rest of the timecode line
                             r"(?P<Text>.+?)"  # line contents
                             r"(?="  # expect next
                             "(?:^[ ]*\d+" "[ ]*$\n*)?" # optional line no.
                             r"^[ ]*\d{1,2}:\d{2}:\d{2}[,.]\d{3}"  # next subtitle start
                             r"|\Z)", re.MULTILINE | re.DOTALL)  # or end of file

    _sub_parser = re.compile(r"^\{(?P<Start>\d+)\}\{(?P<End>\d+)\}(?P<Text>.+)",
                             re.MULTILINE)

    default_info = {"WarpStyle": "0",
                    "PlayResX": "640",
                    "PlayResY": "480",
                    "ScaledBorderAndShadow": "yes"}

    # --------------------------------------------------------------------------
    # loading

    def __init__(self, file=None, encoding=None, fps=None):
        """
        Initialize, optionally from file.

        Arguments:
            file: Path to subtitle file (ASS/SSA/SRT/SUB).
            encoding: Character encoding. When omitted, BOM detection / chardet
                detection takes place.
            fps: Framerate (neccessary for SUB files if they don't provide
                this information on first line).

        Raises:
            IOError: Non-existent or unreadable file.
            UnicodeDecodeError: Cannot decode file with given encoding.
            EncodingDetectionError: Cannot autodetect encoding, please specify.
            UnknownFPSError: fps unspecified and SUB file didn't declare it.
            UnknownFormatError: Subtitle format could not be resolved.
        
        """
        self.events = []
        self.styles = OrderedDict()
        self.info = OrderedDict()
        self.fonts = OrderedDict()
        self._format = None
        self._fps = None

        if file:
            self.from_file(file, encoding, fps)
        else:
            self.info = self.default_info.copy()
            self.styles["Default"] = SSAStyle()

    def from_file(self, file, encoding=None, fps=None):
        """
        Read subtitles from file.

        Arguments:
            file: Path to subtitle file (ASS/SSA/SRT/SUB).
            encoding: Character encoding. When omitted, BOM detection / chardet
                detection takes place.
            fps: Framerate (neccessary for SUB files if they don't provide
                this information on their first line).

        Raises:
            IOError: Non-existent or unreadable file.
            UnicodeDecodeError: Cannot decode file with given encoding.
            EncodingDetectionError: Cannot autodetect encoding, please specify.
            UnknownFPSError: fps unspecified and SUB file didn't declare it.
            UnknownFormatError: Subtitle format could not be resolved.
        
        """
        self.file = file

        if not os.access(file, os.R_OK):
            raise IOError(
                "File '{}' doesn't exist or isn't readable.".format(file))

        if encoding:
            with open(file, encoding=encoding) as sub_file:
                data = sub_file.read()
        else:
            with open(file, mode="rb") as raw_file:
                raw_data = raw_file.read(8000)

            if raw_data.startswith(b"\xef\xbb\xbf"):
                encoding = "utf-8-sig"
            elif raw_data.startswith(b"\xfe\xff"):
                encoding = "utf-16-le"
            elif raw_data.startswith(b"\xff\xfe"):
                encoding = "utf-16-be"
            elif chardet:
                encoding = chardet.detect(raw_data)["encoding"]

            if encoding:
                with open(file, encoding=encoding) as sub_file:
                    data = sub_file.read()
            else:
                raise EncodingDetectionError(
                    "Encoding autodetection failed, use the 'encoding' arg.")

        self.from_str(data, fps)

    def from_str(self, data, fps=None):
        """
        Read subtitles from string.

        Arguments:
            data: str with subtitle file contents.
            fps: Framerate (neccessary for SUB files if they don't provide
                this information on their first line).

        Raises:
            UnknownFPSError: fps unspecified and SUB file didn't declare it.
            UnknownFormatError: Subtitle format could not be resolved.

        """
        format_ = self._format = resolve_format(data)

        if format_ in {"ass", "ssa"}:
            attachments = False
            
            for line in data.splitlines():
                if line.startswith(";"):
                    continue  # ignore script comments

                elif line.startswith("[Fonts]") or line.startswith("[Graphics]"):
                    attachments = True
                    break

                else:
                    try:
                        descriptor, fields = line.split(": ", 1)
                    except ValueError:
                        continue

                    if descriptor in {"Dialogue", "Comment", "Style"}:
                        if descriptor == "Style":
                            line_format = SSAStyle.line_format[format_]
                        else:
                            line_format = SSAEvent.line_format[format_]
                        fields = fields.split(",", len(line_format) - 1)
                        field_dict = {x:y for x, y in zip(line_format, fields)}
                        if descriptor == "Style":
                            new = SSAStyle.from_raw_fields(
                                format_=format_, **field_dict)
                            name = field_dict["Name"]
                            self.styles[name] = new
                        else:
                            field_dict["Type"] = descriptor
                            new = SSAEvent.from_raw_fields(
                                format_=format_, **field_dict)
                            self.events.append(new)

                    # Ignore Format lines. The standard defines them already
                    # and most tools, ie. VSFilter and Aegisub, will ignore
                    # them anyway, rendering any non-standard file virtually
                    # useless. See http://blog.aegisub.org/2008/07/universal-subtitle-format-post-mortem.html
                    elif descriptor == "Format":
                        pass

                    else:
                        self.info[descriptor] = fields

            if attachments:
                for match in re.finditer(
                        "^fontname: (?P<file>.+?)$(?P<data>[!-`\n ]+)",
                        data, re.MULTILINE):
                    content = SSAAttachment(match.group("data"))
                    self.fonts[match.group("file")] = content

        elif format_ == "srt":
            for subtitle in self._srt_parser.finditer(data):
                line = SSAEvent.from_raw_fields(
                    "srt", **subtitle.groupdict())
                self.events.append(line)

            self.info = self.default_info.copy()
            self.styles["Default"] = SSAStyle()

        elif format_ == "sub":
            discard_first_line = False
            if not fps:
                fps_match = re.match("\{[^}]*\}\{[^}]*\}([0-9.]+)", data)
                discard_first_line = True
                if fps_match:
                    fps = float(fps_match.group(1))
                else:
                    raise UnknownFPSError(
                        "SUB file doesn't declare fps, please specify")

            self._fps = fps

            for subtitle in self._sub_parser.finditer(data):
                line = SSAEvent.from_raw_fields(
                    "sub", fps=fps, **subtitle.groupdict())
                self.events.append(line)

            if discard_first_line:
                del self[0]
            self.info = self.default_info.copy()
            self.styles["Default"] = SSAStyle()

    # --------------------------------------------------------------------------
    # saving
    
    def to_str(self, format_="ass", fps=None):
        """
        Return string representation in some subtitle format.

        Arguments:
            format_: Desired output format: "ass"/"ssa"/"srt"/"sub"
            fps: Frame rate, mandatory for SUB format.

        Raises:
            UnknownFormatError: Wrong format_.
            UnknownFPSError: Unspecified fps.
            MalformedFileError: Some timestamps out of representable range.

        """

        output = []
        format_ = format_.lower()
        
        if format_ in {"ass", "ssa"}:
            output.append("[Script Info]\n; Script generated by PySubs")
            self.info["ScriptType"] = "v4.00" if format_ == "ssa" else "v4.00+"
            for key_value in self.info.items():
                output.append(": ".join(key_value))

            if format_ == "ssa":
                output.append("\n[V4 Styles]")
            else:
                output.append("\n[V4+ Styles]")
            format_line = SSAStyle.print_line_format(format_)
            output.append(format_line)
            for name, style in self.styles.items():
                style.name = name
                output.append(style.to_str(format_))

            output.append("\n[Events]")
            format_line = SSAEvent.print_line_format(format_)
            output.append(format_line)
            for line in self:
                output.append(line.to_str(format_))

            if self.fonts:
                output.append("\n[Fonts]")
                for name, font in self.fonts.items():
                    output.append("fontname: {}".format(name))
                    output.append(font.data)

            return "\n".join(output)

        elif format_ in {"srt", "sub"}:
            lines = self._merge_collisions()
            if not fps: fps = self._fps  # little hack -- fall back to
                                         # last known fps
            if format_ == "sub":
                fps = Time.sanitize_framerate(fps)
                output.append("{1}{1}" + str(fps))

            for i, line in enumerate(lines, 1):
                output.append(line.to_str(format_, fps=fps, line_no=i))

            if format_ == "srt":
                return "\n\n".join(output)
            else:
                return "\n".join(output)
            
        else:
            raise UnknownFormatError(
                "Unknown subtitle format: '{}'".format(format_))

    def save(self, file, encoding="utf-8-sig", fps=None):
        """
        Save subtitles to file in given format.

        Output format is resolved via file extension.

        Arguments:
            file: Path to output file (will be overwritten).
            encoding: Character encoding to use.
            fps: Frame rate, mandatory for SUB files.

        Raises:
            UnknownFormatError: Unsupported format (file extension).
            UnicodeEncodeError: Subtitles contain character(s) not representable
                in selected output charset.
            UnknownFPSError: fps unspecified when outputting SUB
            IOError: Error when writing the file.

        """
        format_ = os.path.splitext(file)[1][1:].lower()
        data = self.to_str(format_, fps)
        
        with open(file, "w", encoding=encoding) as subtitle_file:
            print(data, file=subtitle_file)

    def _merge_collisions(self):
        """Return sorted lines with merged overlaps."""
        
        lines = [line for line in self
                 if line.text and line.type == "Dialogue"]
        lines.sort()

        # Get all start/end times together and sort them. This gives us all
        # subtitle boundaries and intervals inbetween, which may be either empty
        # or with one or more lines visible.
        times = ({line.start for line in lines} |
                 {line.end for line in lines})
        times = list(times)
        times.sort()
        intervals = [list() for start_time in times]

        # Insert each line into all intervals it belongs to.
        for line in lines:
            time_idx = bisect.bisect_left(times, line.start)
            while time_idx < len(times) and times[time_idx] < line.end:
                intervals[time_idx].append(line)
                time_idx += 1

        output_lines = []

        # Create new, non-overlapping lines by merging lines in each interval,
        # newer lines stack on top of earlier ones. Any information beyond
        # times and line body is lost, so at least preserve style-level italics.
        # Note that this isn't much of an issue as the lines are to be used for
        # SRT/SUB export anyway.
        for start, end, lines in zip(times, times[1:], intervals):
            if lines:
                text = []
                for line in lines:
                    if self.styles[line.style].italic:
                        text.append("".join(["{\i1}", line["Text"], "{\i0}"]))
                    else:
                        text.append(line.text)

                output = SSAEvent()
                output.start = start
                output.end = end
                output.text = r"\N".join(reversed(text))
                output_lines.append(output)

        return output_lines

    # --------------------------------------------------------------------------
    # manipulation

    def shift(self, ms=0, s=0, m=0, h=0, frame=None, fps=None,
              start=True, end=True):
        """
        Shift all subtitles by given time.

        Arguments:
            s, ms, m, h: Number of seconds etc. to shift by. Negative values
                mean backward shift, positive are forward.
            frame, fps: Shift by given number of frames in given framerate.
                Framerate may be a float or a string alias (eg. "pal").
            start: Shift subtitles' start times (default: True).
            end: Shift subtitles' end times (default: True).

        Raises:
            UnknownFPSError: fps specified, but alias is unknown
        
        """
        for line in self:
            line.shift(s=s, ms=ms, m=m, h=h, frame=frame, fps=fps,
                       start=start, end=end)

    def transform_framerate(self, in_fps, out_fps):
        """
        Transform times by ratio of two framerates, eg. 23.976 / 29.97.

        This is for fixing time-based subtitles poorly converted from
        frame-based format, ie. with bad framerate assumption. in_fps is
        the (wrong) assumed framerate, while out_fps is the actual (good)
        framerate.
        
        Note that this function isn't needed when dealing with frame-based
        subtitles directly; use the fps argument when loading them instead.

        Arguments:
            in_fps: The numerator (eg. "ntsc_film" or 23.976).
            out_fps: The denominator (eg. "ntsc_video" or 29.97).

        UnknownFPSError: unknown fps alias
        ValueError: non-positive fps
        
        """

        in_fps = Time.sanitize_framerate(in_fps)
        out_fps = Time.sanitize_framerate(out_fps)
        ratio = in_fps / out_fps

        for line in self:
            line.start *= ratio
            line.end *= ratio

    def update_styles(self, other, overwrite=True):
        """
        Merge in styles from other SSAFile.

        Arguments:
            other: SSAFile with styles we want to get.
            overwrite: Overwrite on name conflict (default: True).

        Raises:
            TypeError: other was not an SSAFile.
        
        """

        if not isinstance(other, SSAFile):
            raise TypeError("Must supply an SSAFile")

        if overwrite:
            self.styles.update(other.styles)
        else:
            tmp = other.styles.copy()
            tmp.update(self.styles)
            self.styles = tmp

    def rename_style(self, old, new):
        """
        Rename style in SSAFile.styles and in all lines.

        If "new" is name of already existing style, it will be overwritten.

        Arguments:
            name: Style's old name.
            new: Style's new name.

        Raises:
            KeyError: Style not found.
            ValueError: Illegal name.
        
        """
        if not old in self.styles:
            raise KeyError("Style '{}' not found.".format(old))
        elif "," in new:
            raise ValueError("New name cannot have ',' in it.")

        self.styles[new] = self.styles[old]
        self.styles[new]["Name"] = new
        del self.styles[old]
        
        for line in self:
            if line["Style"] == old:
                line["Style"] = new

    def iter_callback(self, callback_function, **kwargs):
        """
        Run every line through callback function, replacing it with line(s)
        the function returns, or deleting it if it returns None.

        Arguments:
            callback_function: Function applied to every line
                (see signature below).
            **kwargs: Optional keyword arguments for callback_function.

        Callback function signature:
            f(SSAFile_obj, line, **kwargs)
                -> None
                -> SSAEvent
                -> iterable (eg. list) of SSAEvents

        Raises:
            ValueError: Callback function isn't callable (oops!).
            TypeError: Callback function doesn't abide by the signature above.
            
        """
        if not callable(callback_function):
            raise ValueError("Callback function not callable.")

        new_lines = []
        for line in self:
            output = callback_function(self, line, **kwargs)
            
            if output is None:
                continue
            elif isinstance(output, SSAEvent):
                new_lines.append(output)
            elif (output and isinstance(output, Iterable) and
                  all(map(lambda x: isinstance(x, SSAEvent), output))):
                new_lines.extend(output)
            else:
                raise TypeError(
                    "Callback returned invalid value: '{}'.".format(output))

        self.events = new_lines

    # --------------------------------------------------------------------------
    # misc

    def __str__(self):
        events = self.events[:]
        events.sort()
        lines = [str(line) for line in events
                 if line["Type"] == "Dialogue" and line["Text"]]
        return "\n".join(lines)

    def __eq__(self, other):
        if isinstance(other, SSAFile):
            info1 = dict(self.info.items()); info1["ScriptType"] = None
            info2 = dict(other.info.items()); info2["ScriptType"] = None
            metadata = info1 == info2
            styles = dict(self.styles.items()) == dict(other.styles.items())
            lines = all(map(lambda x, y: x._data == y._data, self, other))
            fonts = dict(self.fonts.items()) == dict(other.fonts.items())

            return metadata and styles and lines and fonts
        else:
            return NotImplemented

    def __neq__(self, other):
        return not self == other

    def __copy__(self):
        new = SSAFile()
        new.info = self.info.copy()
        new.styles = self.styles.copy()
        new.fonts = self.fonts.copy()
        new.events = [line.copy() for line in self]

        return new

    copy = __copy__

    # --------------------------------------------------------------------------
    # inherited from MutableSequence

    def __len__(self):
        return len(self.events)

    def insert(self, index, value):
        if isinstance(value, SSAEvent):
            self.events.insert(index, value)
        else:
            raise TypeError("Only SSAEvent objects may be inserted.")

    def __getitem__(self, index):
        return self.events[index]

    def __setitem__(self, index, value):
        if isinstance(value, SSAEvent):
            self.events[index] = value
        else:
            raise TypeError("Only SSAEvent objects may be inserted.")

    def __delitem__(self, index):
        del self.events[index]

# ------------------------------------------------------------------------------

class SSALine(Mapping):
    """
    Base class for SSAEvent and SSAStyle implementations.

    Behaves like a dictionary with default values and restricted access.
    Keys may not be added or deleted and assigned values are type-checked
    on assignment.

    It is also possible to access the dictionary via instance attributes,
    eg. for SSAEvent instance foo, foo["Text"] and foo.text are equivalent
    for reading and writing (deletion is forbidden either way). Note the slight
    difference: while the actual key in the dictionary is indeed "Text",
    access via attributes is not case sensitive (ie. foo.text is fine).

    Attributes:
        _data: Dict with line contents. It is usually accessed using
            subscription operator [] or via instance attributes, not directly.

    Class attributes:
        default_data: Default line contents.
        line_format: Names of columns as defined by SSA (ASS) specification.
            Note that non-standard line formats are not supported. (read-only)

    Methods:
        copy(): Return a shallow copy of the line.

    Class methods:
        print_line_format(): Return the format line, eg. "Format: Layer, ...".

    """

    default_data = None
    line_format = None

    def __init__(self):
        raise NotImplementedError("This is an abstract class.")

    @classmethod
    def print_line_format(cls, format_):
        fields = ", ".join(cls.line_format[format_])
        return ": ".join(["Format", fields])

    def __copy__(self):
        new = type(self)()  # new instance of our class
        new._data = self._data.copy()
        return new

    copy = __copy__

    def __getattr__(self, name):
        name = name.capitalize()
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                "No field named '{}'".format(name))

    def __setattr__(self, name, val):
        if name in {"_data", "default_data"}:
            object.__setattr__(self, name, val)
        else:
            name = name.capitalize()
            try:
                self[name] = val
            except (KeyError, TypeError) as e:
                if isinstance(e, KeyError):
                    raise AttributeError(
                        "No field named '{}'".format(name))
                else:
                    raise

    def __getitem__(self, key):
        key = key.capitalize()
        if key in self._data:
            return self._data[key]
        else:
            raise KeyError("No field named '{}'".format(key))

    def __setitem__(self, key, val):
        key = key.capitalize()
        if not key in self._data:
            raise KeyError("No field named '{}'.".format(key))
        else:
            if not isinstance(val, type(self._data[key])):
                raise TypeError("Wrong datatype for this field.")
            else:
                self._data[key] = val

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self.default_data)

# ------------------------------------------------------------------------------

class SSAEvent(SSALine):
    r"""
    An Event line per SSA specification -- one subpicture.

    See SubStation Alpha spec or Aegisub manual for more information on what
    the attributes, which are mostly SSA Event line fields, mean.

    Attributes:
        start: Line's start time (Time instance).
        end: Line's end time (Time instance).
        text: Line's content (str; text & SSA override tags).
        plaintext: Get line content stripped of SSA tags (str; read-only).
        marked: Obsolete (bool).
        layer: Layer number (non-negative int).
        style: Ought to be a key in SSAFile.styles in some SSAFile the line
            belongs to. Note that styles and lines are not directly bound, eg.
            renaming a style in SSAFile.styles does not update its name in
            associated lines. This is what SSAFile.rename_style() is for. (str)
        name: Character's name (str).
        MarginL, MarginR, MarginV: Left, right and vertical margins
            (non-negative int).
        effect: SSA effect field (str).
        type: SSA Event type ("Dialogue" or "Comment"), see also
            SSAEvent.comment(), SSAEvent.uncomment().
    
    Methods:
        SSAEvent(): Create an SSAEvent without any conversion of input fields.
            This is what you want to use when creating lines yourself.
        to_str(): Get string representation in various formats.
        shift(): Shift line's start/end times.
        get_pos(): Work out subtitle's position (so that setting \pos to these
            coordinates would do nothing).
        set_pos(): Set line's position via \pos.
        comment(): Set line type to "Comment".
        uncomment(): Set line type to "Dialogue".

    Static methods:
        from_raw_fields(): Create an SSAEvent with appropriate conversion of
            input fields for given format. This is mainly for implementation
            of SSAFile.
        decode_tags(): Convert override tags to SubStation.
        encode_tags(): Convert SubStation override tags to some format.

    Overloaded operators:
        == != > >= < <=: Relation of two SSAEvents with respect to their start
            and end times. Note this is not like SSAStyle, where == != mean
            (non)equality and other relations are not defined. To compare
            equality of two SSAEvents, one must compare their _data
            attributes.

    """

    default_data = {"Start": Time(),
                    "End": Time(),
                    "Text": "",
                    "Marked": False,      # SSA only
                    "Layer": 0,           # ASS only
                    "Style": "Default",
                    "Name": "",
                    "MarginL": 0,
                    "MarginR": 0,
                    "MarginV": 0,
                    "Effect": "",
                    "Type": "Dialogue"}

    line_format = {"ass": ("Layer", "Start", "End", "Style", "Name",
                           "MarginL", "MarginR", "MarginV", "Effect", "Text"),
                   "ssa": ("Marked", "Start", "End", "Style", "Name",
                           "MarginL", "MarginR", "MarginV", "Effect", "Text")}


    def __init__(self, **fields):
        """
        Create new SSAEvent.

        This constructor is to be given 'polished' data -- that is, it doesn't
        do any conversion itself. If you provide a 'Text' field, make sure it
        is a proper ASS line, else output will get corrupted. There is a factory
        method from_raw_fields(), intended mostly for internal use, that does
        convert the fields.

        Arguments:
            **fields: SubStation fields, eg. 'Text', 'Style', 'MarginR' etc.
                They are case sensitive. Omitted fields will be filled from
                SSAEvent.default_data.

        Returns:
            An SSAEvent.

        Raises:
            KeyError: Non-existing field.
            TypeError: Wrong datatype for some field.
        
        """
        self._data = {key.capitalize(): data for key, data
                      in self.default_data.items()}
        for key, value in fields.items():
            self[key] = value

    def to_str(self, format_, fps=None, line_no=1):
        """
        Output a subtitle in given format.

        Arguments:
            format_: ass/ssa/srt/sub
            fps: Video framerate, mandatory for SUB format.
            line_no: Only applies to SRT -- printed line number.

        Returns:
            String representation in given format.

        Raises:
            MalformedFileError: Timestamp out of representable range
                (SubStation/SRT only).
        """
        print_dict = self._data.copy()
        print_dict["Text"] = self.encode_tags(self["Text"], format_)

        try:
            for time in ("Start", "End"):
                print_dict[time] = self[time].to_str(format_, fps)
        except OverflowError as e:
            raise MalformedFileError(str(e))

        if format_ in {"ass", "ssa"}:
            for margin in ("MarginL", "MarginR", "MarginV"):
                print_dict[margin] = str(self[margin]).zfill(4)
            if format_ == "ssa":
                print_dict["Marked"] = "Marked={}".format(int(self["Marked"]))
            else:
                print_dict["Layer"] = str(self["Layer"])

            fields = [print_dict[field] for field in self.line_format[format_]]
            fields = ",".join(fields)
            line = ": ".join([self["Type"], fields])
            return line

        elif format_ == "srt":
            print_dict["N"] = str(line_no)
            return "{N}\n{Start} --> {End}\n{Text}".format(**print_dict)

        elif format_ == "sub":
            return "".join(["{", print_dict["Start"], "}",
                            "{", print_dict["End"], "}",
                            print_dict["Text"]])

        else:
            raise ValueError("Unknown subtitle format: '{}'".format(format_))

    @staticmethod
    def from_raw_fields(format_, fps=None, **fields):
        """
        Create an SSAEvent from raw field strings.

        Arguments:
            format_: Subtitle format (ass/ssa/srt/sub).
            fps: Required for SUB format, framerate to use for conversion
                of timestamps.
            **fields: SubStation fields, eg. 'Text', 'Style', 'MarginR' etc.
                They are case sensitive. Omitted fields will be filled from
                SSAEvent.default_data.

        Returns:
            An SSAEvent.

        Raises:
            KeyError: Non-existing field.
            TypeError: Wrong datatype for some field.
            ValueError: Cannot interpret some field.

        """
        new_line = SSAEvent()
        
        if "Text" in fields:
            new_line["Text"] = SSAEvent.decode_tags(fields["Text"].strip(), format_)

        if format_ == "sub":
            for time in ("Start", "End"):
                if time in fields:
                    new_line[time] = Time(frame=int(fields[time]), fps=fps)
        else:
            for time in ("Start", "End"):
                if time in fields:
                    new_line[time] = Time(fields[time])

        for string in ("Style", "Name", "Effect", "Type"):
            if string in fields:
                new_line[string] = fields[string]

        for integer in ("Layer", "MarginL", "MarginR", "MarginV"):
            if integer in fields:
                new_line[integer] = int(fields[integer])

        if "Marked" in fields:
            new_line["Marked"] = fields["Marked"].endswith("1")

        return new_line

    @staticmethod
    def decode_tags(text, format_):
        """
        Read line body and return ASS equivalent. (SSA is passed through.)

        SRT features:
            - <b>, <i>, <u>, <s> tags
            - <font> tag with 'color' and/or 'face' argument
            - unknown tags are commented out via {...}

        SUB features:
            - global {Y:[ius]+} tag
            - newline-terminated {y:[ius]+} tag
            - unknown tags are left alone

        Arguments:
            text: Line body.
            format_: Subtitle format (ass/ssa/srt/sub)

        Returns:
            ASS 'Text' field.

        """
        if format_ in {"ass", "ssa"}:
            return text
        
        elif format_ == "srt":
            def font_replace(match):
                ass_tags = []
                html_tags = re.finditer(
                    r"""(?P<tag>\w+) *= *(?P<q>["'])?(?P<val>(?(q)[^"']+|[^ ]+))""",
                    match.group(1))
                
                for match in html_tags:
                    tag = match.group("tag").lower()
                    val = match.group("val")
                    
                    if tag == "face":
                        ass_tags.append(r"\fn{}".format(val))
                    elif tag == "color":
                        try:
                            color = Color(string=val)
                            ass_tags.append(r"\c{:ass_rgb}".format(color))
                        except ValueError:
                            pass
                        
                if ass_tags:
                    ass_tags.insert(0, "{")
                    ass_tags.append("}")
                return "".join(ass_tags)

            trans = [(r"< *([ibus]) *>", r"{\\\g<1>1}"),
                     (r"< */ *([ibus]) *>", r"{\\\g<1>0}"),
                     (r"< *font ([^>]+)>", font_replace),
                     (r"< */ *font *>", r"{\\r}"),
                     ("\n", r"\N"),
                     (r"<[^>]+>", "{\g<0>}")]  # hide unknown tags

            for pattern, repl in trans:
                text = re.sub(pattern, repl, text)
            return text

        elif format_ == "sub":
            def tags_replace(match):
                tags = match.group("tags")
                text = match.group("text")
                start, end = [], []
                for tag in tags:
                    start.append("\{}1".format(tag))
                    end.append("\{}0".format(tag))
                return "".join(["{", "".join(start), "}", text,
                                "{", "".join(end), "}"])
                
            text = re.sub(r"^\{Y:(?P<tags>[iub]+)\}(?P<text>.+)",
                          tags_replace, text)
            text = re.sub(r"\{y:(?P<tags>[iub]+)\}(?P<text>.+?)(?=[|]|$)",
                          tags_replace, text)
            text = text.replace("|", r"\N")
            return text
        
        else:
            raise ValueError("Unknown subtitle format: '{}'".format(format_))

    @staticmethod
    def encode_tags(text, format_):
        """
        Transform ASS line to other format. (SSA is passed through.)

        SRT features:
            - <i> tag

        SUB features:
            - global {Y:i} tag (somewhat hacky)

        Arguments:
            text: ASS 'Text' field.
            format_: Subtitle format (ass/ssa/srt/sub).

        Returns:
            Line body in given format.

        """
        if format_ in {"ass", "ssa"}:
            return text
        
        elif format_ == "srt":
            text = re.sub(r"\{[^}]*\\i1[^}]*\}", "<i>", text)  # italic
            text = re.sub(r"\{[^}]*\\i0[^}]*\}", "</i>", text)
            if text.rfind("<i>") > text.rfind("</i>"):
                text = "".join([text, "</i>"])
            text = re.sub(r" *(?:\\[Nn])+ *", "\n", text)  # newlines
            text = text.replace(r"\h", " ")                # hard spaces
            text = re.sub(r"\{[^}]*\}", "", text)          # clear ASS tags
            return text.rstrip()
        
        elif format_ == "sub":
            # This isn't really correct, but...
            all_italic = text.startswith(r"{\i1}") and text.endswith(r"{\i0}")
            text = re.sub(r"\{[^}]*\}", "", text)
            text = re.sub(r" *(?:\\[Nn])+ *", "|", text)
            text = text.replace(r"\h", " ")
            if all_italic:
                text = "".join(["{Y:i}", text])
            return text.rstrip()
        else:
            raise ValueError("Unknown subtitle format: '{}'".format(format_))

    # --------------------------------------------------------------------------
    # manipulation

    def shift(self, s=0, ms=0, m=0, h=0, frame=None, fps=None,
              start=True, end=True):
        """
        Shift times by given amount.

        Arguments:
            s, ms, m, h: Number of seconds etc. to shift by. Negative values
                mean backward shift, positive are forward.
            frame, fps: Shift by given number of frames in given framerate.
                Framerate may be a float or a string alias (eg. "pal").
            start: Shift subtitles' start times (default: True).
            end: Shift subtitles' end times (default: True).
        
        """
        if frame is not None and fps is not None:
            delta = Time(frame=frame, fps=fps)
        else:
            delta = Time(h=h, m=m, s=s, ms=ms)

        if start:
            self["Start"] += delta
            if self["Start"] < Time():
                self["Start"] = Time()

        if end:
            self["End"] += delta
            if self["End"] < Time():
                self["End"] = Time()

    def get_pos(self, SSAFile_obj):
        """
        Return Vec2 with line anchor point's coordinates.

        This is a function of video frame dimensions, style and line
        margins and inline override tags. Please note that because of this,
        the guess may not be accurate, as we don't know the actual dimensions
        of the line as it is rendered. Eg. a long line aligned to
        {\an2} with big MarginR will return

            (video_w / 2, video_h - max(style_MarginV, MarginV))

        while the subtitle is actually more to the left because of the margin.

        The coordinates are standard ASS coordinates with origin in the
        top left corner of the frame.

        Arguments:
            SSAFile_obj: SSAFile instance in which the subtitle lies -- needed
                for reading frame dimensions and line's style.

        Returns:
            Vec2 with line coordinates.

        Raises:
            KeyError: Cannot get required info from the SSAFile.

        """

        try:
            style = SSAFile_obj.styles[self["Style"]]
        except KeyError:
            raise KeyError("Style '{}' is not defined".format(self["Style"]))
        
        try:
            W = int(SSAFile_obj.info["PlayResX"])
            H = int(SSAFile_obj.info["PlayResY"])
        except KeyError:
            raise KeyError("Cannot get video dimensions from [Script Info]")
                
        # override position with inline tag (if present)
        pos = re.search(r"[{][^}]*\pos[(](?P<x>[0-9.]+), *(?P<y>[0-9.]+)",
                        self["Text"])
        if pos:
            return Vec2(float(pos.group("x")), float(pos.group("y")))

        # override style alignment with inline tag (if present)
        align = re.match(r"[{][^}]*\an(\d)[^}]*[}]", self["Text"])
        align = int(align.group(1)) if align else style["Alignment"]
            
        L_M = max((style["MarginL"], self["MarginL"]))
        R_M = max((style["MarginR"], self["MarginR"]))
        V_M = max((style["MarginV"], self["MarginV"]))

        if align in (2, 5, 8):
            X = W / 2
        elif align in (1, 4, 7):
            X = L_M
        else:
            X = W - R_M

        if align in (4, 5, 6):
            Y = H / 2
        elif align in (7, 8, 9):
            Y = V_M
        else:
            Y = H - V_M

        return Vec2(X, Y)

    def set_pos(self, x=0, y=0):
        """
        Inserts new {\pos(x,y)} tag and clears any previous ones.

        Arguments:
            x, y: New coordinates.
        
        """
        text = self.text
        text = re.sub(r"\\pos[(][0-9.]+,[0-9.]+[)]", "", text)
        text = text.replace("{}", "")
        self.text = "".join(["{", "\pos({:.1f},{:.1f})".format(x, y), "}", text])

    def comment(self):
        """Comment the line out"""
        self["Type"] = "Comment"

    def uncomment(self):
        """Uncomment the line"""
        self["Type"] = "Dialogue"

    # --------------------------------------------------------------------------
    # properties

    @property
    def plaintext(self):
        r"""Return line stripped of SSA tags and start/end whitespace."""
        plaintext = re.sub(r"\{[^}]*\}", "", self._data["Text"])
        plaintext = plaintext.replace(r"\h", " ")
        plaintext = plaintext.replace(r"\n", "\n")
        plaintext = plaintext.replace(r"\N", "\n")
        return plaintext.strip()

    # --------------------------------------------------------------------------
    # misc

    def __str__(self):
        text = self.plaintext.replace("\n", " ")
        if self["Name"]:
            return "{} - {}: ({}) {}".format(self["Start"], self["End"],
                                             self["Name"], text)
        else:
            return "{} - {}: {}".format(self["Start"], self["End"], text)

    # --------------------------------------------------------------------------
    # relations

    def __lt__(self, other):
        if isinstance(other, SSAEvent):
            if self["Start"] != other["Start"]:
                return self["Start"] < other["Start"]
            else:
                return self["End"] < other["End"]
        else:
            return NotImplemented

    def __le__(self, other):
        return self == other or self < other

    def __eq__(self, other):
        if isinstance(other, SSAEvent):
            return (self["Start"] == other["Start"] and
                    self["End"] == other["End"])
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __ge__(self, other):
        return not self < other

    def __gt__(self, other):
        return not self <= other
        
# ------------------------------------------------------------------------------

class SSAStyle(SSALine):
    """
    A Style line per SSA specification.

    See SubStation Alpha spec or Aegisub manual for more information on what
    the attributes, which are SSA Style line fields, mean.

    Attributes:
        Name, Fontname: str
        BorderStyle, Encoding, MarginL, MarginR, MarginV,
            Alignment: non-negative int
        Bold, Italic, Underline, StrikeOut: bool
        Fontsize, ScaleX, ScaleY, Spacing, Angle, Outline, Shadow: float
        PrimaryColour, SecondaryColour, TertiaryColour, OutlineColour,
            BackColour: Color instance
    
    Methods:
        SSAStyle(): Create an SSAStyle without any conversion of input fields.
        to_str(): Get string representation in ASS/SSA format.

    Static methods:
        from_raw_fields(): Create an SSAEvent with appropriate conversion of
            input fields for given format. This is mainly for implementation
            of SSAFile.

    Overloaded operators:
        == !=: Equality of two SSAStyles, save the Name attribute, which should
            be avoided anyway as its function is delegated to SSAFile.styles
            and it has no effect itself.

    """

    default_data = {"Name": "Default",
                    "Fontname": "Arial",
                    "Fontsize": 20.0,
                    "PrimaryColour": Color(255, 255, 255),  # SSA has no alpha
                    "SecondaryColour": Color(255, 0, 0),    # in those, and
                    "OutlineColour":  Color(0, 0, 0),       # OutlineColour is
                    "BackColour":  Color(0, 0, 0),          # Tertiary~ in SSA
                    "Bold": False,
                    "Italic": False,
                    "Underline": False, # ASS only
                    "StrikeOut": False, # ASS only
                    "ScaleX": 100.0,    # ASS only
                    "ScaleY": 100.0,    # ASS only
                    "Spacing": 0.0,     # ASS only
                    "Angle": 0.0,       # ASS only
                    "BorderStyle": 1,
                    "Outline": 2.0,
                    "Shadow": 2.0,
                    "Alignment": 2,     # ASS semantics, SSA is different
                    "MarginL": 10,
                    "MarginR": 10,
                    "MarginV": 10,
                    "AlphaLevel": 0,    # unused in SSA, not present in ASS...
                    "Encoding": 1}

    line_format = {"ass": ("Name", "Fontname", "Fontsize", "PrimaryColour",
                           "SecondaryColour", "OutlineColour", "BackColour",
                           "Bold", "Italic", "Underline", "StrikeOut",
                           "ScaleX", "ScaleY", "Spacing", "Angle",
                           "BorderStyle", "Outline", "Shadow",
                           "Alignment", "MarginL", "MarginR", "MarginV",
                           "Encoding"),
                   "ssa": ("Name", "Fontname", "Fontsize", "PrimaryColour",
                           "SecondaryColour", "TertiaryColour", "BackColour",
                           "Bold", "Italic",
                           "BorderStyle", "Outline", "Shadow",
                           "Alignment", "MarginL", "MarginR", "MarginV",
                           "AlphaLevel", "Encoding")}

    SSA_alignment = (1, 2, 3, 9, 10, 11, 5, 6, 7)

    def __init__(self, **fields):
        """
        Create new SSAStyle.

        This constructor is to be given 'polished' data -- that is, it doesn't
        do any conversion itself. There is a factory method from_raw_fields(),
        intended mostly for internal use, that does convert the fields.

        Arguments:
            **fields: SubStation fields, eg. 'Bold', 'Fontname',
                'PrimaryColour' etc. They are case sensitive.
                Omitted fields will be filled from SSAStyle.default_data.

        Returns:
            An SSAStyle.

        Raises:
            KeyError: Non-existing field.
            TypeError: Wrong datatype for some field.
        
        """

        self._data = {key.capitalize(): data for key, data
                      in self.default_data.items()}
        for key, value in fields.items():
            self[key] = value

    @staticmethod
    def from_raw_fields(format_, **fields):
        """
        Create an SSAStyle from raw field strings.

        Arguments:
            format_: SubStation format (ass/ssa).
            **fields: SubStation fields, eg. 'Bold', 'Fontname',
                'PrimaryColour' etc. They are case sensitive.
                Omitted fields will be filled from SSAStyle.default_data.

        Returns:
            An SSAStyle.

        Raises:
            KeyError: Non-existing field.
            TypeError: Wrong datatype for some field.
            ValueError: Cannot interpret some field.

        """

        new_line = SSAStyle()

        if "Alignment" in fields:
            alignment = int(fields["Alignment"])
            if format_ == "ssa":
                alignment = SSAStyle.SSA_alignment.index(alignment) + 1
            new_line["Alignment"] = alignment

        if "TertiaryColour" in fields:
            new_line["OutlineColour"] = Color(string=fields["TertiaryColour"])

        for string in {"Name", "Fontname"}:
            if string in fields:
                new_line[string] = fields[string]

        for integer in {"BorderStyle", "Encoding",
                        "MarginL", "MarginR", "MarginV"}:
            if integer in fields:
                new_line[integer] = int(fields[integer])

        for boolean in {"Bold", "Italic", "Underline", "StrikeOut"}:
            if boolean in fields:
                new_line[boolean] = fields[boolean] != "0"

        for fp in {"Fontsize", "ScaleX", "ScaleY",
                   "Spacing", "Angle", "Outline", "Shadow"}:
            if fp in fields:
                new_line[fp] = float(fields[fp])

        for color in {"PrimaryColour", "SecondaryColour",
                      "OutlineColour", "BackColour"}:
            if color in fields:
                new_line[color] = Color(string=fields[color])

        return new_line

    def to_str(self, format_):
        """
        Return string representation in ASS/SSA format.

        Arguments:
            format_: "ssa"/"ass"
            
        """
        print_dict = self._data.copy()

        for integer in {"BorderStyle", "Encoding", "AlphaLevel",
                        "MarginL", "MarginR", "MarginV"}:
            print_dict[integer] = str(self[integer])

        for fp in {"Fontsize", "ScaleX", "ScaleY",
                   "Spacing", "Angle", "Outline", "Shadow"}:
            print_dict[fp] = "{:.3g}".format(self[fp])

        for boolean in {"Bold", "Italic", "Underline", "StrikeOut"}:
            print_dict[boolean] = str(-1 * self[boolean])

        for color in {"PrimaryColour", "SecondaryColour",
                      "OutlineColour", "BackColour"}:
            print_dict[color] = self[color].to_str(format_)

        if format_ == "ssa":
            print_dict["TertiaryColour"] = print_dict["OutlineColour"]
            align = self["Alignment"]
            print_dict["Alignment"] = str(self.SSA_alignment[align - 1])
        else:
            print_dict["Alignment"] = str(self["Alignment"])

        fields = [print_dict[field] for field in self.line_format[format_]]
        fields = ",".join(fields)
        line = ": ".join(["Style", fields])
        return line

    # --------------------------------------------------------------------------
    # misc
    
    def __eq__(self, other):
        if isinstance(other, SSAStyle):
            keys = self.default_data.keys() - frozenset("Name")
            return all(
                map(lambda key: self[key] == other[key], keys))
        else:
            return NotImplemented

    def __neq__(self, other):
        return not self == other

# ------------------------------------------------------------------------------

class SSAAttachment:
    """
    Wrapper for binary files encoded via SubStation uuencoding.

    SSA files may embed TrueType fonts or graphics. Annex B of SSA specification
    defines bin->ascii encoder to do this, as SSA is a text-based format.

    Attributes:
        data: str with encoded binary data.

    Methods:
        SSAAttachment(): Init from binary file, bytes or already encoded str.
        from_file(): Encode binary file.
        from_bytes(): Encode bytes/bytearray.
        from_str(): Load already encoded data.
        to_bytes(): Decode data.
        to_file(): Decode data to binary file.
    
    """

    def __init__(self, data=None, file=None):
        """
        There are three ways to create an SSAAttachment:
        
            1. from binary file, specified via 'file'
            2. from bytes/bytearray, specified via 'data'
            3. from str of already encoded bytes via 'data'
            
        Arguments:
            data: Either raw 'bytes' of the file, or already encoded 'str'.
            file: Path to binary file to be loaded.
        
        """
        if file is None and data is None:
            return
        elif isinstance(file, str):
            self.from_file(file)
        elif isinstance(data, str):
            self.from_str(data)
        elif isinstance(data, (bytes, bytearray)):
            self.from_bytes(data)
        else:
            raise TypeError

    def from_file(self, file):
        """Encode binary file"""
        with open(file, "rb") as binfile:
            data = binfile.read()

        self.from_bytes(data)

    def from_bytes(self, data):
        """Encode bytes/bytearray"""
        if isinstance(data, (bytes, bytearray)):
            self.data = bin2ascii(data)
        else:
            raise TypeError("'data' must be bytes/bytearray")

    def from_str(self, data):
        """Load already encoded data"""
        if isinstance(data, str):
            self.data = data.strip()
        else:
            raise TypeError("'data' must be str")

    def to_file(self, file):
        """Decode data, then write to binary file"""
        data = self.to_bytes()
        with open(file, "wb") as binfile:
            print(data, file=binfile)

    def to_bytes(self):
        """Decode data"""
        return ascii2bin(self.data)

# ------------------------------------------------------------------------------

def resolve_format(data):
    """
    Return subtitles' format.

    Arguments:
        data: Subtitle file contents.

    Returns:
        "ass", "ssa", "srt" or "sub" string.

    Raises:
        UnknownFormatError: Not an ASS/SSA/SRT/SUB file.
    
    """
    # don't use startswith() because of potential BOM / whitespace
    if "[Script" in data[:32]:
        return "ass" if "[V4+" in data[:2048] else "ssa"
    elif re.search(r"\d{1,2}:\d{2}:\d{2}[,.]\d{3}"
                   r"[ ->]+"
                   r"\d{1,2}:\d{2}:\d{2}[,.]\d{3}",
                   data[:64]):
        return "srt"
    elif "{" in data[:8]:
        return "sub"
    else:
        raise UnknownFormatError("Subtitle format could not be resolved")
