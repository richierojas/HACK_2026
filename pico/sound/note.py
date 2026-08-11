import synthio

class TemporaryNote:
    def __init__(self, note : synthio.Note, duration):
        self.note = note
        self.duration = duration