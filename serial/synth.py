import math

class Synth:

    def __init__(self, dac):
        self.dac = dac
        self.volume = 0.5  # Default volume level (0.0 to 1.0)
        self.current_note = None
        self.waveform = 'sine'  # Default waveform type

    def sine_wave(self, frequency, time):
        return math.sin(2 * math.pi * frequency * time)

    def note_on(self, frequency):
        self.current_note = frequency
        print ("Playing:", frequency)

        #temporary sample generation for demonstration purposes
        t = 0
        sample = self.sine_wave(frequency, t)
        #send the sample to the DAC with volume adjustment
        self.dac.write(sample * self.volume)

    def note_off(self):
        self.current_note = None
        print("Note off")