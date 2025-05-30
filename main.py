from array import array
from compose_utils import beats_to_ticks
from compose_utils import line, line_strobe, peek_ad, sparkle20, two_bumps, on_off, quick_long_fade, strobe, hurricane, shaky, long_attack, line_random_strobe, long_decay, beats_to_ticks, long_decay_chill
import time
import heapq
import asyncio
from ola.ClientWrapper import ClientWrapper
from dataclasses import dataclass
from typing import List, Callable

@dataclass
class DMXSequencer:
    def __init__(self):
        self.event_queue = []
        self.event_index = 0
        self.current_tick = 0
        self.ticks_per_second = 50  # 20ms per tick
        self.composition_length = 12000  # 4 minutes at 50 ticks/second
        self.time_tracker = 0
        self.events = []
        self.wrapper = ClientWrapper()
        self.client = self.wrapper.Client()
        self.universe = 1
        self.data = array('B', [0] * 512)  # Global DMX data array

    def set_comp_length(self):
        self.composition_length = beats_to_ticks( self.time_tracker )

    def dmx_sent(self, state):
        if not state.Succeeded():
            print('Error: DMX send failed')

    def send_dmx(self, channels):
        # Update only the specified channels
        for channel, value in channels.items():
            self.data[channel - 1] = value  # Convert from 1-indexed to 0-indexed
        # Send the DMX data
        self.client.SendDmx(self.universe, self.data, self.dmx_sent)


    def add_event(self, tick, channels):
        """
        Add a lighting event
        tick: when to trigger the event
        channels: dict of {channel: value}
        """

        heapq.heappush(self.event_queue, (tick, self.event_index, channels))
        self.event_index += 1
        
    # Async system with precise timing
    async def run_async(self):
        while True:
            tick_start = time.time()

            # Process and execute events for the current tick
            while self.event_queue:
                next_tick, cue, channels = self.event_queue[0]  # Peek at the next event

                if next_tick == self.current_tick:
                    # Execute the event and remove it from the queue
                    heapq.heappop(self.event_queue)
                    self.send_dmx(channels)
                    # print(f"event: ${channels}")
                elif next_tick > self.current_tick:
                    # Stop processing if the next event is for a future tick
                    break

            # Increment tick and wrap around
            self.current_tick += 1 

            # Check if the composition loop has completed
            if self.current_tick >= self.composition_length:
                print("Composition loop complete. Resetting...")
                self.reset_composition()  # Call the reset method


            # Calculate precise sleep time
            elapsed = time.time() - tick_start
            sleep_time = max(0, (1/self.ticks_per_second) - elapsed)
            await asyncio.sleep(sleep_time)

    
    # Example usage with easy-to-read composition definition
    def populate_composition(self):
        # create the sequecer
        # sequencer = DMXSequencer()

        # variable to track time (in beats)
        self.time_tracker = 0.0

        # variable for on_off intensity
        tri_brightness = 0.0
        ######### begin jeremy test #######
        # line(self, 21, self.time_tracker, long_decay, 1) 
        # self.time_tracker += 21

        # line(self, 18, self.time_tracker, sparkle20, 1)
        # self.time_tracker += 18
        
        
        ########### begin composition ############
        ####### hurricane calm for a while "chill mode" 10-15 minutes
        for j in range(50):
          for i in range(4):
              line(self, 21, self.time_tracker, long_decay_chill, (i+1))
          self.time_tracker += 21

          
        #### all off for 10 seconds( 15 beats )
        # make sure all are off
        for i in range(4):
          channel_num = i+1
          self.send_dmx({ 
            channel_num: 0,
            channel_num + 1: 0, 
            channel_num + 2: 0
          })

        self.time_tracker += 15
        # print(f"check tracker: {self.qtime_tracker}")

        ##### see peek cycle 14 seconds(21 beats) 
        line(self, 3, self.time_tracker, peek_ad, 1)
        line(self, 3, self.time_tracker+5.25, peek_ad, 2)
        line(self, 3, self.time_tracker+10.50, peek_ad, 3)
        line(self, 3, self.time_tracker+15.75, peek_ad, 4)

        self.time_tracker += 21

        #### random no strobe 12 seconds(18 beats)
        line(self, 18, self.time_tracker, sparkle20, 1)
        line(self, 18, self.time_tracker, sparkle20, 2)
        line(self, 18, self.time_tracker, sparkle20, 3)
        line(self, 18, self.time_tracker, sparkle20, 4)

        self.time_tracker += 18

        # 1/4 round 8 seconds, 12 beats, 3 4beat loops
        tri_brightness = 0.5
        for i in range(3):
          line(self, 2, self.time_tracker, lambda x, arg=tri_brightness: on_off(x, arg), 1) 
          line(self, 2, self.time_tracker+1, lambda x, arg=tri_brightness: on_off(x, arg), 2) 
          line(self, 2, self.time_tracker+2, lambda x, arg=tri_brightness: on_off(x, arg), 3) 
          line(self, 2, self.time_tracker+3, lambda x, arg=tri_brightness: on_off(x, arg), 4)

          self.time_tracker += 4 


        #### cross two bumps, 7secs, loop
        for i in range(2):
          line(self, 2, self.time_tracker, two_bumps, 1)
          line(self, 2, self.time_tracker, two_bumps, 3)
          line(self, 2, self.time_tracker+2, two_bumps, 2)
          line(self, 2, self.time_tracker+2, two_bumps, 4)
          self.time_tracker += 4

        #### cross quick attack, 7secs, 
        for i in range(2):
          line(self, 2, self.time_tracker, quick_long_fade, 1)
          line(self, 2, self.time_tracker, quick_long_fade, 3)
          line(self, 2, self.time_tracker+2, quick_long_fade, 2)
          line(self, 2, self.time_tracker+2, quick_long_fade, 4)
          self.time_tracker += 4

        #### 1/4 note rounds strobe loop
        bright_list = [0.10, 0.18, 0.30, 0.50, 0.70, 1]
        notes = [1, 1, 0.75, 0.5, 0.25, 0.125]
        loops = [1, 2, 3, 4, 5, 6]

        for j in range(6):

          ##### 1/4 note round (4 beats)
          tri_brightness = bright_list[j]
          note_div = notes[j]
          for i in range(loops[j]):
            line(self, note_div, self.time_tracker, lambda x, arg=tri_brightness: strobe(x, arg), 1) 
            line(self, note_div, self.time_tracker+note_div, lambda x, arg=tri_brightness: strobe(x, arg), 2) 
            line(self, note_div, self.time_tracker+(note_div*2), lambda x, arg=tri_brightness: strobe(x, arg), 3) 
            line(self, note_div, self.time_tracker+(note_div*3), lambda x, arg=tri_brightness: strobe(x, arg), 4)

            self.time_tracker += note_div*4

        ##### on off rest sequence
        notes = 0.25 
        loops = [4, 2, 2, 2, 1, 1]
        rests = [1, 2, 2, 2, 1, 1]
        # first rest
        self.time_tracker += 1

        for j in range(6):
            
          ##### 1/4 note round (4 beats)
          tri_brightness = 1
          note_div = notes
          for i in range(loops[j]):
            line(self, note_div, self.time_tracker, lambda x, arg=tri_brightness: strobe(x, arg), 1) 
            line(self, note_div, self.time_tracker+note_div, lambda x, arg=tri_brightness: strobe(x, arg), 2) 
            line(self, note_div, self.time_tracker+(note_div*2), lambda x, arg=tri_brightness: strobe(x, arg), 3) 
            line(self, note_div, self.time_tracker+(note_div*3), lambda x, arg=tri_brightness: strobe(x, arg), 4)

            self.time_tracker += note_div*4 
            # add rest
            self.time_tracker += rests[j]

        #### ALL STROBE
        for i in range(4):
          line_strobe( self, 8, self.time_tracker, i+1, 255, 154, 0)
        # add 4 
        self.time_tracker += 4

        #### All strobe faster
        for i in range(4):
          line_strobe( self, 8, self.time_tracker, i+1, 255, 173, 0)
        # add 4 
        self.time_tracker += 4

        #### All strobe faster
        for i in range(4):
          line_strobe( self, 8, self.time_tracker, i+1, 255, 191, 0)
        # add 4 
        self.time_tracker += 4

        #### All off for a second
        self.time_tracker += 2

        ##### hurricane, loop twice
        for j in range(2):
          for i in range(4):
              line(self, 4, self.time_tracker+(i), hurricane, (i+1))
          self.time_tracker += 7

        ##### all shaky
        for j in range(2):
          for i in range(4):
              line(self, 4, self.time_tracker+(i), shaky, (i+1))
          self.time_tracker += 7

        ##### Other - long attack circles
        for j in range(2):
          for i in range(4):
            line(self, 2, self.time_tracker+(i*0.5), long_attack, (i+1))
          self.time_tracker += 3

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
            line(self, note_div, self.time_tracker, lambda x, arg=tri_brightness: strobe(x, arg), 2) 
            line(self, note_div, self.time_tracker, lambda x, arg=tri_brightness: strobe(x, arg), 3) 
            # 1 and 4
            line(self, note_div, self.time_tracker+note_div, lambda x, arg=tri_brightness: strobe(x, arg), 2) 
            line(self, note_div, self.time_tracker+note_div, lambda x, arg=tri_brightness: strobe(x, arg), 3) 

            self.time_tracker += note_div*2

        ##### 1/4 loop with strobe
        for i in range(4):
          line_strobe( self, 1, self.time_tracker, i+1, 255, 199, 0)
        # add 4 
        self.time_tracker += 4

        ##### random strobe: 185
        # seq, beats, offset, channel, bright, rate, dur, noise):
        for i in range(4):
          line_random_strobe( self, 4, self.time_tracker, i+1, 255, 185, 0, 68)
        self.time_tracker += 4

        ##### all strobe medium
        for i in range(4):
          line_strobe(self, 12, self.time_tracker, i+1, 255, 174, 0)
        self.time_tracker += 12

        ##### all strobe medium2
        for i in range(4):
          line_strobe(self, 2, self.time_tracker, i+1, 255, 213, 0)
        self.time_tracker += 2

        ##### all on
        for i in range(4):
          line(self, 8, self.time_tracker, lambda x, arg=1: strobe(x, arg), i+1)
        self.time_tracker += 8

        ##### all long decay, 21 beats or 14 seconds 
        for i in range(4):
          line(self, 21, self.time_tracker, long_decay, i+1)
        self.time_tracker += 21


        ####### end, set the composition length, and return the full sequence #######
        self.set_comp_length()

    def reset_composition(self):
        self.event_queue = []  # Clear the event queue
        self.event_index = 0    # Reset the event index
        self.current_tick = 0   # Reset the current tick
        self.time_tracker = 0.0 # reset the time tracker
        # Re-populate the event queue
        self.populate_composition() # call the populate composition method

def create_composition():
    sequencer = DMXSequencer()
    sequencer.populate_composition() # populate the composition once on creation
    return sequencer

if __name__ == "__main__":
    sequencer = create_composition()
     
    asyncio.run(sequencer.run_async())