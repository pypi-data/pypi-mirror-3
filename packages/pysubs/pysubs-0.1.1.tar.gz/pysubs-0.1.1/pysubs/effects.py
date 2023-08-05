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
pysubs.effects module
=====================

This module enables scripting of effects for SubStation files. See pysubs/
effect_definitions directory for example effects and effect_template() docstring
for guide on how to apply them.

All this is experimental and leaves a lot to be desired, esp. some karaoke
template and FreeType interface to calculate character/syllable coordinates.

Attributes:
    GENERATED: Identifier of generated lines, so that they may be automatically
        removed before new processing.
    EFFECTS: Functions loaded from pysubs/effect_definitions directory.

Functions:
    effect_template(): Callback function for SSAFile.iter_callback() that parses
        the line's Effect field and calls user defined function, passing it
        the parsed arguments.
    split_frames(): Iterator giving 1-frame-long segments of given subtitle.

"""

import re, sys, os, inspect, glob, imp
from .misc import Time


GENERATED = "Generated line"

def _load_functions(subdir):
    """Return dict of functions from all *.py files in given subdirectory"""

    source_files = glob.glob(
        os.path.join(os.path.split(__file__)[0], subdir, "*.py"))
    output = {}
    for file in source_files:
        with open(file, encoding="utf8") as fp:
            module = imp.load_module(
                file, fp, file, (".py", "r", imp.PY_SOURCE))
        functions = inspect.getmembers(module, predicate=inspect.isfunction)
        for name, func in functions:
            output[name] = func
    return output

EFFECTS = _load_functions("effect_definitions")

def effect_template(SSAFile_obj, line):
    """
    Wrapper for user defined effects, a callback for SSAFile.iter_callback().
    Do not call it directly.

    Suppose we want to make an effect, "my_effect". First, we write Python
    function my_effect(SSAFile_obj, line, arg1, arg2) that takes one line and
    some parameters arg1, arg2, generates new SSAEvents and returns them
    (it should not return the original line, just the generated ones). Save
    the function as "my_effect.py" to pysubs/effect_definitions directory.

    Then, in the ASS/SSA file, we mark the lines to be processed by "my_effect"
    using the "Effect" field, like this: "my_effect:arg1;arg2".

    Finally, we load the subtitles as usual and call iter_callback() method
    with effect_template as the callback function.

    "Effect" field format:
        <effect name>:<arg1>[;<arg2> ...]

    Callback function signature:
        <effect name>(SSAFile_obj, line, <arg1>[, <arg2>, ...]) -> iterable of
                                                                   SSAEvents
    """
    output = line
    effect_match = re.match(r"^([A-zA-Z_][A-zA-Z0-9_]*):(.+)$", line["Effect"])

    if effect_match:
        name, argv = effect_match.groups()
        argv = argv.split(";")

        if name in EFFECTS:
            try:
                generated_lines = EFFECTS[name](SSAFile_obj, line, *argv)
            except TypeError as e:
                print(repr(e), file=sys.stderr)
                return line

            line.comment()
            for gen_line in generated_lines:
                gen_line.effect = GENERATED

            output = [line, ]
            output.extend(generated_lines)
        else:
            print("Cannot find function '{}'".format(name), file=sys.stderr)

    return output

def effect_undo(SSAFile_obj, line):
    """
    Undo what effect_template did -- delete generated lines and uncomment the
    original ones.

    This is a callback for SSAFile.iter_callback(), not to be called directly.
    
    """
    if line.effect == GENERATED:
        return None

    if re.match(r"[A-zA-Z_][A-zA-Z0-9_]*:", line.effect):
        line.uncomment()

    return line

def split_frames(line, fps):
    """
    Iterator giving 1-frame-long segments of given subtitle.

    Arguments:
        fps: The frame rate (either float or keyword alias).

    Yields:
        SSAEvent instance.
    
    """

    start, end = line.start.to_frame(fps), line.end.to_frame(fps)

    for frame in range(start, end):
        new_line = line.copy()
        new_line.start = Time(frame=frame, fps=fps)
        new_line.end = Time(frame=frame + 1, fps=fps)
        yield new_line
