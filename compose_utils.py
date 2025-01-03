import random
import math
# function for creating curves

# all vlaues are 0-1 normalized, then changed to 0-255

# Helper function to convert beats to ticks, hard coded for 50 ticks
def beats_to_ticks(beats, bpm=90):
    return int((beats * 60 * 50) / bpm)

# root line function, use algo callback function
def line( seq, beats, offset, algo, channel ):
    ticks = beats_to_ticks( beats )
    offset_ticks = beats_to_ticks( offset )
    step = 1 / (ticks-1)
    for i in range( ticks ):
        math = algo( i * step )
        ramp = min( max(math * 255, 0), 255)
        seq.add_event(
            i + offset_ticks,
            {channel: int(ramp)}
        )

# # # # # # algos to use with the line function
# simple fastest attack possible, with linear out (use for test)
def linear_ad( v ):
    return 1 - v

# peek algo, 50% fastest attack, taper off
def peek_ad( v ):
    if v == 0:
        return 0.5
    elif v > 0 :
        # ramp down
        return 0.2 - (v * 0.2) 
    
# random twinkle, 20% or 0%
# this may need more work with the lifetime etc...
def sparkle20( v ):
    rand = random.randint(0,100)
    if rand > 61:
        return 0
    else:
        return 0.2

def on_off( v , scale ):
    output = 0
    if v <= 0.5:
        output =  v * 2
    else:
        norm = (v - 0.4999) * 2
        output = 1 - norm
    return output * scale
    
# two bumps, just an absoluted sine
def two_bumps( v ):
    sine = math.sin( v * (math.pi*2) )
    norm = abs( sine )
    return norm * 0.5 

# 100% strobe to 50% fade out
def quick_long_fade( v ):
    if v == 0:
        return 1
    else:
        norm = 1 - v
        ramp = math.pow( norm, 2)
        return ramp * 0.5

# basic strobe
def strobe( v, scale ):
    if v >= 0.999:
        return 0
    else:
        return scale 