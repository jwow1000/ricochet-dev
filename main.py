import time
from array import array
from utils import ADSR
from ola.ClientWrapper import ClientWrapper

def DmxSent(state):
    if not state.Succeeded():
        print('Error: DMX send failed')
    wrapper.Stop()

def SendDMX():
    # Send the data
    client.SendDmx(universe, data, DmxSent)

# Set your universe number (usually 1)
universe = 1

# create the data array
data = array('B', [0] * 512)

# Create a new client wrapper
wrapper = ClientWrapper()

# Get the client
client = wrapper.Client()



# Start the main loop
wrapper.Run()

def run_dmx_loop(adrs, gate, loop_duration, tick_interval):
    start_time = time.time()
    while time.time() - start_time < loop_duration:
        adrs.trigger(gate)
        current_value = adrs.process()
        # Send the DMX data
        SendDMX()
        print(f"Envelope Value: {current_value}")  # Update DMX value here
        time.sleep(tick_interval)  # Sleep for the interval (30ms in this case)

if __name__ == "__main__":
    adsr = ADSR(attack=100, decay=50, sustain=0.5, release=80, max_value=255)
    gate = 1  # Trigger the envelope
    loop_duration = 240  # Total duration of the loop in seconds (4 minutes)
    tick_interval = 0.03  # Tick interval in seconds (30ms)
    
    run_dmx_loop(adsr, gate, loop_duration, tick_interval)