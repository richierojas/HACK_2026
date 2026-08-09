import synthio

class Synth_Presets:

    FOLDER = "/sound_files/"

    # Files
    PIANO_FILE = FOLDER + "pianoc1.raw"
    GUITAR_FILE = FOLDER + "guitarc3.raw"
    BASS_FILE = FOLDER + "bassc3.raw"

    KICK_FILE = FOLDER + "kick.raw"
    SNARE_FILE = FOLDER + "snare.raw"
    HIHAT_FILE = FOLDER + "closed_hihat.raw"

    # Preset names
    PIANO = "PIANO"
    GUITAR = "GUITAR"
    BASS = "BASS"
    KICK = "KICK"
    SNARE = "SNARE"
    HIHAT = "HIHAT"

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

    KICK_ENVELOPE = synthio.Envelope(
        attack_time=0.001,
        decay_time=0.25,
        sustain_level=0.0,
        release_time=0.05,
    )

    SNARE_ENVELOPE = synthio.Envelope(
        attack_time=0.001,
        decay_time=0.15,
        sustain_level=0.0,
        release_time=0.05,
    )

    HIHAT_ENVELOPE = synthio.Envelope(
        attack_time=0.001,
        decay_time=0.07,
        sustain_level=0.0,
        release_time=0.03,
    )

    PRESET_MAP = {
        PIANO:  (PIANO_FILE, PIANO_ENVELOPE),
        GUITAR: (GUITAR_FILE, GUITAR_ENVELOPE),
        BASS:   (BASS_FILE, BASS_ENVELOPE),
        KICK:   (KICK_FILE, KICK_ENVELOPE),
 #       SNARE:  (SNARE_FILE, SNARE_ENVELOPE),
 #       HIHAT:  (HIHAT_FILE, HIHAT_ENVELOPE),
    }

    #TODO: implement percussion with percussion scale?
    PRESETS = [
        PIANO,
        GUITAR,
        BASS,
        KICK,
 #       SNARE,
 #       HIHAT,
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