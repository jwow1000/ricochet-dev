import time
from array import array
from utils import ADSR
from ola.ClientWrapper import ClientWrapper

def DmxSent(state):
    if not state.Succeeded():
        print('Error: DMX send failed')
    wrapper.Stop()

def SendDMX(cli, channels):
    
    # Update the channels you want to modify
    for channel, value in channels.items():
        data[channel - 1] = value  # DMX is 1-indexed, so adjust to 0-indexed

    # Send the DMX data
    cli.SendDmx(universe, data, DmxSent)  

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

# define global ticks
ticks = 0

short_attack_decay = ADSR(attack=1, decay=20, sustain=0, release=20, max_value=127, tick=1)

def run_dmx_loop(loop_duration, tick_interval):
    
    while ticks < loop_duration:
        print(f"tick time: {progress}") 
        # movement 1 first 8 seconds
        while ticks >= 0 and ticks < 200:
            short_attack_decay.trigger( 1 )
            value = short_attack_decay.process()
            channels = {1: value}
            SendDMX(client, channels)
            print(f"Envelope Value: {channels, progress}") 
            time.sleep(tick_interval)  # Sleep for the interval (30ms in this case)
            ticks = ticks+1

            if progress > 6:
                short_attack_decay.trigger = 0

while True:
    print(f"is this working?")
    loop_duration = 500  # Total duration of the loop in seconds (4 minutes)
    tick_interval = 0.03  # Tick interval in seconds (30ms)
    
    run_dmx_loop(loop_duration, tick_interval)


# Start the main loop
wrapper.Run()
