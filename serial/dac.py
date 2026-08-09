import board
import audiobusio
import audiomixer

from sound.synth import Synth_Wrapper
from sound.synth_presets import Synth_Presets
from sound.scale import Scale


class DAC:
    SAMPLE_RATE = 22050
    def __init__(self):
        print("DAC initialized")
        self.scale = Scale('C', 4, Scale.MAJOR)
        self.sample_rate = DAC.SAMPLE_RATE
        self.synth_wrappers = [Synth_Wrapper(scale=self.scale, preset=preset, sample_rate=DAC.SAMPLE_RATE)
                              for preset in Synth_Presets.PRESETS]
        self.active_synth = self.synth_wrappers[0]
        self.audio = audiobusio.I2SOut(
            bit_clock=board.GP1,
            word_select=board.GP2,
            data=board.GP0,
        )
        self.num_voices = len(self.synth_wrappers) * (1 + Synth_Wrapper.RECORDING_CHANNELS)

        self.mixer = audiomixer.Mixer(
            voice_count=self.num_voices,
            sample_rate=self.sample_rate, 
            channel_count=1, 
            bits_per_sample=16, 
            samples_signed=True)

        self.mixer.voice[0].play(self.active_synth.synth)
        self.mixer.voice[0].level = 0.8
        

    def write(self, value):
        print("DAC output:", value)
