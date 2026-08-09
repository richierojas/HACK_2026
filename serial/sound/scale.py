class Scale:
    MAJOR = 'maj'
    MINOR = 'min'
    QUALITY_OFFSETS = { 'maj':[0, 2, 4, 5, 7, 9, 11, 12],  'min':[0, 2, 3, 5, 7, 8, 10, 12] }
    KEY_OFFSETS = {
        'C': 0,
        'C#': 1,
        'Db': 1,
        'D': 2,
        'D#': 3,
        'Eb': 3,
        'E': 4,
        'Fb': 4,
        'E#': 5,
        'F': 5,
        'F#': 6,
        'Gb': 6,
        'G': 7,
        'G#': 8,
        'Ab': 8,
        'A': 9,
        'A#': 10,
        'Bb': 10,
        'B': 11,
        'Cb': 11,
        'B#': 0,
    }
    def __init__(self, key='C', octave = 4, quality = MAJOR):
        if key not in Scale.KEY_OFFSETS:
            raise ValueError(f"Invalid key: {key}")

        if quality not in (Scale.MAJOR, Scale.MINOR):
            raise ValueError(f"Invalid scale quality: {quality}")

        self.key = key
        self.octave = octave
        self.quality = quality

    def __str__(self):
        return f"{self.key}{self.quality}{self.octave}"

    # Returns midi number given a note number relative to the root
    # 1 is the root, 2 is 1 above the root, etc
    # -1 is 1 below the root, etc
    # 'accidental' refers to its musical sense (flat, natural, sharp) for (-1, 0, +1)
    def get_midi_note(self, note_number, accidental_offset=0, octave_offset = 0):
        if note_number > 0:
            step = note_number - 1 #Correct 1+ to an index from 0+
        if note_number < 0:
            step = note_number     #Leave -1 as is for 1 below
        if note_number == 0:
            raise ValueError(f"Note number must be a scale interval, 0 is not allowed")

        octave_change, note_index = divmod(step, 7)

        note = 12 * (self.octave+1+octave_offset+octave_change) + Scale.KEY_OFFSETS[self.key] + Scale.QUALITY_OFFSETS[self.quality][note_index]
        note += accidental_offset
        return note