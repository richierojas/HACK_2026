import synthio

class Synth_Presets:
    FOLDER = "/sound_files/"
    PIANO_FILE = FOLDER + "pianoc1.raw"
    PIANO_ENVELOPE = synthio.Envelope(
                        attack_time=0.005,
                        decay_time=0.8,
                        sustain_level=0.25,
                        release_time=0.8,
                    )
    PIANO = "piano"
    PRESETS = {"piano": (PIANO_FILE, PIANO_ENVELOPE)}

    def __init__(self, preset=PIANO):
        self.waveform, self.envelope = Synth_Presets.get_preset(preset)

    @staticmethod
    #Returns (waveform, envelope) for a preset
    def get_preset(preset = PIANO):
        filename, envelope = Synth_Presets.PRESETS(preset)
        return (Synth_Presets.read_raw_wave(filename), envelope)

    @staticmethod
    def read_raw_wave(filename = PIANO):
        with open(filename, "rb") as f:
            raw = bytearray(f.read())
        return memoryview(raw).cast("h")