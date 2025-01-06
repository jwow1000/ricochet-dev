import random
import math
# function for creating curves

# all vlaues are 0-1 normalized, then changed to 0-255

# Helper function to convert beats to ticks, hard coded for 50 ticks
def beats_to_ticks(beats, bpm=90):
    return int((beats * 60 * 50) / bpm)

# root line function, use algo callback function
def line( seq, beats, offset, algo, channel ):
    channel_num = ((channel-1)*3)+1
    ticks = beats_to_ticks( beats )
    offset_ticks = beats_to_ticks( offset )
    print(f"offset ticks: {offset_ticks}, {channel}, {offset}")
    step = 1 / (ticks-1)
    # turn on light (strobe on) and then control brightness
    seq.add_event( offset_ticks, {channel_num + 1: 0})
    for i in range( ticks ):
        math = algo( i * step )
        ramp = min( max(math * 255, 0), 255)
        seq.add_event(
            i + offset_ticks,
            { channel_num: int(ramp)}
        )

# root line function but for strobe, no need for continuous ticks
def line_strobe( seq, beats, offset, channel, bright, rate, dur):
  channel_num = ((channel-1)*3)+1
  ticks = beats_to_ticks( beats )
  offset_ticks = beats_to_ticks( offset )
  
  # turn on light (strobe on) and then control brightness
  seq.add_event( offset_ticks, {
      channel_num: bright,
      channel_num + 1: rate, 
      channel_num + 2: dur
  })
  # turn off light, and strobe, next effect will turn on
  seq.add_event( offset_ticks + ticks, {
      channel_num: 0,
      channel_num + 1: 6, 
      
  })

  
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

# hurricane sine
def hurricane( v ):
    if v >= 0.999:
        return 0
    else:
        sine = math.sin( v * (math.pi*2) )
        norm = (sine * 0.2) + 0.2
        return norm

# shaky sine
def shaky( v ):
    if v >= 0.999:
        return 0
    else:
        # speed * 7
        sine = math.sin( (v*7) * (math.pi*2) )
        norm = (sine * 0.25) + 0.25
        envelope = math.pow( math.sin( (v/4) * (math.pi*2) ), 6)
        return envelope * norm

# long linear attack, sharp end
def long_attack( v ):
    if v >= 0.999:
        return 0
    else:
        norm = 1 - v
        return norm * 0.48

# long decay 255
def long_decay( v ):
  return math.pow( 1 - v, 6)
  

# random strobe
def line_random_strobe( seq, beats, offset, channel, bright, rate, dur, noise):
  channel_num = ((channel-1)*3)+1
  ticks = beats_to_ticks( beats )
  offset_ticks = beats_to_ticks( offset )

  for i in range( ticks-1 ):
      rand = random.randint(0,100)
      if rand > noise:
        # turn on light (strobe on) and then control brightness
        seq.add_event( offset_ticks + i, {
            channel_num: bright,
            channel_num + 1: rate, 
            channel_num + 2: dur
        })
      else:
        # turn off light
        seq.add_event( offset_ticks + i, {
            channel_num: 0,
        })

  # end the effect
  seq.add_event( offset_ticks + ticks, {
      channel_num: 0,
      channel_num + 1: 6
  })      