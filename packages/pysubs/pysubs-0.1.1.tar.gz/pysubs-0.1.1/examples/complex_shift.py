#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Complex shift example
=====================

Shifting all subtitles by the same amout of time is easily done via
SSAFile.shift() method or --shift commandline argument to pysubs-cli.py.

But what if, say, we have two sync points? In this example, we will shift
all lines after "The Opening" by 10 seconds and all lines after "The Ending"
by additional 10 seconds.

The Opening and Ending sequences are marked by SSA styles. This is
convenient, but not necessary as we may "manually" find/regex text
of the sync point line.

"""

import pysubs

subs = pysubs.SSAFile()
subs.from_str("""\
[Script Info]
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 640
PlayResY: 480

[V4+ Styles]
Style: Dialogue,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Opening-EN,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Opening-JP,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Ending-EN,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Ending-JP,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Dialogue: 0,0:00:00.00,0:00:05.00,Dialogue,,0000,0000,0000,,Line before Opening
Dialogue: 0,0:00:11.00,0:00:13.00,Dialogue,,0000,0000,0000,,Line between Opening and Ending
Dialogue: 0,0:00:23.00,0:00:25.00,Dialogue,,0000,0000,0000,,Line after Ending
Dialogue: 0,0:00:05.00,0:00:07.00,Opening-EN,,0000,0000,0000,,The Opening 1
Dialogue: 0,0:00:05.00,0:00:07.00,Opening-JP,,0000,0000,0000,,ザ·オープニング·一
Dialogue: 0,0:00:09.00,0:00:11.00,Opening-EN,,0000,0000,0000,,The Opening 2
Dialogue: 0,0:00:09.00,0:00:11.00,Opening-JP,,0000,0000,0000,,ザ·オープニング·二
Dialogue: 0,0:00:15.00,0:00:17.00,Ending-EN,,0000,0000,0000,,The Ending 1
Dialogue: 0,0:00:15.00,0:00:17.00,Ending-JP,,0000,0000,0000,,ザ·エンディング·一
Dialogue: 0,0:00:17.00,0:00:21.00,Ending-EN,,0000,0000,0000,,The Ending 2
Dialogue: 0,0:00:17.00,0:00:21.00,Ending-JP,,0000,0000,0000,,ザ·エンディング·二
""")

# ------------------------------------------------------------------------------
# find sync points

last_OP_line = sorted(filter(lambda line: "Opening" in line.style, subs))[-1]
last_ED_line = sorted(filter(lambda line: "Ending" in line.style, subs))[-1]

# alternative: look up sync points by line text

# last_OP_line = next(filter(lambda line: line.text == "The Opening 2", subs))
# last_ED_line = next(filter(lambda line: line.text == "The Ending 2", subs))

OP_end = last_OP_line.end
ED_end = last_ED_line.end

# ------------------------------------------------------------------------------
# shift lines

for line in subs:
    if line.start >= ED_end:
        line.shift(s=20)
    elif line.start >= OP_end:
        line.shift(s=10)

# alternative: add the time progressively -- note that we cannot shift lines
# immediately as that would offset further comparisons

# for line in subs:
#    delta_sec = 0
#    if line.start >= OP_end:
#        delta_sec += 10
#    if line.start >= ED_end:
#        delta_sec += 10
#    line.shift(s=delta_sec)
