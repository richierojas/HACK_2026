import synthio

class Synth_Presets:
    FOLDER = "sound/sound_files/"
    PIANO_FILE = FOLDER + "pianoc1.raw"
    GUITAR_FILE = FOLDER + "guitarc3.raw"
    BASS_FILE = FOLDER + "bassc3.raw"

    #Envelopes are what make these read as different instruments as much as the
    #waveforms do: piano rings and decays, guitar is brighter and shorter, bass
    #sustains hard and stops quickly.
    PIANO_ENVELOPE = synthio.Envelope(
                        attack_time=0.005,
                        decay_time=0.8,
                        sustain_level=0.25,
                        release_time=0.8,
                    )
    #Release times all match piano's 0.8s deliberately. They used to be 0.4 and
    #0.25, which made guitar 3.7dB and bass 5.4dB quieter than piano - not
    #because the waveforms differ (they are within 1dB of each other in RMS) but
    #because presses are short, so the ringing tail is most of what you hear.
    #Decay and sustain still differ, so each instrument keeps its character;
    #only the tail length is equalised.
    #Guitar is deliberately NOT piano-shaped: a plucked string attacks almost
    #instantly and then dies away, where a piano rings on. The low sustain
    #(0.15 vs piano's 0.25) and shorter decay are what stop the two sounding
    #alike. It costs energy, which the gain in PRESETS makes back.
    GUITAR_ENVELOPE = synthio.Envelope(
                        attack_time=0.002,
                        decay_time=0.45,
                        sustain_level=0.15,
                        release_time=0.7,
                    )
    BASS_ENVELOPE = synthio.Envelope(
                        attack_time=0.005,
                        decay_time=0.3,
                        sustain_level=0.60,
                        release_time=0.8,
                    )

    #Uppercase: the OLED font has no lowercase glyphs, so a lowercase name
    #renders as a blank row. These are also the keys code.py looks instruments
    #up by, so the menu label and the dictionary key cannot drift apart.
    PIANO = "PIANO"
    GUITAR = "GUITAR"
    BASS = "BASS"

    #(file, envelope, gain). Gain trims the last of the loudness difference the
    #envelopes leave behind, so switching instrument does not change how loud
    #the instrument is. Keep gains at or below 1.39: above that, 8 overlapping
    #voices push past full scale and synthio clips internally.
    #(file, envelope, gain, octave_offset)
    #
    #octave_offset spreads the three across registers, which is the single
    #strongest cue that they are different instruments - without it they all
    #played identical pitches and only the timbre changed:
    #   bass   an octave below piano   65..131Hz
    #   piano  the middle             131..262Hz
    #   guitar an octave above        262..523Hz
    #Guitar's gain drops when it moves up because the ear hears higher notes as
    #louder; the 0.89 is 1.14 (which sounded right in the middle register)
    #scaled by the A-weighted difference between the two registers.
    #
    #gain equalises PERCEIVED loudness, which is not the same as equal
    #amplitude. It accounts for two things: the envelope energy each instrument
    #delivers on a short press, and how loud its spectrum reads to the ear at
    #the register it plays in (low notes with few harmonics sound much quieter
    #than bright ones at identical amplitude).
    #Keep gains at or below 1.39 - beyond that 8 overlapping voices push past
    #full scale and synthio clips internally.
    #filter_sweep = (start_hz, end_hz, seconds, Q) or None.
    #
    #This is the one thing a fixed wavetable plus an ADSR cannot fake. Every
    #real plucked or struck string starts bright and mellows as it decays - the
    #TIMBRE changes over the note, not just the volume. Without it, changing the
    #waveform and envelope only ever sounds like the same synth with different
    #settings, because the spectrum is frozen for the whole note.
    #Guitar sweeps a low-pass from 8kHz down to 1kHz over half a second, so the
    #pluck rings bright and then dulls the way a real string does.
    #Sweep shape is as much a fingerprint as the waveform. How fast the
    #brightness falls away is a large part of what tells two strings apart:
    #   guitar  an acoustic pluck, mellowing over 0.6s. Plucked at 0.18 along
    #           the string: far enough from the middle that no low harmonic gets
    #           notched out. A notch at h3 leaves a hollow gap that reads as a
    #           lute rather than a guitar.
    #   piano   a felt hammer - less bright, holds its tone much longer (1.2s)
    #   bass    a thumb thump settling onto the fundamental (0.35s). Its
    #           harmonics drop off sharply after h3 - a smooth 1/n rolloff makes
    #           a bass sound like a brass instrument instead.
    #           Bass gain is pinned at the 1.39 ceiling and still sits a little
    #           under the others: a low, fundamental-heavy tone is genuinely
    #           quiet to the ear, and going louder would clip.
    #Each sweep ends ABOVE that instrument's top note so the fundamental always
    #survives; only the harmonics are rolled off.
    PRESETS = {
        PIANO:  (PIANO_FILE,  PIANO_ENVELOPE,  1.00,  0, (6000, 1500, 1.2, 0.7)),
        GUITAR: (GUITAR_FILE, GUITAR_ENVELOPE, 1.22, +1, (4500,  900, 0.6, 0.8)),
        BASS:   (BASS_FILE,   BASS_ENVELOPE,   1.39, -1, (1800,  300, 0.35, 0.9)),
    }

    #Order the instruments menu shows them in
    ALL = (PIANO, GUITAR, BASS)

    def __init__(self, preset=PIANO):
        (self.waveform, self.envelope, self.gain,
         self.octave_offset, self.filter_sweep) = Synth_Presets.get_preset(preset)

    @staticmethod
    #Returns (waveform, envelope, gain, octave_offset, filter_sweep) for a preset
    def get_preset(preset = PIANO):
        filename, envelope, gain, octave_offset, filter_sweep = Synth_Presets.PRESETS[preset]
        return (Synth_Presets.read_raw_wave(filename), envelope, gain,
                octave_offset, filter_sweep)

    @staticmethod
    def read_raw_wave(filename = PIANO):
        with open(filename, "rb") as f:
            raw = bytearray(f.read())
        return memoryview(raw).cast("h")
