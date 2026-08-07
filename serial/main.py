from dac import DAC
from synth import Synth

dac = DAC()

synth = Synth(dac)

synth.note_on(440)  # Play A4 note (440 Hz)