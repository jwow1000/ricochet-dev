from array import array
import time
from ola.ClientWrapper import ClientWrapper
import sys

class LightingSequence:
    def __init__(self):
        self.wrapper = None
        self.client = None
        self.universe = 1  # Change this to match your OLA universe
        self.TICK_INTERVAL = 0.1  # 100ms tick interval
        self.sequence_start_time = None
        self.total_duration = 240  # 4 minutes in seconds
        
        # DMX channels for each light (adjust based on your setup)
        self.lights = {
            'light1': {'start_channel': 1},
            'light2': {'start_channel': 11},
            'light3': {'start_channel': 21},
            'light4': {'start_channel': 31}
        }
        
    def dmx_sent(self, state):
        if not state.Succeeded():
            print('Error: DMX send failed')
            self.wrapper.Stop()

    def tick(self):
        if self.sequence_start_time is None:
            self.sequence_start_time = time.time()
        
        current_time = time.time()
        elapsed_time = current_time - self.sequence_start_time
        
        # Reset sequence if we've reached the end
        if elapsed_time >= self.total_duration:
            self.sequence_start_time = current_time
            elapsed_time = 0
            print("Restarting sequence")
        
        # Create DMX data array
        data = array('B', [0] * 512)  # Initialize all channels to 0
        
        # Example lighting sequence
        # Modify these timings and values to create your desired composition
        for light_name, light_info in self.lights.items():
            base_channel = light_info['start_channel']
            
            # Example timing patterns (adjust these for your composition)
            if 0 <= elapsed_time % 10 < 5:  # Alternating 5-second patterns
                # Strobe effect
                data[base_channel - 1] = 255  # Full brightness
                data[base_channel] = 200      # Fast strobe speed
                data[base_channel + 1] = 0    # No rotation
            elif 5 <= elapsed_time % 10 < 7:  # 2-second break
                # Dim wash light effect
                data[base_channel - 1] = 50   # Low brightness
                data[base_channel] = 0        # No strobe
                data[base_channel + 1] = 128  # Slow rotation
            else:  # 3-second different effect
                # Bright wash light effect
                data[base_channel - 1] = 200  # High brightness
                data[base_channel] = 0        # No strobe
                data[base_channel + 1] = 255  # Fast rotation
        
        # Send DMX data
        self.client.SendDmx(self.universe, data, self.dmx_sent)
        
        # Schedule next tick
        self.wrapper.AddEvent(self.TICK_INTERVAL, self.tick)

    def run(self):
        self.wrapper = ClientWrapper()
        self.client = self.wrapper.Client()
        
        # Start the tick
        self.wrapper.AddEvent(0, self.tick)
        
        # Start the client
        try:
            self.wrapper.Run()
        except KeyboardInterrupt:
            print('Interrupted by user')
            sys.exit(0)

if __name__ == '__main__':
    sequence = LightingSequence()
    
    print("Starting lighting sequence (4-minute loop)")
    print("Press Ctrl+C to quit")
    
    sequence.run()