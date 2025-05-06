# linear adsr function
import time

class ADSR:
    def __init__(self, attack, decay, sustain, release, max_value, tick):
        """
        Initialize the ADSR envelope with given parameters.

        :param attack: Time (in ticks) to go from 0 to max_value
        :param decay: Time (in ticks) to go from max_value to sustain level
        :param sustain: The sustain level (0 to max_value)
        :param release: Time (in ticks) to go from sustain level to 0
        :param max_value: The maximum value of the envelope (e.g., brightness, intensity)
        :param tick: The time increment in ticks (the global time step)
        """
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.max_value = max_value
        self.tick = tick
        self.value = 0  # Current value of the envelope
        self.stage = 'idle'  # Current stage of the envelope: 'idle', 'attack', 'decay', 'sustain', 'release'

    def trigger(self, gate):
        """Trigger the ADSR envelope."""
        if gate:
            self.stage = 'attack'
        else:
            self.stage = 'release'

    def process(self):
        """Process the envelope based on the current stage and update the value."""
        if self.stage == 'attack':
            # Attack phase: increment from 0 to max_value
            self.value += self.max_value / self.attack
            if self.value >= self.max_value:
                self.value = self.max_value
                self.stage = 'decay'
        elif self.stage == 'decay':
            # Decay phase: decrement from max_value to sustain level
            self.value -= (self.max_value - self.sustain) / self.decay
            if self.value <= self.sustain:
                self.value = self.sustain
                self.stage = 'sustain'
        elif self.stage == 'sustain':
            # Sustain phase: maintain the sustain value
            self.value = self.sustain
        elif self.stage == 'release':
            # Release phase: decrement from sustain level to 0
            self.value -= self.sustain / self.release
            if self.value <= 0:
                self.value = 0
                self.stage = 'idle'

        return self.value

# Example usage:
def run_adsr_example():
    # Initialize the ADSR envelope
    adsr = ADSR(attack=100, decay=50, sustain=0.5, release=80, max_value=255, tick=1)

    gate = 1  # Trigger the gate (start the envelope)

    while True:
        adsr.trigger(gate)  # Trigger envelope processing
        current_value = adsr.process()  # Process the ADSR envelope for the current tick
        print(f"Envelope Value: {current_value}")  # You can send this value to OLA or any other system
        time.sleep(0.1)  # Sleep for a tick (100ms)
        
        # Example: After 5 seconds, simulate turning the gate off
        if time.time() > 5:
            gate = 0  # Release the gate after 5 seconds


    



def apply_ease_out(t):
    """Ease-out function for smooth decay (quadratic)."""
    return 1 - (1 - t) ** 2

def attack_decay(channel):
    """Simulate short attack and eased decay."""
    # Short attack to 50% intensity
    dmx_data[channel] = TARGET_INTENSITY
    send_dmx()
    time.sleep(TICK_DURATION)  # 100ms tick

    # Eased decay back to 0
    for tick in range(1, DECAY_TICKS + 1):
        t = tick / DECAY_TICKS  # Normalized time (0 to 1)
        eased_value = int(TARGET_INTENSITY * (1 - apply_ease_out(t)))
        dmx_data[channel] = eased_value
        send_dmx()
        time.sleep(TICK_DURATION)