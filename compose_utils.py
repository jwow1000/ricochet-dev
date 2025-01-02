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