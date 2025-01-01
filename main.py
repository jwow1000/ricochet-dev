from array import array
from utils import ADSR
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
        while True:
            tick_start = time.time()
            
            # Find and execute all events for current tick
            for event_tick, channels in self.events:
                if event_tick == self.current_tick:
                    self.send_dmx(channels)
                    print(f"channels: {channels}")
            
            # Increment tick and wrap around
            self.current_tick = (self.current_tick + 1) % self.composition_length
            
            # Calculate precise sleep time
            elapsed = time.time() - tick_start
            sleep_time = max(0, (1/self.ticks_per_second) - elapsed)
            await asyncio.sleep(sleep_time)

# Example usage with easy-to-read composition definition
def create_composition():
    # print(f"hello?")
    sequencer = DMXSequencer()
    
    # Helper function to convert beats to ticks
    def beats_to_ticks(beats, bpm=90):
        return int((beats * 60 * sequencer.ticks_per_second) / bpm)
    
    # Example events
    # Flash light 1 at full brightness
    # sequencer.add_event(0, {1: 255})
    
    # Set multiple lights at once
    # sequencer.add_event(50, {
    #     1: 128,
    #     2: 128
    # })
    
    # Using musical timing
    # sequencer.add_event(
    #     beats_to_ticks(4),  # On beat 4
    #     {1: 255, 2: 255}    # Full brightness on channels 1 and 2
    # )

    for i in range(100):
        ramp = (i/100) * 255
        sequencer.add_event(
            i,
            {1: int(ramp)}
        )
    for i in range(100):
        ramp = 255 - ((i/100) * 255)
        sequencer.add_event(
            i,
            {2: int(ramp)}
        )
    
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