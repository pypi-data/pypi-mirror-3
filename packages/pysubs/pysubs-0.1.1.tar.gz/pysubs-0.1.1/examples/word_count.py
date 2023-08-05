#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Word count example
==================

Ever wondered how many words are said in a TV series? Which character speaks
the most?

All of this is pretty easy to find out, provided you have SSA subtitles with
filled "Name" fields.

In this example, we will go through all ASS files in current directory,
attributing words in each line (SSA tags are ignored) to their respective
"Name" given in the SSA field. Note that non-dialogue lines will probably get
attributed to "" (or empty string) name, as they usually don't have the field
filled. Before counting total words said, it is necessary to remove these.

"""

import re, glob, collections
import pysubs

words_per_character = collections.Counter()

for file in glob.iglob("*.ass"):
    for line in pysubs.load(file):
        word_count = len(re.findall("\w+", line.plaintext))
        words_per_character[line.name] += word_count

words_per_character[""] = 0
words_total = sum(words_per_character.values())

print("Words in total:", format(words_total, ","))
print("Top 10 characters per word count:")
for name, count in words_per_character.most_common(10):
    print("{:20}{:10,}".format(name, count))
