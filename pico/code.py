import buttons
import oled
import board
import time
import oled
import menu
import joystick
import slider
import json
import gc
import synthio
import asyncio
import audiobusio
import audiomixer

from sound.synth import Synth_Wrapper
from sound.scale import Scale
from sound.synth_presets import Synth_Presets

audio = audiobusio.I2SOut(
    bit_clock=board.GP1,
    word_select=board.GP2,
    data=board.GP0,
)

oled.init()

scale = Scale('C', 3, Scale.MAJOR)
#22050 halves synthio's per-sample work. Since playback runs on a second
#Synthesizer alongside the live one, 44100 could not keep the audio buffer fed
#and it crackled. Raise this back to 44100 only if the loop stays clean.
sample_rate = 22050

#Bytes of audio buffered ahead of the I2S output. Bigger = fewer dropouts but
#more latency between pressing a key and hearing it.
#4096 is about 93ms of slack at 22050Hz mono 16-bit. That is a lot of latency
#between pressing a key and hearing it - try 2048 (46ms) if it feels sluggish,
#and go back up if crackle returns during fast passages.
MIXER_BUFFER_SIZE = 4096

#How long to wait before the menu scrolls again while up/down is held.
MENU_REPEAT_DELAY = 0.20

#The joystick MUST stay physically connected. Its axes are analog inputs on
#GP26/GP27, and reading a floating ADC pin corrupts the next reading on GP28 -
#the volume slider - because the RP2350 puts every ADC channel through one
#converter. Unplug the joystick and the volume starts resetting to 0.

#Applied after synthio has summed its notes. Raising LIVE_LEVEL_MAX to 1.0 was
#tried and made things audibly worse, so these stay at the values measured as
#clean on hardware.
LIVE_LEVEL_MAX = 0.85
RECORD_LEVEL_MAX = 0.4

#Seconds between OLED redraws while the slider moves. Redrawing pushes ~1KB
#over I2C and blocks, which can starve the audio buffer, so cap the rate rather
#than redrawing on every reading.
VOLUME_DRAW_INTERVAL = 0.15
last_volume_draw = 0
#Deadband. The volume will not move until the reading shifts by this much, so
#residual jitter cannot make it crawl. Raise it if the volume still wanders.
VOLUME_CHANGE_THRESHOLD = 4 #percent
last_volume_percent = None

#Volume the instrument comes up at, regardless of where the slider is sitting.
#Full volume. The slider is out of the picture (see SLIDER_CONNECTED), so this
#is simply the volume the instrument runs at. Safe at 100: even 8 voices at
#once reach only ~0.61 of full scale, well clear of clipping.
STARTUP_VOLUME = 100

#Set False when the slider is disconnected or misbehaving. Volume then stays at
#STARTUP_VOLUME instead of chasing a floating input.
#A DISCONNECTED slider pin does not read zero - it floats, picking up ambient
#hum, and swings across the whole range on its own. Compare against a joystick
#axis: a healthy pot sitting still varies by a few hundred ADC counts, not tens
#of thousands. If the volume wanders with nothing touched, suspect the wiring
#before the code.
#The slider is disconnected in software. Its wiper reads as a floating input -
#wandering across 72% of its range untouched, while the joystick pots on the
#same ADC held within 400 counts - so it was moving the volume at random.
#Set back to True once the pot reads steady, and re-run the calibration sweep
#to set MIN/MAX in slider.py, which are currently meaningless.
SLIDER_CONNECTED = False

#How far the slider must physically move before it takes control of the volume.
#Until then STARTUP_VOLUME stands. Without this "soft takeover" the instrument
#adopts whatever the slider reads at power-up, so a slider left at the bottom -
#or one bad ADC reading during boot - comes up silent every time.
#Volume does not need checking 50 times a second, and every check costs a batch
#of ADC conversions plus a mux switch away from the joystick. Polling it slowly
#cuts the crosstalk and the CPU cost at once.
SLIDER_POLL_INTERVAL = 0.12     #seconds
last_slider_poll = 0

SLIDER_TAKEOVER_THRESHOLD = 5   #percent of travel
slider_start_percent = None     #where the slider sat at boot
slider_active = False           #True once it has been moved

#One wrapper per preset. Each gets its own live voice AND its own playback
#voice below, so a loop recorded on one instrument keeps playing while you
#switch to another and play over it.
#Order comes from Synth_Presets.ALL rather than dict key order - CircuitPython
#does not guarantee dictionaries preserve insertion order, and the first name
#here is what the instrument starts on.
INSTRUMENT_NAMES = list(Synth_Presets.ALL)

