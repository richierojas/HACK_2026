import synthio

class Synth_Presets:

    FOLDER = "sound/sound_files/"

    # Files
    PIANO_FILE = FOLDER + "pianoc1.raw"
    GUITAR_FILE = FOLDER + "guitarc3.raw"
    BASS_FILE = FOLDER + "bassc3.raw"

    # Preset names
    PIANO = "PIANO"
    GUITAR = "GUITAR"
    BASS = "BASS"

    #Envelopes
    PIANO_ENVELOPE = synthio.Envelope(
        attack_time=0.005,
        decay_time=0.8,
        sustain_level=0.15,
        release_time=0.4,
    )

    GUITAR_ENVELOPE = synthio.Envelope(
        attack_time=0.003,
        decay_time=0.5,
        sustain_level=0.40,
        release_time=0.4,
    )

    BASS_ENVELOPE = synthio.Envelope(
        attack_time=0.005,
        decay_time=0.3,
        sustain_level=0.60,
        release_time=0.25,
    )

    PRESET_MAP = {
        PIANO:  (PIANO_FILE, PIANO_ENVELOPE),
        GUITAR: (GUITAR_FILE, GUITAR_ENVELOPE),
        BASS:   (BASS_FILE, BASS_ENVELOPE),
    }

    #TODO: implement percussion with percussion scale?
    PRESETS = [
        PIANO,
        GUITAR,
        BASS,
    ]


    def __init__(self, preset=PIANO):
        self.waveform, self.envelope = Synth_Presets.get_preset(preset)
        self.preset = preset

    @staticmethod
    #Returns (waveform, envelope) for a preset
    def get_preset(preset = PIANO):
        filename, envelope = Synth_Presets.PRESET_MAP[preset]
        return (Synth_Presets.read_raw_wave(filename), envelope)

    @staticmethod
    def read_raw_wave(filename = PIANO):
        with open(filename, "rb") as f:
            raw = bytearray(f.read())
        return memoryview(raw).cast("h")