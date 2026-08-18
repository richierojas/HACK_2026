import synthio
import time
import asyncio
import array
from sound.scale import Scale
from sound.synth_presets import Synth_Presets

#To add:
#pitch bend
#vibrato/tremolo
#Volume
#Recording
#arpeggiation

#A synth that plays one type of sound
#TODO: Recording; each synth (type of sound) should be able to record and play their sounds
class Synth_Wrapper:
    RECORDING_CHANNELS = 1

    #synthio sums pressed notes with NO normalisation, so two notes at the
    #default amplitude of 1.0 already overflow full scale and hard-clip - and it
    #clips inside the Synthesizer, before the mixer level can do anything about
    #it. There are 8 buttons, so each note gets 1/8th-ish of the budget.
    #Measured on hardware, not calculated: 0.1 is clean, 0.13 audibly crackles,
    #0.2 is badly crunchy. The arithmetic said 0.13 should have been fine, so
    #something in the chain costs more headroom than the simple
    #voices x amplitude x waveform model predicts - do not raise this without
    #listening to a fast run of notes first.
    #
    #The envelope is what forces it so low: 0.8s decay plus 0.8s release means
    #a note sounds for ~1.6s after release, so all 8 overlap during quick
    #playing. Shortening the release is the way to make this louder.
    NOTE_AMPLITUDE = 0.1
    def __init__(self, scale : Scale, preset = Synth_Presets.PIANO, sample_rate = 22050):
        self.sample_rate = sample_rate
        self.scale = scale
        self.preset = Synth_Presets(preset)
        self.synth = synthio.Synthesizer(sample_rate=self.sample_rate, waveform=self.preset.waveform, envelope=self.preset.envelope)
        #Per-preset gain so every instrument sounds equally loud - see
        #Synth_Presets.PRESETS.
        self.amplitude = Synth_Wrapper.NOTE_AMPLITUDE * self.preset.gain
        #Shifts this instrument's whole range up or down - bass sits an octave
        #below the rest so it actually reads as a bass.
        self.octave_offset = self.preset.octave_offset
        self.filter_sweep = self.preset.filter_sweep
        self.notes = [synthio.Note(frequency=synthio.midi_to_hz(
                                       scale.get_midi_note(i, octave_offset=self.octave_offset)),
                                   amplitude=self.amplitude) for i in range(1, 9)]
        #One LFO per note, or None where the preset has no sweep. Parallel to
        #self.notes so press() can find a note's sweep by number.
        self.note_lfos = [self._attach_filter(n) for n in self.notes]

        #Vibrato applies to LIVE notes only. Loops keep whatever they were
        #recorded with, the same way retune() leaves their pitch alone.
        self.vibrato_lfo = synthio.LFO(rate=Synth_Wrapper.VIBRATO_RATE, scale=0.0)
        for note in self.notes:
            note.bend = self.vibrato_lfo
        #TODO: Add functionality for held notes
        self.held_notes = []
        self.recordings = [[] for _ in range(Synth_Wrapper.RECORDING_CHANNELS)]
        self.record_start_times = [None] * Synth_Wrapper.RECORDING_CHANNELS

        #Note numbers currently held down. Used to close out a recording so a
        #loop never repeats a press that has no matching release.
        self.held_numbers = set()

        self.is_recording = False
        self.is_playback = False

        #Playback gets its own Synthesizer and its own Note objects. self.notes
        #is reused for live playing, and pressing one Note on two synths at once
        #would make a looped note collide with the same note played by hand.
        self.recording_synths = [
            synthio.Synthesizer(sample_rate=self.sample_rate,
                                waveform=self.preset.waveform,
                                envelope=self.preset.envelope)
            for _ in range(Synth_Wrapper.RECORDING_CHANNELS)
        ]
        self.playback_notes = [
            [synthio.Note(frequency=synthio.midi_to_hz(
                              scale.get_midi_note(i, octave_offset=self.octave_offset)),
                          amplitude=self.amplitude) for i in range(1, 9)]
            for _ in range(Synth_Wrapper.RECORDING_CHANNELS)
        ]
        #Looped notes need their own sweeps too, or the loop would play back
        #dull while live notes ring bright.
        self.playback_lfos = [[self._attach_filter(n) for n in channel]
                              for channel in self.playback_notes]

        #How long each recording ran for, so the loop repeats on time instead of
        #restarting the instant the last note happens to fall.
        self.recording_lengths = [0] * Synth_Wrapper.RECORDING_CHANNELS

        self.existing_playbacks = [None] * Synth_Wrapper.RECORDING_CHANNELS
        #Set means running, cleared means paused
        self.playback_pause_events = [asyncio.Event() for _ in range(Synth_Wrapper.RECORDING_CHANNELS)]
        for pause_event in self.playback_pause_events:
            pause_event.set()

    #Vibrato is ONE LFO shared by every note on this instrument, not one per
    #note. Real vibrato moves the whole chord together anyway, and this costs a
    #single object instead of eight - which matters with six synthesizers and
    #48 filters already running.
    #Depth is in octaves: 0.015 is about 18 cents, a musical wobble rather than
    #a siren. Setting scale to 0 switches it off without removing the LFO.
    VIBRATO_RATE = 5.0
    VIBRATO_DEPTH = 0.015

    #Points in the ramp the filter sweep follows. 64 is plenty for a smooth
    #glide and keeps the array small.
    SWEEP_POINTS = 64

    def _attach_filter(self, note):
        """
        Give a note a low-pass filter that closes as the note decays, and return
        the LFO driving it so press() can retrigger the sweep.
        Returns None when this preset has no sweep configured.
        """
        if self.filter_sweep is None:
            return None

        start_hz, end_hz, seconds, q = self.filter_sweep

        #A one-shot descending ramp. LFO value runs +1 -> -1 across the
        #waveform, so scale/offset map that onto start_hz -> end_hz.
        ramp = array.array("h", [int(32767 - 65534 * i / (Synth_Wrapper.SWEEP_POINTS - 1))
                                 for i in range(Synth_Wrapper.SWEEP_POINTS)])
        lfo = synthio.LFO(waveform=ramp,
                          rate=1.0 / seconds,
                          once=True,                    #sweep once per pluck, do not loop
                          scale=(start_hz - end_hz) / 2,
                          offset=(start_hz + end_hz) / 2,
                          interpolate=True)
        note.filter = synthio.Biquad(synthio.FilterMode.LOW_PASS, frequency=lfo, Q=q)
        return lfo

    def set_vibrato(self, on):
        """Switch vibrato on or off by changing the shared LFO's depth."""
        self.vibrato_lfo.scale = Synth_Wrapper.VIBRATO_DEPTH if on else 0.0

    def warm_up(self):
        """
        Press and release every note once, up front.

        synthio allocates its per-note state the first time a given Note is
        pressed. Doing that mid-performance pauses audio rendering long enough
        to hear, which is why the FIRST hit of each button sounded crunchy while
        every hit after it was clean. Getting the allocation out of the way here
        - with the mixer levels still at 0 - moves that cost off the audio path.
        """
        for note in self.notes:
            self.synth.press(note)
        self.synth.release_all()

        for i in range(Synth_Wrapper.RECORDING_CHANNELS):
            for note in self.playback_notes[i]:
                self.recording_synths[i].press(note)
            self.recording_synths[i].release_all()

    def retune(self):
        """
        Rebuild the LIVE notes' pitch after the scale's key, quality or octave
        changes.

        Playback is deliberately left alone. A loop stays in the key it was
        recorded in, so you can lay down a part and then change key and play
        over the top of it. _freeze_playback_pitch() is what pins the loop's
        pitch, and it runs when recording starts.

        The Note objects are REUSED rather than replaced, so synthio does not
        have to allocate per-note state again - that allocation is what
        warm_up() exists to get out of the way. Anything sounding live is
        released first, otherwise a held note would change pitch mid-ring; the
        playback synth is untouched so a running loop does not stutter.
        """
        self.synth.release_all()
        self.held_numbers = set()

        for i in range(len(self.notes)):
            self.notes[i].frequency = synthio.midi_to_hz(
                self.scale.get_midi_note(i + 1, octave_offset=self.octave_offset))

    def _freeze_playback_pitch(self, record_channel_index=0):
        """
        Copy the live pitches into the playback notes.

        Recordings store note NUMBERS, not pitches, so playback needs to know
        which pitch each number meant. Capturing it when recording starts is
        what lets a loop keep its key while the live scale moves on. Without
        this, a loop recorded after a key change would play back in whatever
        key the instrument booted in.
        """
        notes = self.playback_notes[record_channel_index]
        for i in range(len(notes)):
            notes[i].frequency = self.notes[i].frequency

    #Play a note and buffer it for modulation
    #Note number should be 1-8 for scale notes
    #   For intervals before, -1 refers to 1 below the root
    def press(self, note_number):
        #No printing here. This runs on every note, and formatting a string then
        #pushing it over USB serial mid-performance starves the audio buffer.
        if 1 <= note_number <= 8:
            note = self.notes[note_number-1]
        else:
            note = synthio.Note(frequency=synthio.midi_to_hz(
                                    self.scale.get_midi_note(note_number,
                                                             octave_offset=self.octave_offset)),
                                amplitude=self.amplitude)

        #Broadcast it is being played and its frequency/preset
        #TODO?: Add a way to increase sustain and add to held notes if necessary
        #self.held_notes.append(note)
        #Recordings store the note NUMBER, not the Note object, so playback can
        #use its own Note and never share one with the live synth.
        #Restart the brightness sweep so every pluck starts bright. Without
        #this the filter stays wherever the previous note left it.
        if 1 <= note_number <= 8 and self.note_lfos[note_number - 1] is not None:
            self.note_lfos[note_number - 1].retrigger()

        self.held_numbers.add(note_number)
        self.log_event("note-pressed", note_number)
        self.synth.press(note)
        return note

    #Release a note from the active buffer
    def releaseActive(self, note):
        note_number = self._number_for(note)
        #Broadcast relase of note
        self.held_numbers.discard(note_number)
        self.log_event("note-released", note_number)
        self.synth.release(note)

    #self.notes holds one reused Note per scale degree, so identity gives the
    #number back. Returns None for a note built outside that range.
    def _number_for(self, note):
        for i in range(len(self.notes)):
            if self.notes[i] is note:
                return i + 1
        return None

    #Record currently played notes and modulations
    def record(self, record_channel_index=0):
        self.is_recording = True
        #Pin the loop to the key being played right now - see
        #_freeze_playback_pitch. Changing key later will not transpose it.
        self._freeze_playback_pitch(record_channel_index)
        self.recordings[record_channel_index].clear()
        self.recording_lengths[record_channel_index] = 0
        self.record_start_times[record_channel_index] = time.monotonic()
        print("Synth started recording")
        #TODO: Broadcast recording start for OLED to display

    def end_record(self, record_channel_index=0):
        start = self.record_start_times[record_channel_index]

        if start is not None:
            #Close out anything still held. Without this the loop replays a
            #press with no matching release and that note sustains forever.
            for note_number in list(self.held_numbers):
                self.log_event("note-released", note_number)

            #Loop length is how long recording ran, NOT when the last note fell,
            #so trailing silence is preserved and the repeat stays in time.
            self.recording_lengths[record_channel_index] = time.monotonic() - start

        self.is_recording = False
        self.record_start_times[record_channel_index] = None
        print("Synth ended recording")
        #TODO: Broadcast recording pause for OLED to display

    def start_playback(self, record_channel_index=0):
        """Start the loop, or resume it if it is already running."""
        self.is_playback = True
        self.playback_pause_events[record_channel_index].set()

        existing = self.existing_playbacks[record_channel_index]
        if existing is not None and not existing.done():
            return      #already looping; the line above un-paused it

        self.existing_playbacks[record_channel_index] = asyncio.create_task(
            self.play_record(record_channel_index=record_channel_index)
        )

    def pause_playback(self, record_channel_index=0):
        self.is_playback = False
        self.playback_pause_events[record_channel_index].clear()
        #Drop whatever is sounding, otherwise pausing leaves a note ringing
        self.recording_synths[record_channel_index].release_all()

    def resume_playback(self, record_channel_index=0):
        self.is_playback = True
        self.playback_pause_events[record_channel_index].set()

    #Loops the recording forever. Waits on the pause event before every event so
    #pausing takes effect mid-loop without losing its place.
    async def play_record(self, record_channel_index=0):
        synth = self.recording_synths[record_channel_index]
        notes = self.playback_notes[record_channel_index]
        pause_event = self.playback_pause_events[record_channel_index]

        print("Synth playing record")

        while True:
            events = self.recordings[record_channel_index]

            if not events:
                await asyncio.sleep(0.2)    #nothing recorded yet, do not spin
                continue

            previous_time = 0

            for event in events:
                delay = event['time'] - previous_time
                if delay > 0:
                    await asyncio.sleep(delay)
                previous_time = event['time']

                #Wait AFTER the sleep, immediately before the note sounds. If
                #this waited before the sleep instead, pausing during the sleep
                #would still let one more note through.
                await pause_event.wait()

                self.handle_record_event(event, synth, notes)

            #Hold out the remainder of the loop so the repeat lands on time
            tail = self.recording_lengths[record_channel_index] - previous_time
            if tail > 0:
                await asyncio.sleep(tail)

            #Safety net so a stuck note cannot carry into the next repeat
            synth.release_all()

    #Applies one recorded event to the playback synth. Reads 'event_type'
    #because that is the key log_event writes below.
    def handle_record_event(self, event, synth, notes):
        note_number = event['value']

        if note_number is None or not (1 <= note_number <= len(notes)):
            return

        note = notes[note_number - 1]

        if event['event_type'] == 'note-pressed':
            lfos = self.playback_lfos[0]
            if lfos[note_number - 1] is not None:
                lfos[note_number - 1].retrigger()
            synth.press(note)
        elif event['event_type'] == 'note-released':
            synth.release(note)


    def log_event(self, event_type, value):
        for i in range(Synth_Wrapper.RECORDING_CHANNELS):
            if self.record_start_times[i] is not None:
                self.recordings[i].append({'time':time.monotonic() - self.record_start_times[i],
                                    'event_type':event_type,
                                    'value':value})