instruments = {}
for _preset in INSTRUMENT_NAMES:
    instruments[_preset] = Synth_Wrapper(scale, _preset, sample_rate=sample_rate)
voice_map = {} # name: {live:voice#, recording:voice#}

voice_index = 0
for name in INSTRUMENT_NAMES:
    instrument = instruments[name]

    live_voice = voice_index
    voice_index += 1
    #*only one recording per instrument for now
    rec_voice = voice_index
    voice_index += 1

    voice_map[name] = {"live":live_voice, "recording": rec_voice}

num_voices = voice_index

mixer = audiomixer.Mixer(
    voice_count=num_voices,
    sample_rate=sample_rate,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
    buffer_size=MIXER_BUFFER_SIZE,
)
audio.play(mixer)

for name, wrapper in instruments.items():
    voices = voice_map[name]
    mixer.voice[voices["live"]].play(wrapper.synth)
    mixer.voice[voices["recording"]].play(wrapper.recording_synths[0])
    #Start silent so the warm-up below makes no sound. apply_volume() sets the
    #real levels on the first pass of the main loop.
    mixer.voice[voices["live"]].level = 0
    mixer.voice[voices["recording"]].level = 0

#Press every note once while muted, so synthio allocates its per-note state now
#instead of during the first hit of each button. See Synth_Wrapper.warm_up.
for wrapper in instruments.values():
    wrapper.warm_up()

time.sleep(0.2)     #let the muted release tails render out
gc.collect()        #start the main loop with a tidy heap

active_instrument = INSTRUMENT_NAMES[0]
is_recording = False
volume_mode = menu.volume_menu.items[0] #Global, so the slider is a master volume by default

#Sent over USB serial to bridge/serial_bridge.py -> websocket server -> website
#Bridge drops any line that isn't JSON with a known type, so keep these on their own line
def send_event(event_type, value):
    print(json.dumps({"type": event_type, "value": value}))

#* Immediately changes volume to current slider upon change
def set_volume_mode(mode):
    """
    Switches volume between active, global, playbacks.
    """
    global volume_mode
    volume_mode = mode
    apply_volume(last_volume_percent)

def apply_volume(percent):
    fraction = percent / 100

    if volume_mode == "ACTIVE":
        voices = voice_map[active_instrument]
        mixer.voice[voices["live"]].level = fraction * LIVE_LEVEL_MAX

    elif volume_mode == "GLOBAL":
        #Master volume: everything, live and looped. ACTIVE and PLAYBACK exist
        #to ride one against the other, so GLOBAL has to move both.
        for name in INSTRUMENT_NAMES:
            voices = voice_map[name]
            mixer.voice[voices["live"]].level = fraction * LIVE_LEVEL_MAX
            mixer.voice[voices["recording"]].level = fraction * RECORD_LEVEL_MAX

    elif volume_mode == "PLAYBACK":
        for name in INSTRUMENT_NAMES:
            voices = voice_map[name]
            mixer.voice[voices["recording"]].level = fraction * RECORD_LEVEL_MAX

def get_active_instrument():
    return instruments[active_instrument]

def set_active_instrument(name):
    global active_instrument
    instrument = get_active_instrument()
    if instrument.is_recording:
        instrument.end_record()
        instrument.start_playback()
    active_instrument = name
    send_event("instrument", active_instrument)

#Naturals only. font5x7 has no "#" glyph and no lowercase, so C# or Bb would
#render as a blank on the OLED even though the Scale class understands them.
#Arpeggiator. With it on, holding several buttons plays them one at a time in
#a repeating cycle instead of sounding together as a chord. It costs nothing on
#the audio side - it plays notes you could already play, just in sequence.
arp_enabled = False
ARP_RATES = (4, 6, 8, 12)       #notes per second
arp_rate_index = 2
arp_held = []                   #buttons currently down, in the order pressed
arp_index = 0
arp_last_step = 0
arp_note = None                 #note currently sounding, kept so it can be released

vibrato_enabled = False

KEY_LETTERS = ("C", "D", "E", "F", "G", "A", "B")

#Above octave 3 the wavetable starts to alias: the tables carry 32 harmonics,
#and at octave 4 the top note's 32nd harmonic lands past the 11kHz Nyquist and
#folds back as harshness. 5 is allowed but is the bright, gritty end.
MIN_OCTAVE = 2
MAX_OCTAVE = 5


def refresh_effects_menu():
    menu.effects_menu.items[0] = "ARP " + ("ON" if arp_enabled else "OFF")
    menu.effects_menu.items[1] = "ARP RATE " + str(ARP_RATES[arp_rate_index])
    menu.effects_menu.items[2] = "VIBRATO " + ("ON" if vibrato_enabled else "OFF")


