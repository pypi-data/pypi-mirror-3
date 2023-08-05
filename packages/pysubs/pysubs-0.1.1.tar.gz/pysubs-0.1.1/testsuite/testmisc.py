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

from pysubs.misc import Color, Time, Vec2
from pysubs.exceptions import *
import unittest, random, math

class TestColor(unittest.TestCase):

    KNOWN_VALUES = (
        ("#123456", [0x12, 0x34, 0x56, 0], "srt"),
        ("$123456", [0x56, 0x34, 0x12, 0], "sub"),
        ("&H123456&", [0x56, 0x34, 0x12, 0], "ass_rgb"),
        ("&Hab123456", [0x56, 0x34, 0x12, 0xab], "ass"),
        (str(int(0x123456)), [0x56, 0x34, 0x12, 0], "ssa"))
    
    def test_named_colors(self):
        """initialize from HTML named colors"""
        for input_str, rgb_value in Color.NAMED_COLORS.items():
            color = Color(string=input_str)
            color_rgb = (color.r, color.g, color.b)
            self.assertEqual(color_rgb, rgb_value)

    def test_known_values(self):
        """read from various formats and print it back"""
        for input_str, rgba_value, format_ in self.KNOWN_VALUES:
            color = Color(string=input_str)
            self.assertEqual(list(color), rgba_value)
            
            output_str = color.to_str(format_)
            self.assertEqual(output_str.lower(), input_str.lower())
            
            output_str2 = "".join(["{0:", format_, "}"]).format(color)
            self.assertEqual(output_str.lower(), output_str2.lower())

    def test_invalid_input(self):
        """invalid input should fail"""
        with self.assertRaises(TypeError):
            Color(string=3.14)
        with self.assertRaises(TypeError):
            Color("#123456")
        with self.assertRaises(ValueError):
            Color(0,0,0,-5)
        with self.assertRaises(ValueError):
            Color(0,0,0,256)
        with self.assertRaises(ValueError):
            Color(string="foo#123456")


