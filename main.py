import time
from array import array
from utils import ADSR
from ola.ClientWrapper import ClientWrapper

def DmxSent(state):
    if not state.Succeeded():
        print('Error: DMX send failed')
    wrapper.Stop()

def SendDMX(cli, channels):
    # Create a DMX buffer of 512 bytes (default for DMX512)
    dmx_data = [0] * DMX_CHANNELS

    # Update the channels you want to modify
    for channel, value in channels.items():
        dmx_data[channel - 1] = value  # DMX is 1-indexed, so adjust to 0-indexed

    # Send the DMX data
    cli.SendDmx(universe, dmx_data, DmxSent)  

# Set your universe number (usually 1)
universe = 1

# set dmx channels, 4 for ricochet
DMX_CHANNELS = 4

# create the data array
data = array('B', [0] * DMX_CHANNELS)

# Create a new client wrapper
wrapper = ClientWrapper()

# Get the client
client = wrapper.Client()

# Start the main loop
wrapper.Run()

short_attack_decay = ADSR(attack=1, decay=20, sustain=0, release=20, max_value=127)

def run_dmx_loop(loop_duration, tick_interval):
    start_time = time.time()
    while time.time() - start_time < loop_duration:
        progress = time.time() - start_time

        # movement 1 first 8 seconds
        while progress >= 0 and progress < 8:
            short_attack_decay.trigger( 1 )
            value = short_attack_decay.process()
            channels = {1: value}
            SendDMX(client, channels)
            print(f"Envelope Value: {channels}") 
            time.sleep(tick_interval)  # Sleep for the interval (30ms in this case)
            
            if progress > 6:
                short_attack_decay.trigger = 0

if __name__ == "__main__":
  
    loop_duration = 240  # Total duration of the loop in seconds (4 minutes)
    tick_interval = 0.03  # Tick interval in seconds (30ms)
    
    run_dmx_loop(loop_duration, tick_interval)