from array import array
from utils import FANCY_PRINT
from compose_utils import line, peek_ad, sparkle20, two_bumps, on_off
import time
import asyncio
from ola.ClientWrapper import ClientWrapper
from dataclasses import dataclass
from typing import List, Callable

@dataclass
class DMXSequencer:
    def __init__(self):
        self.current_tick = 0
        self.ticks_per_second = 50  # 20ms per tick
        self.composition_length = 12000  # 4 minutes at 50 ticks/second
        self.events = []
        self.wrapper = ClientWrapper()
        self.client = self.wrapper.Client()
        self.universe = 1
        self.data = array('B', [0] * 512)  # Global DMX data array

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
        self.events.append((tick, channels))
    
    #Async system with precise timing
    async def run_async(self):
        print_it = FANCY_PRINT()
        while True:
            tick_start = time.time()
            
            # Find and execute all events for current tick
            for event_tick, channels in self.events:
                if event_tick == self.current_tick:
                    self.send_dmx(channels)
                    print_it.update( channels )
                    
            
            # Increment tick and wrap around
            self.current_tick = (self.current_tick + 1) % self.composition_length
            
            # Calculate precise sleep time
            elapsed = time.time() - tick_start
            sleep_time = max(0, (1/self.ticks_per_second) - elapsed)
            await asyncio.sleep(sleep_time)

# Example usage with easy-to-read composition definition
def create_composition():
    # create the sequecer
    sequencer = DMXSequencer()
    
    # variable to track time (in beats)
    time_tracker = 0.0
    
    ########### begin composition ############
    ##### all off for 10 seconds( 15 beats )
    # time_tracker += 15

    ##### see peek cycle 14 seconds(21 beats) 
    # line(sequencer, 3, time_tracker, peek_ad, 1)
    # line(sequencer, 3, time_tracker+5.25, peek_ad, 2)
    # line(sequencer, 3, time_tracker+10.50, peek_ad, 3)
    # line(sequencer, 3, time_tracker+15.75, peek_ad, 4)

    # time_tracker += 21
    
    ##### random no strobe 12 seconds(18 beats)
    # line(sequencer, 18, time_tracker, sparkle20, 1)
    # line(sequencer, 18, time_tracker, sparkle20, 2)
    # line(sequencer, 18, time_tracker, sparkle20, 3)
    # line(sequencer, 18, time_tracker, sparkle20, 4)

    # time_tracker += 18

    # 1/4 round 8 seconds, 12 beats, two 6beat loops
    for i in range(2):
      line(sequencer, 2, time_tracker, on_off, 1) 
      line(sequencer, 2, time_tracker+1, on_off, 2) 
      line(sequencer, 2, time_tracker+2, on_off, 3) 
      line(sequencer, 2, time_tracker+3, on_off, 4)

      time_tracker += 6 

    
    ##### cross two bumps, 7secs, loop
    # for i in range(2):
    #   line(sequencer, 2, time_tracker, two_bumps, 1)
    #   line(sequencer, 2, time_tracker, two_bumps, 3)
    #   line(sequencer, 2, time_tracker+2, two_bumps, 2)
    #   line(sequencer, 2, time_tracker+2, two_bumps, 4)
    #   time_tracker += 4

    
    




    ####### end and return the full sequence #######
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