def toggle_arp():
    global arp_enabled, arp_note, arp_index

    arp_enabled = not arp_enabled

    #Clear down whichever mode is being left, so nothing is stranded sounding
    if arp_enabled:
        for number in list(active_notes.keys()):
            get_active_instrument().releaseActive(active_notes.pop(number))
    else:
        if arp_note is not None:
            get_active_instrument().releaseActive(arp_note)
            arp_note = None
        del arp_held[:]

    arp_index = 0
    refresh_effects_menu()


def cycle_arp_rate():
    global arp_rate_index
    arp_rate_index = (arp_rate_index + 1) % len(ARP_RATES)
    refresh_effects_menu()


def toggle_vibrato():
    global vibrato_enabled
    vibrato_enabled = not vibrato_enabled
    for wrapper in instruments.values():
        wrapper.set_vibrato(vibrato_enabled)
    refresh_effects_menu()


def refresh_key_menu():
    """Put the current values into the KEY menu labels so the screen shows what
    the scale actually is, rather than three static words."""
    menu.key_menu.items[0] = "KEY " + scale.key
    menu.key_menu.items[1] = "QUALITY " + ("MAJOR" if scale.quality == Scale.MAJOR else "MINOR")
    menu.key_menu.items[2] = "OCTAVE " + str(scale.octave)


def retune_all():
    """Every instrument shares one Scale object, so they all need re-pitching."""
    active_notes.clear()
    for wrapper in instruments.values():
        wrapper.retune()
    refresh_key_menu()


def cycle_key():
    index = KEY_LETTERS.index(scale.key) if scale.key in KEY_LETTERS else 0
    scale.key = KEY_LETTERS[(index + 1) % len(KEY_LETTERS)]
    retune_all()


def cycle_quality():
    scale.quality = Scale.MINOR if scale.quality == Scale.MAJOR else Scale.MAJOR
    retune_all()


def cycle_octave():
    scale.octave += 1
    if scale.octave > MAX_OCTAVE:
        scale.octave = MIN_OCTAVE
    retune_all()


def select_and_handle():
    select_tuple = menu.select() #None if submenu, (menu, item_string) if item
    if select_tuple is None:
        return
    item_menu = select_tuple[0]
    item = select_tuple[1]
    if(item_menu is menu.instruments_menu):
        set_active_instrument(item)
    elif(item_menu is menu.record_menu):
        if item == menu.record_menu.items[0]: #record/stop record
            toggle_record()
        elif item == menu.record_menu.items[1]: #play/pause record
            toggle_playback(active_instrument)
        elif item == menu.record_menu.items[2]: # pause all
            pause_all_playback()
        elif item == menu.record_menu.items[3]: #play all
            play_all_playback()
    elif(item_menu is menu.volume_menu):
        set_volume_mode(item)
    elif(item_menu is menu.effects_menu):
        index = item_menu.selected
        if index == 0:
            toggle_arp()
        elif index == 1:
            cycle_arp_rate()
        elif index == 2:
            toggle_vibrato()
    elif(item_menu is menu.key_menu):
        #Dispatch on position, not on the label text - these labels carry the
        #current value and change every time you cycle them.
        index = item_menu.selected
        if index == 0:
            cycle_key()
        elif index == 1:
            cycle_quality()
        elif index == 2:
            cycle_octave()

#TODO: Add pausing and playing
def toggle_record():
    instrument = get_active_instrument()
    if not instrument.is_recording:
        instrument.record()
    else:
        instrument.end_record()
        instrument.start_playback()

def pause_all_playback():
    for instrument in INSTRUMENT_NAMES:
        pause_playback(instrument)

def play_all_playback():
    for instrument in INSTRUMENT_NAMES:
        play_playback(instrument)

#toggles pause/resume for individual instrument
def toggle_playback(instrument_name):
    instrument = instruments[instrument_name]
    if instrument.is_playback:
        pause_playback(instrument_name)
    else:
        play_playback(instrument_name)

def play_playback(instrument_name):
    instrument = instruments[instrument_name]
    instrument.start_playback() #resumes if already

def pause_playback(instrument_name):
    instrument = instruments[instrument_name]
    instrument.pause_playback()

active_notes = {}

def on_button_pressed(button_number: int):
    if arp_enabled:
        #The arpeggiator decides when this sounds - just note that it is held.
        if button_number not in arp_held:
            arp_held.append(button_number)
        return

    note = get_active_instrument().press(button_number)
    active_notes[button_number] = note

def on_button_released(button_number: int, duration):
    if arp_enabled:
        if button_number in arp_held:
            arp_held.remove(button_number)
        return

    if button_number in active_notes:
        note = active_notes.pop(button_number)
        get_active_instrument().releaseActive(note)

