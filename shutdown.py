from array import array
from compose_utils import beats_to_ticks
from compose_utils import line, line_strobe, peek_ad, sparkle20, two_bumps, on_off, quick_long_fade, strobe, hurricane, shaky, long_attack, line_random_strobe, long_decay, beats_to_ticks
import time
import heapq
import asyncio
from ola.ClientWrapper import ClientWrapper
from dataclasses import dataclass
from typing import List, Callable


# just using the code from main.py to create a seperate "shutdown" event
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
                    # print(f"{self.current_tick}: {channels} {cue}")
                elif next_tick > self.current_tick:
                    # Stop processing if the next event is for a future tick
                    break

            # Increment tick and wrap around
            if self.current_tick < self.composition_length:
              self.current_tick = (self.current_tick + 1) % self.composition_length
            else:
              # make sure all are off
              for i in range(4):
                channel_num = i+1
                sequencer.send_dmx({ 
                  channel_num: 0,
                  channel_num + 1: 0, 
                  channel_num + 2: 0
                })

            # Calculate precise sleep time
            elapsed = time.time() - tick_start
            sleep_time = max(0, (1/self.ticks_per_second) - elapsed)
            await asyncio.sleep(sleep_time)

    # #Async system with precise timing
    # async def run_async(self):
    #     # print_it = FANCY_PRINT()
    #     while True:
    #         tick_start = time.time()

    #         # Find and execute all events for current tick
    #         for event_tick, channels in self.events:
    #             if event_tick == self.current_tick:
    #                 self.send_dmx(channels)
    #                 print(f"{self.current_tick}: {channels}")
    #                 # print_it.update( channels )


    #         # Increment tick and wrap around
    #         self.current_tick = (self.current_tick + 1) % self.composition_length

    #         # Calculate precise sleep time
    #         elapsed = time.time() - tick_start
    #         sleep_time = max(0, (1/self.ticks_per_second) - elapsed)
    #         await asyncio.sleep(sleep_time)

# Example usage with easy-to-read composition definition
def create_composition():
    # create the sequecer
    sequencer = DMXSequencer()

    # variable to track time (in beats)
    sequencer.time_tracker = 0.0

    # variable for on_off intensity
    tri_brightness = 0.0
    ######### begin jeremy test #######
    for i in range(4):
      line(sequencer, 21, sequencer.time_tracker, long_decay, i+1) 

    

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