class TestTime(unittest.TestCase):

    TO_STR_TEST = (
        ("1:23:45.67", "ass"),
        ("12:34:56,789", "srt"))

    def test_float_input(self):
        """float input should be rounded to ms"""

        t1 = Time(ms=0.1)
        self.assertEqual(t1, Time())

        t2 = Time(s=1.0001)
        self.assertEqual(t2, Time(s=1))

    def test_negative(self):
        """negative values"""

        t1 = Time(h=1, m=-60)
        self.assertEqual(t1, Time())

        t2 = Time(ms=-5)
        self.assertEqual(int(t2), -5)
        self.assertEqual(t2.to_times(), (0, 0, 0, -5))
        self.assertEqual(str(t2), "-0:00.005")
        
    
    def test_non_normalized(self):
        """limited non-normalized input is possible"""

        self.assertEqual(Time(h=1), Time(m=60))

        # TODO: should we really let this slide?
        self.assertEqual(Time("1:60:00.00"), Time(h=2))
        

    def test_known_values(self):
        """read from various formats"""
        s1 = "1:23:45.67"
        t1 = Time(h=1, m=23, s=45, ms=670)
        self.assertEqual(t1, Time(s1))

        s2 = "12:34,567"
        t2 = Time(m=12, s=34, ms=567)
        self.assertEqual(t2, Time(s2))

        s3 = "1:30"
        t3 = Time(m=1, s=30)
        self.assertEqual(t3, Time(s3))

        s4 = "12345"
        t4 = Time(frame=12345, fps="ntsc_video")
        self.assertEqual(t4, Time(frame=s4, fps="ntsc_video"))

    def test_to_str(self):
        """read and print back various formats"""

        for input_str, format_ in self.TO_STR_TEST:
            t = Time(input_str)
            s = t.to_str(format_)
            s2 = "".join(("{:", format_, "}")).format(t)
            self.assertEqual(input_str, s)
            self.assertEqual(input_str, s2)

        # SUB needs fps, so we test it separately
        input_str = "123456"
        t = Time(frame=input_str, fps="ntsc_film")
        s = t.to_str("sub", fps="ntsc_film")
        self.assertEqual(input_str, s)

    def test_overflow(self):
        """irrepresentable values should fail"""

        Time("9:59:59.99").to_str("ass")
        with self.assertRaises(OverflowError):
            Time(h=10).to_str("ass")

        Time("99:59:59,999").to_str("srt")
        with self.assertRaises(OverflowError):
            Time(h=100).to_str("srt")

        Time(h=1000).to_str("sub", fps="pal")

    def test_sanitize_framerate(self):
        """test sanitize_framerate()"""

        for alias, fps in Time.NAMED_FPS.items():
            looked_up_fps = Time.sanitize_framerate(alias)
            self.assertEqual(looked_up_fps, fps)

        with self.assertRaises(UnknownFPSError):
            Time.sanitize_framerate("foo")
        with self.assertRaises(ValueError):
            Time.sanitize_framerate(-23.976)
        with self.assertRaises(ValueError):
            Time.sanitize_framerate(0)
        with self.assertRaises(UnknownFPSError):
            Time.sanitize_framerate(None)

    def test_operators(self):
        """test overloaded operators"""

        t1 = Time(m=90)
        t2 = Time(m=60)

        self.assertEqual(t1 + t2, Time(m=90+60))
        self.assertEqual(t1 - t2, Time(m=90-60))
        self.assertEqual(-t1, Time(m=-90))
        self.assertEqual(abs(-t1), t1)
        
        self.assertEqual(t1 * 2, Time(m=90*2))
        self.assertEqual(2 * t1, Time(m=90*2))
        
        self.assertEqual(t1 / 2, Time(m=90//2))
        
        self.assertAlmostEqual(t1 / t2, 90/60)
        
        self.assertEqual(t1 % t2, Time(m=90%60))

        t3 = Time(m=30); t3 += t2
        self.assertEqual(t3, t1)

        t3 = Time(m=30); t3 -= t2
        self.assertEqual(t3, Time(m=-30))

        t3 = Time(m=90); t3 %= t2
        self.assertEqual(t3, Time(m=30))
    

class TestVec2(unittest.TestCase):

    def test_init(self):
        """polar / Carthesian init"""
        u = Vec2(0,1)
        u_ = Vec2(ang=math.radians(90), rad=1)
        self.assertAlmostEqual(u.x, u_.x)
        self.assertAlmostEqual(u.y, u_.y)

    def test_normalize(self):
        """normalize()"""

        u = Vec2(5,5).normalize()
        self.assertAlmostEqual(u.length, 1)
        self.assertAlmostEqual(u.x, 1 / math.sqrt(2))
        self.assertAlmostEqual(u.x, u.y)

        with self.assertRaises(ArithmeticError):
            Vec2(0,0).normalize()

    def test_rotate(self):
        """rotate()"""
        u = Vec2(11, 17)
        u_ = u.rotate(math.radians(360))
        self.assertAlmostEqual(u.x, u_.x)
        self.assertAlmostEqual(u.y, u_.y)

        v = Vec2(1,0)
        for i in range(9): v = v.rotate(math.radians(10))
        self.assertAlmostEqual(v.x, 0)
        self.assertAlmostEqual(v.y, 1)

    def test_dot_prod(self):
        """dot_prod()"""
        u = Vec2(1,0)
        v = Vec2(0,1)
        self.assertEqual(u.dot_prod(v), 0)

        w = Vec2(2,3)
        x = Vec2(-4,2)
        self.assertEqual(w.dot_prod(x), -4 * 2 + 2 * 3)
        
        y = Vec2(0,0)
        self.assertEqual(w.dot_prod(y), 0)

    def test_operators(self):
        """test overloaded operators"""

        u = Vec2(1,0)
        v = Vec2(0,1)
        uv = Vec2(1,1)
        self.assertEqual(u + v, uv)
        self.assertEqual(u + v, v + u)
        self.assertNotEqual(u - v, v - u)

        w = Vec2(4,7)
        w3 = Vec2(4*3,7*3)
        self.assertEqual(3 * w, w * 3)
        self.assertEqual((3 * w).x, w3.x)
        self.assertEqual((3 * w).y, w3.y)
        self.assertAlmostEqual((w3 / 3).x, w.x)
        self.assertAlmostEqual((w3 / 3).y, w.y)

        with self.assertRaises(ZeroDivisionError):
            Vec2(2,5) / 0
