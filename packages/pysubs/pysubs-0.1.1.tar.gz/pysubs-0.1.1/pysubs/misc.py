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
pysubs.misc module
==================

Minor code for handling time, colors and 2-dimensional vectors.

Classes
-------
Color: An 8-bit RGBA color.
Time: Positive or negative time value with millisecond precision.
Vec2: Simple Euclidean vector class, meant for use with pysubs.effects.

"""

import re, math
from collections import namedtuple
from .exceptions import UnknownFPSError

# ------------------------------------------------------------------------------

isnumber = lambda n: isinstance(n, (int, float))

# ------------------------------------------------------------------------------

_Color = namedtuple("Color", "r g b a")

class Color(_Color):
    """
    An 8-bit RGBA color. Based on namedtuple.

    Attributes:
        r, g, b, a: color channels with values in range(256)
        NAMED_COLORS: 16 basic HTML colors, see
            http://www.w3.org/TR/html4/types.html#h-6.5

    Methods:
        Color(): Initialize from <0;256) integers or a string (eg. "#ff0000").
        to_str(): Get various string representations.
        
    
    """
    NAMED_COLORS = {"black": (0,0,0),
                    "silver": (192,192,192), 
                    "gray": (128,128,128), 
                    "white": (255,255,255), 
                    "maroon": (128,0,0), 
                    "red": (255,0,0), 
                    "purple": (128,0,128), 
                    "fuchsia": (255,0,255), 
                    "green": (0,128,0), 
                    "lime": (0,255,0), 
                    "olive": (128,128,0), 
                    "yellow": (255,255,0), 
                    "navy": (0,0,128), 
                    "blue": (0,0,255), 
                    "teal": (0,128,128), 
                    "aqua": (0,255,255)}

    _re_patterns = (
        re.compile(r"&H(?P<a>[0-9a-fA-F]{2})?(?P<b>[0-9a-fA-F]{2})"   # ASS
                   r"(?P<g>[0-9a-fA-F]{2})(?P<r>[0-9a-fA-F]{2})&?$"),
        re.compile(r"\#(?P<r>[0-9a-fA-F]{2})"                         # SRT
                   r"(?P<g>[0-9a-fA-F]{2})(?P<b>[0-9a-fA-F]{2})$"),
        re.compile(r"\$(?P<b>[0-9a-fA-F]{2})"                         # SUB
                   r"(?P<g>[0-9a-fA-F]{2})(?P<r>[0-9a-fA-F]{2})$"))

    # --------------------------------------------------------------------------
    # initialization

    def __new__(cls, r=0, g=0, b=0, a=0, string=None):
        """
        Initialize from numbers or string.

        Arguments:
            r, g, b, a: R/G/B/A channel values, numbers in range(256)
                (A is the alpha channel: 255 means transparent, 0 means opaque)
            string: string with RGB(A) data in one of the following formats

        Supported formats for "string" argument:
            "#rrggbb" (srt): HTML-like, used in SRT subtitle format
            "$bbggrr" (sub): used in SUB format
            "&Haabbggrr" (ass): used in ASS for style definitions
            "&Hbbggrr&" (ass_rgb): used in ASS/SSA for color override tags
            "<integer value of 0xbbggrr>" (ssa): used in SSA for style def.
            "<one of 16 basic HTML colors>", eg. "blue": used in SRT

            ("rr", "bb", "gg", "aa" are hexadecimal R/G/B/A values;
            in parentheses are format keywords for str.format and Color.to_str
            to produce this as output)
        
        """

        if isinstance(r, str):
            raise TypeError("Use keyword argument 'string'")

        if string:
            if not isinstance(string, str):
                raise TypeError("'string' argument must be str")
            
            # "<decimal value of 0xbbggrr>" - convert to "$bbggrr"
            if string.isdecimal():
                string = "".join(["$", hex(int(string))[2:].zfill(6)])

            # hexadecimal formats
            for regex in cls._re_patterns:
                match = regex.match(string)
                if match:
                    match_dict = dict(a="0")
                    match_dict.update(match.groupdict("0"))
                    rgba = [int(match_dict[color], 16) for color in "rgba"]
                    return super(__class__, cls).__new__(cls, *rgba)

            # named colors
            string = string.lower()
            if string in cls.NAMED_COLORS:
                r, g, b = cls.NAMED_COLORS[string]
                return super(__class__, cls).__new__(cls, r, g, b, 0)

            raise ValueError(
                "Cannot interpret given string: '{}'".format(string))
        else:
            for color in (r, g, b, a):
                color = int(color)
                if color not in range(256):
                    raise ValueError(
                        "r, g, b, a argumens must be in range(256)")

        return super(__class__, cls).__new__(cls, r, g, b, a)
            
    # --------------------------------------------------------------------------
    # output

    def to_str(self, format_=""):
        """
        Get string representation in various formats.

        Arguments:
            format_: Output format; see Color.__init__ docstring for a list.
        
        Returns:
            String representation of self.
        
        """
        if format_ == "":
            return repr(self)
        elif format_ == "ass":
            return "&H{3:02X}{2:02X}{1:02X}{0:02X}".format(*self)
        elif format_ == "ass_rgb":
            return "&H{2:02X}{1:02X}{0:02X}&".format(*self)
        elif format_ == "sub":
            return "${2:02X}{1:02X}{0:02X}".format(*self)
        elif format_ == "srt":
            return "#{0:02X}{1:02X}{2:02X}".format(*self)
        elif format_ == "ssa":
            return str(self.r + 0x100 * self.g + 0x10000 * self.b)
        else:
            raise ValueError("Unknown format (use ass/ass_rgb/ssa/srt/sub)")

    def __format__(self, format_):
        return self.to_str(format_)

# ------------------------------------------------------------------------------

class Time:
    """
    Positive or negative time value with millisecond precision.
    Time is immutable and hashable type.

    Class attributes:
        NAMED_FPS: Dictionary of common framerate aliases (eg. "ntsc_film"),
            as in AviSynth's AssumeFPS() function; see
            http://avisynth.org/mediawiki/AssumeFPS
    
    Methods:
        Time(): Initialize from time- or frame-based data.
        to_str(): String representation in various formats.
        to_frame(): Return frame number in given framerate.
        to_times(): Return tuple (h, m, s, ms) or (h, m, s, cs).

    Static methods:
        sanitize_framerate(): Return numeric fps, making sure it's positive,
            looking up an alias in NAMED_FPS if needed.

    Overloaded operators:
        == != < <= > >=: Relation with other Time object.
        + - += -=: Add or subtract Time objects.
        unary -: Return negated time.
        * *=: Multiply time value by int/float (for framerate transforms).
        / /=: Divide time value by int/float.
        /: Divide two Time objects, return float ratio.
        % %=: Modulo with another Time objects, return Time object.
        abs(): Return Time object with positive time amount.
        int(): Return time amount in milliseconds (the inner representation).

    """
    __slots__ = "ms_time"

    NAMED_FPS = {"ntsc_film": 24000/1001,
                 "ntsc": 30000/1001,
                 "ntsc_video": 30000/1001,
                 "ntsc_double": 60000/1001,
                 "ntsc_quad": 120000/1001,
                 "film": 24.0,
                 "pal": 25.0,
                 "pal_video": 25.0,
                 "pal_film": 25.0,
                 "pal_double": 50.0,
                 "pal_quad": 100.0}

    # --------------------------------------------------------------------------
    # read time

    def __init__(self, string=None,
                 fps=None, frame=None,
                 h=0, m=0, s=0, ms=0):
        """
        Initialize from time- or frame-based data.

        Arguments:
            string: Timestamp in various formats, see below.
            fps: Framerate to handle frame-based input; may be either
                a positive int/float or a string (like in AviSynth,
                see NAMED_FPS).
            frame: Frame number, must also specify fps (note: when passing
                eg. "5" as the "string" argument, it is interpreted as
                frame number).
            ms, s, m, h: Positive or negative numbers of int/float type.

        Supported formats for "string":
            "<non-negative integer frame number>" (sub): must specify fps
            "H:MM:SS.cc" (ass): the SubStation timestamp
            "HH:MM:SS,mmm" (srt): the SubRip timestamp
            
            (In parentheres are format keywords for str.format and Time.to_str
            method to produce this output.)
            
        """

        if string is not None:
            match = re.search(r"(?:(\d{1,2}):)?"              # hours (optional)
                              r"(\d{1,2}):"                   # minutes
                              r"(\d{1,2})"                    # seconds
                              r"(?:[,.](\d{1,3}))?", string)  # fractions (opt.)
            if not match:
                raise ValueError("Cannot resolve timestamp format")

            times = list(match.groups("0"))      # (h, m, s, fractions-of-sec)
            times[-1] = times[-1].ljust(3, "0")  # "convert" fractions to ms
            h, m, s, ms = map(int, times)
    
        elif frame is not None:
            fps = self.sanitize_framerate(fps)
            frame = int(frame)
            frame_duration = 1000 / fps
            ms_time = round(frame_duration * frame)
            super().__setattr__("ms_time", ms_time)
            return

        ms_time = round(((h * 60 + m) * 60 + s) * 1000 + ms)
        super().__setattr__("ms_time", ms_time)

    # --------------------------------------------------------------------------
    # output time

    def to_frame(self, fps):
        """
        Return frame number in given framerate.

        Attributes:
            fps: Framerate for the calculation.

        Returns:
            Number of frame in which current time is passed.

        Raises:
            TypeError: fps is not int/float/str
            ValueError: fps is not positive; framerate alias not resolved

        """
        fps = self.sanitize_framerate(fps)
        frame_duration = 1000.0 / fps
        return round(self.ms_time / frame_duration)

    def to_str(self, format_="", fps=None):
        """
        Return string representation.

        Arguments:
            format_: Desired output format, see below.
            fps: Needed for frame-based "sub" format.

        Possible "format_" argument values and their meanings:
            "" (default): [-][HH:]MM:SS.mmm
            "ass", "ssa": H:MM:SS.cc (centiseconds are floor'd milliseconds)
            "srt": HH:MM:SS,mmm
            "sub": frame number

        Returns:
            String representation of self.

        Raises:
            OverflowError: Selected format cannot represent time amount
                this large.
            RuntimeError: Subtitle timestamp format is selected, but the time
                is negative. Negative start/end times are not allowed in
                SSA/SRT/SUB formats.

        """
        h, m, s, ms = times = self.to_times()
        negative = self.ms_time < 0

        if format_ == "":
            if negative:
                h, m, s, ms = (abs(t) for t in times)

            if h == 0:
                output = "{}:{:02d}.{:03d}".format(m, s, ms)
            else:
                output = "{}:{:02d}:{:02d}.{:03d}".format(h, m, s, ms)
                
            return output if not negative else "-" + output

        if negative:
            raise RuntimeError("Negative subtitle timestamps not allowed")
        
        if format_ in {"ass", "ssa"}:
            h, m, s, cs = self.to_times(centiseconds=True)
            
            if h >= 10:
                raise OverflowError("ASS cannot represent times over 10 hrs")
            else:
                # note that ASS uses centiseconds, not milliseconds
                return "{:01d}:{:02d}:{:02d}.{:02d}".format(h, m, s, cs)

        elif format_ == "srt":
            if h >= 100:
                raise OverflowError("SRT cannot represent times over 100 hrs")
            else:
                return "{:02d}:{:02d}:{:02d},{:03d}".format(h, m, s, ms)
            
        elif format_ == "sub":
            if not fps:
                raise AttributeError("Must specify fps")
            frame = self.to_frame(fps)
            return str(frame)

    def to_times(self, centiseconds=False):
        """Return times as (h, m, s, frac)."""
        sign = 1 if self.ms_time >= 0 else -1
        if centiseconds:
            ms_time = abs(round(self.ms_time / 10) * 10)
        else:
            ms_time = abs(self.ms_time)

        times = (ms_time // 3600000,       # hours
                 (ms_time // 60000) % 60,  # minutes
                 (ms_time // 1000) % 60,   # seconds
                 ms_time % 1000)           # milliseconds

        h, m, s, ms = (sign * t for t in times)

        if centiseconds:
            return (h, m, s, ms // 10)
        else:
            return (h, m, s, ms)

    # --------------------------------------------------------------------------
    # misc
    
    @staticmethod
    def sanitize_framerate(fps):
        """
        Return frame rate as a number or raise an exception.

        Arguments:
            fps: Either a positive int/float, or a valid fps alias
                (see Time.NAMED_FPS), or positive number in str.

        Returns:
            int/float frame rate

        Raises:
            ValueError: fps <= 0
            UnknownFPSError: fps was not int, float or valid str alias
            
        """
        if isinstance(fps, str):
            if fps in Time.NAMED_FPS:
                return Time.NAMED_FPS[fps]
            else:
                try:
                    fps = float(fps)
                except ValueError:
                    raise UnknownFPSError("Unknown fps alias: '{}'".format(fps))

        if isinstance(fps, (int, float)):
            if fps > 0:
                return fps
            else:
                raise ValueError(
                    "fps cannot be negative or zero: '{}'".format(fps))
        else:
            raise UnknownFPSError("fps must be either int/float/str")

    def __hash__(self):
        return hash(self.ms_time)

    def __setattr__(self, *args):
        raise TypeError("Time is immutable.")

    __delattr__ = __setattr__

    def __format__(self, format_):
        return self.to_str(format_)

    def __repr__(self):
        return self.to_str()

    def __int__(self):
        return self.ms_time

    # --------------------------------------------------------------------------
    # relations
    
    def __lt__(self, other):
        if isinstance(other, Time):
            return int(self) < int(other)
        else:
            return NotImplemented

    def __le__(self, other):
        return self == other or self < other

    def __eq__(self, other):
        if isinstance(other, Time):
            return int(self) == int(other)
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __ge__(self, other):
        return not self < other

    def __gt__(self, other):
        return not self <= other


    # --------------------------------------------------------------------------
    # arithmetics

    def __neg__(self):
        new_time = -self.ms_time
        return Time(ms=new_time)

    def __abs__(self):
        new_time = abs(self.ms_time)
        return Time(ms=new_time)


    def __add__(self, other):
        if isinstance(other, Time):
            new_time = self.ms_time + other.ms_time
            return Time(ms=new_time)
        else:
            return NotImplemented
        
    def __sub__(self, other):
        if isinstance(other, Time):
            new_time = self.ms_time - other.ms_time
            return Time(ms=new_time)
        else:
            return NotImplemented

    __iadd__ = __add__
    __isub__ = __sub__
    

    def __mul__(self, other):
        if isnumber(other):
            new_time = self.ms_time * other
            return Time(ms=new_time)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Time):
            return self.ms_time / other.ms_time
        elif isnumber(other):
            new_time = self.ms_time / other
            return Time(ms=new_time)
        else:
            return NotImplemented

    __itruediv__ = __truediv__

    def __mod__(self, other):
        if isinstance(other, Time):
            new_time = self.ms_time % other.ms_time
            return Time(ms=new_time)
        else:
            return NotImplemented

    __rmul__ = __imul__ = __mul__
    __imod__ = __mod__
    

# ------------------------------------------------------------------------------

_Vec2 = namedtuple("Vec2", "x y")

class Vec2 (_Vec2):
    """
    2-dimensional Euclidean vector class. Based on namedtuple.

    Attributes:
        x, y: Carthesian coordinates (float).
        angle: Angle with the X axis; atan2(y, x) (read-only).
        length: Vector's norm (read-only).

    Methods:
        Vec2(): Initialize from Carthesian or polar coordinates.
        normalize(): Return normalized vector.
        rotate(): Return rotated vector.
        dot_prod(): Dot product.

    Overloaded operators:
        == !=: Equality of vectors.
        + - += -=: Vector addition (with Vec2 instances).
        * / *= /=: Scalar multiplication (with int/float).
        unary -: Return vector with opposite orientation.

    """

    def __new__(cls, x=0, y=0, ang=None, rad=None):
        """
        Initialize from Carthesian or polar coordinates.

        When providing both ang and rad arguments, it is initialized
        from polar coordinates. Else x and y coordinates are used.

        Arguments:
            x, y: Carthesian coordinates (int/float).
            ang: Angle in radians (int/float).
            rad: Vector's radius (int/float).

        Raises:
            TypeError: Some of supplied arguments were not numeric.
       
        """

        if ang is not None and rad is not None:
            if all(map(isnumber, (ang, rad))):
                x, y = rad * math.cos(ang), rad * math.sin(ang)
            else:
                raise TypeError("'rad' and 'ang' must be numbers")
        else:
            if all(map(isnumber, (x, y))):
                x, y = map(float, (x, y))
            else:
                raise TypeError("'x' and 'y' must be numbers")

        return super(__class__, cls).__new__(cls, x, y)

    # --------------------------------------------------------------------------
    # manipulation

    def normalize(self):
        """
        Return normalized vector (vector of length 1).

        Returns:
            Vec2 instance after normalization.

        Raises:
            ArithmeticError: Attempted to normalize zero vector (not defined).
            
        """
        if self.x == 0 and self.y == 0:
            raise ArithmeticError("Cannot normalize null vector.")
        else:
            length = self.length
            return Vec2(self.x / length, self.y / length)

    def rotate(self, ang):
        """
        Return vector multiplied by rotation matrix for given angle.

        / cos(ang)   -sin(ang) \ / self.x \
        \ sin(ang)    cos(ang) / \ self.y /

        Arguments:
            ang: The angle to rotate by (in radians).

        Returns:
            Vec2 instance after rotation.

        """
        x = self.x * math.cos(ang) - self.y * math.sin(ang)
        y = self.x * math.sin(ang) + self.y * math.cos(ang)
        return Vec2(x, y)

    def dot_prod(self, w):
        """
        Dot product.

        Arguments:
            w: The other Vec2.
        
        Returns:
            int/float product.

        Raises:
            TypeError: Dot product with non-Vec2 object.

        """
        if not isinstance(w, Vec2):
            raise TypeError("Must do dot product with Vec2 object")

        return self.x * w.x + self.y * w.y

    # --------------------------------------------------------------------------
    # properties

    @property
    def angle(self):
        """atan2(y, x)"""
        return math.atan2(self.y, self.x)

    @property
    def length(self):
        """Norm of the vector."""
        return math.hypot(self.x, self.y)

    # --------------------------------------------------------------------------
    # helpers

    def __str__(self):
        return "Vec2(x={:.2f}, y={:.2f}, angle={:.1f} deg, length={:.2f})".format(
            self.x, self.y, math.degrees(self.angle), self.length)

    # --------------------------------------------------------------------------
    # arithmetics

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __add__(self, w):
        """Vector addition."""
        if isinstance(w, Vec2):
            return Vec2(self.x + w.x, self.y + w.y)
        else:
            return NotImplemented

    def __sub__(self, w):
        """Vector subtraction."""
        if isinstance(w, Vec2):
            return Vec2(self.x - w.x, self.y - w.y)
        else:
            return NotImplemented

    def __mul__(self, k):
        """Scalar multiplication."""
        if isnumber(k):
            return Vec2(k * self.x, k * self.y)
        else:
            return NotImplemented

    def __truediv__(self, k):
        """Scalar division."""
        if isnumber(k):
            return Vec2(self.x / k, self.y / k)
        else:
            return NotImplemented
        
    __radd__ = __add__
    __iadd__ = __add__
    __rsub__ = __sub__
    __isub__ = __sub__
    __imul__ = __mul__
    __rmul__ = __mul__
    __itruediv__ = __truediv__
    # scalar / vector isn't defined
