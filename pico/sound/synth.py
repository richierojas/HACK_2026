import synthio
import time
import asyncio
import json

from sound.scale import Scale
from sound.synth_presets import Synth_Presets

#To add:
#pitch bend
#vibrato/tremolo
#Volume
#Recording
#arpeggiation

#A synth that plays one type of sound
#!: Uses async functions for recording. Main loop must allow async operations
#TODO: Recording; each synth (type of sound) should be able to record and play their sounds
class Synth_Wrapper:
    RECORDING_CHANNELS = 1
    def __init__(self, scale : Scale, preset = Synth_Presets.PIANO, sample_rate = 44100):
        self.sample_rate = sample_rate
        self.scale = scale
        self.name = preset
        self.preset = Synth_Presets(preset)
        self.synth = synthio.Synthesizer(sample_rate=self.sample_rate, waveform=self.preset.waveform, envelope=self.preset.envelope)

        self.is_playback = False
        self.is_recording = False

        #? Remove buffering? self.notes = [synthio.Note(frequency=synthio.midi_to_hz(scale.get_midi_note(i))) for i in range(1, 9)]
        self.held_notes = {}
        self.recordings = [[] for _ in range(Synth_Wrapper.RECORDING_CHANNELS)]
        self.recording_synths = [synthio.Synthesizer(sample_rate=self.sample_rate, envelope=self.preset.envelope, waveform=self.preset.waveform)
                                 for _ in range(Synth_Wrapper.RECORDING_CHANNELS)]
        self.record_start_times = [None] * Synth_Wrapper.RECORDING_CHANNELS
        self.existing_playbacks = [None] * Synth_Wrapper.RECORDING_CHANNELS
        self.playback_pause_events = [asyncio.Event() for _ in range(Synth_Wrapper.RECORDING_CHANNELS)]
        for e in self.playback_pause_events:
            e.set() #Create events to pause/start playback, set flag to allow playback on start

    #Returns a deep copy of an envelope object
    @staticmethod
    def copyEnvelope(envelope: synthio.Envelope):
        base = envelope
        return synthio.Envelope(
            attack_time=base.attack_time,
            decay_time=base.decay_time,
            release_time=base.release_time,
            attack_level=base.attack_level,
            sustain_level=base.sustain_level
        )

    #Returns note midi as an ID, used as the key in a dict of stored notes
    def _get_note_key(self, note_number, accidental=0, octave_offset=0):
        return (self.scale.get_midi_note(note_number, accidental_offset=accidental, octave_offset=octave_offset))
        
    #Play a note and buffer it for modulation
    #Note number should be 1-8 for scale notes
    #   For intervals before, -1 refers to 1 below the root
    def press(self, note_number, accidental= 0, octave_offset=0, extra_sustain=False):
        note_key = self._get_note_key(note_number, accidental=accidental, octave_offset=octave_offset)

        if note_key in self.held_notes:
            self.release(note_number=note_number, accidental=accidental, octave_offset=octave_offset)

        #!warn serial logging may cause slowdowns if lots of notes, add separate function for chords
        #print(f'"event": "note-played", "value": "{self.scale}-{note_number}"')

        note = synthio.Note(frequency=synthio.midi_to_hz(self.scale.get_midi_note(note_number, accidental_offset=accidental)),
                            envelope=self.preset.envelope,
                            waveform=self.preset.waveform)

        #Broadcast it is being played and its frequency/preset
        sustain = note.envelope.sustain_level
        #TODO?: Add a way to increase sustain and add to held notes if necessary
        if extra_sustain:
            note.envelope = Synth_Wrapper.copyEnvelope(note.envelope)
            note.envelope.sustain_level = min(1.5*sustain, 1)
            note.envelope.release_time *= 0.66

        #Buffer note for its eventual release
        self.held_notes[note_key] = note

        #self.held_notes.append(note)
        self.log_event("note-pressed", note)
        self.synth.press(note)
        return note

    #Release a note from the active buffer
    def release(self, note_number, accidental = 0):
        note_key = self._get_note_key(note_number=note_number, accidental=accidental)
        note = self.held_notes.pop(note_key, None)
        #Broadcast relase of note
        if note is None:
            print("Attempted to release a key that is not held")
            return

        self.log_event("note-released", note)
        self.synth.release(note)

    #Record currently played notes and modulations
    def record(self, record_channel_index=0):
        self.is_recording = True
        self.recordings[record_channel_index].clear()
        self.record_start_times[record_channel_index] = time.monotonic()
        print("Synth started recording")
        #TODO: Broadcast recording start for OLED to display
        #Keep track of time, and time of:
            #note presses,
            #modulations,
            #note releases
    
    #Ends recording. Sets recorded notes held when recording ends to be released at the end of playback 
    def end_record(self, record_channel_index=0):
        self.is_recording = False
        print("Synth ended recording")
        for note in self.held_notes.values():
                self.log_event("note-released", note)
        self.record_start_times[record_channel_index] = None

        #TODO: Broadcast recording pause for OLED to display

    def start_playback(self, record_channel_index=0):
        self.is_playback = True
        existing = self.existing_playbacks[record_channel_index]
        if existing is not None and not existing.done():
            print("Attempted to replay existing recording")
            self.resume_playback(record_channel_index=record_channel_index)
            return
        self.existing_playbacks[record_channel_index] = asyncio.create_task(
            self.play_record(record_channel_index=record_channel_index)
        )

    def pause_playback(self, record_channel_index=0):
        self.is_playback = False
        self.playback_pause_events[record_channel_index].clear()

    def resume_playback(self, record_channel_index=0):
        self.is_playback = True
        self.playback_pause_events[record_channel_index].set()

    async def play_record(self, record_channel_index=0):
        print("Synth playing record")
        pause_event = self.playback_pause_events[record_channel_index]
        #TODO: Complete play record
        #? Remove envelope and waveform?
        while True:
            prev_elapsed_time = 0
            events = self.recordings[record_channel_index]
            if not events:
                await asyncio.sleep(0.2) #prevent spinning if no events
                continue
            for event in events:
                delay = event['time'] - prev_elapsed_time
                prev_elapsed_time = event['time']
                await asyncio.sleep(delay)
                await pause_event.wait()
                await self.handle_record_event(event, self.recording_synths[record_channel_index])

        #wait for some time
    
    async def handle_record_event(self, event, synth : synthio.Synthesizer):
        event_type = event['type']
        if event_type == 'note-pressed':
            #TODO: Broadcast recording note played
            # ! Will retrigger active note if the played note is part of main scale b/c note is passed by ref
            # ? if want to fix, add a dict/list to track notes?
            note = event['value']
            synth.press(note)
        elif event_type == 'note-released':
            #TODO: Broadcast release
            note = event['value']
            synth.release(note)
        #TODO: Add separate case for a sustaining note that is pressed and held


    def log_event(self, event_type, value):
        for i in range(Synth_Wrapper.RECORDING_CHANNELS):
            if self.record_start_times[i] is not None:
                self.recordings[i].append({'time':time.monotonic() - self.record_start_times[i],
                                    'type':event_type,
                                    'value':value})