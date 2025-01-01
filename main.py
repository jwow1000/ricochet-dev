from array import array
from utils import ADSR
import time
import asyncio
from ola.ClientWrapper import ClientWrapper
from dataclasses import dataclass
from typing import List, Callable

def dmx_sent(state):
    if not state.Succeeded():
        print('Error: DMX send failed')
    wrapper.Stop()

def send_dmx(cli, channels):
    
    # Update the channels you want to modify
    for channel, value in channels.items():
        data[channel - 1] = value  # DMX is 1-indexed, so adjust to 0-indexed

    # Send the DMX data
    cli.SendDmx(universe, data, DmxSent)  

# Create a new client wrapper
wrapper = ClientWrapper()

# Get the client
client = wrapper.Client()

# Set your universe number (usually 1)
universe = 1

# set dmx channels, 4 for ricochet
DMX_CHANNELS = 4

# create the data array
data = array('B', [0] * DMX_CHANNELS)

@dataclass
class LightEvent:
    tick: int
    channels: List[int]
    values: List[int]

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
    
    # Approach 1: Simple tick-based system
    def run_simple(self):
        while True:
            current_events = [e for e in self.events if e.tick == self.current_tick]
            
            if current_events:
                data = array('B', [0] * 512)
                for event in current_events:
                    for channel, value in zip(event.channels, event.values):
                        data[channel-1] = value
                self.client.SendDmx(self.universe, data, self.dmx_sent)
            
            time.sleep(1/self.ticks_per_second)
            self.current_tick += 1
            if self.current_tick >= self.composition_length:
                self.current_tick = 0

    # Approach 2: Time-based system
    def run_time_based(self):
        start_time = time.time()
        while True:
            elapsed_ticks = int((time.time() - start_time) * self.ticks_per_second)
            current_tick = elapsed_ticks % self.composition_length
            
            if current_tick != self.current_tick:
                self.current_tick = current_tick
                # Process events as above...

    # Approach 3: Async system with precise timing
    async def run_async(self):
        while True:
            tick_start = time.time()
            
            # Find and execute all events for current tick
            for event_tick, channels in self.events:
                if event_tick == self.current_tick:
                    self.send_dmx(channels)
            
            # Increment tick and wrap around
            self.current_tick = (self.current_tick + 1) % self.composition_length
            
            # Calculate precise sleep time
            elapsed = time.time() - tick_start
            sleep_time = max(0, (1/self.ticks_per_second) - elapsed)
            await asyncio.sleep(sleep_time)

# Example usage with easy-to-read composition definition
def create_composition():
    sequencer = DMXSequencer()
    
    # Helper function to convert beats to ticks
    def beats_to_ticks(beats, bpm=120):
        return int((beats * 60 * sequencer.ticks_per_second) / bpm)
    
    # Example events
    # Flash light 1 at full brightness
    sequencer.add_event(0, {1: 255})
    
    # Set multiple lights at once
    sequencer.add_event(50, {
        1: 128,
        2: 128
    })
    
    # Using musical timing
    sequencer.add_event(
        beats_to_ticks(4),  # On beat 4
        {1: 255, 2: 255}    # Full brightness on channels 1 and 2
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