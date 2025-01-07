from array import array
from utils import FANCY_PRINT
from compose_utils import line, line_strobe, peek_ad, sparkle20, two_bumps, on_off, quick_long_fade, strobe, hurricane, shaky, long_attack, line_random_strobe, long_decay, beats_to_ticks
import time
import asyncio
import heapq
from ola.ClientWrapper import ClientWrapper
from dataclasses import dataclass, field
from typing import List, Callable

@dataclass
class DMXSequencer:
    ticks_per_second: int = 50
    composition_length: int = 12000
    universe: int = 1
    data: array = field(default_factory=lambda: array('B', [0] * 512))
    events: list = field(default_factory=list)
    current_tick: int = 0
    wrapper: ClientWrapper = None
    client: object = None

    def __post_init__(self):
        self.wrapper, self.client = self._connect_dmx()

    def _connect_dmx(self, max_retries=30, retry_delay=1):
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                wrapper = ClientWrapper()
                client = wrapper.Client()
                if client.SendDmx(self.universe, [0] * 512):
                    print(f"Successfully connected to DMX on attempt {retry_count + 1}")
                    return wrapper, client
            except Exception as e:
                last_error = str(e)
                print(f"Connection attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                time.sleep(retry_delay)

        raise ConnectionError(f"Failed to connect to DMX after {max_retries} attempts. Last error: {last_error}")

    def add_event(self, tick, channels):
        heapq.heappush(self.events, (tick, channels))

    def send_dmx(self, channels):
        for channel, value in channels.items():
            self.data[channel - 1] = value
        self.client.SendDmx(self.universe, self.data, self.dmx_sent)

    def dmx_sent(self, state):
        if not state.Succeeded():
            print('Error: DMX send failed')

    async def run_async(self):
        while True:
            tick_start = asyncio.get_event_loop().time()
            while self.events and self.events[0][0] == self.current_tick:
                _, channels = heapq.heappop(self.events)
                self.send_dmx(channels)
                print(f"{self.current_tick}: {channels}")
            
            self.current_tick = (self.current_tick + 1) % self.composition_length
            elapsed = asyncio.get_event_loop().time() - tick_start
            sleep_time = max(0, (1 / self.ticks_per_second) - elapsed)
            await asyncio.sleep(sleep_time)

    def shutdown(self):
        if self.wrapper:
            self.wrapper.Stop()
            print("DMX client shut down.")

# Example usage with easy-to-read composition definition
def create_composition():
    # create the sequecer
    sequencer = DMXSequencer()
    
    # variable to track time (in beats)
    sequencer.time_tracker = 0.0

    # variable for on_off intensity
    tri_brightness = 0.0
    
    ########### begin composition ############
    #### all off for 10 seconds( 15 beats )
    sequencer.time_tracker += 15
    print(f"check tracker: {sequencer.time_tracker}")

    ##### see peek cycle 14 seconds(21 beats) 
    line(sequencer, 3, sequencer.time_tracker, peek_ad, 1)
    line(sequencer, 3, sequencer.time_tracker+5.25, peek_ad, 2)
    line(sequencer, 3, sequencer.time_tracker+10.50, peek_ad, 3)
    line(sequencer, 3, sequencer.time_tracker+15.75, peek_ad, 4)

    sequencer.time_tracker += 21
    
    #### random no strobe 12 seconds(18 beats)
    line(sequencer, 18, sequencer.time_tracker, sparkle20, 1)
    line(sequencer, 18, sequencer.time_tracker, sparkle20, 2)
    line(sequencer, 18, sequencer.time_tracker, sparkle20, 3)
    line(sequencer, 18, sequencer.time_tracker, sparkle20, 4)

    sequencer.time_tracker += 18

    # 1/4 round 8 seconds, 12 beats, 3 4beat loops
    tri_brightness = 0.5
    for i in range(3):
      line(sequencer, 2, sequencer.time_tracker, lambda x, arg=tri_brightness: on_off(x, arg), 1) 
      line(sequencer, 2, sequencer.time_tracker+1, lambda x, arg=tri_brightness: on_off(x, arg), 2) 
      line(sequencer, 2, sequencer.time_tracker+2, lambda x, arg=tri_brightness: on_off(x, arg), 3) 
      line(sequencer, 2, sequencer.time_tracker+3, lambda x, arg=tri_brightness: on_off(x, arg), 4)

      sequencer.time_tracker += 4 

    
    #### cross two bumps, 7secs, loop
    for i in range(2):
      line(sequencer, 2, sequencer.time_tracker, two_bumps, 1)
      line(sequencer, 2, sequencer.time_tracker, two_bumps, 3)
      line(sequencer, 2, sequencer.time_tracker+2, two_bumps, 2)
      line(sequencer, 2, sequencer.time_tracker+2, two_bumps, 4)
      sequencer.time_tracker += 4

    #### cross quick attack, 7secs, 
    for i in range(2):
      line(sequencer, 2, sequencer.time_tracker, quick_long_fade, 1)
      line(sequencer, 2, sequencer.time_tracker, quick_long_fade, 3)
      line(sequencer, 2, sequencer.time_tracker+2, quick_long_fade, 2)
      line(sequencer, 2, sequencer.time_tracker+2, quick_long_fade, 4)
      sequencer.time_tracker += 4

    #### 1/4 note rounds strobe loop
    bright_list = [0.10, 0.18, 0.30, 0.50, 0.70, 1]
    notes = [1, 1, 0.75, 0.5, 0.25, 0.125]
    loops = [1, 2, 3, 4, 5, 6]
    
    for j in range(6):
        
      ##### 1/4 note round (4 beats)
      tri_brightness = bright_list[j]
      note_div = notes[j]
      for i in range(loops[j]):
        line(sequencer, note_div, sequencer.time_tracker, lambda x, arg=tri_brightness: strobe(x, arg), 1) 
        line(sequencer, note_div, sequencer.time_tracker+note_div, lambda x, arg=tri_brightness: strobe(x, arg), 2) 
        line(sequencer, note_div, sequencer.time_tracker+(note_div*2), lambda x, arg=tri_brightness: strobe(x, arg), 3) 
        line(sequencer, note_div, sequencer.time_tracker+(note_div*3), lambda x, arg=tri_brightness: strobe(x, arg), 4)

        sequencer.time_tracker += note_div*4
    
    ##### on off rest sequence
    notes = 0.25 
    loops = [4, 2, 2, 2, 1, 1]
    rests = [1, 2, 2, 2, 1, 1]
    # first rest
    sequencer.time_tracker += 1

    for j in range(6):
      ##### 1/4 note round (4 beats)
      tri_brightness = 1
      note_div = notes
      for i in range(loops[j]):
        line(sequencer, note_div, sequencer.time_tracker, lambda x, arg=tri_brightness: strobe(x, arg), 1) 
        line(sequencer, note_div, sequencer.time_tracker+note_div, lambda x, arg=tri_brightness: strobe(x, arg), 2) 
        line(sequencer, note_div, sequencer.time_tracker+(note_div*2), lambda x, arg=tri_brightness: strobe(x, arg), 3) 
        line(sequencer, note_div, sequencer.time_tracker+(note_div*3), lambda x, arg=tri_brightness: strobe(x, arg), 4)

        sequencer.time_tracker += note_div*4 
        # add rest
        sequencer.time_tracker += rests[j]
        
    #### ALL STROBE
    for i in range(4):
      line_strobe( sequencer, 8, sequencer.time_tracker, i+1, 255, 154, 0)
    # add 4 
    sequencer.time_tracker += 4
    
    #### All strobe faster
    for i in range(4):
      line_strobe( sequencer, 8, sequencer.time_tracker, i+1, 255, 173, 0)
    # add 4 
    sequencer.time_tracker += 4
    
    #### All strobe faster
    for i in range(4):
      line_strobe( sequencer, 8, sequencer.time_tracker, i+1, 255, 191, 0)
    # add 4 
    sequencer.time_tracker += 4
    
    #### All off for a second
    sequencer.time_tracker += 2

    ##### hurricane, loop twice
    for j in range(2):
      for i in range(4):
          line(sequencer, 4, sequencer.time_tracker+(i), hurricane, (i+1))
      sequencer.time_tracker += 7

    ##### all shaky
    for j in range(2):
      for i in range(4):
          line(sequencer, 4, sequencer.time_tracker+(i), shaky, (i+1))
      sequencer.time_tracker += 7

    ##### Other - long attack circles
    for j in range(2):
      for i in range(4):
        line(sequencer, 2, sequencer.time_tracker+(i*0.5), long_attack, (i+1))
      sequencer.time_tracker += 3

    ##### l/r sequence
    notes = [0.5, 0.25, 0.5, 0.25, 0.5, 0.125] 
    loops = [2, 4, 2, 4, 2, 8]
    brights = [0.42, 0.67, 0.70, 0.80, 0.90, 1]

    for j in range(6):
        
      ##### 1/4 note round (4 beats)
      tri_brightness = brights[j]
      note_div = notes[j]
      
      for i in range(loops[j]):
        # 2 and 3
        line(sequencer, note_div, sequencer.time_tracker, lambda x, arg=tri_brightness: strobe(x, arg), 2) 
        line(sequencer, note_div, sequencer.time_tracker, lambda x, arg=tri_brightness: strobe(x, arg), 3) 
        # 1 and 4
        line(sequencer, note_div, sequencer.time_tracker+note_div, lambda x, arg=tri_brightness: strobe(x, arg), 2) 
        line(sequencer, note_div, sequencer.time_tracker+note_div, lambda x, arg=tri_brightness: strobe(x, arg), 3) 
        
        sequencer.time_tracker += note_div*2

    ##### 1/4 loop with strobe
    for i in range(4):
      line_strobe( sequencer, 1, sequencer.time_tracker, i+1, 255, 199, 0)
    # add 4 
    sequencer.time_tracker += 4

    ##### random strobe: 185
    # seq, beats, offset, channel, bright, rate, dur, noise):
    for i in range(4):
      line_random_strobe( sequencer, 4, sequencer.time_tracker, i+1, 255, 185, 0, 68)
    sequencer.time_tracker += 4

    ##### all strobe medium
    for i in range(4):
      line_strobe(sequencer, 12, sequencer.time_tracker, i+1, 255, 174, 0)
    sequencer.time_tracker += 12

    ##### all strobe medium2
    for i in range(4):
      line_strobe(sequencer, 2, sequencer.time_tracker, i+1, 255, 213, 0)
    sequencer.time_tracker += 2
    
    ##### all on
    for i in range(4):
      line(sequencer, 8, sequencer.time_tracker, lambda x, arg=1: strobe(x, arg), i+1)
    sequencer.time_tracker += 8

    ##### all long decay, 21 beats or 14 seconds 
    for i in range(4):
      line(sequencer, 21, sequencer.time_tracker, long_decay, i+1)
    sequencer.time_tracker += 21


    ####### end, set the composition length, and return the full sequence #######
    sequencer.set_comp_length()

    return sequencer

if __name__ == "__main__":
    sequencer = create_composition()
    # Choose your preferred running method:
    # 1. Simple:
    # sequencer.run_simple()
    # 2. Time-based:
    # sequencer.run_time_based()
    # 3. Async:
    asyncio.run(sequencer.run_async())