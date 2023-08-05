import math, random            # standard C math, Python random module
import pysubs                  # PySubs framework
Vec2 = pysubs.Vec2             # lazyman's vector class
rand = random.random           # rand() gets a random float in range <0;1)

# ------------------------------------------------------------------------------
# effect implementation

def shake(subtitle_obj, line,
          fps, max_radius):
    """
    Simple shaking effect.

    The line will get split into as many lines that they fill its time each
    lasting one frame in given fps (the last line's end may be off, so fix
    that). Set Effect field of each split piece to pysubs.effects.GENERATED
    constant so that it may be cleaned up automagically.

    For every line, compute a random vector distortion_vec,
    |distortion_vec| <= max_radius; planar coordinates are convenient here,
    just shoot a random <0;2pi) angle and <0;max_radius) range.

    Then add distortion_vec to (line's) current_pos, yielding
    translated position. Make this the new line position.

    """

    # convert function arguments
    max_radius = float(max_radius)

    # do the effect
    new_lines = []
    current_pos = Vec2(*line.get_pos(subtitle_obj))
    
    for fx_line in pysubs.effects.split_frames(line, fps):
        fx_line.effect = pysubs.effects.GENERATED
        
        angle = 2 * math.pi * rand()
        radius = max_radius * rand()
        distortion_vec = Vec2(ang=angle, rad=radius)
        
        new_pos = current_pos + distortion_vec
        fx_line.set_pos(*new_pos)
        new_lines.append(fx_line)

    new_lines[-1].end = line.end  # make sure we make it on time

    return new_lines
