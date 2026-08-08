import math
import synthio
import time
import json

from scale import Scale
from synth_presets import Synth_Presets
from note import TemporaryNote

#To add:
#pitch bend
#vibrato/tremolo
#Volume
#Recording
#arpeggiation


class SynthWrapper:
    RECORDING_CHANNELS = 4
    def __init__(self, scale : Scale, preset = Synth_Presets.PIANO, sample_rate = 22050):
        self.sample_rate = sample_rate
        self.scale = scale
        self.preset = Synth_Presets(preset)
        self.synth = synthio.Synthesizer(self.sample_rate)
        self.notes = [synthio.Note(frequency=synthio.midi_to_hz(scale.get_midi_note(i)), 
                                   waveform=self.preset.waveform, 
                                   envelope=self.preset.envelope)
                        for i in range(1, 8)]
        #TODO: Add functionality for held notes
        self.held_notes = []
        self.recordings = [[]] * SynthWrapper.RECORDING_CHANNELS
        self.record_start_times = [None] * SynthWrapper.RECORDING_CHANNELS
        
    #Play a note and buffer it for modulation
    #Note number should be 1-8 for scale notes
    #   For intervals before, -1 refers to 1 below the root
    def pressActive(self, note_number):
        if 1 <= note_number <= 8:
            note = self.notes(note_number-1)
        else:
            note = synthio.Note(frequency=synthio.midi_to_hz(self.scale.get_midi_note(note_number)),
                                )

        #Broadcast it is being played and its frequency/preset
        #TODO?: Add a way to increase sustain and add to held notes if necessary
        #self.held_notes.append(note)

        self.log_event("note-pressed", note)
        self.synth.press(note)

    #Release a note from the active buffer
    def releaseActive(self, note):
        #Broadcast relase of note
        self.log_event("note-released", note)
        #Remove note from modulation buffer
        self.synth.release(note)

    #Record currently played notes and modulations
    def record(self, record_channel_index):
        self.recordings[record_channel_index].clear()
        self.record_start_times[record_channel_index] = time.monotonic()
        #TODO: Broadcast recording start for OLED to display
        #Keep track of time, and time of:
            #note presses,
            #modulations,
            #note releases
    
    def end_record(self, record_channel_index):
        self.record_start_times[record_channel_index] = None
        #TODO: Broadcast recording pause for OLED to display
    
    def play_record(self, record_channel_index):
        #TODO: Complete play record
        pass


    def log_event(self, event_type, value):
        for i in range(SynthWrapper.RECORDING_CHANNELS):
            if self.record_start_times[i] is not None:
                self.recordings[i].append({'time':time.monotonic() - self.record_start_time,
                                    'event_type':event_type,
                                    'value':value})


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