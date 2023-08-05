import math, random            # standard C math, Python random module
import pysubs                  # PySubs framework
Vec2 = pysubs.Vec2             # lazyman's vector class
rand = random.random           # rand() gets a random float in range <0;1)

# ------------------------------------------------------------------------------
# effect implementation

def shake2(subtitle_obj, line,
           fps, max_radius, max_change):
    """
    Shaking effect with distance limiting.

    The line will get split into as many lines that they fill its time each
    lasting one frame in given fps (the last line's end may be off, so fix
    that). Set Effect field of each split piece to pysubs.effects.GENERATED
    constant so that it may be cleaned up automagically.

    For every line, compute a random vector distortion_vec,
    |distortion_vec| <= max_radius; planar coordinates are convenient here,
    just shoot a random <0;2pi) angle and <0;max_radius) range.

    Calculate (distortion_vec - prev_distortion_vec), ie. delta between previous
    and current position. If it exceeds max_change, clamp it to that, then
    forget current distortion_vec and calculate new one by adding the clamped
    vec_delta to prev_distortion_vec. The subtitle will travel in the same
    direction, but only max_change distance.

    Then add distortion_vec to (line's) current_pos, yielding
    translated position. Make this the new line position.

    Assign distortion_vec to prev_distortion_vec and reiterate.
    
    """
    
    # convert function arguments
    max_radius = float(max_radius)
    max_change = float(max_change)

    # do the effect
    new_lines = []
    current_pos = line.get_pos(subtitle_obj)
    prev_distortion_vec = Vec2()
    
    for fx_line in pysubs.effects.split_frames(line, fps):
        fx_line.effect = pysubs.effects.GENERATED
        
        angle = 2 * math.pi * rand()
        radius = max_radius * rand()
        distortion_vec = Vec2(ang=angle, rad=radius)
        vec_delta = distortion_vec - prev_distortion_vec

        if vec_delta.length > max_change: 
            vec_delta = max_change * vec_delta.normalize()
            distortion_vec = prev_distortion_vec + vec_delta
        
        new_pos = current_pos + distortion_vec
        fx_line.set_pos(*new_pos)
        new_lines.append(fx_line)
        prev_distortion_vec = distortion_vec

    new_lines[-1].end = line.end  # make sure we make it on time

    return new_lines
