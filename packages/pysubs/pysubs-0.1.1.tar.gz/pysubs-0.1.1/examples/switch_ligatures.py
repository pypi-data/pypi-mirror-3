#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Switch ligatures example
========================

Advanced typographical features such as ligatures aren't usually seen in
subtitles, but may be feastible when either hardsubbing or distributing
the typeface along with the subtitles (possibly as an MKV or SSA attachment).

While removing ligatures is easily done via replace function on the entire file,
adding them this way (1) gives you zero control over what styles/fonts will
get the ligatures and (2) places ligatures even in text that is not supposed
to be rendered, eg. style names.

Note that it's necessary to adjust the ligature list so that it matches glyphs
available in your typeface. Longer ligatures are at the beginning not to be
overtaken by shorter ones.

"""

import glob
import pysubs

ligatures = [
    ("ffi", "ﬃ"),
    ("ffl", "ﬄ"),
    ("fi", "ﬁ"),
    ("fl", "ﬂ")
    ]

# ------------------------------------------------------------------------------
# compose ligatures

for file in glob.iglob("*.ass"):
    subs = pysubs.load(file)
    for line in subs:
        if line.style == "StyleToGetLigatures":
            for non_ligature, ligature in ligatures:
                line.text = line.text.replace(non_ligature, ligature)
    subs.save(file)

# ------------------------------------------------------------------------------
# decompose ligatures

for file in glob.iglob("*.ass"):
    subs = pysubs.load(file)
    for line in subs:
        for non_ligature, ligature in ligatures:
                line.text = line.text.replace(ligature, non_ligature)
    subs.save(file)
