import math

SAMPLE_RATE = 44100  # Sample rate in Hz

class Synth:

    def __init__(self, dac):
        self.dac = dac
        self.volume = 0.5  # Default volume level (0.0 to 1.0)
        self.current_note = None
        self.waveform = 'sine'  # Default waveform type

    def sine_wave(self, frequency, sample_number):
        t = sample_number / SAMPLE_RATE
        return math.sin(2 * math.pi * frequency * t)

    def note_on(self, frequency):
        self.current_note = frequency
        print ("Playing:", frequency)

        sample_number = 0  # Initialize sample number for waveform generation
        sample = self.sine_wave(frequency, sample_number)
        #send the sample to the DAC with volume adjustment
        self.dac.write(sample * self.volume)

    def note_off(self):
        self.current_note = None
        self.dac.write(0)  # Stop the sound by sending zero to the DAC
        print("Note off")