def step_arp(now):
    """Advance the arpeggio. Called every pass of the main loop."""
    global arp_index, arp_last_step, arp_note

    instrument = get_active_instrument()

    if not arp_held:
        if arp_note is not None:
            instrument.releaseActive(arp_note)
            arp_note = None
        return

    if now - arp_last_step < 1.0 / ARP_RATES[arp_rate_index]:
        return
    arp_last_step = now

    #One note at a time: release the last before pressing the next
    if arp_note is not None:
        instrument.releaseActive(arp_note)

    arp_index = (arp_index + 1) % len(arp_held)
    arp_note = instrument.press(arp_held[arp_index])

#Menu control, all on the joystick now that the keypad is gone:
#   up / down    scroll the menu, repeating while held
#   right/click  enter the highlighted item
#   left         go back up a level
#Each redraws, and a redraw blocks the audio while it writes, so only redraw
#where something actually changed.

def on_joystick_up():
    menu.move_up()
    menu.draw()

def on_joystick_down():
    menu.move_down()
    menu.draw()

def on_joystick_right():
    select_and_handle()
    menu.draw()

def on_joystick_left():
    menu.back()
    menu.draw()

def on_joystick_pressed():
    select_and_handle()
    menu.draw()

async def main_loop():
    global last_volume_percent, last_volume_draw
    global slider_start_percent, slider_active, last_slider_poll

    #Come up at a known-good volume instead of trusting the slider's resting
    #position. The slider takes over as soon as it is actually moved.
    apply_volume(STARTUP_VOLUME)
    last_volume_percent = STARTUP_VOLUME
    menu.volume.value = STARTUP_VOLUME
    send_event("volume", STARTUP_VOLUME)

    refresh_key_menu()      #labels must show the real scale before the first draw
    refresh_effects_menu()
    menu.draw()
    send_event("instrument", active_instrument) #initial state so the website starts in sync
    last_move = 0
    while True:
        now = time.monotonic()

        #only use slider for volume for now
        if SLIDER_CONNECTED and now - last_slider_poll >= SLIDER_POLL_INTERVAL:
            last_slider_poll = now
            volume_percent = slider.percent()

            if slider_start_percent is None:
                slider_start_percent = volume_percent

            if not slider_active and abs(volume_percent - slider_start_percent) >= SLIDER_TAKEOVER_THRESHOLD:
                slider_active = True

            if slider_active and abs(volume_percent - last_volume_percent) >= VOLUME_CHANGE_THRESHOLD:
                apply_volume(volume_percent)
                last_volume_percent = volume_percent
                menu.volume.value = volume_percent
                send_event("volume", volume_percent)

                #Redraw so the bar tracks the slider, but rate-limited: a full
                #OLED write blocks long enough to glitch a note if it happens
                #too often.
                if now - last_volume_draw >= VOLUME_DRAW_INTERVAL:
                    menu.draw()
                    last_volume_draw = now

        # Scrolling repeats while up/down is held
        if joystick.up() and now - last_move > MENU_REPEAT_DELAY:
            on_joystick_up()
            last_move = now

        elif joystick.down() and now - last_move > MENU_REPEAT_DELAY:
            on_joystick_down()
            last_move = now

        # Enter and back fire ONCE per deflection. Without waiting for the
        # stick to recentre, one flick would select repeatedly and run straight
        # down through several menu levels.
        elif joystick.right():
            on_joystick_right()
            while joystick.right():
                await asyncio.sleep(0)
            await asyncio.sleep(0.1)

        elif joystick.left():
            on_joystick_left()
            while joystick.left():
                await asyncio.sleep(0)
            await asyncio.sleep(0.1)

        # Clicking the stick selects, same as pushing right
        if joystick.pressed():
            on_joystick_pressed()

            while joystick.pressed():
                await asyncio.sleep(0) #pass but async

            await asyncio.sleep(0.1)

        #HANDLE BUTTONS
        events = buttons.update()
        for eventraw in events:
            event = json.loads(eventraw)

            if event["type"] == "button-pressed":
                button_number = event["value"]["button"]
                print(eventraw) #already {"type":"button-pressed",...}, forwarded as-is
                on_button_pressed(button_number)

                # synth.note_on(...)

            elif event["type"] == "button-released":
                duration = event["value"]["duration"]
                button_number = event["value"]["button"]
                print(eventraw) #already {"type":"button-released",...} with duration
                on_button_released(button_number, duration)

        if arp_enabled:
            step_arp(now)

        await asyncio.sleep(0.02)

asyncio.run(main_loop())

